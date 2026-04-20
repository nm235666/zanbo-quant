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

    Fast synchronous analysis summary (<= 8s hard SLA).
    Reads ONLY from cached DB data (prices, signals, decision scores).
    NOTE: This endpoint MUST NOT call any LLM — DB reads only.
    """
    import concurrent.futures
    import db_compat as _db

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

    generated_at = datetime.datetime.utcnow().isoformat() + "Z"

    def _fetch_evidence(ts_code: str) -> dict:
        result: dict = {
            "ts_code": ts_code,
            "generated_at": generated_at,
            "confidence_level": "中",
            "view": None,
            "risk": None,
            "suggested_action": None,
            "missing_evidence": [],
            "evidence_used": [],
            "status": "ok",
        }
        conn = _db.connect()
        cur = conn.cursor()
        try:
            # Try to get decision score (using stock_scores_daily as the real score source)
            try:
                cur.execute(
                    """
                    SELECT score_grade, total_score, news_score, risk_score
                    FROM stock_scores_daily
                    WHERE ts_code = ?
                    ORDER BY score_date DESC LIMIT 1
                    """,
                    (ts_code,),
                )
                row = cur.fetchone()
                if row:
                    score_grade, total_score, news_score, risk_score = row
                    total_num = float(total_score or 0)
                    risk_num = float(risk_score or 0)
                    news_num = float(news_score or 0)
                    result["view"] = (
                        f"{score_grade or '中性'}：综合评分 {round(total_num, 1)}"
                        f"（新闻 {round(news_num, 1)} · 风险 {round(risk_num, 1)}）"
                    )
                    if risk_num < 40:
                        result["risk"] = f"风险评分偏低（{round(risk_num, 1)}），建议复核风险事件侧"
                    elif risk_num > 70:
                        result["risk"] = f"风险评分较高（{round(risk_num, 1)}），可作为加仓参考"
                    else:
                        result["risk"] = f"风险评分中性（{round(risk_num, 1)}）"
                    result["evidence_used"].append("stock_scores_daily")
                    result["confidence_level"] = (
                        "高" if total_num > 70 else ("低" if total_num < 40 else "中")
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
                    FROM investment_signal_tracker
                    WHERE ts_code = ?
                    ORDER BY latest_signal_date DESC LIMIT 1
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
        finally:
            cur.close()
            conn.close()
        return result

    start = time.time()
    timed_out = False
    result: dict = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_evidence, ts_code)
        try:
            result = future.result(timeout=8.0)
        except concurrent.futures.TimeoutError:
            timed_out = True
            future.cancel()

    elapsed_ms = int((time.time() - start) * 1000)

    if timed_out:
        handler._send_json({
            "ts_code": ts_code,
            "generated_at": generated_at,
            "status": "degraded",
            "code": "TIMEOUT",
            "error": "数据查询超时，已触发硬截断（8s SLA）",
            "action": "retry_or_use_deep_workflow",
            "confidence_level": "低",
            "view": f"{ts_code} 快速结论暂不可用（查询超时）",
            "risk": None,
            "suggested_action": "启动深度工作流",
            "missing_evidence": ["决策评分", "投资信号"],
            "evidence_used": [],
            "elapsed_ms": elapsed_ms,
            "timeout": True,
        })
        return

    # Evidence completeness check
    has_decision_score = "stock_scores_daily" in result.get("evidence_used", [])
    has_signal = "investment_signal" in result.get("evidence_used", [])

    if not has_decision_score and not has_signal:
        result["status"] = "degraded"
        result["code"] = "INSUFFICIENT_EVIDENCE"
        result["action"] = "run_deep_workflow_for_full_analysis"
        result["confidence_level"] = "低"
        if not result.get("view"):
            result["view"] = f"{ts_code} 受限结论：决策评分与投资信号均缺失"
    elif not has_decision_score:
        result["confidence_level"] = "低"
        if not result.get("view"):
            result["view"] = f"{ts_code} 信号已获取，但缺少决策评分"

    # Build suggested action
    if not result.get("view"):
        result["view"] = f"{ts_code} 受限结论：证据不足"
        result["confidence_level"] = "低"

    result["suggested_action"] = (
        "可关注"
        if result.get("confidence_level") == "高"
        else "建议深度分析"
        if result.get("confidence_level") == "中"
        else "启动深度工作流"
    )
    result["elapsed_ms"] = elapsed_ms

    handler._send_json(result)
