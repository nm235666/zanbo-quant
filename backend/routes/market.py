from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import db_compat as _db


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


def _safe_str(val: Any, default: str = "") -> str:
    return str(val or default).strip()


def _get_market_conclusion() -> dict[str, Any]:
    generated_at = _utc_now()
    global_news_count = 0
    cn_news_count = 0
    macro_count = 0
    theme_count = 0

    trading_theme = ""
    main_risks: list[str] = []
    benefiting_sectors: list[str] = []
    pressured_sectors: list[str] = []
    candidate_directions: list[dict] = []
    conflict_note = ""

    try:
        conn = _db.connect()
        try:
            # Fetch latest global news summary
            if _table_exists(conn, "news_daily_summaries"):
                row = conn.execute(
                    """
                    SELECT summary_text, source_type, summary_date
                    FROM news_daily_summaries
                    WHERE source_type IN ('global', 'international')
                    ORDER BY summary_date DESC, id DESC
                    LIMIT 1
                    """
                ).fetchone()
                if row:
                    d = _row_to_dict(row)
                    global_news_count = 1
                    summary_text = _safe_str(d.get("summary_text"))
                    if summary_text and not trading_theme:
                        trading_theme = summary_text[:200]

            # Fetch latest cn news summary
            if _table_exists(conn, "news_daily_summaries"):
                row = conn.execute(
                    """
                    SELECT summary_text, source_type, summary_date
                    FROM news_daily_summaries
                    WHERE source_type IN ('cn', 'domestic', 'china')
                    ORDER BY summary_date DESC, id DESC
                    LIMIT 1
                    """
                ).fetchone()
                if row:
                    d = _row_to_dict(row)
                    cn_news_count = 1

            # Count recent cn news items
            if _table_exists(conn, "stock_news"):
                row = conn.execute(
                    """
                    SELECT COUNT(*) as cnt FROM stock_news
                    WHERE created_at >= datetime('now', '-24 hours')
                    """
                ).fetchone()
                if row:
                    d = _row_to_dict(row)
                    cn_news_count = int(d.get("cnt") or 0)

            # Fetch macro indicators count
            if _table_exists(conn, "macro_indicators"):
                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM macro_indicators LIMIT 1"
                ).fetchone()
                if row:
                    d = _row_to_dict(row)
                    macro_count = int(d.get("cnt") or 0)

            # Fetch recent theme hotspots
            if _table_exists(conn, "theme_hotspots"):
                rows = conn.execute(
                    """
                    SELECT theme_name, direction, heat_level
                    FROM theme_hotspots
                    WHERE updated_at >= datetime('now', '-48 hours')
                    ORDER BY heat_level DESC NULLS LAST
                    LIMIT 10
                    """
                ).fetchall()
                theme_count = len(rows) if rows else 0
                for r in (rows or []):
                    d = _row_to_dict(r)
                    name = _safe_str(d.get("theme_name"))
                    direction = _safe_str(d.get("direction"))
                    if not name:
                        continue
                    if direction in ("up", "bullish", "涨", "多"):
                        if name not in benefiting_sectors:
                            benefiting_sectors.append(name)
                    elif direction in ("down", "bearish", "跌", "空"):
                        if name not in pressured_sectors:
                            pressured_sectors.append(name)

            # Fetch top investment signals as candidate directions
            if _table_exists(conn, "investment_signals"):
                rows = conn.execute(
                    """
                    SELECT ts_code, signal_name, signal_strength, direction
                    FROM investment_signals
                    WHERE updated_at >= datetime('now', '-48 hours')
                      AND direction IN ('up', 'bullish', '多', '涨')
                    ORDER BY signal_strength DESC NULLS LAST
                    LIMIT 5
                    """
                ).fetchall()
                for r in (rows or []):
                    d = _row_to_dict(r)
                    ts_code = _safe_str(d.get("ts_code"))
                    if not ts_code:
                        continue
                    candidate_directions.append(
                        {
                            "ts_code": ts_code,
                            "name": _safe_str(d.get("signal_name")),
                            "reason": "信号强度驱动",
                            "signal_strength": float(d.get("signal_strength") or 0.0),
                        }
                    )

        finally:
            conn.close()
    except Exception as exc:
        conflict_note = f"数据聚合异常: {exc}"

    if not trading_theme:
        trading_theme = "暂无足够数据生成今日交易主线摘要"

    return {
        "generated_at": generated_at,
        "trading_theme": trading_theme,
        "main_risks": main_risks,
        "benefiting_sectors": benefiting_sectors[:5],
        "pressured_sectors": pressured_sectors[:5],
        "candidate_directions": candidate_directions,
        "conflict_note": conflict_note,
        "resolution_basis": "时效>风险等级>信号强度>AI摘要一致性",
        "sources": {
            "global_news_count": global_news_count,
            "cn_news_count": cn_news_count,
            "macro_indicators": macro_count,
            "theme_signals": theme_count,
        },
    }


def dispatch_get(handler, parsed, deps: dict) -> bool:
    if not parsed.path.startswith("/api/market"):
        return False

    if parsed.path == "/api/market/conclusion":
        try:
            payload = _get_market_conclusion()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"市场结论聚合失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    return False
