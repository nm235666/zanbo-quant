#!/usr/bin/env python3
"""
collect_daily_metrics.py — 每日指标采集与验收门禁

用法:
  python3 collect_daily_metrics.py [--date YYYY-MM-DD] [--gate] [--report]

--gate: 如果任一核心指标低于阈值，非零退出（用于发布阻断）
--report: 打印详细指标报告
--date: 指定采集日期（默认今日）

核心门禁指标（--gate 时检查）:
  - 承接率 (action_承接率): confirm型动作→执行任务比 >= 1.0 (100%)
  - 宏观录入率: macro_regimes 近7日至少有1条 (>= 1)

指标（统计，不阻断）:
  - 今日决策动作数
  - 今日执行订单数
  - 今日复盘记录数
  - 今日宏观状态录入数
  - 今日配置动作录入数
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db_compat


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _query_count(conn, sql: str, params: tuple = ()) -> int | None:
    """Execute a COUNT query and return the integer result, or None on error."""
    try:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        if row is None:
            return 0
        # Row may be a db_compat.Row (dict-like) or a raw tuple
        val = row[0] if not isinstance(row, dict) else list(row.values())[0]
        return int(val)
    except Exception:
        return None


def _table_exists(conn, table_name: str) -> bool:
    """Return True if the named table exists in the current schema."""
    try:
        cur = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = current_schema() AND table_name = ?",
            (table_name,),
        )
        row = cur.fetchone()
        if row is None:
            return False
        val = row[0] if not isinstance(row, dict) else list(row.values())[0]
        return int(val) > 0
    except Exception:
        return False


def _safe_count(conn, table: str, where_clause: str, params: tuple = ()) -> str | int:
    """Query a count from a table, returning 'N/A - table not ready' when absent."""
    if not _table_exists(conn, table):
        return "N/A - table not ready"
    sql = f"SELECT COUNT(*) FROM {table}"
    if where_clause:
        sql += f" WHERE {where_clause}"
    result = _query_count(conn, sql, params)
    if result is None:
        return "N/A - query error"
    return result


# ---------------------------------------------------------------------------
# Analytics table bootstrap
# ---------------------------------------------------------------------------

def ensure_analytics_table(conn) -> None:
    """Create user_analytics_events if it does not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_analytics_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(100) NOT NULL,
            user_id VARCHAR(64),
            session_id VARCHAR(64),
            page_path VARCHAR(200),
            extra_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )
    # autocommit is set on the psycopg2 connection by db_compat.connect(), so
    # no explicit commit is needed; call commit() defensively for SQLite paths.
    try:
        conn.commit()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Metric collection
# ---------------------------------------------------------------------------

def collect_metrics(target_date: date) -> dict[str, Any]:
    """
    Return a dict of metric name → value.
    Values are int, float, or string ('N/A - …').
    """
    date_str = target_date.isoformat()                   # e.g. '2026-04-19'
    seven_days_ago = (target_date - timedelta(days=7)).isoformat()

    conn = db_compat.connect()
    try:
        ensure_analytics_table(conn)

        # ------------------------------------------------------------------
        # Raw counts (informational, do not gate)
        # ------------------------------------------------------------------
        decision_actions_today = _safe_count(
            conn, "decision_actions", "DATE(created_at) = ?", (date_str,)
        )
        confirm_actions_today = _safe_count(
            conn,
            "decision_actions",
            "action_type = 'confirm' AND DATE(created_at) = ?",
            (date_str,),
        )
        orders_today = _safe_count(
            conn, "portfolio_orders", "DATE(created_at) = ?", (date_str,)
        )
        orders_with_action_today = _safe_count(
            conn,
            "portfolio_orders",
            "decision_action_id IS NOT NULL AND DATE(created_at) = ?",
            (date_str,),
        )
        reviews_today = _safe_count(
            conn, "portfolio_reviews", "DATE(created_at) = ?", (date_str,)
        )
        macro_regimes_today = _safe_count(
            conn, "macro_regimes", "DATE(created_at) = ?", (date_str,)
        )
        allocations_today = _safe_count(
            conn, "portfolio_allocations", "DATE(created_at) = ?", (date_str,)
        )

        # 近7日宏观录入数（门禁用）
        macro_regimes_7d = _safe_count(
            conn,
            "macro_regimes",
            "DATE(created_at) >= ?",
            (seven_days_ago,),
        )

        # ------------------------------------------------------------------
        # 承接率: orders_with_action / confirm_actions (门禁用)
        # ------------------------------------------------------------------
        if isinstance(confirm_actions_today, int) and isinstance(orders_with_action_today, int):
            if confirm_actions_today == 0:
                action_acceptance_rate: str | float = "N/A - no confirm actions today"
            else:
                action_acceptance_rate = orders_with_action_today / confirm_actions_today
        else:
            # One or both tables not ready
            action_acceptance_rate = "N/A - table not ready"

    finally:
        try:
            conn.close()
        except Exception:
            pass

    return {
        "date": date_str,
        "decision_actions_today": decision_actions_today,
        "confirm_actions_today": confirm_actions_today,
        "orders_today": orders_today,
        "orders_with_action_today": orders_with_action_today,
        "reviews_today": reviews_today,
        "macro_regimes_today": macro_regimes_today,
        "allocations_today": allocations_today,
        "macro_regimes_7d": macro_regimes_7d,
        "action_承接率": action_acceptance_rate,
    }


# ---------------------------------------------------------------------------
# Gate evaluation
# ---------------------------------------------------------------------------

GATE_CHECKS = [
    {
        "key": "action_承接率",
        "label": "承接率 (confirm动作→执行订单比)",
        "threshold": 1.0,
        "op": ">=",
        "description": "每个confirm动作必须对应至少一条portfolio_order",
        "skip_if_na": True,   # N/A means no confirm actions today → no gate failure
    },
    {
        "key": "macro_regimes_7d",
        "label": "宏观录入率 (近7日macro_regimes条数)",
        "threshold": 1,
        "op": ">=",
        "description": "近7日内至少录入1条宏观状态",
        "skip_if_na": False,  # table not ready → fail gate
    },
]


def evaluate_gates(metrics: dict[str, Any]) -> list[dict]:
    """Return a list of gate failure dicts (empty → all passed)."""
    failures = []
    for check in GATE_CHECKS:
        val = metrics.get(check["key"])
        if isinstance(val, str):
            # N/A string
            if check.get("skip_if_na"):
                continue
            failures.append(
                {
                    "label": check["label"],
                    "value": val,
                    "threshold": check["threshold"],
                    "description": check["description"],
                    "reason": f"指标不可用: {val}",
                }
            )
            continue

        # Numeric comparison
        op = check["op"]
        threshold = check["threshold"]
        passed = (op == ">=" and val >= threshold) or (op == ">" and val > threshold)
        if not passed:
            failures.append(
                {
                    "label": check["label"],
                    "value": val,
                    "threshold": threshold,
                    "description": check["description"],
                    "reason": f"实际值 {val} 未达到阈值 {op} {threshold}",
                }
            )
    return failures


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(metrics: dict[str, Any], failures: list[dict]) -> None:
    date_str = metrics.get("date", "unknown")
    print("=" * 60)
    print(f"  每日指标报告  —  {date_str}")
    print("=" * 60)
    print()
    print("【统计指标】")
    print(f"  今日决策动作数:          {metrics['decision_actions_today']}")
    print(f"  今日confirm动作数:       {metrics['confirm_actions_today']}")
    print(f"  今日执行订单数:          {metrics['orders_today']}")
    print(f"  今日已绑定动作的订单数:  {metrics['orders_with_action_today']}")
    print(f"  今日复盘记录数:          {metrics['reviews_today']}")
    print(f"  今日宏观状态录入数:      {metrics['macro_regimes_today']}")
    print(f"  今日配置动作录入数:      {metrics['allocations_today']}")
    print()
    print("【门禁指标】")
    承接率_val = metrics["action_承接率"]
    if isinstance(承接率_val, float):
        承接率_display = f"{承接率_val:.2%}"
    else:
        承接率_display = str(承接率_val)
    print(f"  承接率 (confirm→order):  {承接率_display}  (阈值 >= 100%)")
    print(f"  近7日宏观录入数:         {metrics['macro_regimes_7d']}  (阈值 >= 1)")
    print()
    if failures:
        print("【门禁结果】FAILED — 以下指标未达标:")
        for f in failures:
            print(f"  x {f['label']}")
            print(f"    {f['reason']}")
            print(f"    说明: {f['description']}")
    else:
        print("【门禁结果】PASSED — 所有门禁指标达标")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="每日指标采集与验收门禁"
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="采集日期 (默认: 今日)",
        default=None,
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="如果门禁指标不达标则以非零状态退出",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="打印详细指标报告",
    )
    args = parser.parse_args()

    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"ERROR: 日期格式无效 '{args.date}'，请使用 YYYY-MM-DD", file=sys.stderr)
            return 2
    else:
        target_date = date.today()

    metrics = collect_metrics(target_date)
    failures = evaluate_gates(metrics)

    if args.report:
        print_report(metrics, failures)
    else:
        # Always print a one-line summary
        status = "FAILED" if failures else "PASSED"
        print(f"[{metrics['date']}] 门禁: {status} | "
              f"决策动作: {metrics['decision_actions_today']} | "
              f"订单: {metrics['orders_today']} | "
              f"承接率: {metrics['action_承接率']}")

    if args.gate and failures:
        print("\nGATE FAILURE SUMMARY:", file=sys.stderr)
        for f in failures:
            print(f"  - {f['label']}: {f['reason']}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
