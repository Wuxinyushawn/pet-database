"""Audit helper functions extracted from api_server to reduce hot-file conflicts."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
import sqlite3
from typing import Any


def ensure_audit_tables(conn: sqlite3.Connection) -> None:
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


def write_audit_log(
    conn: sqlite3.Connection,
    *,
    next_id: int,
    actor_username: str,
    actor_role: str,
    action: str,
    entity: str,
    entity_id: str | None,
    before_state: dict[str, Any] | None,
    after_state: dict[str, Any] | None,
) -> None:
    conn.execute(
        """
        INSERT INTO AUDIT_LOG (
            audit_id, actor_username, actor_role, action, entity, entity_id,
            before_state, after_state, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            next_id,
            actor_username,
            actor_role,
            action,
            entity,
            entity_id,
            json.dumps(before_state, ensure_ascii=False) if before_state is not None else None,
            json.dumps(after_state, ensure_ascii=False) if after_state is not None else None,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


def write_status_audit_log(
    conn: sqlite3.Connection,
    *,
    next_id: int,
    entity_type: str,
    entity_id: int,
    field_name: str,
    old_value: str | None,
    new_value: str,
    changed_by: str | None,
    note: str | None,
) -> None:
    if old_value == new_value:
        return
    conn.execute(
        """
        INSERT INTO STATUS_AUDIT_LOG (
            audit_id, entity_type, entity_id, field_name, old_value, new_value,
            changed_at, changed_by, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (next_id, entity_type, entity_id, field_name, old_value, new_value, date.today().isoformat(), changed_by, note),
    )
