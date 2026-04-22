"""REST API server for the pet database with auth, RBAC and audit logging."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Generator

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from audit_utils import ensure_audit_tables, write_audit_log, write_status_audit_log
from security import ROLE_PERMISSIONS, USER_STORE, create_session_token, verify_session_token

DB_PATH = Path(__file__).parent.parent / "pet_database.db"
SESSION_SECRET = os.getenv("PET_API_SESSION_SECRET", "pet-db-dev-secret-change-me")
SESSION_TTL_HOURS = 12

app = FastAPI(title="Pet Database REST API", version="1.2.0")

APPLICATION_STATUS_PENDING = "Pending"
APPLICATION_STATUS_APPROVED = "Approved"
APPLICATION_STATUS_REJECTED = "Rejected"

PET_STATUS_AVAILABLE = "Available"
PET_STATUS_RESERVED = "Reserved"
PET_STATUS_ADOPTED = "Adopted"


@contextmanager
def db_session(*, write: bool = False) -> Generator[sqlite3.Connection, None, None]:
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


def _normalize_application_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized == "pending":
        return APPLICATION_STATUS_PENDING
    if normalized == "approved":
        return APPLICATION_STATUS_APPROVED
    if normalized == "rejected":
        return APPLICATION_STATUS_REJECTED
    raise ValueError("Invalid application status. Allowed values: Pending, Approved, Rejected")


def _normalize_pet_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized == "available":
        return PET_STATUS_AVAILABLE
    if normalized == "reserved":
        return PET_STATUS_RESERVED
    if normalized == "adopted":
        return PET_STATUS_ADOPTED
    return value


def _ensure_audit_tables() -> None:
    with db_session(write=True) as conn:
        ensure_audit_tables(conn)


@app.on_event("startup")
def startup() -> None:
    _ensure_audit_tables()


@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(_, exc: sqlite3.Error):
    return JSONResponse(status_code=500, content={"detail": f"Database error: {exc}"})


@app.exception_handler(Exception)
async def generic_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})


class LoginBody(BaseModel):
    username: str
    password: str


class SessionUser(BaseModel):
    username: str
    role: str


def require_permission(permission: str):
    def _check(user: SessionUser = Depends(get_current_user)) -> SessionUser:
        if permission not in ROLE_PERMISSIONS.get(user.role, set()):
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
    write_audit_log(
        conn,
        next_id=_next_id(conn, "AUDIT_LOG", "audit_id"),
        actor_username=actor.username,
        actor_role=actor.role,
        action=action,
        entity=entity,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
    )


def _status_audit_log(
    conn: sqlite3.Connection,
    *,
    entity_type: str,
    entity_id: int,
    field_name: str,
    old_value: str | None,
    new_value: str,
    changed_by: str | None,
    note: str | None,
) -> None:
    write_status_audit_log(
        conn,
        next_id=_next_id(conn, "STATUS_AUDIT_LOG", "audit_id"),
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
        note=note,
    )


class CreateApplicationBody(BaseModel):
    applicant_id: int
    pet_id: int
    reason: str | None = None
    application_date: date | None = None
    status: str = APPLICATION_STATUS_PENDING


class ReviewApplicationBody(BaseModel):
    status: str = Field(description="Allowed values: Approved/Rejected")
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


@app.post("/auth/login")
def login(payload: LoginBody) -> dict[str, Any]:
    user = USER_STORE.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    session_user = SessionUser(username=payload.username, role=user["role"])
    return {"data": {"token": create_session_token(username=session_user.username, role=session_user.role, secret=SESSION_SECRET, ttl_hours=SESSION_TTL_HOURS), "user": session_user.model_dump(), "expires_in_hours": SESSION_TTL_HOURS}}


@app.get("/auth/me")
def me(user: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    return {"data": user.model_dump()}


@app.get("/pets")
def get_pets(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT pet_id, shelter_id, name, species, breed, sex, color, intake_date, status FROM PET ORDER BY pet_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/applications")
def get_applications(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT application_id, applicant_id, pet_id, application_date, status, reason, reviewed_date, reviewer_name, decision_note FROM ADOPTION_APPLICATION ORDER BY application_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/adoptions")
def get_adoptions(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT adoption_id, application_id, adoption_date, final_adoption_fee, handover_note FROM ADOPTION_RECORD ORDER BY adoption_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/followups")
def get_followups(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT followup_id, adoption_id, followup_date, followup_type, pet_condition, adopter_feedback, result_status, staff_note FROM FOLLOW_UP ORDER BY followup_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/medical-records")
@app.get("/medical/records")
def get_medical_records(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT mr.record_id, p.name AS pet_name, mr.visit_date, mr.record_type, mr.vet_name FROM MEDICAL_RECORD mr JOIN PET p ON p.pet_id = mr.pet_id ORDER BY mr.record_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/vaccinations")
@app.get("/medical/vaccinations")
def get_vaccinations(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT v.vaccination_id, p.name AS pet_name, v.vaccine_name, v.next_due_date FROM VACCINATION v JOIN PET p ON p.pet_id = v.pet_id ORDER BY v.vaccination_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/volunteers")
def get_volunteers(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT volunteer_id, full_name, email, join_date FROM VOLUNTEER ORDER BY volunteer_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/assignments")
@app.get("/volunteers/assignments")
def get_assignments(_: SessionUser = Depends(get_current_user)) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT ca.assignment_id, v.full_name AS volunteer_name, p.name AS pet_name, ca.shift, ca.task_type, ca.status FROM CARE_ASSIGNMENT ca JOIN VOLUNTEER v ON v.volunteer_id = ca.volunteer_id JOIN PET p ON p.pet_id = ca.pet_id ORDER BY ca.assignment_id").fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/audit-logs/recent")
def get_recent_audit_logs(limit: int = 20, _: SessionUser = Depends(require_permission("audit:read"))) -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute("SELECT audit_id, actor_username, actor_role, action, entity, entity_id, before_state, after_state, created_at FROM AUDIT_LOG ORDER BY audit_id DESC LIMIT ?", (limit,)).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.post("/applications")
def create_application(payload: CreateApplicationBody, user: SessionUser = Depends(require_permission("applications:create"))):
    try:
        with db_session(write=True) as conn:
            target_status = _normalize_application_status(payload.status)
            if target_status != APPLICATION_STATUS_PENDING:
                return JSONResponse(status_code=400, content=_write_error("New applications must start with Pending status"))

            pet = conn.execute("SELECT pet_id, status FROM PET WHERE pet_id = ?", (payload.pet_id,)).fetchone()
            if not pet:
                return JSONResponse(status_code=404, content=_write_error(f"Pet {payload.pet_id} not found"))

            old_pet_status = _normalize_pet_status(str(pet["status"]))
            if old_pet_status == PET_STATUS_ADOPTED:
                return JSONResponse(status_code=400, content=_write_error("Cannot create application for an adopted pet"))

            application_id = _next_id(conn, "ADOPTION_APPLICATION", "application_id")
            application_date = (payload.application_date or date.today()).isoformat()
            conn.execute(
                """
                INSERT INTO ADOPTION_APPLICATION (
                    application_id, applicant_id, pet_id, application_date,
                    status, reason, reviewed_date, reviewer_name, decision_note
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
                """,
                (application_id, payload.applicant_id, payload.pet_id, application_date, target_status, payload.reason),
            )
            conn.execute("UPDATE PET SET status = ? WHERE pet_id = ?", (PET_STATUS_RESERVED, payload.pet_id))

            _audit_log(
                conn,
                actor=user,
                action="create_application",
                entity="ADOPTION_APPLICATION",
                entity_id=str(application_id),
                before_state=None,
                after_state={"application_id": application_id, "applicant_id": payload.applicant_id, "pet_id": payload.pet_id, "application_date": application_date, "status": target_status, "reason": payload.reason},
            )
            _status_audit_log(conn, entity_type="ADOPTION_APPLICATION", entity_id=application_id, field_name="status", old_value=None, new_value=target_status, changed_by=user.username, note="Application created")
            _status_audit_log(conn, entity_type="PET", entity_id=payload.pet_id, field_name="status", old_value=old_pet_status, new_value=PET_STATUS_RESERVED, changed_by=user.username, note=f"Application {application_id} created")

        return _write_success({"application_id": application_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.patch("/applications/{application_id}/review")
@app.post("/applications/{application_id}/review")
def review_application(application_id: int, payload: ReviewApplicationBody, user: SessionUser = Depends(require_permission("applications:review"))):
    try:
        with db_session(write=True) as conn:
            target_status = _normalize_application_status(payload.status)
            if target_status not in (APPLICATION_STATUS_APPROVED, APPLICATION_STATUS_REJECTED):
                return JSONResponse(status_code=400, content=_write_error("Review status must be Approved or Rejected"))

            existing = conn.execute("SELECT * FROM ADOPTION_APPLICATION WHERE application_id = ?", (application_id,)).fetchone()
            if not existing:
                return JSONResponse(status_code=404, content=_write_error(f"Application {application_id} not found"))

            current_status = _normalize_application_status(str(existing["status"]))
            if current_status != APPLICATION_STATUS_PENDING:
                return JSONResponse(status_code=400, content=_write_error("Application status transition allowed only from Pending to Approved/Rejected"))

            reviewed_date = (payload.reviewed_date or date.today()).isoformat()
            conn.execute(
                "UPDATE ADOPTION_APPLICATION SET status = ?, reviewer_name = ?, decision_note = ?, reviewed_date = ? WHERE application_id = ?",
                (target_status, payload.reviewer_name, payload.decision_note, reviewed_date, application_id),
            )

            _audit_log(
                conn,
                actor=user,
                action="review_application",
                entity="ADOPTION_APPLICATION",
                entity_id=str(application_id),
                before_state=dict(existing),
                after_state={**dict(existing), "status": target_status, "reviewer_name": payload.reviewer_name, "decision_note": payload.decision_note, "reviewed_date": reviewed_date},
            )
            _status_audit_log(conn, entity_type="ADOPTION_APPLICATION", entity_id=application_id, field_name="status", old_value=current_status, new_value=target_status, changed_by=user.username, note=payload.decision_note)

            if target_status == APPLICATION_STATUS_REJECTED:
                pet_id = int(existing["pet_id"])
                other_active = conn.execute(
                    "SELECT COUNT(*) AS c FROM ADOPTION_APPLICATION WHERE pet_id = ? AND application_id <> ? AND status IN (?, ?)",
                    (pet_id, application_id, APPLICATION_STATUS_PENDING, APPLICATION_STATUS_APPROVED),
                ).fetchone()
                pet_row = conn.execute("SELECT status FROM PET WHERE pet_id = ?", (pet_id,)).fetchone()
                if pet_row:
                    old_pet_status = _normalize_pet_status(str(pet_row["status"]))
                    if old_pet_status == PET_STATUS_RESERVED and int(other_active["c"]) == 0:
                        conn.execute("UPDATE PET SET status = ? WHERE pet_id = ?", (PET_STATUS_AVAILABLE, pet_id))
                        _status_audit_log(conn, entity_type="PET", entity_id=pet_id, field_name="status", old_value=old_pet_status, new_value=PET_STATUS_AVAILABLE, changed_by=user.username, note=f"Released after application {application_id} rejected")

        return _write_success({"application_id": application_id, "status": target_status})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/adoptions")
def create_adoption(payload: CreateAdoptionBody, user: SessionUser = Depends(require_permission("adoptions:create"))):
    try:
        with db_session(write=True) as conn:
            application = conn.execute(
                "SELECT aa.application_id, aa.pet_id, aa.status, p.status AS pet_status FROM ADOPTION_APPLICATION aa JOIN PET p ON p.pet_id = aa.pet_id WHERE aa.application_id = ?",
                (payload.application_id,),
            ).fetchone()
            if not application:
                return JSONResponse(status_code=404, content=_write_error(f"Application {payload.application_id} not found"))
            if _normalize_application_status(str(application["status"])) != APPLICATION_STATUS_APPROVED:
                return JSONResponse(status_code=400, content=_write_error("Adoption can only be created from an Approved application"))

            already_used = conn.execute("SELECT adoption_id FROM ADOPTION_RECORD WHERE application_id = ?", (payload.application_id,)).fetchone()
            if already_used:
                return JSONResponse(status_code=400, content=_write_error("This application has already been used in an adoption record"))

            adoption_id = _next_id(conn, "ADOPTION_RECORD", "adoption_id")
            adoption_date = (payload.adoption_date or date.today()).isoformat()
            conn.execute(
                "INSERT INTO ADOPTION_RECORD (adoption_id, application_id, adoption_date, final_adoption_fee, handover_note) VALUES (?, ?, ?, ?, ?)",
                (adoption_id, payload.application_id, adoption_date, payload.final_adoption_fee, payload.handover_note),
            )
            old_pet_status = _normalize_pet_status(str(application["pet_status"]))
            conn.execute("UPDATE PET SET status = ? WHERE pet_id = ?", (PET_STATUS_ADOPTED, application["pet_id"]))

            _audit_log(
                conn,
                actor=user,
                action="create_adoption",
                entity="ADOPTION_RECORD",
                entity_id=str(adoption_id),
                before_state=None,
                after_state={"adoption_id": adoption_id, "application_id": payload.application_id, "adoption_date": adoption_date, "final_adoption_fee": str(payload.final_adoption_fee) if payload.final_adoption_fee is not None else None, "handover_note": payload.handover_note},
            )
            _status_audit_log(conn, entity_type="PET", entity_id=int(application["pet_id"]), field_name="status", old_value=old_pet_status, new_value=PET_STATUS_ADOPTED, changed_by=user.username, note=f"Adoption record {adoption_id} created")

        return _write_success({"adoption_id": adoption_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/followups")
def create_followup(payload: CreateFollowupBody, user: SessionUser = Depends(require_permission("followups:create"))):
    try:
        with db_session(write=True) as conn:
            followup_id = _next_id(conn, "FOLLOW_UP", "followup_id")
            followup_date = (payload.followup_date or date.today()).isoformat()
            conn.execute(
                "INSERT INTO FOLLOW_UP (followup_id, adoption_id, followup_date, followup_type, pet_condition, adopter_feedback, result_status, staff_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (followup_id, payload.adoption_id, followup_date, payload.followup_type, payload.pet_condition, payload.adopter_feedback, payload.result_status, payload.staff_note),
            )
            _audit_log(
                conn,
                actor=user,
                action="create_followup",
                entity="FOLLOW_UP",
                entity_id=str(followup_id),
                before_state=None,
                after_state={"followup_id": followup_id, "adoption_id": payload.adoption_id, "followup_date": followup_date, "followup_type": payload.followup_type, "pet_condition": payload.pet_condition, "adopter_feedback": payload.adopter_feedback, "result_status": payload.result_status, "staff_note": payload.staff_note},
            )

        return _write_success({"followup_id": followup_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
