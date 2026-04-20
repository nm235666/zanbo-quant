from __future__ import annotations

import json


def dispatch_post(handler, parsed, payload: dict, deps: dict) -> bool:
    """
    POST /api/analytics/event

    Accepts: { event_type, page_path?, session_id?, extra? }
    Inserts a row into user_analytics_events.
    No authentication required (analytics are low-risk).
    """
    if parsed.path != "/api/analytics/event":
        return False

    event_type = str(payload.get("event_type") or "").strip()
    if not event_type:
        handler._send_json({"ok": False, "error": "event_type 不能为空"}, status=400)
        return True

    page_path = str(payload.get("page_path") or "")[:200]
    session_id = str(payload.get("session_id") or "")[:64]
    extra = payload.get("extra")
    extra_json: str | None
    if extra is not None:
        try:
            extra_json = json.dumps(extra, ensure_ascii=False)
        except (TypeError, ValueError):
            extra_json = str(extra)
    else:
        extra_json = None

    # Resolve user_id from auth context if available (optional)
    auth_ctx = deps.get("auth_context") or {}
    user_id = str(auth_ctx.get("username") or auth_ctx.get("user_id") or "")[:64] or None

    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        import db_compat

        conn = db_compat.connect()
        try:
            conn.execute(
                """
                INSERT INTO user_analytics_events
                    (event_type, user_id, session_id, page_path, extra_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_type, user_id, session_id or None, page_path or None, extra_json),
            )
            try:
                conn.commit()
            except Exception:
                pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover
        handler._send_json({"ok": False, "error": f"analytics insert failed: {exc}"}, status=500)
        return True

    handler._send_json({"ok": True})
    return True
