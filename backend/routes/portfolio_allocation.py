from __future__ import annotations

from urllib.parse import parse_qs


def dispatch_get(handler, parsed, deps: dict) -> bool:
    if not parsed.path.startswith("/api/portfolio/allocation"):
        return False

    if parsed.path == "/api/portfolio/allocation":
        from services.macro_service.regime import get_latest_allocation, list_allocations

        params = parse_qs(parsed.query)
        history = params.get("history", ["0"])[0].strip() == "1"
        if history:
            try:
                page = int(params.get("page", ["1"])[0] or 1)
                page_size = int(params.get("page_size", ["10"])[0] or 10)
            except ValueError:
                handler._send_json({"ok": False, "error": "page/page_size 必须是整数"}, status=400)
                return True
            try:
                payload = list_allocations(page=page, page_size=page_size)
            except Exception as exc:  # pragma: no cover
                handler._send_json({"ok": False, "error": f"配置历史查询失败: {exc}"}, status=500)
                return True
            handler._send_json({"ok": True, **payload})
            return True

        try:
            payload = get_latest_allocation()
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"当前配置查询失败: {exc}"}, status=500)
            return True
        handler._send_json(payload)
        return True

    return False


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    if not parsed.path.startswith("/api/portfolio/allocation"):
        return False

    if parsed.path == "/api/portfolio/allocation":
        from services.macro_service.regime import record_allocation

        auth_ctx = deps.get("auth_context") or {}
        if not auth_ctx.get("authenticated"):
            handler._send_json({"ok": False, "error": "请先登录后再记录配置决策"}, status=401)
            return True

        try:
            cash_ratio = float(payload.get("cash_ratio_pct") or 10.0)
            max_single = float(payload.get("max_single_position_pct") or 8.0)
            max_theme = float(payload.get("max_theme_concentration_pct") or 20.0)
            risk_compression = float(payload.get("risk_budget_compression") or 1.0)
        except (TypeError, ValueError):
            handler._send_json({"ok": False, "error": "数值字段必须是数字"}, status=400)
            return True

        stance = str(payload.get("stance") or "neutral").strip()
        if stance not in {"offensive", "defensive", "neutral"}:
            handler._send_json(
                {"ok": False, "error": "stance 必须是 offensive / defensive / neutral"},
                status=400,
            )
            return True

        user = auth_ctx.get("user") or {}
        created_by = str(user.get("username") or user.get("display_name") or "")

        try:
            result = record_allocation(
                cash_ratio_pct=cash_ratio,
                max_single_position_pct=max_single,
                max_theme_concentration_pct=max_theme,
                stance=stance,
                risk_budget_compression=risk_compression,
                action_notes=str(payload.get("action_notes") or ""),
                regime_id=str(payload.get("regime_id") or ""),
                created_by=created_by,
            )
        except Exception as exc:  # pragma: no cover
            handler._send_json({"ok": False, "error": f"配置记录失败: {exc}"}, status=500)
            return True

        handler._send_json(result)
        return True

    return False
