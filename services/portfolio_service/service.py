from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import db_compat as _db

PORTFOLIO_ORDERS_TABLE = "portfolio_orders"
PORTFOLIO_POSITIONS_TABLE = "portfolio_positions"
PORTFOLIO_REVIEWS_TABLE = "portfolio_reviews"

VALID_ORDER_STATUSES = {"planned", "executed", "cancelled", "partial"}
VALID_ACTION_TYPES = {"buy", "sell", "add", "reduce", "close", "watch", "defer"}

ORDER_TO_EXECUTION_STATUS: dict[str, str] = {
    "planned": "planned",
    "partial": "executing",
    "executed": "done",
    "cancelled": "cancelled",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _table_exists(conn, table_name: str) -> bool:
    try:
        if _db.using_postgres():
            row = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s",
                (table_name,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            ).fetchone()
        return bool(row and int(row[0] or 0) > 0)
    except Exception:
        return False


def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except Exception:
        return {}


def _ensure_portfolio_tables(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PORTFOLIO_ORDERS_TABLE} (
            id TEXT PRIMARY KEY,
            ts_code TEXT NOT NULL,
            action_type TEXT NOT NULL DEFAULT 'buy',
            planned_price REAL,
            executed_price REAL,
            size INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'planned',
            decision_action_id TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            executed_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PORTFOLIO_POSITIONS_TABLE} (
            id TEXT PRIMARY KEY,
            ts_code TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 0,
            avg_cost REAL NOT NULL DEFAULT 0.0,
            last_price REAL,
            market_value REAL,
            unrealized_pnl REAL,
            updated_at TEXT NOT NULL,
            UNIQUE(ts_code)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PORTFOLIO_REVIEWS_TABLE} (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            review_tag TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            slippage REAL,
            latency_ms INTEGER,
            created_at TEXT NOT NULL
        )
        """
    )


def list_positions() -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_POSITIONS_TABLE):
                return {"items": [], "total": 0}
            rows = conn.execute(
                f"""
                SELECT id, ts_code, name, quantity, avg_cost, last_price,
                       market_value, unrealized_pnl, updated_at
                FROM {PORTFOLIO_POSITIONS_TABLE}
                WHERE quantity > 0
                ORDER BY market_value DESC NULLS LAST
                """
            ).fetchall()
            items = [_row_to_dict(r) for r in rows]
            return {"items": items, "total": len(items)}
        finally:
            conn.close()
    except Exception as exc:
        return {"items": [], "total": 0, "error": str(exc)}


def list_orders(
    *,
    status: str = "",
    decision_action_id: str = "",
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_ORDERS_TABLE):
                return {"items": [], "total": 0, "limit": limit, "offset": offset}
            conditions: list[str] = []
            params: list[Any] = []
            if status and status in VALID_ORDER_STATUSES:
                conditions.append("status = ?")
                params.append(status)
            if decision_action_id:
                conditions.append("decision_action_id = ?")
                params.append(decision_action_id)
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            count_row = conn.execute(
                f"SELECT COUNT(*) FROM {PORTFOLIO_ORDERS_TABLE} {where_clause}", params
            ).fetchone()
            total = int(count_row[0] or 0) if count_row else 0
            rows = conn.execute(
                f"""
                SELECT id, ts_code, action_type, planned_price, executed_price,
                       size, status, decision_action_id, note, executed_at,
                       created_at, updated_at
                FROM {PORTFOLIO_ORDERS_TABLE}
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            ).fetchall()
            items = [_row_to_dict(r) for r in rows]
            return {"items": items, "total": total, "limit": limit, "offset": offset}
        finally:
            conn.close()
    except Exception as exc:
        return {"items": [], "total": 0, "limit": limit, "offset": offset, "error": str(exc)}


def create_order(
    *,
    ts_code: str,
    action_type: str,
    planned_price: float | None,
    size: int,
    decision_action_id: str,
    note: str,
) -> dict[str, Any]:
    order_id = str(uuid.uuid4())
    now = _utc_now()
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_ORDERS_TABLE):
                _ensure_portfolio_tables(conn)
            conn.execute(
                f"""
                INSERT INTO {PORTFOLIO_ORDERS_TABLE}
                    (id, ts_code, action_type, planned_price, size, status,
                     decision_action_id, note, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'planned', ?, ?, ?, ?)
                """,
                (
                    order_id,
                    ts_code,
                    action_type,
                    planned_price,
                    size,
                    decision_action_id,
                    note,
                    now,
                    now,
                ),
            )
        finally:
            conn.close()
        return {"ok": True, "id": order_id, "status": "planned"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _writeback_to_decision_action(conn, decision_action_id: str, execution_status: str) -> None:
    """Write portfolio order execution status back to the linked decision action.
    Failure is silently swallowed — must never block the order update itself.
    """
    if not decision_action_id:
        return
    try:
        row = conn.execute(
            "SELECT action_payload_json FROM decision_actions WHERE id = ? LIMIT 1",
            (decision_action_id,),
        ).fetchone()
        if not row:
            return
        d = _row_to_dict(row)
        try:
            payload = json.loads(str(d.get("action_payload_json") or "{}"))
        except Exception:
            payload = {}
        payload["execution_status"] = execution_status
        conn.execute(
            "UPDATE decision_actions SET action_payload_json = ? WHERE id = ?",
            (json.dumps(payload, ensure_ascii=False), decision_action_id),
        )
    except Exception:
        pass  # Writeback failure must not block caller


def update_order(
    order_id: str,
    *,
    status: str | None = None,
    executed_price: float | None = None,
    executed_at: str | None = None,
) -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_ORDERS_TABLE):
                return {"ok": False, "error": "订单表不存在"}
            row = conn.execute(
                f"SELECT id, status FROM {PORTFOLIO_ORDERS_TABLE} WHERE id = ? LIMIT 1",
                (order_id,),
            ).fetchone()
            if not row:
                return {"ok": False, "error": "订单不存在"}
            now = _utc_now()
            set_parts: list[str] = ["updated_at = ?"]
            params: list[Any] = [now]
            if status is not None:
                if status not in VALID_ORDER_STATUSES:
                    return {"ok": False, "error": f"无效订单状态: {status}"}
                set_parts.append("status = ?")
                params.append(status)
            if executed_price is not None:
                set_parts.append("executed_price = ?")
                params.append(executed_price)
            if executed_at is not None:
                set_parts.append("executed_at = ?")
                params.append(executed_at)
            params.append(order_id)
            conn.execute(
                f"UPDATE {PORTFOLIO_ORDERS_TABLE} SET {', '.join(set_parts)} WHERE id = ?",
                params,
            )
            # Writeback execution status to linked decision action
            if status is not None and status in ORDER_TO_EXECUTION_STATUS:
                try:
                    order_row = conn.execute(
                        f"SELECT decision_action_id FROM {PORTFOLIO_ORDERS_TABLE} WHERE id = ? LIMIT 1",
                        (order_id,),
                    ).fetchone()
                    da_id = str(_row_to_dict(order_row).get("decision_action_id") or "") if order_row else ""
                    if da_id:
                        _writeback_to_decision_action(conn, da_id, ORDER_TO_EXECUTION_STATUS[status])
                except Exception:
                    pass  # Writeback failure must not block order update
        finally:
            conn.close()
        return {"ok": True, "id": order_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def list_reviews(
    *,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_REVIEWS_TABLE):
                return {"items": [], "total": 0, "limit": limit, "offset": offset}
            count_row = conn.execute(
                f"SELECT COUNT(*) FROM {PORTFOLIO_REVIEWS_TABLE}"
            ).fetchone()
            total = int(count_row[0] or 0) if count_row else 0
            rows = conn.execute(
                f"""
                SELECT id, order_id, review_tag, review_note, slippage, latency_ms, created_at
                FROM {PORTFOLIO_REVIEWS_TABLE}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                [limit, offset],
            ).fetchall()
            items = [_row_to_dict(r) for r in rows]
            return {"items": items, "total": total, "limit": limit, "offset": offset}
        finally:
            conn.close()
    except Exception as exc:
        return {"items": [], "total": 0, "limit": limit, "offset": offset, "error": str(exc)}


def add_review(
    *,
    order_id: str,
    review_tag: str,
    review_note: str,
    slippage: float | None,
    latency_ms: int | None,
) -> dict[str, Any]:
    review_id = str(uuid.uuid4())
    now = _utc_now()
    try:
        conn = _db.connect()
        try:
            if not _table_exists(conn, PORTFOLIO_REVIEWS_TABLE):
                _ensure_portfolio_tables(conn)
            conn.execute(
                f"""
                INSERT INTO {PORTFOLIO_REVIEWS_TABLE}
                    (id, order_id, review_tag, review_note, slippage, latency_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (review_id, order_id, review_tag, review_note, slippage, latency_ms, now),
            )
        finally:
            conn.close()
        return {"ok": True, "id": review_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
