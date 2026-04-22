"""Authentication and RBAC utilities extracted from api_server for merge-safe maintenance."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

USER_STORE: dict[str, dict[str, str]] = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
    "coordinator": {"password": "coord123", "role": "volunteer_coordinator"},
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"applications:create", "applications:review", "adoptions:create", "followups:create", "audit:read"},
    "staff": {"applications:create", "applications:review", "adoptions:create", "followups:create", "audit:read"},
    "volunteer_coordinator": {"followups:create", "audit:read"},
}


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
    body, sig = token.split(".", 1)
    expected_sig = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url(expected_sig), sig):
        raise ValueError("Invalid session signature")
    payload = json.loads(_b64url_decode(body))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Session expired")
    return {"username": payload["sub"], "role": payload["role"]}
