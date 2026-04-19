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


def _score_conflict_resolution(sources: list[dict]) -> dict:
    """
    Score competing data sources on 4 criteria and return the winner + rationale.

    Criteria (higher = wins):
    1. 时效 (recency): hours since data was updated (lower hours = higher score)
    2. 风险等级 (risk level): high-risk signals get priority (safety-first)
    3. 信号强度 (signal strength): numerical signal confidence
    4. AI摘要一致性 (AI consistency): agreement across multiple AI summaries

    Each source dict should have:
      - source_type: str (e.g. "global_news", "cn_news", "theme_signal", "investment_signal")
      - data_age_hours: float (how old the data is)
      - risk_flag: bool (whether this source indicates elevated risk)
      - signal_strength: float (0.0–1.0, normalized)
      - ai_consistency: float (0.0–1.0, 1=fully consistent)

    Returns: {
        "winning_source": str,
        "score_breakdown": {source_type: {criterion: score}},
        "resolution_basis": str,
        "confidence": float,
    }
    """
    if not sources:
        return {
            "winning_source": "none",
            "score_breakdown": {},
            "resolution_basis": "无足够数据源参与裁决",
            "confidence": 0.0,
        }

    weights = {
        "recency": 0.4,
        "risk_level": 0.25,
        "signal_strength": 0.25,
        "ai_consistency": 0.10,
    }

    scored: list[tuple[float, str, dict]] = []
    for src in sources:
        source_type = str(src.get("source_type") or "unknown")
        age_hours = float(src.get("data_age_hours") or 48.0)
        risk_flag = bool(src.get("risk_flag") or False)
        signal_strength = min(1.0, max(0.0, float(src.get("signal_strength") or 0.5)))
        ai_consistency = min(1.0, max(0.0, float(src.get("ai_consistency") or 0.5)))

        # Recency score: 0 hours -> 1.0, 48+ hours -> 0.0
        recency_score = max(0.0, 1.0 - (age_hours / 48.0))
        # Risk priority: sources flagging risk get a boost (safety-first: 1.0 if risk, 0.5 otherwise)
        risk_score = 1.0 if risk_flag else 0.5

        composite = (
            weights["recency"] * recency_score
            + weights["risk_level"] * risk_score
            + weights["signal_strength"] * signal_strength
            + weights["ai_consistency"] * ai_consistency
        )
        breakdown = {
            "recency": round(recency_score, 3),
            "risk_level": round(risk_score, 3),
            "signal_strength": round(signal_strength, 3),
            "ai_consistency": round(ai_consistency, 3),
            "composite": round(composite, 3),
        }
        scored.append((composite, source_type, breakdown))

    scored.sort(key=lambda x: x[0], reverse=True)
    winner_score, winner_type, winner_breakdown = scored[0]

    # Determine resolution basis narrative
    if len(scored) == 1:
        basis = f"单一来源 {winner_type}，无裁决冲突"
    else:
        second_score = scored[1][0]
        margin = winner_score - second_score
        if winner_breakdown["recency"] > 0.8:
            basis = f"{winner_type} 胜出：时效优势（{margin:.2f} 分差）"
        elif winner_breakdown["risk_level"] == 1.0:
            basis = f"{winner_type} 胜出：风险信号优先原则（安全优先）"
        elif winner_breakdown["signal_strength"] > 0.7:
            basis = f"{winner_type} 胜出：信号强度领先（{winner_breakdown['signal_strength']:.2f}）"
        else:
            basis = f"{winner_type} 胜出：综合评分 {winner_score:.2f}（时效>风险>信号>AI一致性）"

    return {
        "winning_source": winner_type,
        "score_breakdown": {s[1]: s[2] for s in scored},
        "resolution_basis": basis,
        "confidence": round(winner_score, 3),
    }


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
    conflict_sources: list[dict] = []

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
                    conflict_sources.append({
                        "source_type": "global_news",
                        "data_age_hours": 2.0,  # summaries are typically fresh
                        "risk_flag": any(w in trading_theme.lower() for w in ("risk", "风险", "下跌", "bear", "跌")),
                        "signal_strength": 0.6,
                        "ai_consistency": 0.7,
                    })

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
                if theme_count > 0:
                    conflict_sources.append({
                        "source_type": "theme_signal",
                        "data_age_hours": 24.0,
                        "risk_flag": len(pressured_sectors) > len(benefiting_sectors),
                        "signal_strength": min(1.0, theme_count / 10.0),
                        "ai_consistency": 0.5,
                    })

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
                if candidate_directions:
                    avg_strength = sum(c.get("signal_strength", 0.5) for c in candidate_directions) / len(candidate_directions)
                    conflict_sources.append({
                        "source_type": "investment_signal",
                        "data_age_hours": 48.0,
                        "risk_flag": False,
                        "signal_strength": avg_strength,
                        "ai_consistency": 0.6,
                    })

        finally:
            conn.close()
    except Exception as exc:
        conflict_note = f"数据聚合异常: {exc}"

    if not trading_theme:
        trading_theme = "暂无足够数据生成今日交易主线摘要"

    resolution = _score_conflict_resolution(conflict_sources)

    return {
        "generated_at": generated_at,
        "trading_theme": trading_theme,
        "main_risks": main_risks,
        "benefiting_sectors": benefiting_sectors[:5],
        "pressured_sectors": pressured_sectors[:5],
        "candidate_directions": candidate_directions,
        "conflict_note": conflict_note,
        "resolution_basis": resolution["resolution_basis"],
        "conflict_resolution": {
            "winning_source": resolution["winning_source"],
            "confidence": resolution["confidence"],
            "score_breakdown": resolution["score_breakdown"],
        },
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
