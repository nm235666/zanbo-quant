from __future__ import annotations

import json
import time
from urllib.parse import parse_qs

MULTI_ROLE_DEDICATED_GPT_CHANNEL = "gpt-5.4-multi-role"
TREND_DEDICATED_GPT_CHANNEL = "gpt-5.4-trend"
DAILY_SUMMARY_DEDICATED_GPT_CHANNEL = "gpt-5.4-daily-summary"


def _safe_bool(value, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "enabled", "active"}:
        return True
    if text in {"0", "false", "no", "off", "disabled", "inactive"}:
        return False
    return default


def _resolve_roles_from_payload(payload: dict, deps: dict) -> list[str]:
    raw = payload.get("roles", "")
    if isinstance(raw, list):
        role_text = ",".join([str(x).strip() for x in raw if str(x).strip()])
    else:
        role_text = str(raw or "")
    return deps["_resolve_roles"](role_text)


def dispatch_get(handler, parsed, deps: dict) -> bool:
    if parsed.path.startswith("/api/llm/multi-role/v3/jobs/"):
        suffix = parsed.path[len("/api/llm/multi-role/v3/jobs/"):]
        if suffix.endswith("/stream"):
            job_id = suffix[:-len("/stream")].strip().strip("/")
            if not job_id:
                handler._send_json({"error": "缺少 job_id"}, status=400)
                return True
            params = parse_qs(parsed.query)
            try:
                interval_ms = int(params.get("interval_ms", ["1000"])[0] or 1000)
            except ValueError:
                handler._send_json({"error": "interval_ms 必须是整数"}, status=400)
                return True
            try:
                timeout_seconds = int(params.get("timeout_seconds", ["180"])[0] or 180)
            except ValueError:
                handler._send_json({"error": "timeout_seconds 必须是整数"}, status=400)
                return True
            interval_ms = max(300, min(5000, interval_ms))
            timeout_seconds = max(10, min(600, timeout_seconds))
            first_job = deps["get_multi_role_v3_job_by_id"](job_id)
            if not first_job:
                handler._send_json({"error": f"任务不存在或已过期: {job_id}"}, status=404)
                return True
            handler.send_response(200)
            handler.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            handler.send_header("Cache-Control", "no-cache, no-transform")
            handler.send_header("Connection", "keep-alive")
            handler.end_headers()

            def _stream_write(payload: dict) -> bool:
                try:
                    handler.wfile.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
                    handler.wfile.flush()
                    return True
                except Exception:
                    return False

            started = time.time()
            last_signature = ""
            while True:
                job = deps["get_multi_role_v3_job_by_id"](job_id)
                if not job:
                    _stream_write({"ok": False, "event": "error", "job_id": job_id, "error": f"任务不存在或已过期: {job_id}", "terminal": True})
                    return True
                status = str(job.get("status") or "")
                signature = "|".join(
                    [
                        str(job.get("status") or ""),
                        str(job.get("stage") or ""),
                        str(job.get("updated_at") or ""),
                        str(job.get("progress") or 0),
                        str(len(list(job.get("node_runs") or []))),
                    ]
                )
                if signature != last_signature:
                    if not _stream_write({"ok": True, "event": "update", "job_id": job_id, "job": job}):
                        return True
                    last_signature = signature
                if status in {"approved", "rejected", "deferred", "done_with_warnings", "error"}:
                    _stream_write({"ok": True, "event": "end", "job_id": job_id, "terminal": True, "status": status})
                    return True
                if (time.time() - started) >= timeout_seconds:
                    _stream_write({"ok": True, "event": "timeout", "job_id": job_id, "terminal": False})
                    return True
                time.sleep(interval_ms / 1000.0)
        job_id = suffix.strip().strip("/")
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        job = deps["get_multi_role_v3_job_by_id"](job_id)
        if not job:
            handler._send_json({"error": f"任务不存在或已过期: {job_id}"}, status=404)
            return True
        handler._send_json({"ok": True, **job})
        return True

    if parsed.path == "/api/stock-detail":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0].strip().upper()
        keyword = params.get("keyword", [""])[0].strip()
        try:
            lookback = int(params.get("lookback", ["60"])[0])
        except ValueError:
            handler._send_json({"error": "lookback 必须是整数"}, status=400)
            return True
        if not ts_code and not keyword:
            handler._send_json({"error": "缺少 ts_code 或 keyword"}, status=400)
            return True
        try:
            payload = deps["query_stock_detail"](ts_code=ts_code, keyword=keyword, lookback=lookback)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"详情查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/stocks":
        params = parse_qs(parsed.query)
        keyword = params.get("keyword", [""])[0]
        status = params.get("status", [""])[0]
        market = params.get("market", [""])[0]
        area = params.get("area", [""])[0]

        try:
            page = int(params.get("page", ["1"])[0])
            page_size = int(params.get("page_size", ["20"])[0])
        except ValueError:
            handler._send_json({"error": "page/page_size 必须是整数"}, status=400)
            return True

        try:
            payload = deps["query_stocks"](keyword, status, market, area, page, page_size)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True

        handler._send_json(payload)
        return True

    if parsed.path == "/api/stocks/filters":
        try:
            payload = deps["query_stock_filters"]()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/stock-scores/filters":
        try:
            payload = deps["query_stock_score_filters"]()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/stock-scores":
        params = parse_qs(parsed.query)
        keyword = params.get("keyword", [""])[0]
        market = params.get("market", [""])[0]
        area = params.get("area", [""])[0]
        industry = params.get("industry", [""])[0]
        sort_by = params.get("sort_by", ["total_score"])[0]
        sort_order = params.get("sort_order", ["desc"])[0]
        try:
            min_score = float(params.get("min_score", ["0"])[0] or 0)
            page = int(params.get("page", ["1"])[0])
            page_size = int(params.get("page_size", ["20"])[0])
        except ValueError:
            handler._send_json({"error": "min_score/page/page_size 参数格式错误"}, status=400)
            return True
        try:
            payload = deps["query_stock_scores"](
                keyword=keyword,
                market=market,
                area=area,
                industry=industry,
                min_score=min_score,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/prices":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0]
        start_date = params.get("start_date", [""])[0]
        end_date = params.get("end_date", [""])[0]

        try:
            page = int(params.get("page", ["1"])[0])
            page_size = int(params.get("page_size", ["20"])[0])
        except ValueError:
            handler._send_json({"error": "page/page_size 必须是整数"}, status=400)
            return True

        try:
            payload = deps["query_prices"](ts_code, start_date, end_date, page, page_size)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True

        handler._send_json(payload)
        return True

    if parsed.path == "/api/minline":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0]
        trade_date = params.get("trade_date", [""])[0]
        try:
            page = int(params.get("page", ["1"])[0])
            page_size = int(params.get("page_size", ["240"])[0])
        except ValueError:
            handler._send_json({"error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_minline"](ts_code, trade_date, page, page_size)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/llm/trend":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0].strip().upper()
        requested_model = deps["normalize_model_name"](params.get("model", [""])[0])
        requested_key = str(requested_model or "").strip().lower()
        if requested_key == MULTI_ROLE_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-multi-role 仅允许多角色公司分析链路使用"}, status=400)
            return True
        if requested_key == DAILY_SUMMARY_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-daily-summary 仅允许新闻日报生成链路使用"}, status=400)
            return True
        # 股票走势分析固定走专用 GPT 通道，不与通用模型池混用。
        if requested_key and requested_key not in {"auto", "default", "gpt-5.4", TREND_DEDICATED_GPT_CHANNEL}:
            handler._send_json({"error": "股票走势分析仅允许使用 gpt-5.4-trend 专用通道"}, status=400)
            return True
        model = TREND_DEDICATED_GPT_CHANNEL
        if not ts_code:
            handler._send_json({"error": "缺少 ts_code"}, status=400)
            return True
        try:
            lookback = int(params.get("lookback", ["120"])[0])
        except ValueError:
            handler._send_json({"error": "lookback 必须是整数"}, status=400)
            return True
        auth_ctx = deps.get("auth_context") or {}
        quota = deps["consume_trend_daily_quota"](auth_ctx.get("user"))
        if not quota.get("allowed", True):
            handler._send_json(
                {
                    "error": f"LLM走势分析今日次数已用完（{quota.get('limit')} 次/日），请明日再试或升级权限",
                    "quota": quota,
                },
                status=429,
            )
            return True
        try:
            payload = deps["run_trend_analysis"](
                deps,
                ts_code=ts_code,
                lookback=lookback,
                model=model,
                temperature=0.2,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"分析失败: {exc}"}, status=500)
            return True
        payload["quota"] = quota
        handler._send_json(payload)
        return True

    if parsed.path == "/api/llm/multi-role":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0].strip().upper()
        model = deps["normalize_model_name"](params.get("model", [deps["DEFAULT_LLM_MODEL"]])[0])
        if str(model or "").strip().lower() == TREND_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-trend 仅允许股票走势分析链路使用"}, status=400)
            return True
        if str(model or "").strip().lower() == DAILY_SUMMARY_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-daily-summary 仅允许新闻日报生成链路使用"}, status=400)
            return True
        roles_raw = params.get("roles", [""])[0]
        if not ts_code:
            handler._send_json({"error": "缺少 ts_code"}, status=400)
            return True
        try:
            lookback = int(params.get("lookback", ["120"])[0])
        except ValueError:
            handler._send_json({"error": "lookback 必须是整数"}, status=400)
            return True
        auth_ctx = deps.get("auth_context") or {}
        quota = deps["consume_multi_role_daily_quota"](auth_ctx.get("user"))
        if not quota.get("allowed", True):
            handler._send_json(
                {
                    "error": f"LLM多角色分析今日次数已用完（{quota.get('limit')} 次/日），请明日再试或升级权限",
                    "quota": quota,
                },
                status=429,
            )
            return True
        roles = deps["_resolve_roles"](roles_raw)
        try:
            payload = deps["run_multi_role_analysis"](
                deps,
                ts_code=ts_code,
                lookback=lookback,
                roles=roles,
                model=model,
                temperature=0.2,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"分析失败: {exc}"}, status=500)
            return True
        payload["quota"] = quota
        handler._send_json(payload)
        return True

    if parsed.path == "/api/llm/multi-role/start":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0].strip().upper()
        model = deps["normalize_model_name"](params.get("model", [deps["DEFAULT_LLM_MODEL"]])[0])
        if str(model or "").strip().lower() == TREND_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-trend 仅允许股票走势分析链路使用"}, status=400)
            return True
        if str(model or "").strip().lower() == DAILY_SUMMARY_DEDICATED_GPT_CHANNEL:
            handler._send_json({"error": "gpt-5.4-daily-summary 仅允许新闻日报生成链路使用"}, status=400)
            return True
        roles_raw = params.get("roles", [""])[0]
        if not ts_code:
            handler._send_json({"error": "缺少 ts_code"}, status=400)
            return True
        try:
            lookback = int(params.get("lookback", ["120"])[0])
        except ValueError:
            handler._send_json({"error": "lookback 必须是整数"}, status=400)
            return True
        auth_ctx = deps.get("auth_context") or {}
        quota = deps["consume_multi_role_daily_quota"](auth_ctx.get("user"))
        if not quota.get("allowed", True):
            handler._send_json(
                {
                    "error": f"LLM多角色分析今日次数已用完（{quota.get('limit')} 次/日），请明日再试或升级权限",
                    "quota": quota,
                },
                status=429,
            )
            return True
        roles = deps["_resolve_roles"](roles_raw)
        try:
            job = deps["start_async_multi_role_job"](ts_code, lookback, model, roles)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"error": f"启动分析失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, "quota": quota, **job})
        return True

    if parsed.path == "/api/llm/multi-role/task":
        params = parse_qs(parsed.query)
        job_id = params.get("job_id", [""])[0].strip()
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        job = deps["get_async_multi_role_job"](job_id)
        if not job:
            handler._send_json({"error": f"任务不存在或已过期: {job_id}"}, status=404)
            return True
        handler._send_json({"ok": True, **job})
        return True

    if parsed.path == "/api/llm/multi-role/v2/task":
        params = parse_qs(parsed.query)
        job_id = params.get("job_id", [""])[0].strip()
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        job = deps["get_async_multi_role_v2_job"](job_id)
        if not job:
            handler._send_json({"error": f"任务不存在或已过期: {job_id}"}, status=404)
            return True
        handler._send_json({"ok": True, **job})
        return True

    if parsed.path == "/api/llm/multi-role/v2/stream":
        params = parse_qs(parsed.query)
        job_id = params.get("job_id", [""])[0].strip()
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        try:
            interval_ms = int(params.get("interval_ms", ["1000"])[0] or 1000)
        except ValueError:
            handler._send_json({"error": "interval_ms 必须是整数"}, status=400)
            return True
        try:
            timeout_seconds = int(params.get("timeout_seconds", ["180"])[0] or 180)
        except ValueError:
            handler._send_json({"error": "timeout_seconds 必须是整数"}, status=400)
            return True
        interval_ms = max(300, min(5000, interval_ms))
        timeout_seconds = max(10, min(600, timeout_seconds))

        first_job = deps["get_async_multi_role_v2_job"](job_id)
        if not first_job:
            handler._send_json({"error": f"任务不存在或已过期: {job_id}"}, status=404)
            return True

        handler.send_response(200)
        handler.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        handler.send_header("Cache-Control", "no-cache, no-transform")
        handler.send_header("Connection", "keep-alive")
        handler.end_headers()

        def _stream_write(payload: dict) -> bool:
            try:
                handler.wfile.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
                handler.wfile.flush()
                return True
            except Exception:
                return False

        started = time.time()
        last_signature = ""
        while True:
            job = deps["get_async_multi_role_v2_job"](job_id)
            if not job:
                _stream_write({"ok": False, "event": "error", "job_id": job_id, "error": f"任务不存在或已过期: {job_id}", "terminal": True})
                return True
            status = str(job.get("status") or "")
            signature = "|".join(
                [
                    str(job.get("status") or ""),
                    str(job.get("stage") or ""),
                    str(job.get("progress") or 0),
                    str(job.get("updated_at") or ""),
                    str((job.get("aggregator_run") or {}).get("status") or ""),
                    str(len(list(job.get("role_runs") or []))),
                ]
            )
            if signature != last_signature:
                if not _stream_write({"ok": True, "event": "update", "job_id": job_id, "job": job}):
                    return True
                last_signature = signature
            if status in {"done", "done_with_warnings", "error"}:
                _stream_write({"ok": True, "event": "end", "job_id": job_id, "terminal": True, "status": status})
                return True
            if (time.time() - started) >= timeout_seconds:
                _stream_write({"ok": True, "event": "timeout", "job_id": job_id, "terminal": False})
                return True
            time.sleep(interval_ms / 1000.0)

    if parsed.path == "/api/llm/multi-role/v2/history":
        params = parse_qs(parsed.query)
        version = params.get("version", ["v2"])[0]
        ts_code = params.get("ts_code", [""])[0]
        status = params.get("status", [""])[0]
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["20"])[0] or 20)
        except ValueError:
            handler._send_json({"error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_multi_role_analysis_history"](
                version=version,
                ts_code=ts_code,
                status=status,
                page=page,
                page_size=page_size,
            )
        except Exception as exc:
            handler._send_json({"error": f"查询历史失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    return False


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    if parsed.path == "/api/llm/multi-role/v3/jobs":
        ts_code = str(payload.get("ts_code", "") or "").strip().upper()
        if not ts_code:
            handler._send_json({"error": "缺少 ts_code"}, status=400)
            return True
        auth_ctx = deps.get("auth_context") or {}
        quota = deps["consume_multi_role_daily_quota"](auth_ctx.get("user"))
        if not quota.get("allowed", True):
            handler._send_json(
                {
                    "error": f"LLM多角色分析今日次数已用完（{quota.get('limit')} 次/日），请明日再试或升级权限",
                    "quota": quota,
                },
                status=429,
            )
            return True
        try:
            job = deps["start_multi_role_v3_job"](payload)
        except ValueError as exc:
            handler._send_json({"error": str(exc)}, status=400)
            return True
        except Exception as exc:
            handler._send_json({"error": f"创建 V3 任务失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, "quota": quota, **job})
        return True

    if parsed.path.startswith("/api/llm/multi-role/v3/jobs/"):
        suffix = parsed.path[len("/api/llm/multi-role/v3/jobs/"):]
        if suffix.endswith("/decisions"):
            job_id = suffix[:-len("/decisions")].strip().strip("/")
            if not job_id:
                handler._send_json({"error": "缺少 job_id"}, status=400)
                return True
            action = str(payload.get("action", "") or "").strip().lower()
            if action not in {"retry", "degrade", "abort", "resume"}:
                handler._send_json({"error": "action 必须是 retry|degrade|abort|resume"}, status=400)
                return True
            try:
                result = deps["decide_multi_role_v3_job"](job_id=job_id, action=action)
            except ValueError as exc:
                handler._send_json({"error": str(exc)}, status=400)
                return True
            except RuntimeError as exc:
                handler._send_json({"error": str(exc)}, status=409)
                return True
            except Exception as exc:
                handler._send_json({"error": f"处理 V3 决策失败: {exc}"}, status=500)
                return True
            handler._send_json({"ok": True, **result})
            return True
        if suffix.endswith("/actions"):
            job_id = suffix[:-len("/actions")].strip().strip("/")
            if not job_id:
                handler._send_json({"error": "缺少 job_id"}, status=400)
                return True
            action = str(payload.get("action", "") or "").strip().lower()
            stage = str(payload.get("stage", "") or "").strip()
            if action not in {"retry_stage", "re_aggregate", "abort", "resume"}:
                handler._send_json({"error": "action 必须是 retry_stage|re_aggregate|abort|resume"}, status=400)
                return True
            try:
                result = deps["action_multi_role_v3_job"](job_id=job_id, action=action, stage=stage)
            except ValueError as exc:
                handler._send_json({"error": str(exc)}, status=400)
                return True
            except RuntimeError as exc:
                handler._send_json({"error": str(exc)}, status=409)
                return True
            except Exception as exc:
                handler._send_json({"error": f"处理 V3 action 失败: {exc}"}, status=500)
                return True
            handler._send_json({"ok": True, **result})
            return True

    if parsed.path == "/api/llm/multi-role/v2/start":
        ts_code = str(payload.get("ts_code", "") or "").strip().upper()
        if not ts_code:
            handler._send_json({"error": "缺少 ts_code"}, status=400)
            return True
        try:
            lookback = int(payload.get("lookback", 120) or 120)
        except ValueError:
            handler._send_json({"error": "lookback 必须是整数"}, status=400)
            return True
        try:
            decision_timeout_seconds = int(payload.get("decision_timeout_seconds", 600) or 600)
        except ValueError:
            handler._send_json({"error": "decision_timeout_seconds 必须是整数"}, status=400)
            return True
        accept_auto_degrade = _safe_bool(payload.get("accept_auto_degrade", True), True)
        roles = _resolve_roles_from_payload(payload, deps)
        try:
            reusable = deps["find_today_reusable_multi_role_v2_job"](
                ts_code=ts_code,
                lookback=lookback,
                roles=roles,
            )
        except Exception as exc:
            print(f"[multi-role-v2] reusable-check failed ts_code={ts_code} lookback={lookback} error={exc}", flush=True)
            reusable = None
        if reusable:
            quota = deps["get_multi_role_daily_quota_status"]((deps.get("auth_context") or {}).get("user"))
            handler._send_json(
                {
                    "ok": True,
                    "reused_today": True,
                    "message": "检测到当日已完成分析，直接复用历史结果",
                    "quota": quota,
                    **reusable,
                }
            )
            return True
        auth_ctx = deps.get("auth_context") or {}
        quota = deps["consume_multi_role_daily_quota"](auth_ctx.get("user"))
        if not quota.get("allowed", True):
            handler._send_json(
                {
                    "error": f"LLM多角色分析今日次数已用完（{quota.get('limit')} 次/日），请明日再试或升级权限",
                    "quota": quota,
                },
                status=429,
            )
            return True
        try:
            job = deps["start_async_multi_role_v2_job"](
                ts_code=ts_code,
                lookback=lookback,
                roles=roles,
                accept_auto_degrade=accept_auto_degrade,
                decision_timeout_seconds=decision_timeout_seconds,
            )
        except Exception as exc:
            handler._send_json({"error": f"启动 V2 分析失败: {exc}"}, status=500)
            return True
        handler._send_json(
            {
                "ok": True,
                "quota": quota,
                "failure_policy": {
                    "initial_retry": 1,
                    "pending_action_on_fail": not accept_auto_degrade,
                    "retry_on_decision": 2,
                },
                **job,
            }
        )
        return True

    if parsed.path == "/api/llm/multi-role/v2/decision":
        job_id = str(payload.get("job_id", "") or "").strip()
        action = str(payload.get("action", "") or "").strip().lower()
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        if action not in {"retry", "degrade", "abort"}:
            handler._send_json({"error": "action 必须是 retry|degrade|abort"}, status=400)
            return True
        try:
            result = deps["decide_async_multi_role_v2_job"](job_id=job_id, action=action)
        except ValueError as exc:
            handler._send_json({"error": str(exc)}, status=400)
            return True
        except RuntimeError as exc:
            handler._send_json({"error": str(exc)}, status=409)
            return True
        except Exception as exc:
            handler._send_json({"error": f"处理决策失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **result})
        return True

    if parsed.path == "/api/llm/multi-role/v2/retry-aggregate":
        job_id = str(payload.get("job_id", "") or "").strip()
        if not job_id:
            handler._send_json({"error": "缺少 job_id"}, status=400)
            return True
        try:
            result = deps["retry_async_multi_role_v2_aggregate"](job_id=job_id)
        except ValueError as exc:
            handler._send_json({"error": str(exc)}, status=400)
            return True
        except RuntimeError as exc:
            handler._send_json({"error": str(exc)}, status=409)
            return True
        except Exception as exc:
            handler._send_json({"error": f"重试汇总失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **result})
        return True

    return False
