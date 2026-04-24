from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import db_compat as db
from mcp_server import schemas

from .common import clamp_limit, require_write_allowed, row_to_dict


def _count(conn, table: str, where: str = "", params=()) -> int:
    if not db.table_exists(conn, table):
        return 0
    sql = f"SELECT COUNT(*) AS cnt FROM {table} {where}"
    row = conn.execute(sql, tuple(params or ())).fetchone()
    d = row_to_dict(row)
    return int(d.get("cnt", row[0] if row else 0) or 0)


def closure_gap_scan(_: schemas.EmptyArgs) -> dict[str, Any]:
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        funnel_by_state = {}
        if db.table_exists(conn, "funnel_candidates"):
            for r in conn.execute("SELECT state, COUNT(*) AS cnt FROM funnel_candidates GROUP BY state").fetchall():
                d = row_to_dict(r)
                funnel_by_state[str(d.get("state") or "")] = int(d.get("cnt") or 0)
        order_by_status = {}
        if db.table_exists(conn, "portfolio_orders"):
            for r in conn.execute("SELECT status, COUNT(*) AS cnt FROM portfolio_orders GROUP BY status").fetchall():
                d = row_to_dict(r)
                order_by_status[str(d.get("status") or "")] = int(d.get("cnt") or 0)
        gaps = []
        if funnel_by_state.get("ingested", 0) > max(funnel_by_state.get("decision_ready", 0), 1):
            gaps.append("funnel_ingested_backlog")
        if _count(conn, "decision_actions") < 20:
            gaps.append("decision_action_sample_insufficient")
        if _count(conn, "portfolio_positions") == 0 and _count(conn, "portfolio_orders") > 0:
            gaps.append("portfolio_positions_empty")
        if _count(conn, "portfolio_reviews") == 0 and _count(conn, "portfolio_orders", "WHERE status = 'executed'") > 0:
            gaps.append("portfolio_reviews_empty_after_executions")
        return {
            "ok": True,
            "counts": {
                "decision_actions": _count(conn, "decision_actions"),
                "funnel_candidates": _count(conn, "funnel_candidates"),
                "portfolio_orders": _count(conn, "portfolio_orders"),
                "portfolio_positions": _count(conn, "portfolio_positions"),
                "portfolio_reviews": _count(conn, "portfolio_reviews"),
            },
            "funnel_by_state": funnel_by_state,
            "order_by_status": order_by_status,
            "gaps": gaps,
            "requires_attention": bool(gaps),
        }
    finally:
        conn.close()


def repair_funnel_score_align(args: schemas.FunnelScoreAlignArgs) -> dict[str, Any]:
    require_write_allowed(args)
    if args.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "planned_changes": [{"kind": "funnel_score_align", "score_date": args.score_date, "max_candidates": args.max_candidates}],
            "changed_count": 0,
            "skipped_count": 0,
            "warnings": ["dry_run_only"],
        }
    from services.funnel_service.service import promote_ingested_when_score_present

    result = promote_ingested_when_score_present(
        score_date=args.score_date or None,
        max_candidates=clamp_limit(args.max_candidates, maximum=50000),
    )
    return {
        "ok": bool(result.get("ok")),
        "dry_run": False,
        "planned_changes": [],
        "changed_count": int(result.get("promoted") or 0),
        "skipped_count": int(result.get("skipped_no_score") or 0) + int(result.get("idempotent_skips") or 0),
        "warnings": [str(x) for x in result.get("errors", [])],
        "result": result,
    }


def repair_funnel_review_refresh(args: schemas.FunnelReviewRefreshArgs) -> dict[str, Any]:
    require_write_allowed(args)
    if args.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "planned_changes": [{"kind": "funnel_review_refresh", "horizon_days": args.horizon_days, "limit": args.limit}],
            "changed_count": 0,
            "skipped_count": 0,
            "warnings": ["dry_run_only"],
        }
    from services.funnel_service.service import refresh_funnel_review_snapshots

    result = refresh_funnel_review_snapshots(
        horizon_days=max(1, min(int(args.horizon_days or 5), 60)),
        limit=clamp_limit(args.limit, maximum=2000),
    )
    return {
        "ok": bool(result.get("ok")),
        "dry_run": False,
        "planned_changes": [],
        "changed_count": int(result.get("written") or 0),
        "skipped_count": int(result.get("skipped") or 0),
        "warnings": [str(x) for x in result.get("errors", [])],
        "result": result,
    }


def run_decision_snapshot(args: schemas.DecisionSnapshotArgs) -> dict[str, Any]:
    require_write_allowed(args)
    if args.dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "planned_changes": [{"kind": "decision_snapshot", "job_key": args.job_key}],
            "changed_count": 0,
            "skipped_count": 0,
            "warnings": ["dry_run_only"],
        }
    from pathlib import Path
    import db_compat as sqlite3_module
    from services.decision_service import run_decision_scheduled_job

    result = run_decision_scheduled_job(
        sqlite3_module=sqlite3_module,
        db_path=str(Path(__file__).resolve().parents[2] / "stock_codes.db"),
        job_key=args.job_key or "decision_daily_snapshot",
    )
    return {
        "ok": bool(result.get("ok", True)),
        "dry_run": False,
        "planned_changes": [],
        "changed_count": int(result.get("snapshot_id") is not None or result.get("synced", 0) or 0),
        "skipped_count": 0,
        "warnings": [] if result.get("ok", True) else [str(result.get("error") or "decision_snapshot_failed")],
        "result": result,
    }


def portfolio_closure_scan(_: schemas.EmptyArgs) -> dict[str, Any]:
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        executed_orders = _count(
            conn,
            "portfolio_orders",
            "WHERE status = 'executed' AND executed_price IS NOT NULL AND COALESCE(size, 0) > 0",
        )
        positions = _count(conn, "portfolio_positions", "WHERE COALESCE(quantity, 0) > 0")
        reviews = _count(conn, "portfolio_reviews")
        missing_review_orders = 0
        decision_writeback_candidates = 0
        if db.table_exists(conn, "portfolio_orders"):
            if db.table_exists(conn, "portfolio_reviews"):
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS cnt
                    FROM portfolio_orders o
                    WHERE o.status = 'executed'
                      AND o.executed_price IS NOT NULL
                      AND COALESCE(o.size, 0) > 0
                      AND NOT EXISTS (
                        SELECT 1 FROM portfolio_reviews r WHERE r.order_id = o.id
                      )
                    """
                ).fetchone()
                missing_review_orders = int(row_to_dict(row).get("cnt", row[0] if row else 0) or 0)
            else:
                missing_review_orders = executed_orders
            if db.table_exists(conn, "decision_actions"):
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS cnt
                    FROM portfolio_orders o
                    WHERE o.status = 'executed'
                      AND COALESCE(o.decision_action_id, '') <> ''
                    """
                ).fetchone()
                decision_writeback_candidates = int(row_to_dict(row).get("cnt", row[0] if row else 0) or 0)
        gaps = []
        if executed_orders > 0 and positions == 0:
            gaps.append("portfolio_positions_empty_after_executions")
        if missing_review_orders > 0:
            gaps.append("portfolio_reviews_missing_after_executions")
        return {
            "ok": True,
            "executed_orders": executed_orders,
            "positions": positions,
            "reviews": reviews,
            "missing_review_orders": missing_review_orders,
            "decision_writeback_candidates": decision_writeback_candidates,
            "requires_position_reconcile": executed_orders > 0 and positions == 0,
            "requires_review_generation": missing_review_orders > 0,
            "gaps": gaps,
            "requires_attention": bool(gaps),
        }
    finally:
        conn.close()


@dataclass
class PositionState:
    ts_code: str
    quantity: int = 0
    avg_cost: float = 0.0
    last_price: float | None = None
    name: str = ""


def _latest_price_and_name(conn, ts_code: str) -> tuple[float | None, str]:
    latest_price = None
    name = ""
    try:
        row = conn.execute(
            "SELECT close FROM stock_daily_prices WHERE ts_code = ? AND close IS NOT NULL ORDER BY trade_date DESC LIMIT 1",
            (ts_code,),
        ).fetchone()
        d = row_to_dict(row)
        if d:
            latest_price = float(d.get("close")) if d.get("close") is not None else None
    except Exception:
        latest_price = None
    try:
        row = conn.execute("SELECT name FROM stock_codes WHERE ts_code = ? LIMIT 1", (ts_code,)).fetchone()
        d = row_to_dict(row)
        name = str(d.get("name") or "")
    except Exception:
        name = ""
    return latest_price, name


def _simulate_positions(conn, limit: int) -> tuple[dict[str, PositionState], list[dict[str, Any]], list[str]]:
    rows = conn.execute(
        """
        SELECT id, ts_code, action_type, executed_price, size, executed_at, created_at
        FROM portfolio_orders
        WHERE status = 'executed'
          AND executed_price IS NOT NULL
          AND COALESCE(size, 0) > 0
        ORDER BY COALESCE(executed_at, created_at), created_at
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    states: dict[str, PositionState] = {}
    changes: list[dict[str, Any]] = []
    warnings: list[str] = []
    for row in rows:
        d = row_to_dict(row)
        ts = str(d.get("ts_code") or "").strip().upper()
        action = str(d.get("action_type") or "").strip().lower()
        size = int(d.get("size") or 0)
        price = float(d.get("executed_price") or 0)
        if not ts or size <= 0 or price <= 0:
            continue
        state = states.setdefault(ts, PositionState(ts_code=ts))
        before_qty = state.quantity
        before_cost = state.avg_cost
        if action in {"buy", "add"}:
            total_cost = state.quantity * state.avg_cost + size * price
            state.quantity += size
            state.avg_cost = total_cost / state.quantity if state.quantity else 0.0
        elif action in {"sell", "reduce", "close"}:
            sell_size = state.quantity if action == "close" else size
            if sell_size > state.quantity:
                warnings.append(f"order {d.get('id')} sell_size>{state.quantity} for {ts}")
                continue
            state.quantity -= sell_size
            if state.quantity == 0:
                state.avg_cost = 0.0
        else:
            warnings.append(f"order {d.get('id')} unsupported_action:{action}")
            continue
        changes.append(
            {
                "order_id": d.get("id"),
                "ts_code": ts,
                "action_type": action,
                "before_quantity": before_qty,
                "after_quantity": state.quantity,
                "before_avg_cost": round(before_cost, 4),
                "after_avg_cost": round(state.avg_cost, 4),
            }
        )
    for ts, state in states.items():
        latest_price, name = _latest_price_and_name(conn, ts)
        state.last_price = latest_price if latest_price is not None else state.avg_cost
        state.name = name
    return states, changes, warnings


def reconcile_portfolio_positions(args: schemas.ReconcilePositionsArgs) -> dict[str, Any]:
    require_write_allowed(args)
    limit = clamp_limit(args.limit, maximum=5000)
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        if not db.table_exists(conn, "portfolio_orders"):
            return {"ok": False, "error": "portfolio_orders_missing"}
        from services.portfolio_service.service import _ensure_portfolio_tables

        _ensure_portfolio_tables(conn)
        states, changes, warnings = _simulate_positions(conn, limit)
        planned = []
        for state in states.values():
            market_value = (state.last_price or 0.0) * state.quantity
            unrealized = ((state.last_price or state.avg_cost) - state.avg_cost) * state.quantity if state.quantity else 0.0
            planned.append(
                {
                    "ts_code": state.ts_code,
                    "name": state.name,
                    "quantity": state.quantity,
                    "avg_cost": round(state.avg_cost, 4),
                    "last_price": state.last_price,
                    "market_value": round(market_value, 4),
                    "unrealized_pnl": round(unrealized, 4),
                }
            )
        if args.dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "planned_changes": planned,
                "order_changes": changes,
                "changed_count": 0,
                "skipped_count": 0,
                "warnings": warnings,
                "conflicts": warnings,
                "requires_manual_review": bool(warnings),
            }
        if warnings:
            return {
                "ok": False,
                "dry_run": False,
                "planned_changes": planned,
                "order_changes": changes,
                "changed_count": 0,
                "skipped_count": len(warnings),
                "warnings": warnings,
                "conflicts": warnings,
                "requires_manual_review": True,
                "error": "portfolio_reconcile_conflicts",
            }
        now_row = conn.execute("SELECT CURRENT_TIMESTAMP AS now").fetchone()
        now = str(row_to_dict(now_row).get("now") or "")
        conn.execute("DELETE FROM portfolio_positions")
        changed = 0
        for item in planned:
            if int(item["quantity"] or 0) <= 0:
                continue
            conn.execute(
                """
                INSERT INTO portfolio_positions
                    (id, ts_code, name, quantity, avg_cost, last_price, market_value, unrealized_pnl, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"pos:{item['ts_code']}",
                    item["ts_code"],
                    item["name"],
                    item["quantity"],
                    item["avg_cost"],
                    item["last_price"],
                    item["market_value"],
                    item["unrealized_pnl"],
                    now,
                ),
            )
            changed += 1
        try:
            conn.commit()
        except Exception:
            pass
        return {
            "ok": True,
            "dry_run": False,
            "planned_changes": planned,
            "order_changes": changes,
            "changed_count": changed,
            "skipped_count": max(0, len(planned) - changed),
            "warnings": warnings,
        }
    finally:
        conn.close()


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _anchor_to_trade_date(value: Any) -> str:
    text = str(value or "").strip()
    digits = "".join(ch for ch in text[:10] if ch.isdigit())
    return digits[:8]


def _latest_close_on_or_after(conn, ts_code: str, anchor: str, horizon_days: int) -> tuple[str, float] | None:
    if not db.table_exists(conn, "stock_daily_prices"):
        return None
    rows = conn.execute(
        """
        SELECT trade_date, close
        FROM stock_daily_prices
        WHERE ts_code = ?
          AND trade_date >= ?
          AND close IS NOT NULL
        ORDER BY trade_date
        LIMIT ?
        """,
        (ts_code, anchor, max(1, int(horizon_days or 5) + 1)),
    ).fetchall()
    if not rows:
        return None
    row = rows[min(len(rows) - 1, max(0, int(horizon_days or 5)))]
    d = row_to_dict(row)
    try:
        return str(d.get("trade_date") or ""), float(d.get("close") or 0)
    except Exception:
        return None


def _review_candidates(conn, *, horizon_days: int, limit: int, order_status: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not db.table_exists(conn, "portfolio_orders"):
        return [], [{"reason": "portfolio_orders_missing"}]
    rows = conn.execute(
        """
        SELECT id, ts_code, action_type, executed_price, planned_price, size, status,
               decision_action_id, note, executed_at, created_at
        FROM portfolio_orders
        WHERE status = ?
        ORDER BY COALESCE(executed_at, created_at), created_at
        LIMIT ?
        """,
        (order_status or "executed", clamp_limit(limit, maximum=2000)),
    ).fetchall()
    planned: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    review_table_exists = db.table_exists(conn, "portfolio_reviews")
    for row in rows:
        order = row_to_dict(row)
        order_id = str(order.get("id") or "")
        ts_code = str(order.get("ts_code") or "").strip().upper()
        try:
            executed_price = float(order.get("executed_price") or 0)
            size = int(order.get("size") or 0)
        except Exception:
            executed_price = 0
            size = 0
        if not order_id or not ts_code or executed_price <= 0 or size <= 0:
            skipped.append({"order_id": order_id, "reason": "missing_executed_price_or_size"})
            continue
        if review_table_exists:
            existing = conn.execute("SELECT id FROM portfolio_reviews WHERE order_id = ? LIMIT 1", (order_id,)).fetchone()
            if existing:
                skipped.append({"order_id": order_id, "reason": "review_exists"})
                continue
        anchor = _anchor_to_trade_date(order.get("executed_at") or order.get("created_at"))
        if not anchor:
            skipped.append({"order_id": order_id, "reason": "missing_anchor_date"})
            continue
        close = _latest_close_on_or_after(conn, ts_code, anchor, horizon_days)
        if not close:
            skipped.append({"order_id": order_id, "reason": "price_missing", "ts_code": ts_code, "anchor": anchor})
            continue
        review_date, close_price = close
        direction = -1 if str(order.get("action_type") or "").lower() in {"sell", "reduce", "close"} else 1
        return_pct = ((close_price - executed_price) / executed_price * 100 * direction) if executed_price else 0.0
        planned_price = order.get("planned_price")
        slippage = None
        try:
            if planned_price is not None:
                slippage = (executed_price - float(planned_price)) / float(planned_price) * 100
        except Exception:
            slippage = None
        tag = "positive" if return_pct >= 1 else ("negative" if return_pct <= -1 else "neutral")
        summary = {
            "horizon_days": horizon_days,
            "anchor_trade_date": anchor,
            "review_trade_date": review_date,
            "executed_price": executed_price,
            "review_close": close_price,
            "return_pct": round(return_pct, 4),
            "rule_correction_hint": "维持规则" if abs(return_pct) < 1 else ("复核买入依据" if return_pct < 0 else "记录有效信号"),
        }
        planned.append(
            {
                "order_id": order_id,
                "ts_code": ts_code,
                "decision_action_id": str(order.get("decision_action_id") or ""),
                "review_tag": tag,
                "review_note": json.dumps(summary, ensure_ascii=False, default=str),
                "slippage": round(slippage, 4) if slippage is not None else None,
                "latency_ms": None,
                "summary": summary,
            }
        )
    return planned, skipped


def _writeback_review_to_decision(conn, decision_action_id: str, conclusion: str) -> None:
    if not decision_action_id or not db.table_exists(conn, "decision_actions"):
        return
    try:
        row = conn.execute("SELECT action_payload_json FROM decision_actions WHERE id = ? LIMIT 1", (decision_action_id,)).fetchone()
        if not row:
            return
        payload = {}
        try:
            payload = json.loads(str(row_to_dict(row).get("action_payload_json") or "{}"))
        except Exception:
            payload = {}
        payload["review_conclusion"] = conclusion
        payload["review_updated_at"] = _utc_now()
        conn.execute(
            "UPDATE decision_actions SET action_payload_json = ? WHERE id = ?",
            (json.dumps(payload, ensure_ascii=False, default=str), decision_action_id),
        )
    except Exception:
        return


def generate_portfolio_order_reviews(args: schemas.PortfolioOrderReviewsArgs) -> dict[str, Any]:
    require_write_allowed(args)
    horizon_days = max(1, min(int(args.horizon_days or 5), 60))
    order_status = str(args.order_status or "executed").strip() or "executed"
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        from services.portfolio_service.service import _ensure_portfolio_tables

        _ensure_portfolio_tables(conn)
        planned, skipped = _review_candidates(conn, horizon_days=horizon_days, limit=args.limit, order_status=order_status)
        if args.dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "planned_changes": planned,
                "changed_count": 0,
                "skipped_count": len(skipped),
                "skipped": skipped,
                "warnings": [],
            }
        now = _utc_now()
        changed = 0
        for item in planned:
            review_id = f"review:{item['order_id']}:{horizon_days}"
            conn.execute(
                """
                INSERT INTO portfolio_reviews
                    (id, order_id, review_tag, review_note, slippage, latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    item["order_id"],
                    item["review_tag"],
                    item["review_note"],
                    item["slippage"],
                    item["latency_ms"],
                    now,
                ),
            )
            changed += 1
            _writeback_review_to_decision(conn, item.get("decision_action_id") or "", item["review_note"])
        try:
            conn.commit()
        except Exception:
            pass
        return {
            "ok": True,
            "dry_run": False,
            "planned_changes": planned,
            "changed_count": changed,
            "skipped_count": len(skipped),
            "skipped": skipped,
            "warnings": [],
        }
    finally:
        conn.close()
