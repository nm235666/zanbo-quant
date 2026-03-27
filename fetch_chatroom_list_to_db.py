#!/usr/bin/env python3
"""
定时抓取群聊列表并写入 PostgreSQL 主库。

默认接口:
  http://192.168.5.29:7030/api/v1/chatroom

默认写入表:
  chatroom_list_items

示例:
  python3 fetch_chatroom_list_to_db.py --once
  python3 fetch_chatroom_list_to_db.py --interval-seconds 300
"""

from __future__ import annotations

import argparse
import csv
import io
import db_compat as sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from realtime_streams import publish_app_event

DEFAULT_URL = "http://192.168.5.29:7030/api/v1/chatroom"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_TABLE_NAME = "chatroom_list_items"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="定时抓取群聊列表并入库")
    parser.add_argument("--url", default=DEFAULT_URL, help="群聊列表接口地址")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--table-name", default=DEFAULT_TABLE_NAME, help="目标数据表名")
    parser.add_argument("--interval-seconds", type=int, default=300, help="轮询间隔秒数")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="HTTP 请求超时秒数")
    parser.add_argument("--once", action="store_true", help="只抓取一次")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            room_id TEXT PRIMARY KEY,
            remark TEXT,
            nick_name TEXT,
            owner TEXT,
            user_count INTEGER,
            source_url TEXT,
            raw_csv_row TEXT,
            first_seen_at TEXT,
            last_seen_at TEXT,
            update_time TEXT
        )
        """
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_owner ON {table_name}(owner)"
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_nick_name ON {table_name}(nick_name)"
    )
    conn.commit()


def fetch_csv_text(url: str, timeout_seconds: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/csv,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")


def parse_rows(csv_text: str) -> list[dict]:
    text = csv_text.strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    items = []
    for row in reader:
        room_id = (row.get("Name") or "").strip()
        if not room_id:
            continue
        user_count_raw = (row.get("UserCount") or "").strip()
        try:
            user_count = int(user_count_raw) if user_count_raw else None
        except ValueError:
            user_count = None
        items.append(
            {
                "room_id": room_id,
                "remark": (row.get("Remark") or "").strip(),
                "nick_name": (row.get("NickName") or "").strip(),
                "owner": (row.get("Owner") or "").strip(),
                "user_count": user_count,
                "raw_csv_row": ",".join(
                    [
                        row.get("Name") or "",
                        row.get("Remark") or "",
                        row.get("NickName") or "",
                        row.get("Owner") or "",
                        row.get("UserCount") or "",
                    ]
                ),
            }
        )
    return items


def upsert_rows(conn: sqlite3.Connection, table_name: str, rows: list[dict], source_url: str) -> int:
    if not rows:
        return 0
    now = utc_now()
    conn.executemany(
        f"""
        INSERT INTO {table_name} (
            room_id, remark, nick_name, owner, user_count, source_url,
            raw_csv_row, first_seen_at, last_seen_at, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(room_id) DO UPDATE SET
            remark=excluded.remark,
            nick_name=excluded.nick_name,
            owner=excluded.owner,
            user_count=excluded.user_count,
            source_url=excluded.source_url,
            raw_csv_row=excluded.raw_csv_row,
            last_seen_at=excluded.last_seen_at,
            update_time=excluded.update_time
        """,
        [
            (
                item["room_id"],
                item["remark"],
                item["nick_name"],
                item["owner"],
                item["user_count"],
                source_url,
                item["raw_csv_row"],
                now,
                now,
                now,
            )
            for item in rows
        ],
    )
    conn.commit()
    return len(rows)


def run_once(db_path: Path, table_name: str, url: str, timeout_seconds: int) -> int:
    csv_text = fetch_csv_text(url, timeout_seconds=timeout_seconds)
    rows = parse_rows(csv_text)
    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, table_name)
        affected = upsert_rows(conn, table_name, rows, source_url=url)
        total = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    finally:
        conn.close()
    print(f"fetched={len(rows)} upserted={affected} total_rows={total}")
    publish_app_event(
        event="chatroom_list_update",
        payload={
            "fetched": int(len(rows)),
            "upserted": int(affected),
            "total_rows": int(total),
            "table": table_name,
        },
        producer="fetch_chatroom_list_to_db.py",
    )
    return affected


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    while True:
        started = utc_now()
        try:
            run_once(
                db_path=db_path,
                table_name=args.table_name,
                url=args.url,
                timeout_seconds=args.timeout_seconds,
            )
            print(f"[{started}] ok")
        except urllib.error.URLError as exc:
            print(f"[{started}] fetch_failed: {exc}")
        except Exception as exc:
            print(f"[{started}] unexpected_error: {exc}")

        if args.once:
            break
        time.sleep(max(args.interval_seconds, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
