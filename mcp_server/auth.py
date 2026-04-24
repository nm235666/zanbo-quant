from __future__ import annotations

import secrets
from dataclasses import dataclass

from . import config


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    status: int = 200
    error: str = ""


def normalize_origin(origin: str) -> str:
    return str(origin or "").strip().rstrip("/")


def origin_allowed(origin: str) -> bool:
    normalized = normalize_origin(origin)
    if not normalized:
        return True
    return normalized in config.MCP_ALLOWED_ORIGINS


def extract_bearer_token(header_value: str) -> str:
    text = str(header_value or "").strip()
    if not text:
        return ""
    lower = text.lower()
    if lower.startswith("bearer "):
        return text[7:].strip()
    return ""


def verify_request(*, authorization: str, origin: str = "") -> AuthResult:
    if not origin_allowed(origin):
        return AuthResult(False, 403, "origin_not_allowed")
    expected = config.MCP_ADMIN_TOKEN
    if not expected:
        return AuthResult(False, 401, "mcp_admin_token_not_configured")
    token = extract_bearer_token(authorization)
    if not token or not secrets.compare_digest(token, expected):
        return AuthResult(False, 401, "invalid_mcp_token")
    return AuthResult(True)

