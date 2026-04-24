from __future__ import annotations

import os


DEFAULT_ALLOWED_ORIGINS = {
    "http://127.0.0.1:8077",
    "http://localhost:8077",
    "http://127.0.0.1:8765",
    "http://localhost:8765",
    "http://192.168.5.52:8077",
    "http://tianbo.asia:6273",
}


def _csv_set(value: str) -> set[str]:
    return {item.strip().rstrip("/") for item in str(value or "").split(",") if item.strip()}


MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1").strip() or "127.0.0.1"
MCP_PORT = int(os.getenv("MCP_PORT", "8765") or "8765")
MCP_ADMIN_TOKEN = os.getenv("MCP_ADMIN_TOKEN", "").strip()
MCP_WRITE_ENABLED = os.getenv("MCP_WRITE_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}
MCP_PUBLIC_BASE_URL = os.getenv("MCP_PUBLIC_BASE_URL", "http://tianbo.asia:6273").strip().rstrip("/")
MCP_LAN_BASE_URL = os.getenv("MCP_LAN_BASE_URL", "http://192.168.5.52:8077").strip().rstrip("/")
MCP_ALLOWED_ORIGINS = _csv_set(os.getenv("MCP_ALLOWED_ORIGINS", "")) or set(DEFAULT_ALLOWED_ORIGINS)
MCP_HEALTH_PUBLIC = os.getenv("MCP_HEALTH_PUBLIC", "0").strip().lower() in {"1", "true", "yes", "on"}

