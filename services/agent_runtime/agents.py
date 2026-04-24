from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from mcp_server import config as mcp_config

from . import config, store
from .executor import execute_tool_step


FUNNEL_AGENT_KEY = "funnel_progress_agent"
FUNNEL_WRITE_TOOLS = {
    "business.repair_funnel_score_align",
    "business.repair_funnel_review_refresh",
}
PORTFOLIO_RECONCILE_AGENT_KEY = "portfolio_reconcile_agent"
PORTFOLIO_REVIEW_AGENT_KEY = "portfolio_review_agent"


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _stable_key(*parts: Any) -> str:
    raw = "|".join(str(p or "") for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _state_count(closure: dict[str, Any], state: str) -> int:
    try:
        return int((closure.get("funnel_by_state") or {}).get(state) or 0)
    except Exception:
        return 0


def _planned_actions(goal: dict[str, Any], closure: dict[str, Any]) -> list[dict[str, Any]]:
    gaps = set(str(x) for x in closure.get("gaps", []) if str(x))
    actions: list[dict[str, Any]] = []
    ingested = _state_count(closure, "ingested")
    if "funnel_ingested_backlog" in gaps or ingested > 0 or goal.get("force_score_align"):
        actions.append(
            {
                "tool_name": "business.repair_funnel_score_align",
                "arguments": {
                    "score_date": str(goal.get("score_date") or ""),
                    "max_candidates": int(goal.get("max_candidates") or 10000),
                },
            }
        )
    review_candidates = sum(_state_count(closure, state) for state in ("confirmed", "executed", "reviewed"))
    if review_candidates > 0 or goal.get("force_review_refresh"):
        actions.append(
            {
                "tool_name": "business.repair_funnel_review_refresh",
                "arguments": {
                    "horizon_days": int(goal.get("horizon_days") or 5),
                    "limit": int(goal.get("review_limit") or 200),
                },
            }
        )
    return actions


def run_funnel_progress_agent(run: dict[str, Any]) -> dict[str, Any]:
    run_id = str(run.get("id") or "")
    goal = dict(run.get("goal") or {})
    actor = "agent:funnel_progress_agent"
    step_index = 1
    observations: dict[str, Any] = {}
    executed_actions: list[dict[str, Any]] = []
    skipped_actions: list[dict[str, Any]] = []
    requires_approval_actions: list[dict[str, Any]] = []
    warnings: list[str] = []

    def call(tool_name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        out = execute_tool_step(run_id=run_id, step_index=step_index, tool_name=tool_name, arguments=args or {})
        step_index += 1
        if not out.get("ok"):
            raise RuntimeError(f"{tool_name}: {out.get('error')}")
        result = out.get("result")
        return result if isinstance(result, dict) else {"result": result}

    observations["health"] = call("system.health_snapshot")
    closure = call("business.closure_gap_scan")
    observations["closure_gap_scan"] = closure
    observations["funnel_score_job_runs"] = call("jobs.list_runs", {"job_key": "funnel_ingested_score_align", "limit": 10})
    observations["funnel_review_job_runs"] = call("jobs.list_runs", {"job_key": "funnel_review_refresh", "limit": 10})

    planned_actions = _planned_actions(goal, closure)
    plan = {
        "agent_key": FUNNEL_AGENT_KEY,
        "observe_steps": [
            "system.health_snapshot",
            "business.closure_gap_scan",
            "jobs.list_runs:funnel_ingested_score_align",
            "jobs.list_runs:funnel_review_refresh",
        ],
        "planned_actions": planned_actions,
    }

    allowlist = config.auto_write_allowlist()
    can_auto_write = config.auto_write_enabled() and bool(mcp_config.MCP_WRITE_ENABLED)
    if not config.auto_write_enabled():
        warnings.append("agent_auto_write_disabled")
    if not mcp_config.MCP_WRITE_ENABLED:
        warnings.append("mcp_write_disabled")

    for action in planned_actions:
        tool_name = str(action.get("tool_name") or "")
        base_args = dict(action.get("arguments") or {})
        dry_args = {
            **base_args,
            "dry_run": True,
            "actor": actor,
            "reason": "funnel_progress_agent dry-run precheck",
            "idempotency_key": f"dryrun:{run_id}:{tool_name}",
        }
        dry_result = call(tool_name, dry_args)
        action_record = {"tool_name": tool_name, "dry_run": dry_result}
        if dry_result.get("ok") is False:
            action_record["reason"] = "dry_run_failed"
            skipped_actions.append(action_record)
            continue
        if tool_name not in FUNNEL_WRITE_TOOLS or tool_name not in allowlist:
            action_record["reason"] = "tool_not_auto_write_allowlisted"
            requires_approval_actions.append(action_record)
            continue
        if not can_auto_write:
            action_record["reason"] = "auto_write_disabled"
            skipped_actions.append(action_record)
            continue
        write_args = {
            **base_args,
            "dry_run": False,
            "confirm": True,
            "actor": actor,
            "reason": f"funnel_progress_agent auto repair via {tool_name}",
            "idempotency_key": f"agent:{FUNNEL_AGENT_KEY}:{tool_name}:{run.get('schedule_key') or _now_date()}:{_stable_key(base_args)}",
        }
        write_result = call(tool_name, write_args)
        executed_actions.append({"tool_name": tool_name, "dry_run": dry_result, "write": write_result})

    if not planned_actions:
        skipped_actions.append({"reason": "no_funnel_gap_detected"})

    closure_status = "requires_attention" if requires_approval_actions or warnings else "closed_or_progressed"
    if not planned_actions:
        closure_status = "no_action_needed"

    return {
        "ok": True,
        "agent_key": FUNNEL_AGENT_KEY,
        "observations": observations,
        "plan": plan,
        "planned_actions": planned_actions,
        "executed_actions": executed_actions,
        "skipped_actions": skipped_actions,
        "requires_approval_actions": requires_approval_actions,
        "warnings": warnings,
        "closure_status": closure_status,
        "changed_count": sum(int((item.get("write") or {}).get("changed_count") or 0) for item in executed_actions),
    }


def _approval_idempotency_key(run: dict[str, Any], tool_name: str, args: dict[str, Any]) -> str:
    return f"agent:{run.get('agent_key')}:{tool_name}:{run.get('schedule_key') or _now_date()}:{_stable_key(args)}"


def _portfolio_observations(run_id: str) -> tuple[dict[str, Any], int]:
    step_index = 1
    observations: dict[str, Any] = {}

    def call(tool_name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        nonlocal step_index
        out = execute_tool_step(run_id=run_id, step_index=step_index, tool_name=tool_name, arguments=args or {})
        step_index += 1
        if not out.get("ok"):
            raise RuntimeError(f"{tool_name}: {out.get('error')}")
        result = out.get("result")
        return result if isinstance(result, dict) else {"result": result}

    observations["health"] = call("system.health_snapshot")
    observations["closure_gap_scan"] = call("business.closure_gap_scan")
    observations["portfolio_closure_scan"] = call("business.portfolio_closure_scan")
    return observations, step_index


def run_portfolio_reconcile_agent(run: dict[str, Any]) -> dict[str, Any]:
    run_id = str(run.get("id") or "")
    goal = dict(run.get("goal") or {})
    observations, step_index = _portfolio_observations(run_id)
    scan = observations.get("portfolio_closure_scan") or {}
    planned_actions: list[dict[str, Any]] = []
    requires_approval_actions: list[dict[str, Any]] = []
    skipped_actions: list[dict[str, Any]] = []
    pending_write_steps: list[dict[str, Any]] = []
    warnings: list[str] = []

    if scan.get("requires_position_reconcile") or goal.get("force_reconcile"):
        base_args = {"limit": int(goal.get("limit") or 500)}
        dry_args = {
            **base_args,
            "dry_run": True,
            "actor": "agent:portfolio_reconcile_agent",
            "reason": "portfolio_reconcile_agent dry-run precheck",
            "idempotency_key": f"dryrun:{run_id}:business.reconcile_portfolio_positions",
        }
        out = execute_tool_step(
            run_id=run_id,
            step_index=step_index,
            tool_name="business.reconcile_portfolio_positions",
            arguments=dry_args,
        )
        step_index += 1
        if not out.get("ok"):
            raise RuntimeError(f"business.reconcile_portfolio_positions: {out.get('error')}")
        dry_result = out.get("result") if isinstance(out.get("result"), dict) else {}
        action = {"tool_name": "business.reconcile_portfolio_positions", "dry_run": dry_result}
        planned_actions.append({"tool_name": "business.reconcile_portfolio_positions", "arguments": base_args})
        if dry_result.get("requires_manual_review"):
            warnings.append("portfolio_reconcile_requires_manual_review")
            action["reason"] = "dry_run_conflicts"
            skipped_actions.append(action)
        elif dry_result.get("ok") is False:
            action["reason"] = "dry_run_failed"
            skipped_actions.append(action)
        else:
            write_args = {
                **base_args,
                "dry_run": False,
                "confirm": True,
                "actor": "agent:portfolio_reconcile_agent",
                "reason": "",
                "idempotency_key": _approval_idempotency_key(run, "business.reconcile_portfolio_positions", base_args),
            }
            step_id = store.insert_pending_step(
                run_id=run_id,
                step_index=step_index,
                tool_name="business.reconcile_portfolio_positions",
                args=write_args,
            )
            pending = {"step_id": step_id, "tool_name": "business.reconcile_portfolio_positions", "arguments": write_args, "dry_run": dry_result}
            requires_approval_actions.append(pending)
            pending_write_steps.append(pending)
    else:
        skipped_actions.append({"reason": "no_position_reconcile_gap_detected"})

    return {
        "ok": True,
        "agent_key": PORTFOLIO_RECONCILE_AGENT_KEY,
        "observations": observations,
        "plan": {"agent_key": PORTFOLIO_RECONCILE_AGENT_KEY, "planned_actions": planned_actions},
        "planned_actions": planned_actions,
        "executed_actions": [],
        "skipped_actions": skipped_actions,
        "requires_approval_actions": requires_approval_actions,
        "pending_write_steps": pending_write_steps,
        "warnings": warnings,
        "closure_status": "requires_approval" if pending_write_steps else ("requires_attention" if warnings else "no_action_needed"),
        "changed_count": 0,
    }


def run_portfolio_review_agent(run: dict[str, Any]) -> dict[str, Any]:
    run_id = str(run.get("id") or "")
    goal = dict(run.get("goal") or {})
    observations, step_index = _portfolio_observations(run_id)
    scan = observations.get("portfolio_closure_scan") or {}
    planned_actions: list[dict[str, Any]] = []
    requires_approval_actions: list[dict[str, Any]] = []
    skipped_actions: list[dict[str, Any]] = []
    pending_write_steps: list[dict[str, Any]] = []

    if scan.get("requires_review_generation") or goal.get("force_review_generation"):
        base_args = {
            "horizon_days": int(goal.get("horizon_days") or 5),
            "limit": int(goal.get("limit") or 200),
            "order_status": "executed",
        }
        dry_args = {
            **base_args,
            "dry_run": True,
            "actor": "agent:portfolio_review_agent",
            "reason": "portfolio_review_agent dry-run precheck",
            "idempotency_key": f"dryrun:{run_id}:business.generate_portfolio_order_reviews",
        }
        out = execute_tool_step(
            run_id=run_id,
            step_index=step_index,
            tool_name="business.generate_portfolio_order_reviews",
            arguments=dry_args,
        )
        step_index += 1
        if not out.get("ok"):
            raise RuntimeError(f"business.generate_portfolio_order_reviews: {out.get('error')}")
        dry_result = out.get("result") if isinstance(out.get("result"), dict) else {}
        planned_actions.append({"tool_name": "business.generate_portfolio_order_reviews", "arguments": base_args})
        action = {"tool_name": "business.generate_portfolio_order_reviews", "dry_run": dry_result}
        if dry_result.get("ok") is False or int(dry_result.get("changed_count") or 0) < 0:
            action["reason"] = "dry_run_failed"
            skipped_actions.append(action)
        elif not dry_result.get("planned_changes"):
            action["reason"] = "no_review_candidates"
            skipped_actions.append(action)
        else:
            write_args = {
                **base_args,
                "dry_run": False,
                "confirm": True,
                "actor": "agent:portfolio_review_agent",
                "reason": "",
                "idempotency_key": _approval_idempotency_key(run, "business.generate_portfolio_order_reviews", base_args),
            }
            step_id = store.insert_pending_step(
                run_id=run_id,
                step_index=step_index,
                tool_name="business.generate_portfolio_order_reviews",
                args=write_args,
            )
            pending = {"step_id": step_id, "tool_name": "business.generate_portfolio_order_reviews", "arguments": write_args, "dry_run": dry_result}
            requires_approval_actions.append(pending)
            pending_write_steps.append(pending)
    else:
        skipped_actions.append({"reason": "no_review_gap_detected"})

    return {
        "ok": True,
        "agent_key": PORTFOLIO_REVIEW_AGENT_KEY,
        "observations": observations,
        "plan": {"agent_key": PORTFOLIO_REVIEW_AGENT_KEY, "planned_actions": planned_actions},
        "planned_actions": planned_actions,
        "executed_actions": [],
        "skipped_actions": skipped_actions,
        "requires_approval_actions": requires_approval_actions,
        "pending_write_steps": pending_write_steps,
        "warnings": [],
        "closure_status": "requires_approval" if pending_write_steps else "no_action_needed",
        "changed_count": 0,
    }
