from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import db_compat as _db

MACRO_REGIMES_TABLE = "macro_regimes"
PORTFOLIO_ALLOCATIONS_TABLE = "portfolio_allocations"

VALID_STATES = {"expansion", "slowdown", "risk_rising", "volatile", "contraction", "recovery"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except Exception:
        return {}


def _ensure_tables(conn) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {MACRO_REGIMES_TABLE} (
            id TEXT PRIMARY KEY,
            short_term_state TEXT NOT NULL DEFAULT 'volatile',
            short_term_confidence REAL NOT NULL DEFAULT 0.7,
            short_term_change_reason TEXT NOT NULL DEFAULT '',
            short_term_changed INTEGER NOT NULL DEFAULT 0,
            medium_term_state TEXT NOT NULL DEFAULT 'volatile',
            medium_term_confidence REAL NOT NULL DEFAULT 0.7,
            medium_term_change_reason TEXT NOT NULL DEFAULT '',
            medium_term_changed INTEGER NOT NULL DEFAULT 0,
            long_term_state TEXT NOT NULL DEFAULT 'volatile',
            long_term_confidence REAL NOT NULL DEFAULT 0.7,
            long_term_change_reason TEXT NOT NULL DEFAULT '',
            long_term_changed INTEGER NOT NULL DEFAULT 0,
            portfolio_action_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PORTFOLIO_ALLOCATIONS_TABLE} (
            id TEXT PRIMARY KEY,
            regime_id TEXT NOT NULL DEFAULT '',
            cash_ratio_pct REAL NOT NULL DEFAULT 10.0,
            max_single_position_pct REAL NOT NULL DEFAULT 8.0,
            max_theme_concentration_pct REAL NOT NULL DEFAULT 20.0,
            stance TEXT NOT NULL DEFAULT 'neutral',
            risk_budget_compression REAL NOT NULL DEFAULT 1.0,
            action_notes TEXT NOT NULL DEFAULT '',
            conflict_ruling TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL DEFAULT ''
        )
        """
    )
    _ensure_outcome_columns(conn)


def _ensure_outcome_columns(conn) -> None:
    conn.execute("""
        ALTER TABLE macro_regimes
        ADD COLUMN IF NOT EXISTS outcome_notes VARCHAR(1000)
    """, [])
    conn.execute("""
        ALTER TABLE macro_regimes
        ADD COLUMN IF NOT EXISTS outcome_rating VARCHAR(20)
    """, [])
    conn.execute("""
        ALTER TABLE macro_regimes
        ADD COLUMN IF NOT EXISTS correction_suggestion VARCHAR(2000)
    """, [])


def _compute_portfolio_suggestion(
    short_state: str,
    medium_state: str,
    long_state: str,
) -> tuple[list[dict], str]:
    """Derive portfolio action suggestions and conflict ruling from regime states."""
    defensive_states = {"contraction", "risk_rising"}
    offensive_states = {"expansion", "recovery"}

    short_def = short_state in defensive_states
    medium_def = medium_state in defensive_states
    long_def = long_state in defensive_states

    short_off = short_state in offensive_states
    medium_off = medium_state in offensive_states
    long_off = long_state in offensive_states

    if short_off and medium_off and long_off:
        return [
            {"type": "cash", "description": "建议现金比例 5%，充分利用进攻机会"},
            {"type": "risk_budget", "description": "风险预算不压缩，允许充分配置"},
            {"type": "theme", "description": "主题集中度上限 25%"},
            {"type": "sector_rotation", "description": "行业权重向高景气进攻方向倾斜"},
            {"type": "strategy_switch", "description": "恢复趋势跟随与高弹性短线策略"},
        ], ""

    if long_def and short_off:
        return [
            {"type": "cash", "description": "建议现金比例 20%，长线防守优先"},
            {"type": "risk_budget", "description": "风险预算压缩至 60%，允许局部高确定性短线参与"},
            {"type": "theme", "description": "单主题集中度上限 15%，禁止高波动策略"},
            {"type": "defence", "description": "同步执行防守动作：提高现金、限制总仓位 ≤ 60%"},
            {"type": "sector_rotation", "description": "行业权重回撤至防守板块，降低高波动赛道暴露"},
            {"type": "strategy_switch", "description": "暂停高波动短线策略，仅保留高确定性参与"},
        ], "短线进攻信号与长线防守状态冲突：允许局部高确定性短线参与，但同步压缩风险预算至60%，限制总仓位≤60%，禁止高波动策略"

    if medium_def and long_def:
        return [
            {"type": "cash", "description": "建议现金比例 30%，中长线均防守"},
            {"type": "risk_budget", "description": "风险预算压缩至 40%"},
            {"type": "theme", "description": "单主题集中度上限 10%"},
            {"type": "defence", "description": "暂停高波动策略，减少净多头敞口"},
            {"type": "sector_rotation", "description": "行业权重切向低波动防守资产"},
            {"type": "strategy_switch", "description": "暂停激进短线策略，保留低波动防守仓位"},
        ], ""

    if short_def or medium_def or long_def:
        return [
            {"type": "cash", "description": "建议现金比例 15%，保持一定防守缓冲"},
            {"type": "risk_budget", "description": "风险预算压缩至 75%"},
            {"type": "theme", "description": "单主题集中度上限 18%"},
            {"type": "sector_rotation", "description": "行业权重适度转向稳健板块"},
            {"type": "strategy_switch", "description": "收缩高波动短线策略，优先低回撤交易"},
        ], ""

    return [
        {"type": "cash", "description": "建议现金比例 10%，中性配置"},
        {"type": "risk_budget", "description": "风险预算不压缩"},
        {"type": "theme", "description": "单主题集中度上限 20%"},
        {"type": "sector_rotation", "description": "行业权重保持均衡配置"},
        {"type": "strategy_switch", "description": "维持当前短线策略节奏"},
    ], ""


def _derive_allocation_params(
    short_state: str,
    long_state: str,
) -> tuple[float, float, float, str, float]:
    """Returns (cash_ratio, max_single, max_theme, stance, risk_compression)."""
    if long_state in {"contraction", "risk_rising"}:
        return 25.0, 5.0, 15.0, "defensive", 0.5
    if short_state in {"expansion", "recovery"} and long_state in {"expansion", "recovery"}:
        return 5.0, 10.0, 25.0, "offensive", 1.0
    if short_state in {"contraction", "risk_rising"}:
        return 18.0, 6.0, 17.0, "defensive", 0.7
    return 10.0, 8.0, 20.0, "neutral", 1.0


def _status_payload(
    *,
    status: str,
    status_reason: str,
    missing_inputs: list[str] | None = None,
    generated_from: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "status_reason": status_reason,
        "missing_inputs": list(missing_inputs or []),
        "generated_from": list(generated_from or []),
    }


def _build_conflict_constraints(allocation: dict[str, Any], macro_actions: list[dict[str, Any]]) -> dict[str, Any]:
    conflict_ruling = str(allocation.get("conflict_ruling") or "").strip()
    compression = float(allocation.get("risk_budget_compression") or 1.0)
    theme_limit = allocation.get("max_theme_concentration_pct")
    defence_action = next((item for item in macro_actions if item.get("type") == "defence"), None)
    strategy_action = next((item for item in macro_actions if item.get("type") == "strategy_switch"), None)

    if not conflict_ruling and compression >= 1 and not defence_action and not strategy_action:
        return {}

    allowed_actions = []
    if "允许局部高确定性短线参与" in conflict_ruling:
        allowed_actions.append("仅允许高确定性短线动作")
    elif compression < 1:
        allowed_actions.append("短线动作需按压缩后风险预算执行")
    else:
        allowed_actions.append("可按当前配置动作执行")

    defence_requirements = []
    if defence_action and defence_action.get("description"):
        defence_requirements.append(str(defence_action.get("description")))
    if theme_limit not in (None, ""):
        defence_requirements.append(f"主题集中度上限收敛至 {float(theme_limit):.0f}%")
    if strategy_action and strategy_action.get("description"):
        defence_requirements.append(str(strategy_action.get("description")))

    trigger_condition = "宏观长线防守与短线进攻信号同时出现时立即生效" if conflict_ruling else "当风险预算进入压缩状态时生效"
    return {
        "allowed_actions": allowed_actions,
        "required_defence_actions": defence_requirements,
        "risk_budget_pct": int(round(compression * 100)),
        "effective_condition": trigger_condition,
    }


def get_latest_regime() -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        if not _db.table_exists(conn, MACRO_REGIMES_TABLE):
            return {
                "ok": True,
                "regime": None,
                **_status_payload(
                    status="not_initialized",
                    status_reason="尚未建立三周期状态记录，请先生成系统建议并完成首次人工复核。",
                    missing_inputs=["macro_regimes"],
                ),
            }
        row = conn.execute(
            f"SELECT * FROM {MACRO_REGIMES_TABLE} ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return {
                "ok": True,
                "regime": None,
                **_status_payload(
                    status="not_initialized",
                    status_reason="当前还没有已确认的三周期状态。",
                    missing_inputs=["macro_regime_record"],
                ),
            }
        d = _row_to_dict(row)
        try:
            d["portfolio_action_json"] = json.loads(d.get("portfolio_action_json") or "[]")
        except Exception:
            d["portfolio_action_json"] = []
        alloc_row = conn.execute(
            f"SELECT conflict_ruling FROM {PORTFOLIO_ALLOCATIONS_TABLE} WHERE regime_id = ? ORDER BY created_at DESC LIMIT 1",
            (str(d.get("id") or ""),),
        ).fetchone() if _db.table_exists(conn, PORTFOLIO_ALLOCATIONS_TABLE) else None
        conflict_ruling = str(_row_to_dict(alloc_row).get("conflict_ruling") or "") if alloc_row else ""
        return {
            "ok": True,
            "regime": d,
            "conflict_ruling": conflict_ruling,
            **_status_payload(
                status="ready",
                status_reason="已存在可用于组合动作映射的三周期状态。",
                generated_from=["macro_regimes", "portfolio_allocations" if conflict_ruling else "macro_regimes"],
            ),
        }
    except Exception as exc:
        return {
            "ok": True,
            "regime": None,
            "error": str(exc),
            **_status_payload(
                status="error",
                status_reason=f"读取三周期状态失败：{exc}",
                missing_inputs=["macro_regimes"],
            ),
        }
    finally:
        conn.close()


def record_regime(
    short_term_state: str,
    medium_term_state: str,
    long_term_state: str,
    short_term_confidence: float = 0.7,
    medium_term_confidence: float = 0.7,
    long_term_confidence: float = 0.7,
    short_term_change_reason: str = "",
    medium_term_change_reason: str = "",
    long_term_change_reason: str = "",
    short_term_changed: bool = False,
    medium_term_changed: bool = False,
    long_term_changed: bool = False,
    created_by: str = "",
) -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        _ensure_tables(conn)
        actions, conflict_ruling = _compute_portfolio_suggestion(
            short_term_state, medium_term_state, long_term_state
        )
        now = _utc_now()
        regime_id = str(uuid.uuid4())[:16]
        conn.execute(
            f"""
            INSERT INTO {MACRO_REGIMES_TABLE}
            (id, short_term_state, short_term_confidence, short_term_change_reason, short_term_changed,
             medium_term_state, medium_term_confidence, medium_term_change_reason, medium_term_changed,
             long_term_state, long_term_confidence, long_term_change_reason, long_term_changed,
             portfolio_action_json, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                regime_id,
                short_term_state, short_term_confidence, short_term_change_reason, int(short_term_changed),
                medium_term_state, medium_term_confidence, medium_term_change_reason, int(medium_term_changed),
                long_term_state, long_term_confidence, long_term_change_reason, int(long_term_changed),
                json.dumps(actions, ensure_ascii=False), now, created_by,
            ),
        )
        # Auto-create linked allocation record
        cash_ratio, max_single, max_theme, stance, risk_compression = _derive_allocation_params(
            short_term_state, long_term_state
        )
        conn.execute(
            f"""
            INSERT INTO {PORTFOLIO_ALLOCATIONS_TABLE}
            (id, regime_id, cash_ratio_pct, max_single_position_pct, max_theme_concentration_pct,
             stance, risk_budget_compression, action_notes, conflict_ruling, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4())[:16], regime_id,
                cash_ratio, max_single, max_theme,
                stance, risk_compression, "", conflict_ruling, now, created_by,
            ),
        )
        return {"ok": True, "id": regime_id, "portfolio_actions": actions, "conflict_ruling": conflict_ruling}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        conn.close()


def list_regimes(page: int = 1, page_size: int = 10) -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        if not _db.table_exists(conn, MACRO_REGIMES_TABLE):
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 1,
                **_status_payload(
                    status="not_initialized",
                    status_reason="尚无三周期历史记录。",
                    missing_inputs=["macro_regimes"],
                ),
            }
        total_row = conn.execute(f"SELECT COUNT(*) FROM {MACRO_REGIMES_TABLE}").fetchone()
        total = int(total_row[0] or 0) if total_row else 0
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"SELECT * FROM {MACRO_REGIMES_TABLE} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
        items = []
        for r in rows:
            d = _row_to_dict(r)
            try:
                d["portfolio_action_json"] = json.loads(d.get("portfolio_action_json") or "[]")
            except Exception:
                d["portfolio_action_json"] = []
            items.append(d)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, -(-total // page_size)),
            **_status_payload(
                status="ready" if total > 0 else "empty",
                status_reason="已加载三周期历史记录。" if total > 0 else "当前暂无三周期历史记录。",
                generated_from=["macro_regimes"] if total > 0 else [],
            ),
        }
    except Exception as exc:
        return {
            "items": [],
            "total": 0,
            "error": str(exc),
            **_status_payload(
                status="error",
                status_reason=f"三周期历史读取失败：{exc}",
                missing_inputs=["macro_regimes"],
            ),
        }
    finally:
        conn.close()


def get_latest_allocation() -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        if not _db.table_exists(conn, PORTFOLIO_ALLOCATIONS_TABLE):
            regime_exists = _db.table_exists(conn, MACRO_REGIMES_TABLE) and bool(
                conn.execute(f"SELECT COUNT(*) FROM {MACRO_REGIMES_TABLE}").fetchone()[0]
            )
            return {
                "ok": True,
                "allocation": None,
                **_status_payload(
                    status="insufficient_evidence" if regime_exists else "not_initialized",
                    status_reason="已有宏观状态，但尚未生成配置动作。" if regime_exists else "尚未建立宏观状态，无法生成配置动作。",
                    missing_inputs=["portfolio_allocations"] if regime_exists else ["macro_regimes", "portfolio_allocations"],
                ),
            }
        row = conn.execute(
            f"SELECT * FROM {PORTFOLIO_ALLOCATIONS_TABLE} ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            regime_exists = _db.table_exists(conn, MACRO_REGIMES_TABLE) and bool(
                conn.execute(f"SELECT COUNT(*) FROM {MACRO_REGIMES_TABLE}").fetchone()[0]
            )
            return {
                "ok": True,
                "allocation": None,
                **_status_payload(
                    status="insufficient_evidence" if regime_exists else "not_initialized",
                    status_reason="三周期状态已存在，但配置动作尚未生成。" if regime_exists else "尚未有可用的三周期状态来推导配置动作。",
                    missing_inputs=["portfolio_allocations"] if regime_exists else ["macro_regimes", "portfolio_allocations"],
                ),
            }
        allocation = _row_to_dict(row)
        regime_id = str(allocation.get("regime_id") or "").strip()
        macro_actions: list[dict[str, Any]] = []
        if regime_id and _db.table_exists(conn, MACRO_REGIMES_TABLE):
            regime_row = conn.execute(
                f"SELECT portfolio_action_json FROM {MACRO_REGIMES_TABLE} WHERE id = ? LIMIT 1",
                (regime_id,),
            ).fetchone()
            regime_payload = _row_to_dict(regime_row)
            try:
                raw_actions = json.loads(regime_payload.get("portfolio_action_json") or "[]")
                if isinstance(raw_actions, list):
                    macro_actions = [item for item in raw_actions if isinstance(item, dict)]
            except Exception:
                macro_actions = []
        allocation["macro_actions"] = macro_actions
        allocation["conflict_constraints"] = _build_conflict_constraints(allocation, macro_actions)
        if regime_id and _db.table_exists(conn, MACRO_REGIMES_TABLE):
            review_row = conn.execute(
                f"SELECT outcome_rating, outcome_notes, correction_suggestion, created_at FROM {MACRO_REGIMES_TABLE} WHERE id = ? LIMIT 1",
                (regime_id,),
            ).fetchone()
            review_payload = _row_to_dict(review_row)
            allocation["long_term_review"] = {
                "regime_id": regime_id,
                "outcome_rating": review_payload.get("outcome_rating") or "",
                "outcome_notes": review_payload.get("outcome_notes") or "",
                "correction_suggestion": review_payload.get("correction_suggestion") or "",
                "regime_created_at": review_payload.get("created_at") or "",
                "action_count": len(macro_actions),
            }
        else:
            allocation["long_term_review"] = {
                "regime_id": regime_id,
                "outcome_rating": "",
                "outcome_notes": "",
                "correction_suggestion": "",
                "regime_created_at": "",
                "action_count": len(macro_actions),
            }
        source = "manual_allocation" if not regime_id else "macro_regime_allocation"
        return {
            "ok": True,
            "allocation": allocation,
            **_status_payload(
                status="ready",
                status_reason="已生成可用于账户级仓位约束的配置动作。",
                generated_from=[source, "portfolio_allocations", "macro_regimes" if macro_actions else source],
            ),
        }
    except Exception as exc:
        return {
            "ok": True,
            "allocation": None,
            "error": str(exc),
            **_status_payload(
                status="error",
                status_reason=f"读取配置动作失败：{exc}",
                missing_inputs=["portfolio_allocations"],
            ),
        }
    finally:
        conn.close()


def record_allocation(
    cash_ratio_pct: float = 10.0,
    max_single_position_pct: float = 8.0,
    max_theme_concentration_pct: float = 20.0,
    stance: str = "neutral",
    risk_budget_compression: float = 1.0,
    action_notes: str = "",
    regime_id: str = "",
    created_by: str = "",
) -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        _ensure_tables(conn)
        now = _utc_now()
        alloc_id = str(uuid.uuid4())[:16]
        conn.execute(
            f"""
            INSERT INTO {PORTFOLIO_ALLOCATIONS_TABLE}
            (id, regime_id, cash_ratio_pct, max_single_position_pct, max_theme_concentration_pct,
             stance, risk_budget_compression, action_notes, conflict_ruling, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alloc_id, regime_id,
                cash_ratio_pct, max_single_position_pct, max_theme_concentration_pct,
                stance, risk_budget_compression, action_notes, "", now, created_by,
            ),
        )
        return {"ok": True, "id": alloc_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        conn.close()


def list_allocations(page: int = 1, page_size: int = 10) -> dict[str, Any]:
    conn = _db.connect()
    try:
        _db.apply_row_factory(conn)
        if not _db.table_exists(conn, PORTFOLIO_ALLOCATIONS_TABLE):
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 1,
                **_status_payload(
                    status="not_initialized",
                    status_reason="尚无配置动作历史。",
                    missing_inputs=["portfolio_allocations"],
                ),
            }
        total_row = conn.execute(f"SELECT COUNT(*) FROM {PORTFOLIO_ALLOCATIONS_TABLE}").fetchone()
        total = int(total_row[0] or 0) if total_row else 0
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"SELECT * FROM {PORTFOLIO_ALLOCATIONS_TABLE} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
        return {
            "items": [_row_to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, -(-total // page_size)),
            **_status_payload(
                status="ready" if total > 0 else "empty",
                status_reason="已加载配置历史。" if total > 0 else "当前暂无配置历史。",
                generated_from=["portfolio_allocations"] if total > 0 else [],
            ),
        }
    except Exception as exc:
        return {
            "items": [],
            "total": 0,
            "error": str(exc),
            **_status_payload(
                status="error",
                status_reason=f"配置历史读取失败：{exc}",
                missing_inputs=["portfolio_allocations"],
            ),
        }
    finally:
        conn.close()


def update_regime_outcome(regime_id: str, outcome_notes: str, outcome_rating: str, correction_suggestion: str = "") -> dict:
    """Record the actual result and effectiveness rating for a past regime entry."""
    with _db.connect() as conn:
        conn.execute(
            "UPDATE macro_regimes SET outcome_notes=?, outcome_rating=?, correction_suggestion=? WHERE id=?",
            [outcome_notes, outcome_rating, correction_suggestion, regime_id]
        )
        return {"ok": True, "id": regime_id}


def suggest_regime() -> dict:
    """
    Auto-suggest macro regime states based on available market signal data.

    Algorithm:
    1. Query theme_hotspot_tracker (last 7 days) for direction distribution
    2. Infer short-term state from bullish/bearish ratio
    3. For medium/long term: use existing regime history trend if available, else default to 'volatile'
    4. Return suggestions with basis text and confidence
    """
    try:
        conn = _db.connect()
        try:
            _db.apply_row_factory(conn)
            # ① Theme direction distribution (last 7 days)
            bullish = bearish = neutral = 0
            try:
                rows = conn.execute(
                    "SELECT direction, COUNT(*) AS cnt "
                    "FROM theme_hotspot_tracker "
                    "WHERE CAST(NULLIF(latest_evidence_time, '') AS timestamptz) "
                    ">= NOW() - INTERVAL '7 days' "
                    "GROUP BY direction"
                ).fetchall()
            except Exception:
                rows = []

            for row in rows:
                d = str(row[0] or '').strip().lower()
                c = int(row[1] or 0)
                if d in ('bullish', '看多', '多', 'up', '涨'):
                    bullish += c
                elif d in ('bearish', '看空', '空', 'down', '跌'):
                    bearish += c
                else:
                    neutral += c

            total = bullish + bearish + neutral or 1
            bull_ratio = bullish / total
            bear_ratio = bearish / total

            # Short-term state from theme distribution
            if bull_ratio >= 0.6:
                short_term = 'expansion'
                short_conf = round(bull_ratio, 2)
            elif bear_ratio >= 0.5:
                short_term = 'risk_rising'
                short_conf = round(bear_ratio, 2)
            elif bull_ratio >= 0.4:
                short_term = 'recovery'
                short_conf = 0.55
            else:
                short_term = 'volatile'
                short_conf = 0.5

            # ② Medium/long term: use latest regime history trend
            medium_term = long_term = 'volatile'
            medium_conf = long_conf = 0.4
            try:
                latest_rows = conn.execute(
                    f"SELECT medium_term_state, long_term_state FROM {MACRO_REGIMES_TABLE} ORDER BY created_at DESC LIMIT 1",
                    []
                ).fetchone()
                if latest_rows:
                    medium_term = str(latest_rows[0] or 'volatile')
                    long_term = str(latest_rows[1] or 'volatile')
                    medium_conf = 0.6
                    long_conf = 0.6
            except Exception:
                pass

            basis_parts = []
            if bullish + bearish + neutral > 0:
                basis_parts.append(f"近7日主题：多{bullish}/空{bearish}/中性{neutral}")
            if medium_conf > 0.4:
                basis_parts.append("参考历史周期记录")
            basis = "，".join(basis_parts) if basis_parts else "数据不足，建议人工判断"

            return {
                "ok": True,
                "suggestion": {
                    "short_term_state": short_term,
                    "short_term_confidence": short_conf,
                    "medium_term_state": medium_term,
                    "medium_term_confidence": medium_conf,
                    "long_term_state": long_term,
                    "long_term_confidence": long_conf,
                    "basis": basis,
                    "data_points": bullish + bearish + neutral,
                }
            }
        finally:
            conn.close()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "suggestion": None}
