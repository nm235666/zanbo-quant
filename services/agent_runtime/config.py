from __future__ import annotations

import os


DEFAULT_AUTO_WRITE_ALLOWLIST = {
    "business.repair_funnel_score_align",
    "business.repair_funnel_review_refresh",
}


def _csv_set(value: str) -> set[str]:
    return {item.strip() for item in str(value or "").split(",") if item.strip()}


def auto_write_enabled() -> bool:
    return os.getenv("AGENT_AUTO_WRITE_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}


def auto_write_allowlist() -> set[str]:
    return _csv_set(os.getenv("AGENT_AUTO_WRITE_TOOL_ALLOWLIST", "")) or set(DEFAULT_AUTO_WRITE_ALLOWLIST)


def worker_poll_seconds() -> float:
    try:
        return max(0.2, float(os.getenv("AGENT_WORKER_POLL_SECONDS", "1.0") or 1.0))
    except Exception:
        return 1.0
