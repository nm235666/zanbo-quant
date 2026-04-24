from __future__ import annotations

from typing import Any

import db_compat as db
from mcp_server import config, schemas

from .common import KEY_TABLES, db_counts, row_to_dict


def _scalar(conn, sql: str, params=(), default: Any = None) -> Any:
    try:
        row = conn.execute(sql, params).fetchone()
        if not row:
            return default
        d = row_to_dict(row)
        if d:
            return next(iter(d.values()))
        return row[0]
    except Exception:
        return default


def health_snapshot(_: schemas.EmptyArgs) -> dict[str, Any]:
    conn = db.connect()
    db.apply_row_factory(conn)
    try:
        tables = db_counts(KEY_TABLES)
        table_count = _scalar(
            conn,
            "SELECT COUNT(*) AS cnt FROM information_schema.tables WHERE table_schema = current_schema()",
            default=None,
        )
        if table_count is None:
            table_count = _scalar(conn, "SELECT COUNT(*) AS cnt FROM sqlite_master WHERE type='table'", default=0)
        latest = {
            "stock_price": _scalar(conn, "SELECT MAX(trade_date) AS dt FROM stock_daily_prices", default=""),
            "score": _scalar(conn, "SELECT MAX(score_date) AS dt FROM stock_scores_daily", default=""),
            "news": _scalar(conn, "SELECT MAX(pub_time) AS dt FROM news_feed_items", default=""),
            "stock_news": _scalar(conn, "SELECT MAX(pub_time) AS dt FROM stock_news_items", default=""),
            "signal": _scalar(conn, "SELECT MAX(created_at) AS dt FROM investment_signal_events", default=""),
            "job_run": _scalar(conn, "SELECT MAX(created_at) AS dt FROM job_runs", default=""),
            "decision_action": _scalar(conn, "SELECT MAX(created_at) AS dt FROM decision_actions", default=""),
            "funnel_update": _scalar(conn, "SELECT MAX(updated_at) AS dt FROM funnel_candidates", default=""),
        }
        job_status_rows = []
        try:
            job_status_rows = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM job_runs GROUP BY status ORDER BY cnt DESC"
            ).fetchall()
        except Exception:
            job_status_rows = []
        return {
            "ok": True,
            "service": "zanbo-mcp",
            "db_label": db.db_label(),
            "using_postgres": db.using_postgres(),
            "table_count": int(table_count or 0),
            "key_tables": tables,
            "latest": latest,
            "job_status": {str(row_to_dict(r).get("status") or ""): int(row_to_dict(r).get("cnt") or 0) for r in job_status_rows},
            "base_urls": {"lan": config.MCP_LAN_BASE_URL, "public": config.MCP_PUBLIC_BASE_URL},
            "write_enabled": config.MCP_WRITE_ENABLED,
        }
    finally:
        conn.close()

