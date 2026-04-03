from __future__ import annotations

from pathlib import Path

import db_compat as sqlite3
from check_gpt_provider_nodes import check_once
from services.agent_service.multi_role_v3 import reclaim_stale_multi_role_v3_jobs


ROOT_DIR = Path(__file__).resolve().parent.parent


def get_llm_job_target(job_key: str) -> dict:
    registry = {
        "llm_provider_nodes_probe": {
            "job_key": "llm_provider_nodes_probe",
            "category": "maintenance",
            "runner_type": "llm_probe",
            "target": "check_gpt_provider_nodes.check_once(all_providers=true)",
        },
        "multi_role_v3_stale_recovery": {
            "job_key": "multi_role_v3_stale_recovery",
            "category": "maintenance",
            "runner_type": "multi_role_maintenance",
            "target": "services.agent_service.multi_role_v3.reclaim_stale_multi_role_v3_jobs",
        },
    }
    if job_key not in registry:
        raise KeyError(job_key)
    return registry[job_key]


def run_llm_job(job_key: str) -> dict:
    if job_key == "llm_provider_nodes_probe":
        rc = check_once(
            config_path=ROOT_DIR / "config" / "llm_providers.json",
            provider_key="gpt-5.4",
            all_providers=True,
            probe_model="gpt-5.4",
            case_mode="auto",
            timeout=20.0,
            probe_retries=1,
            disable_fail_threshold=2,
            keep_unhealthy_enabled=False,
        )
        return {
            "ok": rc == 0,
            "meta": {"return_code": rc, "all_providers": True},
            "stdout": "",
            "stderr": "",
        }
    if job_key == "multi_role_v3_stale_recovery":
        payload = reclaim_stale_multi_role_v3_jobs(
            sqlite3_module=sqlite3,
            db_path=ROOT_DIR / "stock_codes.db",
            stale_after_seconds=300,
        )
        return {
            "ok": bool(payload.get("ok", False)),
            "meta": payload,
            "stdout": "",
            "stderr": "",
        }
    raise KeyError(job_key)
