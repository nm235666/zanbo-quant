"""
Unified error code dictionary for the backend.
All route handlers should use these helpers for consistent error semantics.
Format: {"error": str, "code": str, "action": str}
"""
from __future__ import annotations


# ── Auth ──────────────────────────────────────────────────────────────────────
NOT_AUTHENTICATED = {
    "error": "请先登录",
    "code": "NOT_AUTHENTICATED",
    "action": "redirect_to_login",
}
NOT_AUTHORIZED = {
    "error": "权限不足",
    "code": "NOT_AUTHORIZED",
    "action": "contact_admin_or_upgrade",
}

# ── Validation ────────────────────────────────────────────────────────────────
MISSING_FIELD = {
    "error": "缺少必要参数",
    "code": "MISSING_FIELD",
    "action": "check_request_fields",
}
INVALID_VALUE = {
    "error": "参数值无效",
    "code": "INVALID_VALUE",
    "action": "check_request_fields",
}

# ── Resource ──────────────────────────────────────────────────────────────────
NOT_FOUND = {
    "error": "资源不存在",
    "code": "NOT_FOUND",
    "action": "verify_id_and_retry",
}
CONFLICT = {
    "error": "资源冲突",
    "code": "CONFLICT",
    "action": "reload_and_retry",
}
VERSION_CONFLICT = {
    "error": "状态版本冲突，请刷新后重试",
    "code": "VERSION_CONFLICT",
    "action": "reload_resource_and_retry",
}
DUPLICATE = {
    "error": "重复提交，已忽略",
    "code": "DUPLICATE",
    "action": "no_action_needed",
}

# ── State machine ─────────────────────────────────────────────────────────────
INVALID_STATE_TRANSITION = {
    "error": "不允许的状态转换",
    "code": "INVALID_STATE_TRANSITION",
    "action": "check_current_state_and_allowed_transitions",
}
TERMINAL_STATE_PROTECTED = {
    "error": "终态保护：低优先级触发源无法覆盖已设定的终态",
    "code": "TERMINAL_STATE_PROTECTED",
    "action": "use_higher_priority_trigger_source",
}

# ── Analysis / LLM ────────────────────────────────────────────────────────────
TIMEOUT = {
    "error": "请求超时",
    "code": "TIMEOUT",
    "action": "retry_or_use_deep_workflow",
}
INSUFFICIENT_EVIDENCE = {
    "error": "证据不足，无法生成可信结论",
    "code": "INSUFFICIENT_EVIDENCE",
    "action": "run_deep_workflow_for_full_analysis",
}
LLM_UNAVAILABLE = {
    "error": "LLM 服务暂不可用",
    "code": "LLM_UNAVAILABLE",
    "action": "retry_later_or_check_provider_config",
}

# ── System ────────────────────────────────────────────────────────────────────
INTERNAL_ERROR = {
    "error": "内部错误",
    "code": "INTERNAL_ERROR",
    "action": "contact_admin_with_request_id",
}


def make_error(code_dict: dict, *, detail: str = "", status: int = 400) -> tuple[dict, int]:
    """Return (response_body, http_status) for use in route handlers.

    Example:
        body, status = make_error(NOT_FOUND, detail="候选标的 abc123 不存在")
        handler._send_json(body, status=status)
    """
    body = dict(code_dict)
    if detail:
        body["error"] = f"{body['error']}：{detail}"
    return body, status
