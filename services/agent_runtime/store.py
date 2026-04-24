from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

import db_compat as db


RUN_TABLE = "agent_runs"
STEP_TABLE = "agent_steps"
APPROVAL_TABLE = "agent_approvals"

ACTIVE_STATUSES = {"queued", "running", "waiting_approval"}
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dumps(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, default=str)


def loads(raw: Any, default: Any):
    try:
        parsed = json.loads(str(raw or ""))
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def row_to_dict(row) -> dict[str, Any]:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except Exception:
        return {}


def rows_to_dicts(rows) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]


def apply_row_factory(conn) -> None:
    if isinstance(conn, sqlite3.Connection):
        return
    db.apply_row_factory(conn)


def ensure_agent_tables(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {RUN_TABLE} (
            id TEXT PRIMARY KEY,
            agent_key TEXT NOT NULL,
            status TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'auto',
            trigger_source TEXT NOT NULL DEFAULT '',
            schedule_key TEXT NOT NULL DEFAULT '',
            actor TEXT NOT NULL DEFAULT '',
            goal_json TEXT NOT NULL DEFAULT '{{}}',
            plan_json TEXT NOT NULL DEFAULT '{{}}',
            result_json TEXT NOT NULL DEFAULT '{{}}',
            error_text TEXT NOT NULL DEFAULT '',
            approval_required INTEGER NOT NULL DEFAULT 0,
            worker_id TEXT NOT NULL DEFAULT '',
            lease_until TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            finished_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {STEP_TABLE} (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            step_index INTEGER NOT NULL,
            tool_name TEXT NOT NULL,
            args_json TEXT NOT NULL DEFAULT '{{}}',
            dry_run INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL,
            audit_id INTEGER NOT NULL DEFAULT 0,
            result_json TEXT NOT NULL DEFAULT '{{}}',
            error_text TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {APPROVAL_TABLE} (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            step_id TEXT NOT NULL DEFAULT '',
            actor TEXT NOT NULL DEFAULT '',
            decision TEXT NOT NULL,
            reason TEXT NOT NULL DEFAULT '',
            idempotency_key TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{RUN_TABLE}_status ON {RUN_TABLE}(status, created_at)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{RUN_TABLE}_agent_schedule ON {RUN_TABLE}(agent_key, schedule_key, created_at)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{STEP_TABLE}_run ON {STEP_TABLE}(run_id, step_index)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{APPROVAL_TABLE}_run ON {APPROVAL_TABLE}(run_id, created_at)")
    try:
        conn.commit()
    except Exception:
        pass


def _hydrate_run(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    out = dict(row)
    out["goal"] = loads(out.pop("goal_json", "{}"), {})
    out["plan"] = loads(out.pop("plan_json", "{}"), {})
    out["result"] = loads(out.pop("result_json", "{}"), {})
    out["approval_required"] = bool(out.get("approval_required"))
    return out


def _hydrate_step(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["args"] = loads(out.pop("args_json", "{}"), {})
    out["result"] = loads(out.pop("result_json", "{}"), {})
    out["dry_run"] = bool(out.get("dry_run"))
    return out


def create_run(
    *,
    agent_key: str,
    mode: str = "auto",
    trigger_source: str = "manual",
    actor: str = "",
    goal: dict[str, Any] | None = None,
    schedule_key: str = "",
    dedupe: bool = True,
) -> dict[str, Any]:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        agent_key = str(agent_key or "").strip()
        if not agent_key:
            raise ValueError("agent_key_required")
        schedule_key = str(schedule_key or "").strip()
        if dedupe and schedule_key:
            row = conn.execute(
                f"""
                SELECT *
                FROM {RUN_TABLE}
                WHERE agent_key = ?
                  AND schedule_key = ?
                  AND status IN ('queued', 'running', 'waiting_approval', 'succeeded')
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (agent_key, schedule_key),
            ).fetchone()
            existing = _hydrate_run(row_to_dict(row))
            if existing:
                existing["deduped"] = True
                return existing
        now = utc_now()
        run_id = f"agent_run_{uuid.uuid4().hex}"
        conn.execute(
            f"""
            INSERT INTO {RUN_TABLE} (
                id, agent_key, status, mode, trigger_source, schedule_key, actor,
                goal_json, plan_json, result_json, error_text, approval_required,
                worker_id, lease_until, created_at, updated_at, finished_at
            ) VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, '{{}}', '{{}}', '', 0, '', '', ?, ?, '')
            """,
            (run_id, agent_key, str(mode or "auto"), str(trigger_source or ""), schedule_key, str(actor or ""), dumps(goal), now, now),
        )
        try:
            conn.commit()
        except Exception:
            pass
        return get_run(run_id) or {"id": run_id, "agent_key": agent_key, "status": "queued"}
    finally:
        conn.close()


def list_runs(*, agent_key: str = "", status: str = "", limit: int = 50) -> dict[str, Any]:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        where: list[str] = []
        params: list[Any] = []
        if str(agent_key or "").strip():
            where.append("agent_key = ?")
            params.append(str(agent_key).strip())
        if str(status or "").strip():
            where.append("status = ?")
            params.append(str(status).strip())
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        rows = conn.execute(
            f"SELECT * FROM {RUN_TABLE} {where_sql} ORDER BY created_at DESC LIMIT ?",
            (*params, max(1, min(int(limit or 50), 200))),
        ).fetchall()
        return {"ok": True, "items": [_hydrate_run(row_to_dict(row)) for row in rows]}
    finally:
        conn.close()


def get_run(run_id: str, *, include_steps: bool = True) -> dict[str, Any] | None:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        row = conn.execute(f"SELECT * FROM {RUN_TABLE} WHERE id = ?", (str(run_id or "").strip(),)).fetchone()
        run = _hydrate_run(row_to_dict(row))
        if not run:
            return None
        if include_steps:
            steps = conn.execute(
                f"SELECT * FROM {STEP_TABLE} WHERE run_id = ? ORDER BY step_index, created_at",
                (run["id"],),
            ).fetchall()
            run["steps"] = [_hydrate_step(row_to_dict(step)) for step in steps]
        return run
    finally:
        conn.close()


def claim_next_run(*, worker_id: str) -> dict[str, Any] | None:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        row = conn.execute(
            f"SELECT * FROM {RUN_TABLE} WHERE status = 'queued' ORDER BY created_at LIMIT 1"
        ).fetchone()
        run = _hydrate_run(row_to_dict(row))
        if not run:
            return None
        now = utc_now()
        conn.execute(
            f"UPDATE {RUN_TABLE} SET status = 'running', worker_id = ?, updated_at = ? WHERE id = ? AND status = 'queued'",
            (worker_id, now, run["id"]),
        )
        try:
            conn.commit()
        except Exception:
            pass
        return get_run(run["id"], include_steps=False)
    finally:
        conn.close()


def update_run(
    run_id: str,
    *,
    status: str | None = None,
    plan: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    error_text: str | None = None,
    approval_required: bool | None = None,
    finished: bool = False,
) -> None:
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        fields = ["updated_at = ?"]
        params: list[Any] = [utc_now()]
        if status is not None:
            fields.append("status = ?")
            params.append(status)
        if plan is not None:
            fields.append("plan_json = ?")
            params.append(dumps(plan))
        if result is not None:
            fields.append("result_json = ?")
            params.append(dumps(result))
        if error_text is not None:
            fields.append("error_text = ?")
            params.append(str(error_text or "")[:4000])
        if approval_required is not None:
            fields.append("approval_required = ?")
            params.append(1 if approval_required else 0)
        if finished:
            fields.append("finished_at = ?")
            params.append(utc_now())
        params.append(str(run_id or ""))
        conn.execute(f"UPDATE {RUN_TABLE} SET {', '.join(fields)} WHERE id = ?", tuple(params))
        try:
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()


def insert_step(*, run_id: str, step_index: int, tool_name: str, args: dict[str, Any], dry_run: bool) -> str:
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        now = utc_now()
        step_id = f"agent_step_{uuid.uuid4().hex}"
        conn.execute(
            f"""
            INSERT INTO {STEP_TABLE} (
                id, run_id, step_index, tool_name, args_json, dry_run, status,
                audit_id, result_json, error_text, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'running', 0, '{{}}', '', ?, ?)
            """,
            (step_id, run_id, int(step_index), tool_name, dumps(args), 1 if dry_run else 0, now, now),
        )
        try:
            conn.commit()
        except Exception:
            pass
        return step_id
    finally:
        conn.close()


def insert_pending_step(*, run_id: str, step_index: int, tool_name: str, args: dict[str, Any]) -> str:
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        now = utc_now()
        step_id = f"agent_step_{uuid.uuid4().hex}"
        conn.execute(
            f"""
            INSERT INTO {STEP_TABLE} (
                id, run_id, step_index, tool_name, args_json, dry_run, status,
                audit_id, result_json, error_text, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 0, 'pending_approval', 0, '{{}}', '', ?, ?)
            """,
            (step_id, run_id, int(step_index), tool_name, dumps(args), now, now),
        )
        try:
            conn.commit()
        except Exception:
            pass
        return step_id
    finally:
        conn.close()


def finish_step(
    step_id: str,
    *,
    status: str,
    result: dict[str, Any] | None = None,
    error_text: str = "",
    audit_id: int = 0,
) -> None:
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        conn.execute(
            f"""
            UPDATE {STEP_TABLE}
            SET status = ?, result_json = ?, error_text = ?, audit_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, dumps(result), str(error_text or "")[:4000], int(audit_id or 0), utc_now(), step_id),
        )
        try:
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()


def update_step_args(step_id: str, *, args: dict[str, Any], status: str | None = None) -> None:
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        fields = ["args_json = ?", "dry_run = ?", "updated_at = ?"]
        params: list[Any] = [dumps(args), 1 if bool(args.get("dry_run", True)) else 0, utc_now()]
        if status is not None:
            fields.append("status = ?")
            params.append(str(status or ""))
        params.append(str(step_id or ""))
        conn.execute(f"UPDATE {STEP_TABLE} SET {', '.join(fields)} WHERE id = ?", tuple(params))
        try:
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()


def get_step(step_id: str) -> dict[str, Any] | None:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        row = conn.execute(f"SELECT * FROM {STEP_TABLE} WHERE id = ?", (str(step_id or ""),)).fetchone()
        data = row_to_dict(row)
        return _hydrate_step(data) if data else None
    finally:
        conn.close()


def list_pending_steps(run_id: str) -> list[dict[str, Any]]:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        rows = conn.execute(
            f"SELECT * FROM {STEP_TABLE} WHERE run_id = ? AND status = 'pending_approval' ORDER BY step_index",
            (str(run_id or ""),),
        ).fetchall()
        return [_hydrate_step(row_to_dict(row)) for row in rows]
    finally:
        conn.close()


def cancel_run(run_id: str, *, actor: str = "", reason: str = "") -> dict[str, Any]:
    run = get_run(run_id, include_steps=False)
    if not run:
        return {"ok": False, "error": "agent_run_not_found"}
    if run.get("status") in TERMINAL_STATUSES:
        return {"ok": True, "run": run, "skipped": True}
    update_run(run_id, status="cancelled", result={"cancelled_by": actor, "reason": reason}, finished=True)
    return {"ok": True, "run": get_run(run_id)}


def record_approval(run_id: str, *, actor: str, reason: str = "", idempotency_key: str = "", decision: str = "approved") -> dict[str, Any]:
    run = get_run(run_id, include_steps=False)
    if not run:
        return {"ok": False, "error": "agent_run_not_found"}
    conn = db.connect()
    try:
        ensure_agent_tables(conn)
        conn.execute(
            f"""
            INSERT INTO {APPROVAL_TABLE} (id, run_id, step_id, actor, decision, reason, idempotency_key, created_at)
            VALUES (?, ?, '', ?, ?, ?, ?, ?)
            """,
            (f"agent_approval_{uuid.uuid4().hex}", run_id, str(actor or ""), str(decision or "approved"), str(reason or ""), str(idempotency_key or ""), utc_now()),
        )
        try:
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()
    return {"ok": True, "run": get_run(run_id)}


def approve_run(run_id: str, *, actor: str, reason: str = "", idempotency_key: str = "", decision: str = "approved") -> dict[str, Any]:
    return record_approval(run_id, actor=actor, reason=reason, idempotency_key=idempotency_key, decision=decision)


def list_steps(run_id: str) -> list[dict[str, Any]]:
    conn = db.connect()
    apply_row_factory(conn)
    try:
        ensure_agent_tables(conn)
        rows = conn.execute(f"SELECT * FROM {STEP_TABLE} WHERE run_id = ? ORDER BY step_index", (run_id,)).fetchall()
        return [_hydrate_step(row) for row in rows_to_dicts(rows)]
    finally:
        conn.close()
