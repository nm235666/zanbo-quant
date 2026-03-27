#!/usr/bin/env python3
"""
基于 rate_curve_points 派生利差数据到 spread_daily。

当前派生：
- CN_SHIBOR_1Y_MINUS_1M
- CN_SHIBOR_3M_MINUS_ON
- US_TSY_10Y_MINUS_2Y
- US_TSY_30Y_MINUS_10Y
- US_TSY_10Y_MINUS_3M

单位：
- bp（基点）
"""

from __future__ import annotations

import argparse
import db_compat as sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


SPREAD_SPECS = [
    ("CN_SHIBOR_1Y_MINUS_1M", "CN", "shibor", "1Y", "1M"),
    ("CN_SHIBOR_3M_MINUS_ON", "CN", "shibor", "3M", "ON"),
    ("US_TSY_10Y_MINUS_2Y", "US", "treasury", "10Y", "2Y"),
    ("US_TSY_30Y_MINUS_10Y", "US", "treasury", "30Y", "10Y"),
    ("US_TSY_10Y_MINUS_3M", "US", "treasury", "10Y", "3M"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="基于 rate_curve_points 派生 spread_daily")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--table-name", default="spread_daily", help="目标表名")
    parser.add_argument("--start-date", default="", help="开始日期(YYYYMMDD)")
    parser.add_argument("--end-date", default="", help="结束日期(YYYYMMDD)")
    parser.add_argument("--lookback-days", type=int, default=365, help="默认回溯天数")
    parser.add_argument("--truncate", action="store_true", help="执行前清空目标表")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def calc_start(end_date: str, lookback_days: int) -> str:
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    return (end_dt - timedelta(days=max(lookback_days, 1))).strftime("%Y%m%d")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            spread_code TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            value REAL,
            unit TEXT DEFAULT 'bp',
            source TEXT,
            update_time TEXT,
            PRIMARY KEY (spread_code, trade_date)
        )
        """
    )
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name}(trade_date)")
    conn.commit()


def upsert_rows(conn: sqlite3.Connection, table_name: str, rows: list[tuple]) -> int:
    if not rows:
        return 0
    sql = f"""
    INSERT INTO {table_name} (
        spread_code, trade_date, value, unit, source, update_time
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(spread_code, trade_date) DO UPDATE SET
        value=excluded.value,
        unit=excluded.unit,
        source=excluded.source,
        update_time=excluded.update_time
    """
    cur = conn.cursor()
    cur.executemany(sql, rows)
    conn.commit()
    return len(rows)


def fetch_curve_map(conn: sqlite3.Connection, start_date: str, end_date: str) -> dict[tuple[str, str, str, str], float]:
    rows = conn.execute(
        """
        SELECT market, curve_code, trade_date, tenor, value
        FROM rate_curve_points
        WHERE trade_date >= ? AND trade_date <= ?
        """,
        (start_date, end_date),
    ).fetchall()
    return {(r[0], r[1], r[2], r[3]): float(r[4]) for r in rows if r[4] is not None}


def main() -> int:
    args = parse_args()
    end_date = args.end_date.strip() or utc_today()
    start_date = args.start_date.strip() or calc_start(end_date, args.lookback_days)

    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)
        if args.truncate:
            conn.execute(f"DELETE FROM {args.table_name}")
            conn.commit()
            print(f"已清空旧数据: {args.table_name}")

        curve_map = fetch_curve_map(conn, start_date, end_date)
        trade_dates = sorted({key[2] for key in curve_map.keys()})
        update_time = utc_now()
        rows: list[tuple] = []

        for spread_code, market, curve_code, long_tenor, short_tenor in SPREAD_SPECS:
            for trade_date in trade_dates:
                long_key = (market, curve_code, trade_date, long_tenor)
                short_key = (market, curve_code, trade_date, short_tenor)
                if long_key not in curve_map or short_key not in curve_map:
                    continue
                spread_bp = (curve_map[long_key] - curve_map[short_key]) * 100.0
                rows.append(
                    (
                        spread_code,
                        trade_date,
                        spread_bp,
                        "bp",
                        "derived.rate_curve_points",
                        update_time,
                    )
                )

        n = upsert_rows(conn, args.table_name, rows)
        final_count = conn.execute(f"SELECT COUNT(*) FROM {args.table_name}").fetchone()[0]
        print(
            f"完成: trade_dates={len(trade_dates)}, upsert_rows={n}, table_rows={final_count}, range={start_date}~{end_date}"
        )
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
