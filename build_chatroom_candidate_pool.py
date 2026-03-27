#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import db_compat as sqlite3
from datetime import datetime, timezone
from pathlib import Path

from realtime_streams import publish_app_event

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_SOURCE_TABLE = "chatroom_investment_analysis"
DEFAULT_TARGET_TABLE = "chatroom_stock_candidate_pool"


def normalize_text(value: str) -> str:
    return str(value or "").strip().upper()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把群聊投资倾向分析汇总成股票/主题候选池")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--source-table", default=DEFAULT_SOURCE_TABLE, help="来源表名")
    parser.add_argument("--target-table", default=DEFAULT_TARGET_TABLE, help="目标表名")
    parser.add_argument("--min-room-count", type=int, default=1, help="至少被多少个群提到才入池")
    parser.add_argument("--only-bias", default="", help="只汇总指定方向：看多 或 看空")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            candidate_type TEXT,
            bullish_room_count INTEGER DEFAULT 0,
            bearish_room_count INTEGER DEFAULT 0,
            net_score INTEGER DEFAULT 0,
            dominant_bias TEXT,
            mention_count INTEGER DEFAULT 0,
            room_count INTEGER DEFAULT 0,
            latest_analysis_date TEXT,
            sample_reasons_json TEXT,
            source_room_ids_json TEXT,
            source_talkers_json TEXT,
            created_at TEXT,
            update_time TEXT
        )
        """
    )
    conn.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS uq_{table_name}_candidate_name ON {table_name}(candidate_name)"
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_dominant_bias ON {table_name}(dominant_bias)"
    )
    conn.commit()


def load_stock_aliases(conn: sqlite3.Connection) -> set[str]:
    aliases: set[str] = set()
    table_exists = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='stock_codes'"
    ).fetchone()[0]
    if not table_exists:
        return aliases

    for row in conn.execute(
        """
        SELECT ts_code, symbol, name
        FROM stock_codes
        WHERE COALESCE(ts_code, '') <> ''
           OR COALESCE(symbol, '') <> ''
           OR COALESCE(name, '') <> ''
        """
    ):
        for value in row:
            text = str(value or "").strip()
            if text:
                aliases.add(normalize_text(text))
    return aliases


def classify_candidate_type(name: str, stock_aliases: set[str]) -> str:
    text = str(name or "").strip()
    if not text:
        return "未知"
    if normalize_text(text) in stock_aliases:
        return "股票"
    if text.endswith((".SZ", ".SH", ".BJ")):
        return "股票"
    keywords = [
        "ETF", "原油", "黄金", "白银", "铜", "航运", "算力", "科技股", "银行股", "储能",
        "芯片", "电力", "液冷", "AI", "LNG", "LPG", "A股大盘", "恒生科技"
    ]
    for kw in keywords:
        if kw in text:
            return "主题"
    return "标的"


def load_latest_rows(conn: sqlite3.Connection, table_name: str) -> list[sqlite3.Row]:
    sql = f"""
    SELECT a.*
    FROM {table_name} a
    JOIN (
        SELECT room_id, MAX(update_time) AS max_update_time
        FROM {table_name}
        GROUP BY room_id
    ) latest
      ON latest.room_id = a.room_id AND latest.max_update_time = a.update_time
    ORDER BY a.update_time DESC, a.id DESC
    """
    return conn.execute(sql).fetchall()


def upsert_candidate_rows(conn: sqlite3.Connection, table_name: str, rows: list[dict]) -> int:
    now = now_utc_str()
    conn.execute(f"DELETE FROM {table_name}")
    conn.executemany(
        f"""
        INSERT INTO {table_name} (
            candidate_name, candidate_type, bullish_room_count, bearish_room_count, net_score,
            dominant_bias, mention_count, room_count, latest_analysis_date, sample_reasons_json,
            source_room_ids_json, source_talkers_json, created_at, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["candidate_name"],
                row["candidate_type"],
                row["bullish_room_count"],
                row["bearish_room_count"],
                row["net_score"],
                row["dominant_bias"],
                row["mention_count"],
                row["room_count"],
                row["latest_analysis_date"],
                row["sample_reasons_json"],
                row["source_room_ids_json"],
                row["source_talkers_json"],
                now,
                now,
            )
            for row in rows
        ],
    )
    conn.commit()
    return len(rows)


def main() -> int:
    args = parse_args()
    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_table(conn, args.target_table)
        stock_aliases = load_stock_aliases(conn)
        table_exists = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
            (args.source_table,),
        ).fetchone()[0]
        if not table_exists:
            print(f"来源表不存在: {args.source_table}")
            return 1

        latest_rows = load_latest_rows(conn, args.source_table)
        pool: dict[str, dict] = {}
        for row in latest_rows:
            try:
                targets = json.loads(row["targets_json"] or "[]")
            except Exception:
                targets = []
            if not isinstance(targets, list):
                continue

            seen_in_room: set[tuple[str, str]] = set()
            for item in targets:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name") or "").strip()
                bias = str(item.get("bias") or "").strip()
                reason = str(item.get("reason") or "").strip()
                if not name or bias not in {"看多", "看空"}:
                    continue
                if args.only_bias.strip() and bias != args.only_bias.strip():
                    continue

                bucket = pool.setdefault(
                    name,
                    {
                        "candidate_name": name,
                        "candidate_type": classify_candidate_type(name, stock_aliases),
                        "bullish_room_ids": set(),
                        "bearish_room_ids": set(),
                        "room_ids": set(),
                        "talkers": set(),
                        "reasons": [],
                        "mention_count": 0,
                        "latest_analysis_date": str(row["analysis_date"] or ""),
                    },
                )
                bucket["mention_count"] += 1
                bucket["room_ids"].add(str(row["room_id"] or ""))
                bucket["talkers"].add(str(row["talker"] or ""))
                if reason and len(bucket["reasons"]) < 10:
                    bucket["reasons"].append({"bias": bias, "reason": reason, "talker": str(row["talker"] or "")})
                key = (str(row["room_id"] or ""), bias)
                if key not in seen_in_room:
                    if bias == "看多":
                        bucket["bullish_room_ids"].add(str(row["room_id"] or ""))
                    else:
                        bucket["bearish_room_ids"].add(str(row["room_id"] or ""))
                    seen_in_room.add(key)
                latest_date = str(row["analysis_date"] or "")
                if latest_date and latest_date > bucket["latest_analysis_date"]:
                    bucket["latest_analysis_date"] = latest_date

        final_rows: list[dict] = []
        for name, bucket in pool.items():
            bullish_room_count = len(bucket["bullish_room_ids"])
            bearish_room_count = len(bucket["bearish_room_ids"])
            room_count = len(bucket["room_ids"])
            if room_count < max(args.min_room_count, 1):
                continue
            net_score = bullish_room_count - bearish_room_count
            dominant_bias = "看多" if net_score >= 0 else "看空"
            final_rows.append(
                {
                    "candidate_name": name,
                    "candidate_type": bucket["candidate_type"],
                    "bullish_room_count": bullish_room_count,
                    "bearish_room_count": bearish_room_count,
                    "net_score": net_score,
                    "dominant_bias": dominant_bias,
                    "mention_count": bucket["mention_count"],
                    "room_count": room_count,
                    "latest_analysis_date": bucket["latest_analysis_date"],
                    "sample_reasons_json": json.dumps(bucket["reasons"][:6], ensure_ascii=False),
                    "source_room_ids_json": json.dumps(sorted(x for x in bucket["room_ids"] if x), ensure_ascii=False),
                    "source_talkers_json": json.dumps(sorted(x for x in bucket["talkers"] if x), ensure_ascii=False),
                }
            )

        final_rows.sort(
            key=lambda x: (
                -abs(int(x["net_score"])),
                -int(x["room_count"]),
                -int(x["mention_count"]),
                x["candidate_name"],
            )
        )
        affected = upsert_candidate_rows(conn, args.target_table, final_rows)
    finally:
        conn.close()

    print(f"source_rows={len(latest_rows)} candidates={affected}")
    publish_app_event(
        event="chatroom_candidate_pool_update",
        payload={
            "source_rows": int(len(latest_rows)),
            "candidates": int(affected),
            "target_table": args.target_table,
        },
        producer="build_chatroom_candidate_pool.py",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
