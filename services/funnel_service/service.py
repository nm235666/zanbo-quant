from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import db_compat as _db
from services.decision_service.service import build_stock_evidence_packet, summarize_evidence_packet

FUNNEL_CANDIDATES_TABLE = "funnel_candidates"
FUNNEL_TRANSITIONS_TABLE = "funnel_transitions"

VALID_STATES = {
    "ingested",
    "amplified",
    "ai_screen_passed",
    "shortlisted",
    "decision_ready",
    "confirmed",
    "rejected",
    "deferred",
    "executed",
    "reviewed",
}

TERMINAL_STATES = {"confirmed", "rejected", "executed", "reviewed"}

# Priority rank: higher number = higher authority
TRIGGER_SOURCE_PRIORITY: dict[str, int] = {
    "decision_action": 5,
    "researcher": 4,
    "execution_feedback": 3,
    "system_rule": 2,
    "ai_screen": 1,
    "signal": 0,
}

# Valid transitions: from_state -> set of valid to_states
VALID_TRANSITIONS: dict[str, set[str]] = {
    "ingested": {"amplified", "rejected"},
    "amplified": {"ai_screen_passed", "rejected"},
    "ai_screen_passed": {"shortlisted", "rejected"},
    "shortlisted": {"decision_ready", "deferred", "rejected"},
    "decision_ready": {"confirmed", "rejected", "deferred"},
    "confirmed": {"executed"},
    "deferred": {"executed", "rejected", "shortlisted"},
    "executed": {"reviewed"},
    "rejected": set(),
    "reviewed": set(),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_json(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return {}


def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except Exception:
        return {}


def _load_upstream_scores_hint(conn) -> dict[str, Any]:
    if not _db.table_exists(conn, "stock_scores_daily"):
        return {"status": "missing_source", "latest_score_date": "", "latest_count": 0}
    latest_row = conn.execute("SELECT MAX(score_date) AS dt FROM stock_scores_daily").fetchone()
    latest_score_date = str(_row_to_dict(latest_row).get("dt") if latest_row else "").strip()
    if not latest_score_date:
        return {"status": "empty", "latest_score_date": "", "latest_count": 0}
    count_row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM stock_scores_daily WHERE score_date = ?",
        (latest_score_date,),
    ).fetchone()
    latest_count = int(_row_to_dict(count_row).get("cnt") if count_row else 0)
    return {
        "status": "ready" if latest_count > 0 else "empty",
        "latest_score_date": latest_score_date,
        "latest_count": latest_count,
    }


def _derive_funnel_status(*, total: int, table_exists: bool, upstream_hint: dict[str, Any], error: str = "") -> dict[str, Any]:
    missing_inputs: list[str] = []
    if not table_exists:
        missing_inputs.append(FUNNEL_CANDIDATES_TABLE)
    if str(upstream_hint.get("status") or "") in {"missing_source", "empty"}:
        missing_inputs.append("stock_scores_daily")
    if error:
        status = "degraded"
        status_reason = "漏斗查询异常，建议检查数据库连接与表结构。"
    elif total > 0:
        status = "ready"
        status_reason = "漏斗候选已就绪，可继续执行筛选与状态流转。"
    elif upstream_hint.get("latest_count"):
        status = "degraded"
        status_reason = "上游评分已就绪，但漏斗候选仍为空，请检查入池同步任务。"
    elif table_exists:
        status = "empty"
        status_reason = "漏斗表存在但暂无候选。"
    else:
        status = "not_initialized"
        status_reason = "漏斗表尚未初始化。"
    return {
        "status": status,
        "status_reason": status_reason,
        "missing_inputs": missing_inputs,
    }


def list_candidates(
    *,
    state: str = "",
    ts_q: str = "",
    limit: int = 50,
    offset: int = 0,
    include_evidence: bool = False,
) -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            table_exists = _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE)
            upstream_hint = _load_upstream_scores_hint(conn)
            if not table_exists:
                status_payload = _derive_funnel_status(total=0, table_exists=False, upstream_hint=upstream_hint)
                return {"items": [], "total": 0, "limit": limit, "offset": offset, "upstream_scores": upstream_hint, **status_payload}
            clauses: list[str] = []
            params: list[Any] = []
            if state and state in VALID_STATES:
                clauses.append("state = ?")
                params.append(state)
            ts_norm = str(ts_q or "").strip().upper()
            if ts_norm:
                clauses.append("(UPPER(TRIM(ts_code)) LIKE ? OR UPPER(TRIM(name)) LIKE ?)")
                like = f"%{ts_norm}%"
                params.extend([like, like])
            where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            count_sql = f"SELECT COUNT(*) FROM {FUNNEL_CANDIDATES_TABLE} {where_clause}"
            total_row = conn.execute(count_sql, params).fetchone()
            total = int(total_row[0] or 0) if total_row else 0

            sql = f"""
                SELECT id, ts_code, name, source, trigger_source, reason, evidence_ref,
                       state, state_version, created_at, updated_at
                FROM {FUNNEL_CANDIDATES_TABLE}
                {where_clause}
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """
            params_page = params + [limit, offset]
            rows = conn.execute(sql, params_page).fetchall()
            items = [_row_to_dict(r) for r in rows]
            if include_evidence:
                for item in items:
                    packet = build_stock_evidence_packet(
                        conn,
                        ts_code=str(item.get("ts_code") or ""),
                        name=str(item.get("name") or ""),
                    )
                    item["evidence_summary"] = summarize_evidence_packet(packet)
            status_payload = _derive_funnel_status(total=total, table_exists=True, upstream_hint=upstream_hint)
            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset,
                "upstream_scores": upstream_hint,
                **status_payload,
            }
        finally:
            conn.close()
    except Exception as exc:
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "upstream_scores": {"status": "unknown", "latest_score_date": "", "latest_count": 0},
            **_derive_funnel_status(total=0, table_exists=False, upstream_hint={"status": "unknown"}, error=str(exc)),
            "error": str(exc),
        }


def get_candidate(candidate_id: str) -> dict[str, Any] | None:
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE):
                return None
            row = conn.execute(
                f"""
                SELECT id, ts_code, name, source, trigger_source, reason, evidence_ref,
                       state, state_version, created_at, updated_at
                FROM {FUNNEL_CANDIDATES_TABLE}
                WHERE id = ?
                LIMIT 1
                """,
                (candidate_id,),
            ).fetchone()
            if not row:
                return None
            candidate = _row_to_dict(row)
            # Load transition history
            transitions: list[dict] = []
            if _db.table_exists(conn, FUNNEL_TRANSITIONS_TABLE):
                t_rows = conn.execute(
                    f"""
                    SELECT id, candidate_id, from_state, to_state, reason, evidence_ref,
                           trigger_source, operator, idempotency_key, created_at
                    FROM {FUNNEL_TRANSITIONS_TABLE}
                    WHERE candidate_id = ?
                    ORDER BY id ASC
                    """,
                    (candidate_id,),
                ).fetchall()
                transitions = [_row_to_dict(r) for r in t_rows]
            candidate["transitions"] = transitions
            packet = build_stock_evidence_packet(
                conn,
                ts_code=str(candidate.get("ts_code") or ""),
                name=str(candidate.get("name") or ""),
            )
            candidate["evidence_packet"] = packet
            candidate["evidence_status"] = packet.get("evidence_status", "incomplete")
            candidate["missing_evidence"] = list(packet.get("missing_evidence") or [])
            candidate["warning_messages"] = list(packet.get("warning_messages") or [])
            candidate["evidence_chain_complete"] = bool(packet.get("evidence_chain_complete"))
            return candidate
        finally:
            conn.close()
    except Exception:
        return None


def create_candidate(
    *,
    ts_code: str,
    name: str,
    source: str,
    trigger_source: str,
    reason: str,
    evidence_ref: str,
) -> dict[str, Any]:
    candidate_id = str(uuid.uuid4())
    now = _utc_now()
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE):
                _ensure_funnel_tables(conn)
            conn.execute(
                f"""
                INSERT INTO {FUNNEL_CANDIDATES_TABLE}
                    (id, ts_code, name, source, trigger_source, reason, evidence_ref,
                     state, state_version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ingested', 1, ?, ?)
                """,
                (candidate_id, ts_code, name, source, trigger_source, reason, evidence_ref, now, now),
            )
            # Record initial ingestion transition
            _record_transition(
                conn,
                candidate_id=candidate_id,
                from_state="",
                to_state="ingested",
                reason=reason,
                evidence_ref=evidence_ref,
                trigger_source=trigger_source,
                operator="system",
                idempotency_key="",
            )
            try:
                conn.commit()
            except Exception:
                pass
        finally:
            conn.close()
        return {"ok": True, "id": candidate_id, "state": "ingested"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _record_transition(
    conn,
    *,
    candidate_id: str,
    from_state: str,
    to_state: str,
    reason: str,
    evidence_ref: str,
    trigger_source: str,
    operator: str,
    idempotency_key: str,
) -> None:
    now = _utc_now()
    conn.execute(
        f"""
        INSERT INTO {FUNNEL_TRANSITIONS_TABLE}
            (id, candidate_id, from_state, to_state, reason, evidence_ref,
             trigger_source, operator, idempotency_key, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            candidate_id,
            from_state,
            to_state,
            reason,
            evidence_ref,
            trigger_source,
            operator,
            idempotency_key,
            now,
        ),
    )


def transition_candidate(
    candidate_id: str,
    *,
    to_state: str,
    reason: str,
    evidence_ref: str,
    trigger_source: str,
    operator: str,
    idempotency_key: str,
    state_version: int,
) -> dict[str, Any]:
    if to_state not in VALID_STATES:
        return {"ok": False, "error": f"无效目标状态: {to_state}"}
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE):
                return {"ok": False, "error": "候选标的表不存在"}
            # Idempotency check
            if idempotency_key and _db.table_exists(conn, FUNNEL_TRANSITIONS_TABLE):
                existing = conn.execute(
                    f"SELECT id FROM {FUNNEL_TRANSITIONS_TABLE} WHERE idempotency_key = ? LIMIT 1",
                    (idempotency_key,),
                ).fetchone()
                if existing:
                    return {"ok": True, "idempotent": True, "candidate_id": candidate_id}
            # Load current candidate
            row = conn.execute(
                f"SELECT state, state_version FROM {FUNNEL_CANDIDATES_TABLE} WHERE id = ? LIMIT 1",
                (candidate_id,),
            ).fetchone()
            if not row:
                return {"ok": False, "error": "候选标的不存在"}
            current = _row_to_dict(row)
            current_state = str(current.get("state") or "")
            current_version = int(current.get("state_version") or 0)
            # Optimistic lock check
            if state_version and state_version != current_version:
                return {
                    "ok": False,
                    "error": f"状态版本冲突: 期望 {state_version}, 当前 {current_version}",
                    "current_state": current_state,
                    "current_version": current_version,
                }
            # Terminal state protection: only higher-priority sources can overwrite
            if current_state in TERMINAL_STATES:
                incoming_priority = TRIGGER_SOURCE_PRIORITY.get(trigger_source, 0)
                # Find the priority of the trigger_source that last set the terminal state
                last_terminal_source = trigger_source  # default
                if _db.table_exists(conn, FUNNEL_TRANSITIONS_TABLE):
                    last_row = conn.execute(
                        f"SELECT trigger_source FROM {FUNNEL_TRANSITIONS_TABLE} "
                        f"WHERE candidate_id = ? AND to_state = ? ORDER BY id DESC LIMIT 1",
                        (candidate_id, current_state),
                    ).fetchone()
                    if last_row:
                        last_terminal_source = str(_row_to_dict(last_row).get("trigger_source") or "signal")
                last_priority = TRIGGER_SOURCE_PRIORITY.get(last_terminal_source, 0)
                if incoming_priority <= last_priority:
                    return {
                        "ok": False,
                        "error": f"终态保护：{trigger_source}(优先级{incoming_priority})不能覆盖已由{last_terminal_source}(优先级{last_priority})设定的终态 {current_state}",
                        "current_state": current_state,
                        "blocked_by_priority": True,
                    }
            # Validate transition
            allowed = VALID_TRANSITIONS.get(current_state, set())
            if to_state not in allowed:
                return {
                    "ok": False,
                    "error": f"不允许的状态转换: {current_state} -> {to_state}",
                    "current_state": current_state,
                    "allowed_transitions": sorted(allowed),
                }
            now = _utc_now()
            new_version = current_version + 1
            conn.execute(
                f"""
                UPDATE {FUNNEL_CANDIDATES_TABLE}
                SET state = ?, state_version = ?, updated_at = ?
                WHERE id = ?
                """,
                (to_state, new_version, now, candidate_id),
            )
            _record_transition(
                conn,
                candidate_id=candidate_id,
                from_state=current_state,
                to_state=to_state,
                reason=reason,
                evidence_ref=evidence_ref,
                trigger_source=trigger_source,
                operator=operator,
                idempotency_key=idempotency_key,
            )
            try:
                conn.commit()
            except Exception:
                pass
            return {
                "ok": True,
                "candidate_id": candidate_id,
                "from_state": current_state,
                "to_state": to_state,
                "state_version": new_version,
                "trigger_source_priority": TRIGGER_SOURCE_PRIORITY.get(trigger_source, 0),
            }
        finally:
            conn.close()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def promote_ingested_when_score_present(
    *,
    score_date: str | None = None,
    max_candidates: int = 10_000,
) -> dict[str, Any]:
    """
    For each funnel row still in ``ingested``, if ``stock_scores_daily`` contains a row
    for the same ``ts_code`` on the effective ``score_date`` (latest batch by default),
    transition to ``amplified`` using ``system_rule`` with an auditable idempotency key.
    """
    scanned = 0
    promoted = 0
    skipped_no_score = 0
    idempotent_skips = 0
    errors: list[dict[str, Any]] = []
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE):
                return {
                    "ok": True,
                    "scanned": 0,
                    "promoted": 0,
                    "skipped_no_score": 0,
                    "idempotent_skips": 0,
                    "score_date": "",
                    "errors": [],
                    "note": "funnel_candidates missing",
                }
            if not _db.table_exists(conn, "stock_scores_daily"):
                hint = _load_upstream_scores_hint(conn)
                return {
                    "ok": True,
                    "scanned": 0,
                    "promoted": 0,
                    "skipped_no_score": 0,
                    "idempotent_skips": 0,
                    "score_date": "",
                    "errors": [],
                    "upstream_scores": hint,
                    "note": "stock_scores_daily missing",
                }
            hint = _load_upstream_scores_hint(conn)
            effective = (score_date or "").strip()
            if not effective:
                if str(hint.get("status") or "") != "ready" or not str(hint.get("latest_score_date") or "").strip():
                    return {
                        "ok": True,
                        "scanned": 0,
                        "promoted": 0,
                        "skipped_no_score": 0,
                        "idempotent_skips": 0,
                        "score_date": "",
                        "errors": [],
                        "upstream_scores": hint,
                        "note": "no_score_date",
                    }
                effective = str(hint["latest_score_date"]).strip()

            score_rows = conn.execute(
                """
                SELECT DISTINCT UPPER(TRIM(ts_code)) AS ts_code_norm
                FROM stock_scores_daily
                WHERE score_date = ?
                """,
                (effective,),
            ).fetchall()
            scored_ts: set[str] = set()
            for r in score_rows:
                d = _row_to_dict(r)
                norm = str(d.get("ts_code_norm") or d.get("TS_CODE_NORM") or "").strip()
                if norm:
                    scored_ts.add(norm)
            ing_rows = conn.execute(
                f"""
                SELECT id, ts_code, state_version
                FROM {FUNNEL_CANDIDATES_TABLE}
                WHERE state = 'ingested'
                ORDER BY updated_at ASC
                LIMIT ?
                """,
                (max(1, min(int(max_candidates or 10_000), 50_000)),),
            ).fetchall()
            ing_payload = [_row_to_dict(r) for r in ing_rows]
        finally:
            conn.close()

        scanned = len(ing_payload)
        for d in ing_payload:
            cid = str(d.get("id") or "")
            ts_raw = str(d.get("ts_code") or "").strip().upper()
            ver = int(d.get("state_version") or 0)
            if not cid or not ts_raw:
                skipped_no_score += 1
                continue
            if ts_raw not in scored_ts:
                skipped_no_score += 1
                continue
            idem = f"funnel:ingested_to_amplified:{cid}:{effective}"
            reason = f"score_row_present:{effective}"
            evidence = f"stock_scores_daily:{effective}:{ts_raw}"
            res = transition_candidate(
                cid,
                to_state="amplified",
                reason=reason,
                evidence_ref=evidence,
                trigger_source="system_rule",
                operator="scheduler",
                idempotency_key=idem,
                state_version=ver,
            )
            if res.get("idempotent"):
                idempotent_skips += 1
            elif res.get("ok"):
                promoted += 1
            else:
                errors.append({"candidate_id": cid, "ts_code": ts_raw, "error": res.get("error", "unknown")})
        return {
            "ok": True,
            "scanned": scanned,
            "promoted": promoted,
            "skipped_no_score": skipped_no_score,
            "idempotent_skips": idempotent_skips,
            "score_date": effective,
            "errors": errors,
            "upstream_scores": hint,
        }
    except Exception as exc:
        return {
            "ok": False,
            "scanned": scanned,
            "promoted": promoted,
            "skipped_no_score": skipped_no_score,
            "idempotent_skips": idempotent_skips,
            "score_date": str(score_date or "").strip(),
            "errors": errors + [{"error": str(exc)}],
        }


FUNNEL_REVIEW_SNAPSHOTS_TABLE = "funnel_review_snapshots"


def _ensure_funnel_review_snapshots_table(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FUNNEL_REVIEW_SNAPSHOTS_TABLE} (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            ts_code TEXT NOT NULL,
            state_at_run TEXT NOT NULL,
            ref_date TEXT NOT NULL,
            horizon_days INTEGER NOT NULL,
            return_pct REAL,
            basis TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(candidate_id, ref_date, horizon_days)
        )
        """
    )


def refresh_funnel_review_snapshots(
    *,
    horizon_days: int = 5,
    limit: int = 200,
) -> dict[str, Any]:
    """
    Append-or-replace simple T+N close-to-close returns for funnel rows in terminal-ish states,
    using ``stock_daily_prices`` when available. Decoupled from stage auto-promotion.
    """
    hz = max(1, min(int(horizon_days or 5), 60))
    lim = max(1, min(int(limit or 200), 2_000))
    processed = 0
    written = 0
    skipped = 0
    errors: list[dict[str, Any]] = []
    now = _utc_now()
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE):
                return {"ok": True, "processed": 0, "written": 0, "skipped": 0, "errors": [], "note": "no funnel table"}
            _ensure_funnel_review_snapshots_table(conn)
            prices_ok = _db.table_exists(conn, "stock_daily_prices")
            rows = conn.execute(
                f"""
                SELECT id, ts_code, state, updated_at
                FROM {FUNNEL_CANDIDATES_TABLE}
                WHERE state IN ('confirmed', 'executed', 'reviewed')
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (lim,),
            ).fetchall()
            for row in rows:
                processed += 1
                d = _row_to_dict(row)
                cid = str(d.get("id") or "")
                ts = str(d.get("ts_code") or "").strip().upper()
                st = str(d.get("state") or "")
                upd = str(d.get("updated_at") or "")
                if not cid or not ts:
                    skipped += 1
                    continue
                ref_date = upd[:10] if len(upd) >= 10 else ""
                if len(ref_date) != 10:
                    skipped += 1
                    continue
                ref_compact = ref_date.replace("-", "")
                if not prices_ok or len(ref_compact) != 8:
                    skipped += 1
                    continue
                pr = conn.execute(
                    """
                    SELECT trade_date, close
                    FROM stock_daily_prices
                    WHERE ts_code = ? AND trade_date >= ? AND close IS NOT NULL
                    ORDER BY trade_date ASC
                    LIMIT ?
                    """,
                    (ts, ref_compact, hz + 15),
                ).fetchall()
                closes: list[float] = []
                for p in pr:
                    pd = _row_to_dict(p)
                    cl = pd.get("close")
                    if cl is None:
                        continue
                    try:
                        closes.append(float(cl))
                    except (TypeError, ValueError):
                        continue
                if len(closes) <= hz or closes[0] == 0:
                    skipped += 1
                    continue
                ret_pct = round((closes[hz] - closes[0]) / closes[0] * 100.0, 4)
                basis = f"stock_daily_prices:{ref_compact}:h{hz}"
                snap_id = str(uuid.uuid4())
                try:
                    conn.execute(
                        f"DELETE FROM {FUNNEL_REVIEW_SNAPSHOTS_TABLE} WHERE candidate_id = ? AND ref_date = ? AND horizon_days = ?",
                        (cid, ref_date, hz),
                    )
                    conn.execute(
                        f"""
                        INSERT INTO {FUNNEL_REVIEW_SNAPSHOTS_TABLE}
                            (id, candidate_id, ts_code, state_at_run, ref_date, horizon_days, return_pct, basis, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (snap_id, cid, ts, st, ref_date, hz, ret_pct, basis, now),
                    )
                    written += 1
                except Exception as exc:  # pragma: no cover
                    errors.append({"candidate_id": cid, "error": str(exc)})
            conn.commit()
            return {"ok": True, "processed": processed, "written": written, "skipped": skipped, "errors": errors, "horizon_days": hz}
        finally:
            conn.close()
    except Exception as exc:
        return {
            "ok": False,
            "processed": processed,
            "written": written,
            "skipped": skipped,
            "errors": errors + [{"error": str(exc)}],
        }


def list_funnel_review_snapshots(
    *,
    candidate_id: str = "",
    limit: int = 50,
) -> dict[str, Any]:
    lim = max(1, min(int(limit or 50), 200))
    cid = (candidate_id or "").strip()
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            if not _db.table_exists(conn, FUNNEL_REVIEW_SNAPSHOTS_TABLE):
                return {"items": [], "total": 0}
            if cid:
                rows = conn.execute(
                    f"""
                    SELECT id, candidate_id, ts_code, state_at_run, ref_date, horizon_days, return_pct, basis, created_at
                    FROM {FUNNEL_REVIEW_SNAPSHOTS_TABLE}
                    WHERE candidate_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (cid, lim),
                ).fetchall()
                total_row = conn.execute(
                    f"SELECT COUNT(*) FROM {FUNNEL_REVIEW_SNAPSHOTS_TABLE} WHERE candidate_id = ?",
                    (cid,),
                ).fetchone()
            else:
                rows = conn.execute(
                    f"""
                    SELECT id, candidate_id, ts_code, state_at_run, ref_date, horizon_days, return_pct, basis, created_at
                    FROM {FUNNEL_REVIEW_SNAPSHOTS_TABLE}
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (lim,),
                ).fetchall()
                total_row = conn.execute(f"SELECT COUNT(*) FROM {FUNNEL_REVIEW_SNAPSHOTS_TABLE}").fetchone()
            total = int(total_row[0] or 0) if total_row else 0
            items = [_row_to_dict(r) for r in rows]
            return {"items": items, "total": total, "limit": lim}
        finally:
            conn.close()
    except Exception as exc:
        return {"items": [], "total": 0, "error": str(exc)}


def get_funnel_metrics() -> dict[str, Any]:
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            table_exists = _db.table_exists(conn, FUNNEL_CANDIDATES_TABLE)
            upstream_hint = _load_upstream_scores_hint(conn)
            if not table_exists:
                status_payload = _derive_funnel_status(total=0, table_exists=False, upstream_hint=upstream_hint)
                return {"state_counts": {}, "total": 0, "upstream_scores": upstream_hint, **status_payload}
            rows = conn.execute(
                f"SELECT state, COUNT(*) as cnt FROM {FUNNEL_CANDIDATES_TABLE} GROUP BY state"
            ).fetchall()
            state_counts: dict[str, int] = {}
            total = 0
            for row in rows:
                d = _row_to_dict(row)
                state = str(d.get("state") or "")
                cnt = int(d.get("cnt") or 0)
                state_counts[state] = cnt
                total += cnt
            avg_days_to_decision: float | None = None
            conversion_rate: float | None = None
            if total > 0:
                executed_cnt = int(state_counts.get("executed", 0) or 0)
                reviewed_cnt = int(state_counts.get("reviewed", 0) or 0)
                conversion_rate = float(executed_cnt + reviewed_cnt) / float(total)
            if total > 0 and _db.table_exists(conn, FUNNEL_TRANSITIONS_TABLE):
                try:
                    avg_row = conn.execute(
                        f"""
                        WITH first_decision AS (
                            SELECT candidate_id, MIN(created_at) AS t_dec
                            FROM {FUNNEL_TRANSITIONS_TABLE}
                            WHERE to_state = 'decision_ready'
                            GROUP BY candidate_id
                        )
                        SELECT AVG(JULIANDAY(fd.t_dec) - JULIANDAY(c.created_at)) AS avg_days
                        FROM first_decision fd
                        INNER JOIN {FUNNEL_CANDIDATES_TABLE} c ON c.id = fd.candidate_id
                        """
                    ).fetchone()
                    if avg_row:
                        raw_avg = _row_to_dict(avg_row).get("avg_days")
                        if raw_avg is not None:
                            avg_days_to_decision = round(float(raw_avg), 2)
                except Exception:
                    avg_days_to_decision = None
            status_payload = _derive_funnel_status(total=total, table_exists=True, upstream_hint=upstream_hint)
            return {
                "state_counts": state_counts,
                "total": total,
                "avg_days_to_decision": avg_days_to_decision,
                "conversion_rate": conversion_rate,
                "upstream_scores": upstream_hint,
                **status_payload,
            }
        finally:
            conn.close()
    except Exception as exc:
        return {
            "state_counts": {},
            "total": 0,
            "upstream_scores": {"status": "unknown", "latest_score_date": "", "latest_count": 0},
            **_derive_funnel_status(total=0, table_exists=False, upstream_hint={"status": "unknown"}, error=str(exc)),
            "error": str(exc),
        }


def _ensure_funnel_tables(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FUNNEL_CANDIDATES_TABLE} (
            id TEXT PRIMARY KEY,
            ts_code TEXT NOT NULL,
            name TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT '',
            trigger_source TEXT NOT NULL DEFAULT '',
            reason TEXT NOT NULL DEFAULT '',
            evidence_ref TEXT NOT NULL DEFAULT '',
            state TEXT NOT NULL DEFAULT 'ingested',
            state_version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {FUNNEL_TRANSITIONS_TABLE} (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            from_state TEXT NOT NULL DEFAULT '',
            to_state TEXT NOT NULL,
            reason TEXT NOT NULL DEFAULT '',
            evidence_ref TEXT NOT NULL DEFAULT '',
            trigger_source TEXT NOT NULL DEFAULT '',
            operator TEXT NOT NULL DEFAULT '',
            idempotency_key TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
