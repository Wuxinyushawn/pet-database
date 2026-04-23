"""Authentication and RBAC utilities extracted from api_server for merge-safe maintenance."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

DEMO_MODE = os.getenv("PET_API_DEMO_MODE", "").lower() in {"1", "true", "yes", "on"}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"applications:create", "applications:review", "adoptions:create", "followups:create", "audit:read"},
    "staff": {"applications:create", "applications:review", "adoptions:create", "followups:create", "audit:read"},
    "volunteer_coordinator": {"followups:create", "audit:read"},
}


def _load_user_store() -> dict[str, dict[str, str]]:
    """Load configured users, keeping built-in demo accounts only in demo mode."""
    if DEMO_MODE:
        return {
            "admin": {"password": "admin123", "role": "admin"},
            "staff": {"password": "staff123", "role": "staff"},
            "coordinator": {"password": "coord123", "role": "volunteer_coordinator"},
        }

    users_json = os.getenv("PET_API_USERS_JSON", "")
    if not users_json:
        return {}

    try:
        loaded = json.loads(users_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError("PET_API_USERS_JSON must be valid JSON") from exc

    if not isinstance(loaded, dict):
        raise RuntimeError("PET_API_USERS_JSON must decode to an object mapping usernames to user records")

    user_store: dict[str, dict[str, str]] = {}
    for username, user_record in loaded.items():
        if not isinstance(username, str):
            raise RuntimeError("PET_API_USERS_JSON usernames must be strings")
        if not isinstance(user_record, dict):
            raise RuntimeError("PET_API_USERS_JSON user records must be objects")

        password = user_record.get("password")
        role = user_record.get("role")
        if not isinstance(password, str) or not isinstance(role, str):
            raise RuntimeError("PET_API_USERS_JSON user records must contain string 'password' and 'role' fields")

        user_store[username] = {"password": password, "role": role}

    return user_store


USER_STORE: dict[str, dict[str, str]] = _load_user_store()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


def create_session_token(*, username: str, role: str, secret: str, ttl_hours: int) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).timestamp()),
    }
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    return f"{body}.{_b64url(signature)}"


def verify_session_token(token: str, *, secret: str) -> dict[str, str]:
    try:
        body, sig = token.split(".", 1)
        expected_sig = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected_sig), sig):
            raise ValueError("Invalid session signature")
        payload = json.loads(_b64url_decode(body))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Session expired")

        username = payload["sub"]
        role = payload["role"]
        if not isinstance(username, str) or not isinstance(role, str):
            raise ValueError("Invalid session payload")
        return {"username": username, "role": role}
    except (TypeError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid session token") from exc
