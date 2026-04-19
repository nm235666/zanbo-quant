from __future__ import annotations

from urllib.parse import parse_qs


def dispatch_get(handler, parsed, deps: dict) -> bool:
    if not parsed.path.startswith("/api/decision"):
        return False

    if parsed.path == "/api/decision/board":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["12"])[0] or 12)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_board"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
                keyword=params.get("keyword", [""])[0].strip(),
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"决策板查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/scores":
        params = parse_qs(parsed.query)
        try:
            page_size = int(params.get("page_size", ["8"])[0] or 8)
        except ValueError:
            handler._send_json({"ok": False, "error": "page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_scoreboard"](page_size=page_size)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"评分总览查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/stock":
        params = parse_qs(parsed.query)
        ts_code = params.get("ts_code", [""])[0].strip().upper()
        keyword = params.get("keyword", [""])[0].strip()
        if not ts_code and not keyword:
            handler._send_json({"ok": False, "error": "缺少 ts_code 或 keyword"}, status=400)
            return True
        try:
            payload = deps["query_decision_stock"](ts_code=ts_code, keyword=keyword)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"股票决策查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/plan":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["12"])[0] or 12)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_trade_plan"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
                keyword=params.get("keyword", [""])[0].strip(),
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"决策板查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/strategies":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["12"])[0] or 12)
            run_id = int(params.get("run_id", ["0"])[0] or 0)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_strategy_lab"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
                keyword=params.get("keyword", [""])[0].strip(),
                run_id=run_id,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"策略生成查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/strategy-runs":
        params = parse_qs(parsed.query)
        run_id_raw = params.get("run_id", [""])[0].strip()
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["20"])[0] or 20)
            run_id = int(run_id_raw) if run_id_raw else 0
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            if run_id:
                payload = deps["query_decision_strategy_lab"](
                    page=page,
                    page_size=page_size,
                    ts_code=params.get("ts_code", [""])[0].strip().upper(),
                    keyword=params.get("keyword", [""])[0].strip(),
                    run_id=run_id,
                )
                handler._send_json({"ok": True, **payload})
                return True
            payload = deps["query_decision_strategy_runs"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
                keyword=params.get("keyword", [""])[0].strip(),
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"策略运行历史查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/history":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["20"])[0] or 20)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_history"](page=page, page_size=page_size)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"历史查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/actions":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["20"])[0] or 20)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_actions"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"动作查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/calibration":
        params = parse_qs(parsed.query)
        try:
            page = int(params.get("page", ["1"])[0] or 1)
            page_size = int(params.get("page_size", ["20"])[0] or 20)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            payload = deps["query_decision_calibration"](
                page=page,
                page_size=page_size,
                ts_code=params.get("ts_code", [""])[0].strip().upper(),
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"裁决精准度查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    if parsed.path == "/api/decision/kill-switch":
        try:
            payload = deps["get_decision_kill_switch"]()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"状态查询失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **payload})
        return True

    return False


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    if not parsed.path.startswith("/api/decision"):
        return False

    if parsed.path == "/api/decision/kill-switch":
        auth_ctx = deps.get("auth_context") or {}
        if not auth_ctx.get("is_admin"):
            handler._send_json({"ok": False, "error": "仅管理员可切换 Kill Switch"}, status=403)
            return True
        allow_trading = payload.get("allow_trading", payload.get("enabled", True))
        reason = str(payload.get("reason", "") or "").strip()
        try:
            result = deps["set_decision_kill_switch"](allow_trading=bool(allow_trading), reason=reason)
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"状态更新失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **result})
        return True

    if parsed.path == "/api/decision/snapshot/run":
        auth_ctx = deps.get("auth_context") or {}
        if not auth_ctx.get("is_admin"):
            handler._send_json({"ok": False, "error": "仅管理员可触发快照"}, status=403)
            return True
        try:
            payload = deps["run_decision_snapshot"]()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"快照运行失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    if parsed.path == "/api/decision/strategy-runs/run":
        auth_ctx = deps.get("auth_context") or {}
        if not auth_ctx.get("authenticated"):
            handler._send_json({"ok": False, "error": "请先登录后再生成策略批次"}, status=401)
            return True
        ts_code = str(payload.get("ts_code", "") or "").strip().upper()
        keyword = str(payload.get("keyword", "") or "").strip()
        try:
            page = int(payload.get("page", 1) or 1)
            page_size = int(payload.get("page_size", 12) or 12)
        except ValueError:
            handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
            return True
        try:
            result = deps["run_decision_strategy_generation"](
                page=page,
                page_size=page_size,
                ts_code=ts_code,
                keyword=keyword,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"策略批次生成失败: {exc}"}, status=500)
            return True
        handler._send_json({"ok": True, **result})
        return True

    if parsed.path == "/api/decision/actions":
        auth_ctx = deps.get("auth_context") or {}
        if not auth_ctx.get("authenticated"):
            handler._send_json({"ok": False, "error": "请先登录后再记录决策动作"}, status=401)
            return True
        user = auth_ctx.get("user") or {}
        action_type = str(payload.get("action_type", "") or "").strip().lower()
        ts_code = str(payload.get("ts_code", "") or "").strip().upper()
        stock_name = str(payload.get("stock_name", "") or "").strip()
        note = str(payload.get("note", "") or "").strip()
        snapshot_date = str(payload.get("snapshot_date", "") or "").strip()
        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        # Structured evidence and review fields — stored in payload JSON blob
        evidence_sources_raw = payload.get("evidence_sources")
        evidence_sources = evidence_sources_raw if isinstance(evidence_sources_raw, list) else []
        execution_status = str(payload.get("execution_status", "") or "").strip()
        review_conclusion = str(payload.get("review_conclusion", "") or "").strip()
        # P1-5: Idempotency key — prevent duplicate submissions (double-click protection)
        idempotency_key = str(payload.get("idempotency_key", "") or "").strip()
        if not ts_code:
            handler._send_json({"ok": False, "error": "缺少 ts_code"}, status=400)
            return True
        if not action_type:
            handler._send_json({"ok": False, "error": "缺少 action_type"}, status=400)
            return True
        # P0-5: Evidence chain enforcement — warn if key actions lack evidence sources
        evidence_warnings = []
        if action_type in ("confirm", "reject") and not evidence_sources:
            evidence_warnings.append("此动作缺少证据来源引用，建议通过决策板附加 trace_id 或 run_id")
        action_payload: dict = {
            "context": context,
            "source": str(context.get("source") or "decision_board"),
            "evidence_chain_complete": bool(evidence_sources),
        }
        if evidence_sources:
            action_payload["evidence_sources"] = evidence_sources
        if execution_status:
            action_payload["execution_status"] = execution_status
        if review_conclusion:
            action_payload["review_conclusion"] = review_conclusion
        if idempotency_key:
            action_payload["idempotency_key"] = idempotency_key
            # Check for duplicate idempotency key in recent actions
            try:
                from db_compat import get_db_connection
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "SELECT id FROM decision_actions WHERE action_payload_json::text LIKE %s ORDER BY created_at DESC LIMIT 1",
                    (f'%"idempotency_key": "{idempotency_key}"%',)
                )
                existing = cur.fetchone()
                cur.close()
                conn.close()
                if existing:
                    handler._send_json({"ok": True, "action_id": existing[0], "deduplicated": True, "message": "重复提交已忽略（幂等键匹配）"})
                    return True
            except Exception:
                pass  # If dedup check fails, proceed normally
        try:
            result = deps["record_decision_action"](
                action_type=action_type,
                ts_code=ts_code,
                stock_name=stock_name,
                note=note,
                actor=str(user.get("username") or user.get("display_name") or "anonymous"),
                snapshot_date=snapshot_date,
                payload=action_payload,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"动作记录失败: {exc}"}, status=500)
            return True
        response = {"ok": True, **result}
        if evidence_warnings:
            response["evidence_warnings"] = evidence_warnings

        # P0-4: Auto-create execution task for actionable verdicts
        # Use integer id for DB operations; action_id (trace format) is for display only
        _numeric_action_id = result.get("id")  # integer PK
        action_id = str(result.get("action_id") or _numeric_action_id or "")
        if action_type in ("confirm", "reject", "defer", "watch") and ts_code and _numeric_action_id:
            try:
                from services.portfolio_service.service import create_order as _create_portfolio_order
                order_action_type = {
                    "confirm": "buy",
                    "reject": "sell",  # reject maps to a sell/cancel record for audit trail
                    "defer": "defer",
                    "watch": "watch",
                }.get(action_type, action_type)
                order_note_prefix = {
                    "confirm": "",
                    "reject": "[拒绝记录] ",
                    "defer": "[延迟观察] ",
                    "watch": "[跟踪观察] ",
                }.get(action_type, "")
                order_result = _create_portfolio_order(
                    ts_code=ts_code,
                    action_type=order_action_type,
                    planned_price=None,
                    size=0,
                    decision_action_id=str(_numeric_action_id),
                    note=f"{order_note_prefix}{note}".strip(),
                )
                if order_result.get("ok"):
                    response["execution_task"] = {
                        "order_id": order_result.get("id"),
                        "status": "planned",
                        "auto_created": True,
                    }
                    # Writeback initial execution_status = "planned" to the decision action
                    try:
                        from db_compat import connect as _db_connect
                        import json as _json
                        _conn = _db_connect()
                        try:
                            _row = _conn.execute(
                                "SELECT action_payload_json FROM decision_actions WHERE id = ? LIMIT 1",
                                (_numeric_action_id,),
                            ).fetchone()
                            if _row:
                                _d = dict(_row) if hasattr(_row, 'keys') else {}
                                try:
                                    _payload = _json.loads(str(_d.get("action_payload_json") or "{}"))
                                except Exception:
                                    _payload = {}
                                _payload["execution_status"] = "planned"
                                _conn.execute(
                                    "UPDATE decision_actions SET action_payload_json = ? WHERE id = ?",
                                    (_json.dumps(_payload, ensure_ascii=False), _numeric_action_id),
                                )
                        finally:
                            _conn.close()
                    except Exception:
                        pass  # Writeback failure must not block response
            except Exception as _exc:
                # Auto-link failure must NOT fail the decision action itself
                response["execution_task_warning"] = f"执行任务自动创建失败（不影响决策记录）: {_exc}"

        handler._send_json(response)
        return True

    return False
