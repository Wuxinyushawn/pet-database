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
                    payload.status,
                    payload.reason,
                ),
            )
        return _write_success({"application_id": application_id})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/applications/{application_id}/review")
def review_application(application_id: int, payload: ReviewApplicationBody):
    try:
        with db_session(write=True) as conn:
            existing = conn.execute(
                "SELECT application_id FROM ADOPTION_APPLICATION WHERE application_id = ?",
                (application_id,),
            ).fetchone()
            if not existing:
                return JSONResponse(status_code=404, content=_write_error(f"Application {application_id} not found"))

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
                    (payload.reviewed_date or date.today()).isoformat(),
                    application_id,
                ),
            )
        return _write_success({"application_id": application_id, "status": payload.status})
    except Exception as exc:
        return JSONResponse(status_code=400, content=_write_error(str(exc)))


@app.post("/adoptions")
def create_adoption(payload: CreateAdoptionBody):
    try:
        with db_session(write=True) as conn:
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
