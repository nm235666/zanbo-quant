from __future__ import annotations

from typing import Any

from job_orchestrator import dry_run_job, query_job_alerts, query_job_definitions, query_job_runs, run_job
from mcp_server import schemas

from .common import WRITE_JOB_ALLOWLIST, clamp_limit, require_write_allowed


def list_definitions(_: schemas.EmptyArgs) -> dict[str, Any]:
    payload = query_job_definitions()
    return {"ok": True, **payload}


def list_runs(args: schemas.JobListArgs) -> dict[str, Any]:
    payload = query_job_runs(job_key=args.job_key, status=args.status, limit=clamp_limit(args.limit, maximum=200))
    return {"ok": True, **payload}


def list_alerts(args: schemas.JobListArgs) -> dict[str, Any]:
    payload = query_job_alerts(
        job_key=args.job_key,
        unresolved_only=bool(args.unresolved_only),
        limit=clamp_limit(args.limit, maximum=200),
    )
    return {"ok": True, **payload}


def trigger(args: schemas.JobTriggerArgs) -> dict[str, Any]:
    require_write_allowed(args)
    job_key = str(args.job_key or "").strip()
    if job_key not in WRITE_JOB_ALLOWLIST:
        raise ValueError(f"job_not_allowlisted:{job_key}")
    if args.dry_run:
        result = dry_run_job(job_key, trigger_mode="mcp-dry-run")
        return {
            "ok": True,
            "dry_run": True,
            "planned_changes": [{"kind": "job_trigger", "job_key": job_key, "commands": result.get("commands", [])}],
            "changed_count": 0,
            "skipped_count": 0,
            "warnings": [],
            "result": result,
        }
    result = run_job(job_key, trigger_mode="mcp-manual")
    return {
        "ok": bool(result.get("ok")),
        "dry_run": False,
        "planned_changes": [],
        "changed_count": 1 if result.get("run_id") else 0,
        "skipped_count": 0,
        "warnings": [] if result.get("ok") else [str(result.get("error") or result.get("status") or "job_failed")],
        "result": result,
    }

