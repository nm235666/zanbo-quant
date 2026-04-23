from __future__ import annotations

from typing import Any


def run_funnel_job(job_key: str) -> dict[str, Any]:
    """Dispatch funnel maintenance jobs (score align, review snapshots)."""
    if job_key == "funnel_ingested_score_align":
        from services.funnel_service.service import promote_ingested_when_score_present

        return promote_ingested_when_score_present()
    if job_key == "funnel_review_refresh":
        from services.funnel_service.service import refresh_funnel_review_snapshots

        return refresh_funnel_review_snapshots()
    return {"ok": False, "error": f"unknown funnel job_key: {job_key}"}
