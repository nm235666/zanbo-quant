from __future__ import annotations

from pathlib import Path

import db_compat as sqlite3

from services.decision_service import run_decision_scheduled_job

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_decision_job_target(job_key: str) -> dict:
    registry = {
        "decision_daily_snapshot": {
            "job_key": "decision_daily_snapshot",
            "category": "research",
            "runner_type": "service",
            "target": "services.decision_service.run_decision_scheduled_job",
        },
    }
    if job_key not in registry:
        raise KeyError(job_key)
    return registry[job_key]


def run_decision_job(job_key: str) -> dict:
    return run_decision_scheduled_job(
        sqlite3_module=sqlite3,
        db_path=str(ROOT_DIR / "stock_codes.db"),
        job_key=job_key,
    )
