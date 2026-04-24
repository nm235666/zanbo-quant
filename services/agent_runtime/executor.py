from __future__ import annotations

from typing import Any

from mcp_server.audit import record_tool_audit

from . import store


WRITE_TOOLS = {
    "jobs.trigger",
    "business.repair_funnel_score_align",
    "business.repair_funnel_review_refresh",
    "business.run_decision_snapshot",
    "business.reconcile_portfolio_positions",
    "business.generate_portfolio_order_reviews",
}


def execute_tool_step(
    *,
    run_id: str,
    step_index: int,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    args = dict(arguments or {})
    dry_run = bool(args.get("dry_run", True))
    step_id = store.insert_step(
        run_id=run_id,
        step_index=step_index,
        tool_name=tool_name,
        args=args,
        dry_run=dry_run,
    )
    request_id = f"agent:{run_id}:{step_id}"
    actor = str(args.get("actor") or "")
    audit_id = 0
    try:
        from mcp_server.tools.registry import call_tool

        result = call_tool(tool_name, args)
        audit_id = record_tool_audit(
            request_id=request_id,
            actor=actor,
            tool_name=tool_name,
            args=args,
            dry_run=dry_run,
            status="success",
            result=result,
        )
        if isinstance(result, dict):
            result.setdefault("audit_id", audit_id)
            result.setdefault("agent_step_id", step_id)
        store.finish_step(step_id, status="success", result=result, audit_id=audit_id)
        return {"ok": True, "step_id": step_id, "audit_id": audit_id, "result": result}
    except Exception as exc:
        audit_id = record_tool_audit(
            request_id=request_id,
            actor=actor,
            tool_name=tool_name,
            args=args,
            dry_run=dry_run,
            status="error",
            result={"agent_step_id": step_id},
            error_text=str(exc),
        )
        store.finish_step(step_id, status="error", result={"agent_step_id": step_id}, error_text=str(exc), audit_id=audit_id)
        return {"ok": False, "step_id": step_id, "audit_id": audit_id, "error": str(exc)}


def execute_existing_step(*, step: dict[str, Any], arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    step_id = str(step.get("id") or "")
    run_id = str(step.get("run_id") or "")
    tool_name = str(step.get("tool_name") or "")
    args = dict(arguments if arguments is not None else (step.get("args") or {}))
    dry_run = bool(args.get("dry_run", True))
    store.update_step_args(step_id, args=args, status="running")
    request_id = f"agent:{run_id}:{step_id}"
    actor = str(args.get("actor") or "")
    audit_id = 0
    try:
        from mcp_server.tools.registry import call_tool

        result = call_tool(tool_name, args)
        audit_id = record_tool_audit(
            request_id=request_id,
            actor=actor,
            tool_name=tool_name,
            args=args,
            dry_run=dry_run,
            status="success",
            result=result,
        )
        if isinstance(result, dict):
            result.setdefault("audit_id", audit_id)
            result.setdefault("agent_step_id", step_id)
        store.finish_step(step_id, status="success", result=result, audit_id=audit_id)
        return {"ok": True, "step_id": step_id, "audit_id": audit_id, "result": result}
    except Exception as exc:
        audit_id = record_tool_audit(
            request_id=request_id,
            actor=actor,
            tool_name=tool_name,
            args=args,
            dry_run=dry_run,
            status="error",
            result={"agent_step_id": step_id},
            error_text=str(exc),
        )
        store.finish_step(step_id, status="error", result={"agent_step_id": step_id}, error_text=str(exc), audit_id=audit_id)
        return {"ok": False, "step_id": step_id, "audit_id": audit_id, "error": str(exc)}
