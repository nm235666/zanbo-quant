#!/usr/bin/env python3
"""
补缺版：仅针对 stock_financials 中缺失的 ts_code + report_period 做逐股精补。

推荐用法：
1) 先跑高速版铺底
   python3 fast_backfill_stock_financials.py --recent-periods 8
2) 再跑本脚本补缺
   python3 backfill_missing_stock_financials.py --recent-periods 8

也支持只补指定报告期：
   python3 backfill_missing_stock_financials.py --periods 20251231,20250630
"""

from __future__ import annotations

import argparse
import db_compat as sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from backfill_stock_financials import (
    DEFAULT_TOKEN,
    ensure_table,
    fetch_financial_context,
    upsert_rows,
)

LOCAL_DEPS = Path(__file__).resolve().parent / ".deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import tushare as ts

QUARTER_ENDS = ("1231", "0930", "0630", "0331")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="补抓 stock_financials 缺失的 ts_code + report_period")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Tushare Token")
    parser.add_argument("--table-name", default="stock_financials", help="目标表名")
    parser.add_argument("--recent-periods", type=int, default=8, help="最近多少期，默认8")
    parser.add_argument("--periods", default="", help="手工指定报告期，逗号分隔")
    parser.add_argument("--start-from", default="", help="从指定 ts_code 开始补")
    parser.add_argument("--limit-stocks", type=int, default=0, help="最多补多少只股票")
    parser.add_argument("--pause", type=float, default=0.12, help="每只股票请求后暂停秒数")
    parser.add_argument("--retry", type=int, default=3, help="单接口失败最大重试次数")
    parser.add_argument("--all-status", action="store_true", help="抓全部状态股票")
    parser.add_argument("--preview", action="store_true", help="仅预览缺口，不执行补抓")
    return parser.parse_args()


def get_recent_periods(n: int) -> list[str]:
    now = datetime.now(timezone.utc)
    ymd = now.strftime("%Y%m%d")
    candidates: list[str] = []
    year = now.year
    while len(candidates) < max(n, 1) + 4:
        for suffix in QUARTER_ENDS:
            period = f"{year}{suffix}"
            if period <= ymd:
                candidates.append(period)
        year -= 1
    periods = candidates[: max(n, 1)]
    return periods


def load_code_scope(conn: sqlite3.Connection, all_status: bool, start_from: str, limit_stocks: int) -> list[str]:
    where = []
    params: list[object] = []
    if not all_status:
        where.append("list_status = 'L'")
    if start_from.strip():
        where.append("ts_code >= ?")
        params.append(start_from.strip().upper())
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    limit_sql = f" LIMIT {int(limit_stocks)}" if limit_stocks > 0 else ""
    sql = f"SELECT ts_code FROM stock_codes{where_sql} ORDER BY ts_code{limit_sql}"
    return [row[0] for row in conn.execute(sql, params).fetchall()]


def build_missing_map(
    conn: sqlite3.Connection,
    periods: list[str],
    codes: list[str],
    table_name: str,
) -> dict[str, list[str]]:
    if not codes or not periods:
        return {}
    code_set = set(codes)
    placeholders = ",".join(["?"] * len(periods))
    sql = f"SELECT ts_code, report_period FROM {table_name} WHERE report_period IN ({placeholders})"
    existing = conn.execute(sql, periods).fetchall()
    have: dict[str, set[str]] = {}
    for ts_code, period in existing:
        if ts_code not in code_set:
            continue
        have.setdefault(ts_code, set()).add(period)

    missing: dict[str, list[str]] = {}
    for ts_code in codes:
        periods_missing = [p for p in periods if p not in have.get(ts_code, set())]
        if periods_missing:
            missing[ts_code] = periods_missing
    return missing


def main() -> int:
    args = parse_args()
    periods = [x.strip() for x in args.periods.split(",") if x.strip()] if args.periods else get_recent_periods(args.recent_periods)
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"错误: 数据库不存在: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)
        codes = load_code_scope(conn, args.all_status, args.start_from, args.limit_stocks)
        missing_map = build_missing_map(conn, periods, codes, args.table_name)
        total_missing_rows = sum(len(v) for v in missing_map.values())
        print(
            f"范围股票数: {len(codes)}, 缺口股票数: {len(missing_map)}, 缺口组合数: {total_missing_rows}, periods={periods}"
        )

        if args.preview:
            shown = 0
            for ts_code, miss in missing_map.items():
                print(f"{ts_code}\t{','.join(miss)}")
                shown += 1
                if shown >= 50:
                    break
            return 0

        if not missing_map:
            print("没有缺口需要补抓。")
            return 0
    finally:
        conn.close()

    pro = ts.pro_api(args.token)
    conn = sqlite3.connect(db_path)
    try:
        total_upsert = 0
        failed = 0
        items = list(missing_map.items())
        for idx, (ts_code, missing_periods) in enumerate(items, start=1):
            try:
                rows = fetch_financial_context(
                    pro=pro,
                    ts_code=ts_code,
                    recent_periods=max(args.recent_periods, len(periods)),
                    retry=args.retry,
                )
                rows = [row for row in rows if row["report_period"] in set(missing_periods)]
                n = upsert_rows(conn, args.table_name, rows)
                total_upsert += n
                print(
                    f"[{idx}/{len(items)}] {ts_code}: missing={','.join(missing_periods)} fetched={len(rows)} upsert={n}"
                )
            except Exception as exc:
                failed += 1
                print(f"[{idx}/{len(items)}] {ts_code}: 失败 -> {exc}", file=sys.stderr)
            if args.pause > 0:
                time.sleep(args.pause)

        final_rows = conn.execute(f"SELECT COUNT(*) FROM {args.table_name}").fetchone()[0]
        print(
            f"完成: failed={failed}, upsert_rows={total_upsert}, table_rows={final_rows}, db={db_path}"
        )
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
