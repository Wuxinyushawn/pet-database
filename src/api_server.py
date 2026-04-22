"""REST API server for the pet database.

Adds authentication/authorization and audit logging for all write APIs.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Generator

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).parent.parent / "pet_database.db"
SESSION_SECRET = os.getenv("PET_API_SESSION_SECRET", "pet-db-dev-secret-change-me")
SESSION_TTL_HOURS = 12

app = FastAPI(title="Pet Database REST API", version="1.1.0")


# ── Database Management ───────────────────────────────────────────────────────

@contextmanager
def db_session(*, write: bool = False) -> Generator[sqlite3.Connection, None, None]:
    """Manage DB connection + transaction in one place."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        if write:
            conn.commit()
    except Exception:
        if write:
            conn.rollback()
        raise
    finally:
        conn.close()


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _next_id(conn: sqlite3.Connection, table: str, id_column: str) -> int:
    cur = conn.execute(f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table}")
    row = cur.fetchone()
    return int(row["next_id"])


def _write_success(data: Any = None) -> dict[str, Any]:
    return {"success": True, "data": data, "error": None}


def _write_error(message: str) -> dict[str, Any]:
    return {"success": False, "data": None, "error": message}


def _ensure_audit_table() -> None:
    with db_session(write=True) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS AUDIT_LOG (
                audit_id INTEGER PRIMARY KEY,
                actor_username VARCHAR(100) NOT NULL,
                actor_role VARCHAR(50) NOT NULL,
                action VARCHAR(100) NOT NULL,
                entity VARCHAR(100) NOT NULL,
                entity_id VARCHAR(100),
                before_state TEXT,
                after_state TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


@app.on_event("startup")
def startup() -> None:
    _ensure_audit_table()


# ── Error Handling ────────────────────────────────────────────────────────────

@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(_, exc: sqlite3.Error):
    return JSONResponse(status_code=500, content={"detail": f"Database error: {exc}"})


@app.exception_handler(Exception)
async def generic_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})


# ── Auth / RBAC ───────────────────────────────────────────────────────────────

class LoginBody(BaseModel):
    username: str
    password: str


class SessionUser(BaseModel):
    username: str
    role: str


# demo accounts; can be replaced by DB-backed users later
USER_STORE: dict[str, dict[str, str]] = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
    "coordinator": {"password": "coord123", "role": "volunteer_coordinator"},
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {
        "applications:create",
        "applications:review",
        "adoptions:create",
        "followups:create",
        "audit:read",
    },
    "staff": {
        "applications:create",
        "applications:review",
        "adoptions:create",
        "followups:create",
        "audit:read",
    },
    "volunteer_coordinator": {
        "followups:create",
        "audit:read",
    },
}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


def _create_session_token(user: SessionUser) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)).timestamp()),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    body = _b64url(payload_bytes)
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    return f"{body}.{_b64url(signature)}"


def _verify_session_token(token: str) -> SessionUser:
    try:
        body, sig = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token") from exc

    expected_sig = hmac.new(SESSION_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url(expected_sig), sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session signature")

    payload = json.loads(_b64url_decode(body))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return SessionUser(username=payload["sub"], role=payload["role"])


def get_current_user(authorization: str | None = Header(default=None)) -> SessionUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return _verify_session_token(authorization.removeprefix("Bearer ").strip())


def require_permission(permission: str):
    def _check(user: SessionUser = Depends(get_current_user)) -> SessionUser:
        permissions = ROLE_PERMISSIONS.get(user.role, set())
        if permission not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role {user.role} lacks {permission}")
        return user

    return _check


def _audit_log(
    conn: sqlite3.Connection,
    *,
    actor: SessionUser,
    action: str,
    entity: str,
    entity_id: str | None,
    before_state: dict[str, Any] | None,
    after_state: dict[str, Any] | None,
) -> None:
    audit_id = _next_id(conn, "AUDIT_LOG", "audit_id")
    conn.execute(
        """
        INSERT INTO AUDIT_LOG (
            audit_id, actor_username, actor_role, action, entity, entity_id,
            before_state, after_state, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            audit_id,
            actor.username,
            actor.role,
            action,
            entity,
            entity_id,
            json.dumps(before_state, ensure_ascii=False) if before_state is not None else None,
            json.dumps(after_state, ensure_ascii=False) if after_state is not None else None,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


# ── Request Schemas ───────────────────────────────────────────────────────────

class CreateApplicationBody(BaseModel):
    applicant_id: int
    pet_id: int
    reason: str | None = None
    application_date: date | None = None
    status: str = "under_review"


class ReviewApplicationBody(BaseModel):
    status: str = Field(description="Typical values: approved/rejected")
    reviewer_name: str | None = None
    decision_note: str | None = None
    reviewed_date: date | None = None


class CreateAdoptionBody(BaseModel):
    application_id: int
    adoption_date: date | None = None
    final_adoption_fee: Decimal | None = None
    handover_note: str | None = None


class CreateFollowupBody(BaseModel):
    adoption_id: int
    followup_date: date | None = None
    followup_type: str | None = None
    pet_condition: str | None = None
    adopter_feedback: str | None = None
    result_status: str | None = None
    staff_note: str | None = None


# ── Auth Endpoint ─────────────────────────────────────────────────────────────

@app.post("/auth/login")
def login(payload: LoginBody) -> dict[str, Any]:
    user = USER_STORE.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    session_user = SessionUser(username=payload.username, role=user["role"])
    token = _create_session_token(session_user)
    return {"data": {"token": token, "user": session_user.model_dump(), "expires_in_hours": SESSION_TTL_HOURS}}


# ── Read Endpoints ────────────────────────────────────────────────────────────

@app.get("/auth/me")
def me(user: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    return {"data": user.model_dump()}


@app.get("/pets")
def get_pets(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT pet_id, shelter_id, name, species, breed, sex, color, intake_date, status
            FROM PET
            ORDER BY pet_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/applications")
def get_applications(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT aa.application_id, aa.applicant_id, aa.pet_id, aa.application_date, aa.status,
                   aa.reason, aa.reviewed_date, aa.reviewer_name, aa.decision_note
            FROM ADOPTION_APPLICATION aa
            ORDER BY aa.application_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/adoptions")
def get_adoptions(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT adoption_id, application_id, adoption_date, final_adoption_fee, handover_note
            FROM ADOPTION_RECORD
            ORDER BY adoption_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/followups")
def get_followups(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT followup_id, adoption_id, followup_date, followup_type,
                   pet_condition, adopter_feedback, result_status, staff_note
            FROM FOLLOW_UP
            ORDER BY followup_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}




@app.get("/medical-records")
def get_medical_records(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT mr.record_id, p.name AS pet_name, mr.visit_date, mr.record_type, mr.vet_name
            FROM MEDICAL_RECORD mr
            JOIN PET p ON p.pet_id = mr.pet_id
            ORDER BY mr.record_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/vaccinations")
def get_vaccinations(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT v.vaccination_id, p.name AS pet_name, v.vaccine_name, v.next_due_date
            FROM VACCINATION v
            JOIN PET p ON p.pet_id = v.pet_id
            ORDER BY v.vaccination_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/volunteers")
def get_volunteers(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT volunteer_id, full_name, email, join_date
            FROM VOLUNTEER
            ORDER BY volunteer_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/assignments")
def get_assignments(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT ca.assignment_id, v.full_name AS volunteer_name, p.name AS pet_name,
                   ca.shift, ca.task_type, ca.status
            FROM CARE_ASSIGNMENT ca
            JOIN VOLUNTEER v ON v.volunteer_id = ca.volunteer_id
            JOIN PET p ON p.pet_id = ca.pet_id
            ORDER BY ca.assignment_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/audit-logs/recent")
def get_recent_audit_logs(
    limit: int = 20,
    _: SessionUser = Depends(require_permission("audit:read")),
) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT audit_id, actor_username, actor_role, action, entity, entity_id,
                   before_state, after_state, created_at
            FROM AUDIT_LOG
            ORDER BY audit_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


# ── Write Endpoints ───────────────────────────────────────────────────────────

@app.post("/applications")
def create_application(
    payload: CreateApplicationBody,
    user: SessionUser = Depends(require_permission("applications:create")),
):
    try:
        with db_session(write=True) as conn:
            application_id = _next_id(conn, "ADOPTION_APPLICATION", "application_id")
            after_state = {
                "application_id": application_id,
                "applicant_id": payload.applicant_id,
                "pet_id": payload.pet_id,
                "application_date": (payload.application_date or date.today()).isoformat(),
                "status": payload.status,
                "reason": payload.reason,
            }
            conn.execute(
                """
                INSERT INTO ADOPTION_APPLICATION (
                    application_id, applicant_id, pet_id, application_date,
                    status, reason, reviewed_date, reviewer_name, decision_note
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
                """,
                (
                    application_id,
                    payload.applicant_id,
                    payload.pet_id,
                    after_state["application_date"],
                    payload.status,
                    payload.reason,
                ),
            )
            _audit_log(
                conn,
                actor=user,
                action="create_application",
                entity="ADOPTION_APPLICATION",
                entity_id=str(application_id),
                before_state=None,
                after_state=after_state,
            )
        return _write_success({"application_id": application_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.patch("/applications/{application_id}/review")
@app.post("/applications/{application_id}/review")
def review_application(
    application_id: int,
    payload: ReviewApplicationBody,
    user: SessionUser = Depends(require_permission("applications:review")),
):
    try:
        with db_session(write=True) as conn:
            existing = conn.execute(
                "SELECT * FROM ADOPTION_APPLICATION WHERE application_id = ?",
                (application_id,),
            ).fetchone()
            if not existing:
                return JSONResponse(status_code=404, content=_write_error(f"Application {application_id} not found"))

            before_state = dict(existing)
            reviewed_date = (payload.reviewed_date or date.today()).isoformat()
            conn.execute(
                """
                UPDATE ADOPTION_APPLICATION
                SET status = ?, reviewer_name = ?, decision_note = ?, reviewed_date = ?
                WHERE application_id = ?
                """,
                (
                    payload.status,
                    payload.reviewer_name,
                    payload.decision_note,
                    reviewed_date,
                    application_id,
                ),
            )
            after_state = {
                **before_state,
                "status": payload.status,
                "reviewer_name": payload.reviewer_name,
                "decision_note": payload.decision_note,
                "reviewed_date": reviewed_date,
            }
            _audit_log(
                conn,
                actor=user,
                action="review_application",
                entity="ADOPTION_APPLICATION",
                entity_id=str(application_id),
                before_state=before_state,
                after_state=after_state,
            )
        return _write_success({"application_id": application_id, "status": payload.status})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/adoptions")
def create_adoption(
    payload: CreateAdoptionBody,
    user: SessionUser = Depends(require_permission("adoptions:create")),
):
    try:
        with db_session(write=True) as conn:
            adoption_id = _next_id(conn, "ADOPTION_RECORD", "adoption_id")
            after_state = {
                "adoption_id": adoption_id,
                "application_id": payload.application_id,
                "adoption_date": (payload.adoption_date or date.today()).isoformat(),
                "final_adoption_fee": str(payload.final_adoption_fee) if payload.final_adoption_fee is not None else None,
                "handover_note": payload.handover_note,
            }
            conn.execute(
                """
                INSERT INTO ADOPTION_RECORD (
                    adoption_id, application_id, adoption_date, final_adoption_fee, handover_note
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    adoption_id,
                    payload.application_id,
                    after_state["adoption_date"],
                    payload.final_adoption_fee,
                    payload.handover_note,
                ),
            )
            _audit_log(
                conn,
                actor=user,
                action="create_adoption",
                entity="ADOPTION_RECORD",
                entity_id=str(adoption_id),
                before_state=None,
                after_state=after_state,
            )
        return _write_success({"adoption_id": adoption_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/followups")
def create_followup(
    payload: CreateFollowupBody,
    user: SessionUser = Depends(require_permission("followups:create")),
):
    try:
        with db_session(write=True) as conn:
            followup_id = _next_id(conn, "FOLLOW_UP", "followup_id")
            after_state = {
                "followup_id": followup_id,
                "adoption_id": payload.adoption_id,
                "followup_date": (payload.followup_date or date.today()).isoformat(),
                "followup_type": payload.followup_type,
                "pet_condition": payload.pet_condition,
                "adopter_feedback": payload.adopter_feedback,
                "result_status": payload.result_status,
                "staff_note": payload.staff_note,
            }
            conn.execute(
                """
                INSERT INTO FOLLOW_UP (
                    followup_id, adoption_id, followup_date, followup_type,
                    pet_condition, adopter_feedback, result_status, staff_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    followup_id,
                    payload.adoption_id,
                    after_state["followup_date"],
                    payload.followup_type,
                    payload.pet_condition,
                    payload.adopter_feedback,
                    payload.result_status,
                    payload.staff_note,
                ),
            )
            _audit_log(
                conn,
                actor=user,
                action="create_followup",
                entity="FOLLOW_UP",
                entity_id=str(followup_id),
                before_state=None,
                after_state=after_state,
            )
        return _write_success({"followup_id": followup_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
