from __future__ import annotations

import socket
import time
from typing import Any

import db_compat as db

from . import config, store
from .agents import (
    FUNNEL_AGENT_KEY,
    PORTFOLIO_RECONCILE_AGENT_KEY,
    PORTFOLIO_REVIEW_AGENT_KEY,
    run_funnel_progress_agent,
    run_portfolio_reconcile_agent,
    run_portfolio_review_agent,
)
from .executor import execute_existing_step


def ensure_agent_tables(conn=None) -> None:
    if conn is not None:
        store.ensure_agent_tables(conn)
        return
    owned = db.connect()
    try:
        store.ensure_agent_tables(owned)
    finally:
        owned.close()


def create_run(
    *,
    agent_key: str,
    mode: str = "auto",
    trigger_source: str = "manual",
    actor: str = "",
    goal: dict[str, Any] | None = None,
    schedule_key: str = "",
    dedupe: bool = True,
) -> dict[str, Any]:
    return store.create_run(
        agent_key=agent_key,
        mode=mode,
        trigger_source=trigger_source,
        actor=actor,
        goal=goal,
        schedule_key=schedule_key,
        dedupe=dedupe,
    )


def list_runs(*, agent_key: str = "", status: str = "", limit: int = 50) -> dict[str, Any]:
    return store.list_runs(agent_key=agent_key, status=status, limit=limit)


def get_run(run_id: str) -> dict[str, Any] | None:
    return store.get_run(run_id)


def cancel_run(run_id: str, *, actor: str = "", reason: str = "") -> dict[str, Any]:
    return store.cancel_run(run_id, actor=actor, reason=reason)


def approve_run(run_id: str, *, actor: str, reason: str = "", idempotency_key: str = "") -> dict[str, Any]:
    return decide_run(run_id, actor=actor, reason=reason, idempotency_key=idempotency_key, decision="approved")


def reject_run(run_id: str, *, actor: str, reason: str = "", idempotency_key: str = "") -> dict[str, Any]:
    return decide_run(run_id, actor=actor, reason=reason, idempotency_key=idempotency_key, decision="rejected")


def decide_run(
    run_id: str,
    *,
    actor: str,
    reason: str = "",
    idempotency_key: str = "",
    decision: str = "approved",
) -> dict[str, Any]:
    decision = str(decision or "approved").strip().lower()
    if decision not in {"approved", "rejected"}:
        return {"ok": False, "error": "invalid_approval_decision"}
    run = store.get_run(run_id)
    if not run:
        return {"ok": False, "error": "agent_run_not_found"}
    if run.get("status") != "waiting_approval":
        return {"ok": False, "error": "agent_run_not_waiting_approval", "run": run}
    if not str(reason or "").strip():
        return {"ok": False, "error": "approval_reason_required", "run": run}
    store.record_approval(
        run_id,
        actor=actor,
        reason=reason,
        idempotency_key=idempotency_key,
        decision=decision,
    )
    if decision == "rejected":
        store.update_run(
            run_id,
            status="cancelled",
            result={**dict(run.get("result") or {}), "approval_decision": "rejected", "approval_reason": reason},
            approval_required=False,
            finished=True,
        )
        return {"ok": True, "run": store.get_run(run_id)}
    return resume_run(run_id, actor=actor, reason=reason)


def resume_run(run_id: str, *, actor: str = "", reason: str = "") -> dict[str, Any]:
    run = store.get_run(run_id)
    if not run:
        return {"ok": False, "error": "agent_run_not_found"}
    pending = store.list_pending_steps(run_id)
    if not pending:
        store.update_run(run_id, status="succeeded", approval_required=False, finished=True)
        return {"ok": True, "run": store.get_run(run_id), "resumed_steps": 0}
    executed: list[dict[str, Any]] = []
    errors: list[str] = []
    agent_key = str(run.get("agent_key") or "")
    for step in pending:
        args = dict(step.get("args") or {})
        args.update(
            {
                "dry_run": False,
                "confirm": True,
                "actor": f"agent:{agent_key}",
                "reason": str(reason or "approved agent write"),
            }
        )
        if not str(args.get("idempotency_key") or "").strip():
            args["idempotency_key"] = f"agent:{agent_key}:{step.get('tool_name')}:{run.get('schedule_key') or run_id}:{step.get('id')}"
        out = execute_existing_step(step=step, arguments=args)
        executed.append({"tool_name": step.get("tool_name"), **out})
        if not out.get("ok"):
            errors.append(str(out.get("error") or "step_failed"))
            break
    base_result = dict(run.get("result") or {})
    previous_executed = list(base_result.get("executed_actions") or [])
    base_result["executed_actions"] = previous_executed + executed
    base_result["approval_decision"] = "approved"
    base_result["approval_reason"] = reason
    base_result["changed_count"] = sum(
        int(((item.get("result") or {}) if isinstance(item, dict) else {}).get("changed_count") or 0)
        for item in base_result["executed_actions"]
        if isinstance(item, dict)
    )
    if errors:
        store.update_run(
            run_id,
            status="failed",
            result=base_result,
            error_text="; ".join(errors),
            approval_required=False,
            finished=True,
        )
        return {"ok": False, "error": "; ".join(errors), "run": store.get_run(run_id)}
    store.update_run(
        run_id,
        status="succeeded",
        result=base_result,
        approval_required=False,
        finished=True,
    )
    return {"ok": True, "run": store.get_run(run_id), "resumed_steps": len(executed)}


def run_one(run: dict[str, Any]) -> dict[str, Any]:
    run_id = str(run.get("id") or "")
    try:
        agent_key = str(run.get("agent_key") or "")
        if agent_key == FUNNEL_AGENT_KEY:
            result = run_funnel_progress_agent(run)
        elif agent_key == PORTFOLIO_RECONCILE_AGENT_KEY:
            result = run_portfolio_reconcile_agent(run)
        elif agent_key == PORTFOLIO_REVIEW_AGENT_KEY:
            result = run_portfolio_review_agent(run)
        else:
            raise ValueError(f"unknown_agent_key:{run.get('agent_key')}")
        plan = result.get("plan") if isinstance(result.get("plan"), dict) else {}
        requires_approval = bool(result.get("requires_approval_actions"))
        status = "waiting_approval" if requires_approval else "succeeded"
        store.update_run(
            run_id,
            status=status,
            plan=plan,
            result=result,
            approval_required=requires_approval,
            finished=not requires_approval,
        )
        return {"ok": True, "run": store.get_run(run_id)}
    except Exception as exc:
        store.update_run(
            run_id,
            status="failed",
            error_text=str(exc),
            result={"ok": False, "error": str(exc)},
            finished=True,
        )
        return {"ok": False, "error": str(exc), "run": store.get_run(run_id)}


def run_next_once(*, worker_id: str = "") -> dict[str, Any]:
    worker = worker_id or f"{socket.gethostname()}:{id(object())}"
    run = store.claim_next_run(worker_id=worker)
    if not run:
        return {"ok": True, "processed": 0}
    result = run_one(run)
    result["processed"] = 1
    return result


def run_worker_loop(*, once: bool = False, poll_seconds: float | None = None) -> None:
    sleep_s = config.worker_poll_seconds() if poll_seconds is None else max(0.2, float(poll_seconds or 1.0))
    while True:
        out = run_next_once()
        if once:
            return
        if int(out.get("processed") or 0) <= 0:
            time.sleep(sleep_s)
