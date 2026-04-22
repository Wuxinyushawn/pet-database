"""REST API server for the pet database.

This module provides a minimal HTTP JSON interface for front-end usage,
while `src/mcp_server.py` remains dedicated to MCP interactions.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Generator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).parent.parent / "pet_database.db"

app = FastAPI(title="Pet Database REST API", version="1.0.0")

APPLICATION_STATUS_PENDING = "Pending"
APPLICATION_STATUS_APPROVED = "Approved"
APPLICATION_STATUS_REJECTED = "Rejected"

PET_STATUS_AVAILABLE = "Available"
PET_STATUS_RESERVED = "Reserved"
PET_STATUS_ADOPTED = "Adopted"


# ── Database Management ───────────────────────────────────────────────────────

@contextmanager
def db_session(*, write: bool = False) -> Generator[sqlite3.Connection, None, None]:
    """Manage DB connection + transaction in one place.

    - read session: no commit
    - write session: commit on success, rollback on failure
    """
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


def _normalize_application_status(status: str) -> str:
    value = status.strip().lower()
    if value == "pending":
        return APPLICATION_STATUS_PENDING
    if value == "approved":
        return APPLICATION_STATUS_APPROVED
    if value == "rejected":
        return APPLICATION_STATUS_REJECTED
    raise ValueError("Invalid application status. Allowed values: Pending, Approved, Rejected")


def _normalize_pet_status(status: str) -> str:
    value = status.strip().lower()
    if value == "available":
        return PET_STATUS_AVAILABLE
    if value == "reserved":
        return PET_STATUS_RESERVED
    if value == "adopted":
        return PET_STATUS_ADOPTED
    return status


def _ensure_audit_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS STATUS_AUDIT_LOG (
            audit_id INTEGER PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            changed_by TEXT,
            note TEXT
        )
        """
    )


def _insert_audit_log(
    conn: sqlite3.Connection,
    *,
    entity_type: str,
    entity_id: int,
    field_name: str,
    old_value: str | None,
    new_value: str,
    changed_by: str | None = None,
    note: str | None = None,
) -> None:
    if old_value == new_value:
        return
    _ensure_audit_table(conn)
    audit_id = _next_id(conn, "STATUS_AUDIT_LOG", "audit_id")
    conn.execute(
        """
        INSERT INTO STATUS_AUDIT_LOG (
            audit_id, entity_type, entity_id, field_name,
            old_value, new_value, changed_at, changed_by, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            audit_id,
            entity_type,
            entity_id,
            field_name,
            old_value,
            new_value,
            date.today().isoformat(),
            changed_by,
            note,
        ),
    )


# ── Error Handling ────────────────────────────────────────────────────────────

@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(_, exc: sqlite3.Error):
    return JSONResponse(status_code=500, content={"detail": f"Database error: {exc}"})


@app.exception_handler(Exception)
async def generic_exception_handler(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})


# ── Request Schemas ───────────────────────────────────────────────────────────

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


# ── Read Endpoints ────────────────────────────────────────────────────────────

@app.get("/pets")
def get_pets() -> dict[str, Any]:
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT pet_id, shelter_id, name, species, breed, sex, color, intake_date, status
            FROM PET
            ORDER BY pet_id
            """
        ).fetchall()
        return {"data": _rows_to_dicts(rows)}


@app.get("/pets/{pet_id}")
def get_pet(pet_id: int) -> dict[str, Any]:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM PET WHERE pet_id = ?", (pet_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Pet {pet_id} not found")
        return {"data": dict(row)}


@app.get("/applications")
def get_applications() -> dict[str, Any]:
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
def get_adoptions() -> dict[str, Any]:
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
def get_followups() -> dict[str, Any]:
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


@app.get("/dashboard/summary")
def get_dashboard_summary() -> dict[str, Any]:
    with db_session() as conn:
        total_pets = conn.execute("SELECT COUNT(*) AS c FROM PET").fetchone()["c"]
        available_pets = conn.execute("SELECT COUNT(*) AS c FROM PET WHERE status = 'available'").fetchone()["c"]
        total_applications = conn.execute("SELECT COUNT(*) AS c FROM ADOPTION_APPLICATION").fetchone()["c"]
        pending_applications = conn.execute(
            "SELECT COUNT(*) AS c FROM ADOPTION_APPLICATION WHERE status IN ('under_review', 'pending')"
        ).fetchone()["c"]
        approved_applications = conn.execute(
            "SELECT COUNT(*) AS c FROM ADOPTION_APPLICATION WHERE status = 'approved'"
        ).fetchone()["c"]
        total_adoptions = conn.execute("SELECT COUNT(*) AS c FROM ADOPTION_RECORD").fetchone()["c"]
        total_followups = conn.execute("SELECT COUNT(*) AS c FROM FOLLOW_UP").fetchone()["c"]

    return {
        "data": {
            "total_pets": total_pets,
            "available_pets": available_pets,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "approved_applications": approved_applications,
            "total_adoptions": total_adoptions,
            "total_followups": total_followups,
        }
    }


# ── Write Endpoints ───────────────────────────────────────────────────────────

@app.post("/applications")
def create_application(payload: CreateApplicationBody):
    try:
        with db_session(write=True) as conn:
            target_status = _normalize_application_status(payload.status)
            if target_status != APPLICATION_STATUS_PENDING:
                return JSONResponse(
                    status_code=400,
                    content=_write_error("New applications must start with Pending status"),
                )

            pet = conn.execute("SELECT pet_id, status FROM PET WHERE pet_id = ?", (payload.pet_id,)).fetchone()
            if not pet:
                return JSONResponse(status_code=404, content=_write_error(f"Pet {payload.pet_id} not found"))

            pet_status = _normalize_pet_status(str(pet["status"]))
            if pet_status == PET_STATUS_ADOPTED:
                return JSONResponse(
                    status_code=400,
                    content=_write_error("Cannot create application for an adopted pet"),
                )

            application_id = _next_id(conn, "ADOPTION_APPLICATION", "application_id")
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
                    (payload.application_date or date.today()).isoformat(),
                    target_status,
                    payload.reason,
                ),
            )
            conn.execute("UPDATE PET SET status = ? WHERE pet_id = ?", (PET_STATUS_RESERVED, payload.pet_id))
            _insert_audit_log(
                conn,
                entity_type="ADOPTION_APPLICATION",
                entity_id=application_id,
                field_name="status",
                old_value=None,
                new_value=target_status,
                changed_by=None,
                note="Application created",
            )
            _insert_audit_log(
                conn,
                entity_type="PET",
                entity_id=payload.pet_id,
                field_name="status",
                old_value=pet_status,
                new_value=PET_STATUS_RESERVED,
                changed_by=None,
                note=f"Application {application_id} created",
            )
        return _write_success({"application_id": application_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/applications/{application_id}/review")
def review_application(application_id: int, payload: ReviewApplicationBody):
    try:
        with db_session(write=True) as conn:
            target_status = _normalize_application_status(payload.status)
            if target_status not in (APPLICATION_STATUS_APPROVED, APPLICATION_STATUS_REJECTED):
                return JSONResponse(
                    status_code=400,
                    content=_write_error("Review status must be Approved or Rejected"),
                )

            existing = conn.execute(
                """
                SELECT application_id, pet_id, status, reviewer_name, decision_note, reviewed_date
                FROM ADOPTION_APPLICATION
                WHERE application_id = ?
                """,
                (application_id,),
            ).fetchone()
            if not existing:
                return JSONResponse(status_code=404, content=_write_error(f"Application {application_id} not found"))

            current_status = _normalize_application_status(str(existing["status"]))
            if current_status != APPLICATION_STATUS_PENDING:
                return JSONResponse(
                    status_code=400,
                    content=_write_error("Application status transition allowed only from Pending to Approved/Rejected"),
                )

            reviewed_date = (payload.reviewed_date or date.today()).isoformat()
            conn.execute(
                """
                UPDATE ADOPTION_APPLICATION
                SET status = ?, reviewer_name = ?, decision_note = ?, reviewed_date = ?
                WHERE application_id = ?
                """,
                (
                    target_status,
                    payload.reviewer_name if target_status == APPLICATION_STATUS_APPROVED else None,
                    payload.decision_note if target_status == APPLICATION_STATUS_APPROVED else payload.decision_note,
                    reviewed_date,
                    application_id,
                ),
            )
            _insert_audit_log(
                conn,
                entity_type="ADOPTION_APPLICATION",
                entity_id=application_id,
                field_name="status",
                old_value=current_status,
                new_value=target_status,
                changed_by=payload.reviewer_name,
                note=payload.decision_note,
            )

            if target_status == APPLICATION_STATUS_REJECTED:
                other_active = conn.execute(
                    """
                    SELECT COUNT(*) AS c
                    FROM ADOPTION_APPLICATION
                    WHERE pet_id = ?
                      AND application_id <> ?
                      AND status IN (?, ?)
                    """,
                    (
                        existing["pet_id"],
                        application_id,
                        APPLICATION_STATUS_PENDING,
                        APPLICATION_STATUS_APPROVED,
                    ),
                ).fetchone()
                pet_row = conn.execute(
                    "SELECT status FROM PET WHERE pet_id = ?",
                    (existing["pet_id"],),
                ).fetchone()
                if pet_row:
                    old_pet_status = _normalize_pet_status(str(pet_row["status"]))
                    if old_pet_status == PET_STATUS_RESERVED and int(other_active["c"]) == 0:
                        conn.execute(
                            "UPDATE PET SET status = ? WHERE pet_id = ?",
                            (PET_STATUS_AVAILABLE, existing["pet_id"]),
                        )
                        _insert_audit_log(
                            conn,
                            entity_type="PET",
                            entity_id=int(existing["pet_id"]),
                            field_name="status",
                            old_value=old_pet_status,
                            new_value=PET_STATUS_AVAILABLE,
                            changed_by=payload.reviewer_name,
                            note=f"Released after application {application_id} rejected",
                        )

        return _write_success({"application_id": application_id, "status": target_status})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/adoptions")
def create_adoption(payload: CreateAdoptionBody):
    try:
        with db_session(write=True) as conn:
            application = conn.execute(
                """
                SELECT aa.application_id, aa.pet_id, aa.status, p.status AS pet_status
                FROM ADOPTION_APPLICATION aa
                JOIN PET p ON p.pet_id = aa.pet_id
                WHERE aa.application_id = ?
                """,
                (payload.application_id,),
            ).fetchone()
            if not application:
                return JSONResponse(
                    status_code=404,
                    content=_write_error(f"Application {payload.application_id} not found"),
                )
            if _normalize_application_status(str(application["status"])) != APPLICATION_STATUS_APPROVED:
                return JSONResponse(
                    status_code=400,
                    content=_write_error("Adoption can only be created from an Approved application"),
                )

            already_used = conn.execute(
                "SELECT adoption_id FROM ADOPTION_RECORD WHERE application_id = ?",
                (payload.application_id,),
            ).fetchone()
            if already_used:
                return JSONResponse(
                    status_code=400,
                    content=_write_error("This application has already been used in an adoption record"),
                )

            adoption_id = _next_id(conn, "ADOPTION_RECORD", "adoption_id")
            conn.execute(
                """
                INSERT INTO ADOPTION_RECORD (
                    adoption_id, application_id, adoption_date, final_adoption_fee, handover_note
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    adoption_id,
                    payload.application_id,
                    (payload.adoption_date or date.today()).isoformat(),
                    payload.final_adoption_fee,
                    payload.handover_note,
                ),
            )
            old_pet_status = _normalize_pet_status(str(application["pet_status"]))
            conn.execute(
                "UPDATE PET SET status = ? WHERE pet_id = ?",
                (PET_STATUS_ADOPTED, application["pet_id"]),
            )
            _insert_audit_log(
                conn,
                entity_type="PET",
                entity_id=int(application["pet_id"]),
                field_name="status",
                old_value=old_pet_status,
                new_value=PET_STATUS_ADOPTED,
                changed_by=None,
                note=f"Adoption record {adoption_id} created from application {payload.application_id}",
            )
        return _write_success({"adoption_id": adoption_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/followups")
def create_followup(payload: CreateFollowupBody):
    try:
        with db_session(write=True) as conn:
            followup_id = _next_id(conn, "FOLLOW_UP", "followup_id")
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
                    (payload.followup_date or date.today()).isoformat(),
                    payload.followup_type,
                    payload.pet_condition,
                    payload.adopter_feedback,
                    payload.result_status,
                    payload.staff_note,
                ),
            )
        return _write_success({"followup_id": followup_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
