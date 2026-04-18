from __future__ import annotations

"""Routes for /api/llm/quick-insight — fast synchronous analysis summary."""

import json
import time
import datetime


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    if parsed.path != "/api/llm/quick-insight":
        return False

    _handle_quick_insight(handler, payload)
    return True


def _handle_quick_insight(handler, payload: dict) -> None:
    """POST /api/llm/quick-insight

    Fast synchronous analysis summary (<= 8s target).
    Reads available cached data (prices, signals, news summaries) for the ts_code
    and returns a structured conclusion card.
    Does NOT trigger multi-role analysis or deep LLM calls.
    """
    from db_compat import get_db_connection

    ts_code = str(payload.get("ts_code", "") or "").strip().upper()
    if not ts_code:
        handler._send_json(
            {
                "error": "缺少必要参数",
                "code": "MISSING_FIELD",
                "action": "check_request",
            },
            status=400,
        )
        return

    start = time.time()
    result = {
        "ts_code": ts_code,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "confidence_level": "中",
        "view": None,
        "risk": None,
        "suggested_action": None,
        "missing_evidence": [],
        "evidence_used": [],
    }

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Try to get decision score
        try:
            cur.execute(
                """
                SELECT position_label, total_score, reason, risk
                FROM decision_stocks
                WHERE ts_code = %s
                ORDER BY score_date DESC LIMIT 1
                """,
                (ts_code,),
            )
            row = cur.fetchone()
            if row:
                position_label, total_score, reason, risk = row
                result["view"] = (
                    f"{position_label or '中性'}: "
                    f"{reason or '综合评分 ' + str(round(total_score or 0, 1))}"
                )
                result["risk"] = risk or "无明确风险提示"
                result["evidence_used"].append("decision_score")
                result["confidence_level"] = (
                    "高" if total_score and total_score > 70 else "中"
                )
            else:
                result["missing_evidence"].append("决策评分")
        except Exception:
            result["missing_evidence"].append("决策评分")

        # Try to get latest signal
        try:
            cur.execute(
                """
                SELECT signal_type, signal_strength, direction
                FROM investment_signals
                WHERE ts_code = %s
                ORDER BY signal_date DESC LIMIT 1
                """,
                (ts_code,),
            )
            sig = cur.fetchone()
            if sig:
                sig_type, _strength, direction = sig
                if not result["view"]:
                    result["view"] = f"信号: {sig_type or ''} {direction or ''}".strip()
                result["evidence_used"].append("investment_signal")
            else:
                result["missing_evidence"].append("投资信号")
        except Exception:
            result["missing_evidence"].append("投资信号")

        cur.close()
        conn.close()
    except Exception:
        result["missing_evidence"].extend(["价格快照", "催化摘要", "信号摘要"])

    # Build suggested action
    if not result["view"]:
        result["view"] = f"{ts_code} 受限结论：证据不足"
        result["confidence_level"] = "低"

    result["suggested_action"] = (
        "可关注"
        if result["confidence_level"] == "高"
        else "建议深度分析"
        if result["confidence_level"] == "中"
        else "启动深度工作流"
    )
    result["elapsed_ms"] = int((time.time() - start) * 1000)

    handler._send_json(result)
