from __future__ import annotations

import re
from urllib.parse import parse_qs

from services.agent_runtime import decide_run, cancel_run, create_run, get_run, list_runs, resume_run


_RUN_RE = re.compile(r"^/api/agents/runs/([^/]+)(/(cancel|approve|resume))?$")


def _actor(deps: dict) -> str:
    auth = deps.get("auth_context") or {}
    user = auth.get("user") or {}
    return str(user.get("username") or auth.get("auth_mode") or "api").strip()


def dispatch_get(handler, parsed, deps: dict) -> bool:
    if not parsed.path.startswith("/api/agents"):
        return False
    if parsed.path == "/api/agents/runs":
        params = parse_qs(parsed.query)
        agent_key = params.get("agent_key", [""])[0].strip()
        status = params.get("status", [""])[0].strip()
        try:
            limit = int(params.get("limit", ["50"])[0] or 50)
        except ValueError:
            handler._send_json({"ok": False, "error": "limit must be integer"}, status=400)
            return True
        handler._send_json(list_runs(agent_key=agent_key, status=status, limit=limit))
        return True
    match = _RUN_RE.match(parsed.path)
    if match and not match.group(2):
        run = get_run(match.group(1))
        if not run:
            handler._send_json({"ok": False, "error": "agent_run_not_found"}, status=404)
            return True
        handler._send_json({"ok": True, "run": run})
        return True
    return False


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    if not parsed.path.startswith("/api/agents"):
        return False
    if parsed.path == "/api/agents/runs":
        agent_key = str(payload.get("agent_key") or "funnel_progress_agent").strip()
        run = create_run(
            agent_key=agent_key,
            mode=str(payload.get("mode") or "auto").strip(),
            trigger_source=str(payload.get("trigger_source") or "manual").strip(),
            actor=str(payload.get("actor") or _actor(deps)),
            goal=payload.get("goal") if isinstance(payload.get("goal"), dict) else {},
            schedule_key=str(payload.get("schedule_key") or "").strip(),
            dedupe=bool(payload.get("dedupe", True)),
        )
        handler._send_json({"ok": True, "run": run})
        return True
    match = _RUN_RE.match(parsed.path)
    if match and match.group(3) == "cancel":
        result = cancel_run(match.group(1), actor=_actor(deps), reason=str(payload.get("reason") or "api cancel"))
        handler._send_json(result, status=200 if result.get("ok") else 404)
        return True
    if match and match.group(3) == "approve":
        result = decide_run(
            match.group(1),
            actor=str(payload.get("actor") or _actor(deps)),
            reason=str(payload.get("reason") or ""),
            idempotency_key=str(payload.get("idempotency_key") or ""),
            decision=str(payload.get("decision") or "approved"),
        )
        err = str(result.get("error") or "")
        handler._send_json(result, status=200 if result.get("ok") else (400 if err != "agent_run_not_found" else 404))
        return True
    if match and match.group(3) == "resume":
        result = resume_run(
            match.group(1),
            actor=str(payload.get("actor") or _actor(deps)),
            reason=str(payload.get("reason") or "manual resume"),
        )
        handler._send_json(result, status=200 if result.get("ok") else 404)
        return True
    return False
