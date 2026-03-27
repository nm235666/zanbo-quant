#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import db_compat as sqlite3

LOCAL_DEPS = Path(__file__).resolve().parent / ".deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import pandas as pd
import akshare as ak


DEFAULT_SPECS = [
    {
        "api": "macro_china_cpi_yearly",
        "freq": "M",
        "period_col": "日期",
        "publish_col": "日期",
        "item_col": "商品",
        "metrics": [
            ("今值", "current", "pct"),
            ("预测值", "forecast", "pct"),
            ("前值", "previous", "pct"),
        ],
    },
    {
        "api": "macro_china_ppi_yearly",
        "freq": "M",
        "period_col": "日期",
        "publish_col": "日期",
        "item_col": "商品",
        "metrics": [
            ("今值", "current", "pct"),
            ("预测值", "forecast", "pct"),
            ("前值", "previous", "pct"),
        ],
    },
    {
        "api": "macro_china_gdp_yearly",
        "freq": "Q",
        "period_col": "日期",
        "publish_col": "日期",
        "item_col": "商品",
        "metrics": [
            ("今值", "current", "pct"),
            ("预测值", "forecast", "pct"),
            ("前值", "previous", "pct"),
        ],
    },
    {
        "api": "macro_china_m2_yearly",
        "freq": "M",
        "period_col": "日期",
        "publish_col": "日期",
        "item_col": "商品",
        "metrics": [
            ("今值", "current", "pct"),
            ("预测值", "forecast", "pct"),
            ("前值", "previous", "pct"),
        ],
    },
    {
        "api": "macro_china_pmi_yearly",
        "freq": "M",
        "period_col": "日期",
        "publish_col": "日期",
        "item_col": "商品",
        "metrics": [
            ("今值", "current", "index"),
            ("预测值", "forecast", "index"),
            ("前值", "previous", "index"),
        ],
    },
    {
        "api": "macro_china_shrzgm",
        "freq": "M",
        "period_col": "月份",
        "publish_col": "",
        "item_col": "",
        "metrics": [
            ("社会融资规模增量", "social_financing_increment", "cny_100m"),
            ("其中-人民币贷款", "rmb_loans", "cny_100m"),
            ("其中-委托贷款外币贷款", "entrusted_foreign_loans", "cny_100m"),
            ("其中-委托贷款", "entrusted_loans", "cny_100m"),
            ("其中-信托贷款", "trust_loans", "cny_100m"),
            ("其中-未贴现银行承兑汇票", "undiscounted_bank_acceptance", "cny_100m"),
            ("其中-企业债券", "corporate_bonds", "cny_100m"),
            ("其中-非金融企业境内股票融资", "equity_financing", "cny_100m"),
        ],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 AKShare 回填宏观数据到 macro_series")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--table-name", default="macro_series", help="目标表名")
    parser.add_argument(
        "--apis",
        default=",".join(spec["api"] for spec in DEFAULT_SPECS),
        help="要抓取的 AKShare 宏观接口，逗号分隔",
    )
    parser.add_argument("--max-apis", type=int, default=0, help="最多处理多少个接口，0=全部")
    parser.add_argument("--retry", type=int, default=2, help="单接口失败重试次数")
    parser.add_argument("--backoff", type=float, default=1.0, help="失败后的指数退避基数秒")
    parser.add_argument("--pause", type=float, default=0.2, help="每个接口之间暂停秒数")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            indicator_code TEXT NOT NULL,
            indicator_name TEXT,
            freq TEXT NOT NULL,
            period TEXT NOT NULL,
            value REAL,
            unit TEXT,
            source TEXT,
            publish_date TEXT,
            update_time TEXT,
            PRIMARY KEY (indicator_code, freq, period)
        )
        """
    )
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_period ON {table_name}(period)")
    conn.commit()


def safe_float(value):
    try:
        if value is None:
            return None
        num = float(value)
        if math.isnan(num):
            return None
        return num
    except Exception:
        return None


def normalize_period(value, freq: str) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        d = value.date()
    elif isinstance(value, date):
        d = value
    else:
        text = str(value).strip()
        if not text:
            return ""
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) == 8:
            if freq == "Q":
                month = int(digits[4:6])
                quarter = (month - 1) // 3 + 1
                return f"{digits[:4]}Q{quarter}"
            if freq == "M":
                return digits[:6]
            return digits
        if len(digits) == 6:
            return digits if freq == "M" else digits + "01"
        return text
    if freq == "Q":
        quarter = (d.month - 1) // 3 + 1
        return f"{d.year}Q{quarter}"
    if freq == "M":
        return d.strftime("%Y%m")
    return d.strftime("%Y%m%d")


def normalize_publish_date(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    text = str(value).strip()
    if not text:
        return ""
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 8:
        return digits[:8]
    if len(digits) == 6:
        return digits + "01"
    return text


def build_rows_from_spec(spec: dict, df: pd.DataFrame) -> list[tuple]:
    rows: list[tuple] = []
    if df is None or df.empty:
        return rows

    period_col = spec["period_col"]
    publish_col = spec.get("publish_col", "")
    item_col = spec.get("item_col", "")
    update_time = now_utc_str()

    for _, row in df.iterrows():
        period = normalize_period(row.get(period_col), spec["freq"])
        if not period:
            continue
        publish_date = normalize_publish_date(row.get(publish_col)) if publish_col else ""
        item_name = str(row.get(item_col) or "").strip() if item_col else spec["api"]

        for raw_col, metric_code, unit in spec["metrics"]:
            value = safe_float(row.get(raw_col))
            if value is None:
                continue
            indicator_code = f"{spec['api']}.{metric_code}"
            indicator_name = f"{item_name}-{raw_col}" if item_name else raw_col
            rows.append(
                (
                    indicator_code,
                    indicator_name[:200],
                    spec["freq"],
                    period,
                    value,
                    unit,
                    f"akshare.{spec['api']}",
                    publish_date,
                    update_time,
                )
            )
    return rows


def upsert_rows(conn: sqlite3.Connection, table_name: str, rows: list[tuple]) -> int:
    if not rows:
        return 0
    conn.executemany(
        f"""
        INSERT INTO {table_name} (
            indicator_code, indicator_name, freq, period, value, unit, source, publish_date, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(indicator_code, freq, period) DO UPDATE SET
            indicator_name=excluded.indicator_name,
            value=excluded.value,
            unit=excluded.unit,
            source=excluded.source,
            publish_date=CASE
                WHEN COALESCE(excluded.publish_date, '') <> '' THEN excluded.publish_date
                ELSE {table_name}.publish_date
            END,
            update_time=excluded.update_time
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def fetch_with_retry(api_name: str, retry: int, backoff: float) -> pd.DataFrame:
    last_exc = None
    fn = getattr(ak, api_name)
    for attempt in range(retry + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retry:
                time.sleep(backoff * (2**attempt))
    raise last_exc  # type: ignore[misc]


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    spec_map = {spec["api"]: spec for spec in DEFAULT_SPECS}
    api_names = [x.strip() for x in args.apis.split(",") if x.strip()]
    if args.max_apis > 0:
        api_names = api_names[: args.max_apis]
    if not api_names:
        print("没有可处理的接口。")
        return 1

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)
        total_written = 0
        success = 0
        failed = 0

        for idx, api_name in enumerate(api_names, start=1):
            spec = spec_map.get(api_name)
            if not spec:
                print(f"[{idx}/{len(api_names)}] {api_name}: 未配置，跳过")
                continue
            try:
                df = fetch_with_retry(api_name, retry=args.retry, backoff=args.backoff)
                rows = build_rows_from_spec(spec, df)
                written = upsert_rows(conn, args.table_name, rows)
                total_written += written
                success += 1
                print(f"[{idx}/{len(api_names)}] {api_name}: raw_rows={0 if df is None else len(df)} metric_rows={written}")
            except Exception as exc:  # noqa: BLE001
                failed += 1
                print(f"[{idx}/{len(api_names)}] {api_name}: 失败 -> {exc}")
            if args.pause > 0:
                time.sleep(args.pause)

        total_rows = conn.execute(f"SELECT COUNT(*) FROM {args.table_name}").fetchone()[0]
        print(f"完成: success={success}, failed={failed}, written={total_written}, table_rows={total_rows}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
