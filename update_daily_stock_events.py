#!/usr/bin/env python3
"""
按公告日增量更新 stock_events。

适合放到定时任务里每天跑一次。
"""

from __future__ import annotations

import argparse
import db_compat as sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backfill_stock_events import (
    DEFAULT_TOKEN,
    build_dividend_events,
    build_express_events,
    build_forecast_events,
    build_holdertrade_events,
    build_repurchase_events,
    ensure_table,
    upsert_rows,
)

LOCAL_DEPS = Path(__file__).resolve().parent / ".deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import tushare as ts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按公告日增量更新 stock_events")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Tushare Token")
    parser.add_argument("--table-name", default="stock_events", help="目标表名")
    parser.add_argument("--ann-date", default="", help="公告日 YYYYMMDD，默认北京时间今天")
    return parser.parse_args()


def china_today() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y%m%d")


def main() -> int:
    args = parse_args()
    ann_date = args.ann_date.strip() or china_today()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"错误: 数据库不存在: {db_path}", file=sys.stderr)
        return 1

    pro = ts.pro_api(args.token)
    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)

        builders = [
            ("forecast", build_forecast_events),
            ("express", build_express_events),
            ("dividend", build_dividend_events),
            ("repurchase", build_repurchase_events),
            ("stk_holdertrade", build_holdertrade_events),
        ]

        total_inserted = 0
        total_fetched = 0
        for api_name, builder in builders:
            try:
                df = getattr(pro, api_name)(ann_date=ann_date)
            except Exception as exc:
                print(f"{api_name}: 失败 -> {exc}", file=sys.stderr)
                continue

            rows = []
            if df is not None and not df.empty:
                for ts_code, sub_df in df.groupby("ts_code"):
                    rows.extend(builder(sub_df, ts_code))
            inserted = upsert_rows(conn, args.table_name, rows)
            total_fetched += len(rows)
            total_inserted += inserted
            print(f"{api_name}: fetched={len(rows)} inserted={inserted}")

        final_rows = conn.execute(f"SELECT COUNT(*) FROM {args.table_name}").fetchone()[0]
        print(
            f"完成: ann_date={ann_date}, fetched={total_fetched}, inserted={total_inserted}, table_rows={final_rows}"
        )
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
