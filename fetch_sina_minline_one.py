#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import db_compat as sqlite3
import urllib.parse
import urllib.request
from pathlib import Path

from market_calendar import DEFAULT_TOKEN, resolve_trade_date
from realtime_streams import publish_app_event

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取新浪1只股票分时并入库")
    parser.add_argument("--ts-code", default="600114.SH", help="股票代码，如 600114.SH")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--table-name", default="stock_minline", help="分钟线表名")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Tushare Token，用于按交易日历解析默认日期")
    parser.add_argument("--trade-date", default="", help="交易日 YYYYMMDD，默认北京时间今天")
    return parser.parse_args()


def ts_to_sina_symbol(ts_code: str) -> str:
    code = ts_code.strip().upper()
    if "." not in code:
        raise ValueError("ts_code 格式应为 000001.SZ / 600000.SH")
    symbol, exch = code.split(".", 1)
    if exch == "SH":
        return f"sh{symbol}"
    if exch == "SZ":
        return f"sz{symbol}"
    if exch == "BJ":
        return f"bj{symbol}"
    raise ValueError(f"不支持的交易所: {exch}")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            ts_code TEXT NOT NULL,
            trade_date TEXT NOT NULL,
            minute_time TEXT NOT NULL,
            price REAL,
            avg_price REAL,
            volume REAL,
            total_volume REAL,
            source TEXT DEFAULT 'sina',
            PRIMARY KEY (ts_code, trade_date, minute_time),
            FOREIGN KEY (ts_code) REFERENCES stock_codes(ts_code)
        )
        """
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_td_time ON {table_name}(trade_date, minute_time)"
    )
    conn.commit()


def fetch_sina_data(sina_symbol: str) -> list[dict]:
    callback = f"var t1{sina_symbol}="
    qs = urllib.parse.urlencode(
        {
            "symbol": sina_symbol,
            "callback": callback,
            "dpc": "1",
        }
    )
    url = f"https://quotes.sina.cn/cn/api/openapi.php/CN_MinlineService.getMinlineData?{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://finance.sina.com.cn/realstock/company/{sina_symbol}/nc.shtml",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode("utf-8", errors="ignore")

    m = re.match(r"var\s+t1\w+=\((.*)\);?$", text)
    if not m:
        raise RuntimeError("新浪接口返回格式异常")
    obj = json.loads(m.group(1))
    result = obj.get("result", {})
    status = result.get("status", {})
    if status.get("code") != 0:
        raise RuntimeError(f"新浪接口错误: {status}")
    data = result.get("data", [])
    if not isinstance(data, list):
        raise RuntimeError("新浪接口 data 不是数组")
    return data


def upsert_minline(
    conn: sqlite3.Connection, table_name: str, ts_code: str, trade_date: str, data: list[dict]
) -> int:
    rows = []
    for r in data:
        rows.append(
            (
                ts_code,
                trade_date,
                str(r.get("m", "")),
                float(r.get("p")) if r.get("p") not in (None, "") else None,
                float(r.get("avg_p")) if r.get("avg_p") not in (None, "") else None,
                float(r.get("v")) if r.get("v") not in (None, "") else None,
                float(r.get("tot_v")) if r.get("tot_v") not in (None, "") else None,
                "sina",
            )
        )

    sql = f"""
    INSERT INTO {table_name} (
        ts_code, trade_date, minute_time, price, avg_price, volume, total_volume, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(ts_code, trade_date, minute_time) DO UPDATE SET
        price=excluded.price,
        avg_price=excluded.avg_price,
        volume=excluded.volume,
        total_volume=excluded.total_volume,
        source=excluded.source
    """
    cur = conn.cursor()
    cur.executemany(sql, rows)
    conn.commit()
    return len(rows)


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        raise SystemExit(f"数据库不存在: {db_path}")

    ts_code = args.ts_code.strip().upper()
    trade_date = resolve_trade_date(args.trade_date, args.token)
    sina_symbol = ts_to_sina_symbol(ts_code)

    data = fetch_sina_data(sina_symbol)
    if not data:
        raise SystemExit("接口未返回分钟线数据")

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)
        n = upsert_minline(conn, args.table_name, ts_code, trade_date, data)
        print(
            f"入库完成: ts_code={ts_code}, trade_date={trade_date}, rows={n}, table={args.table_name}"
        )
        publish_app_event(
            event="minline_update",
            payload={
                "ts_code": ts_code,
                "trade_date": trade_date,
                "rows": int(n),
                "table": args.table_name,
                "mode": "single",
            },
            producer="fetch_sina_minline_one.py",
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
