#!/usr/bin/env python3
"""
批量回填所有群聊最近 N 天聊天记录，并为超过 N 天无发言的群聊打标。

设计原则：
- 优先新建脚本，尽量不改现有定时抓群聊列表/单群聊天记录脚本
- 按“群聊 x 单日”逐天抓取，避免区间抓取时消息日期写错
- 若最近 N 天全部抓取成功且无任何原始消息，则标记该群聊后续跳过实时监控/入库

示例：
  python3 /home/zanbo/zanbotest/backfill_wechat_chatlogs_30d.py
  python3 /home/zanbo/zanbotest/backfill_wechat_chatlogs_30d.py --days 30 --room-limit 10
  python3 /home/zanbo/zanbotest/backfill_wechat_chatlogs_30d.py --only-room "Vito吃瓜3.0"
  python3 /home/zanbo/zanbotest/backfill_wechat_chatlogs_30d.py --include-skipped
"""

from __future__ import annotations

import argparse
import db_compat as sqlite3
import time
import urllib.error
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fetch_wechat_chatlog_clean_to_db import (
    DEFAULT_BASE_URL as DEFAULT_CHATLOG_BASE_URL,
    DEFAULT_TABLE_NAME as DEFAULT_CHATLOG_TABLE,
    HEADER_RE,
    build_request_url,
    clean_content_lines,
    ensure_table as ensure_chatlog_table,
    fetch_chatlog_text,
    parse_chatlog_text,
    split_blocks,
)


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_CHATROOM_TABLE = "chatroom_list_items"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量回填所有群聊最近 N 天聊天记录并标记沉默群聊")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--chatroom-table", default=DEFAULT_CHATROOM_TABLE, help="群聊列表表名")
    parser.add_argument("--chatlog-table", default=DEFAULT_CHATLOG_TABLE, help="聊天记录表名")
    parser.add_argument("--base-url", default=DEFAULT_CHATLOG_BASE_URL, help="聊天记录 API 地址")
    parser.add_argument("--days", type=int, default=30, help="回填最近多少天，默认 30")
    parser.add_argument(
        "--silence-threshold-days",
        type=int,
        default=30,
        help="连续多少天无消息才标记为跳过实时监控，默认 30",
    )
    parser.add_argument("--timeout-seconds", type=int, default=20, help="单次 HTTP 超时秒数")
    parser.add_argument("--pause-seconds", type=float, default=0.05, help="每次请求之间暂停秒数")
    parser.add_argument("--room-limit", type=int, default=0, help="只处理前 N 个群聊，0 表示全部")
    parser.add_argument("--only-room", default="", help="只处理指定群聊名（优先匹配 remark，再匹配 nick_name，再匹配 room_id）")
    parser.add_argument("--include-skipped", action="store_true", help="包含已标记为跳过实时监控的群聊")
    parser.add_argument("--verbose", action="store_true", help="输出每个日期的抓取详情")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def daterange_days(days: int) -> list[str]:
    end_day = today_utc()
    start_day = end_day - timedelta(days=max(days - 1, 0))
    values = []
    cur = start_day
    while cur <= end_day:
        values.append(cur.isoformat())
        cur += timedelta(days=1)
    return values


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row[1]) for row in rows}


def ensure_chatroom_columns(conn: sqlite3.Connection, table_name: str) -> None:
    expected_columns: dict[str, str] = {
        "skip_realtime_monitor": "INTEGER DEFAULT 0",
        "skip_realtime_reason": "TEXT",
        "skip_realtime_marked_at": "TEXT",
        "last_message_date": "TEXT",
        "last_chatlog_backfill_at": "TEXT",
        "last_chatlog_backfill_status": "TEXT",
        "last_30d_raw_message_count": "INTEGER DEFAULT 0",
        "last_30d_clean_message_count": "INTEGER DEFAULT 0",
        "last_30d_fetch_fail_count": "INTEGER DEFAULT 0",
        "silent_candidate_runs": "INTEGER DEFAULT 0",
        "silent_candidate_since": "TEXT",
    }
    existing = table_columns(conn, table_name)
    for column_name, column_type in expected_columns.items():
        if column_name not in existing:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_skip_realtime_monitor ON {table_name}(skip_realtime_monitor)"
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_last_message_date ON {table_name}(last_message_date)"
    )
    conn.commit()


def choose_talker_name(row: sqlite3.Row) -> str:
    for key in ("remark", "nick_name", "room_id"):
        value = str(row[key] or "").strip()
        if value:
            return value
    return ""


def count_raw_message_blocks(raw_text: str) -> int:
    total = 0
    for block in split_blocks(raw_text):
        lines = clean_content_lines(block.splitlines())
        if len(lines) < 2:
            continue
        if HEADER_RE.match(lines[0].strip()):
            total += 1
    return total


def replace_day_rows(
    conn: sqlite3.Connection,
    table_name: str,
    talker: str,
    day_text: str,
    items: list[dict],
) -> int:
    conn.execute(
        f"DELETE FROM {table_name} WHERE talker = ? AND query_date_start = ? AND query_date_end = ?",
        (talker, day_text, day_text),
    )
    if items:
        conn.executemany(
            f"""
            INSERT INTO {table_name} (
                talker, query_date_start, query_date_end, message_date, message_time,
                sender_name, sender_id, message_key, message_type, content, content_clean, is_quote,
                quote_sender_name, quote_sender_id, quote_time_text, quote_content,
                raw_block, source_url, fetched_at, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(message_key) DO UPDATE SET
                query_date_start=excluded.query_date_start,
                query_date_end=excluded.query_date_end,
                message_type=excluded.message_type,
                content=excluded.content,
                is_quote=excluded.is_quote,
                quote_sender_name=excluded.quote_sender_name,
                quote_sender_id=excluded.quote_sender_id,
                quote_time_text=excluded.quote_time_text,
                quote_content=excluded.quote_content,
                raw_block=excluded.raw_block,
                source_url=excluded.source_url,
                fetched_at=excluded.fetched_at,
                update_time=excluded.update_time
            """,
            [
                (
                    item["talker"],
                    item["query_date_start"],
                    item["query_date_end"],
                    item["message_date"],
                    item["message_time"],
                    item["sender_name"],
                    item["sender_id"],
                    item["message_key"],
                    item["message_type"],
                    item["content"],
                    item["content_clean"],
                    item["is_quote"],
                    item["quote_sender_name"],
                    item["quote_sender_id"],
                    item["quote_time_text"],
                    item["quote_content"],
                    item["raw_block"],
                    item["source_url"],
                    item["fetched_at"],
                    item["update_time"],
                )
                for item in items
            ],
        )
    conn.commit()
    return len(items)


def load_rooms(
    conn: sqlite3.Connection,
    table_name: str,
    only_room: str,
    include_skipped: bool,
    room_limit: int,
) -> list[sqlite3.Row]:
    where_parts = []
    params: list[object] = []
    if only_room:
        where_parts.append("(remark = ? OR nick_name = ? OR room_id = ?)")
        params.extend([only_room, only_room, only_room])
    if not include_skipped:
        where_parts.append("COALESCE(skip_realtime_monitor, 0) = 0")
    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
    limit_sql = f" LIMIT {int(room_limit)}" if room_limit and room_limit > 0 else ""
    sql = f"""
        SELECT room_id, remark, nick_name, owner, user_count, skip_realtime_monitor
        FROM {table_name}
        {where_sql}
        ORDER BY COALESCE(remark, ''), COALESCE(nick_name, ''), room_id
        {limit_sql}
    """
    return conn.execute(sql, params).fetchall()


def update_room_status(
    conn: sqlite3.Connection,
    table_name: str,
    room_id: str,
    *,
    last_message_date: str,
    status: str,
    raw_count: int,
    clean_count: int,
    fail_count: int,
    mark_skip: bool,
    skip_reason: str,
    silent_candidate_runs: int,
    silent_candidate_since: str | None,
) -> None:
    now = utc_now()
    if mark_skip:
        conn.execute(
            f"""
            UPDATE {table_name}
            SET last_message_date = ?,
                last_chatlog_backfill_at = ?,
                last_chatlog_backfill_status = ?,
                last_30d_raw_message_count = ?,
                last_30d_clean_message_count = ?,
                last_30d_fetch_fail_count = ?,
                skip_realtime_monitor = 1,
                skip_realtime_reason = ?,
                skip_realtime_marked_at = COALESCE(skip_realtime_marked_at, ?),
                silent_candidate_runs = ?,
                silent_candidate_since = ?
            WHERE room_id = ?
            """,
            (
                last_message_date,
                now,
                status,
                raw_count,
                clean_count,
                fail_count,
                skip_reason,
                now,
                silent_candidate_runs,
                silent_candidate_since,
                room_id,
            ),
        )
    else:
        conn.execute(
            f"""
            UPDATE {table_name}
            SET last_message_date = ?,
                last_chatlog_backfill_at = ?,
                last_chatlog_backfill_status = ?,
                last_30d_raw_message_count = ?,
                last_30d_clean_message_count = ?,
                last_30d_fetch_fail_count = ?,
                silent_candidate_runs = ?,
                silent_candidate_since = ?,
                skip_realtime_monitor = CASE
                    WHEN skip_realtime_reason = 'silent_over_30_days' THEN 0
                    ELSE COALESCE(skip_realtime_monitor, 0)
                END,
                skip_realtime_reason = CASE
                    WHEN skip_realtime_reason = 'silent_over_30_days' THEN NULL
                    ELSE skip_realtime_reason
                END,
                skip_realtime_marked_at = CASE
                    WHEN skip_realtime_reason = 'silent_over_30_days' THEN NULL
                    ELSE skip_realtime_marked_at
                END
            WHERE room_id = ?
            """,
            (
                last_message_date,
                now,
                status,
                raw_count,
                clean_count,
                fail_count,
                silent_candidate_runs,
                silent_candidate_since,
                room_id,
            ),
        )
    conn.commit()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path)
    days_list = daterange_days(max(args.days, 1))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_chatlog_table(conn, args.chatlog_table)
        ensure_chatroom_columns(conn, args.chatroom_table)
        rooms = load_rooms(
            conn,
            args.chatroom_table,
            only_room=args.only_room.strip(),
            include_skipped=args.include_skipped,
            room_limit=args.room_limit,
        )
        if not rooms:
            print("没有匹配到需要处理的群聊。")
            return 0

        print(
            f"准备处理群聊数={len(rooms)} days={len(days_list)} "
            f"date_range={days_list[0]}~{days_list[-1]}"
        )

        summary = {
            "ok": 0,
            "partial": 0,
            "error": 0,
            "marked_skip": 0,
            "rooms": 0,
            "raw_count": 0,
            "clean_count": 0,
        }

        for idx, room_row in enumerate(rooms, start=1):
            talker = choose_talker_name(room_row)
            room_id = str(room_row["room_id"] or "").strip()
            room_state = conn.execute(
                f"""
                SELECT
                    COALESCE(skip_realtime_monitor, 0),
                    COALESCE(skip_realtime_reason, ''),
                    COALESCE(silent_candidate_runs, 0),
                    silent_candidate_since
                FROM {args.chatroom_table}
                WHERE room_id = ?
                """,
                (room_id,),
            ).fetchone()
            print(f"[{idx}/{len(rooms)}] {talker} ({room_id})")

            raw_count = 0
            clean_count = 0
            fail_count = 0
            last_message_date = ""

            for day_text in days_list:
                url = build_request_url(args.base_url, day_text, day_text, talker)
                try:
                    raw_text = fetch_chatlog_text(url, timeout_seconds=args.timeout_seconds)
                    day_raw_count = count_raw_message_blocks(raw_text)
                    day_items = parse_chatlog_text(
                        raw_text,
                        talker=talker,
                        start_date=day_text,
                        end_date=day_text,
                        source_url=url,
                    )
                    replace_day_rows(conn, args.chatlog_table, talker, day_text, day_items)
                    raw_count += day_raw_count
                    clean_count += len(day_items)
                    if day_raw_count > 0:
                        last_message_date = day_text
                    if args.verbose:
                        print(f"    {day_text}: raw={day_raw_count} clean={len(day_items)}")
                except urllib.error.URLError as exc:
                    fail_count += 1
                    print(f"    {day_text}: fetch_failed -> {exc}")
                except Exception as exc:
                    fail_count += 1
                    print(f"    {day_text}: unexpected_error -> {exc}")
                if args.pause_seconds > 0:
                    time.sleep(args.pause_seconds)

            if fail_count == 0:
                status = "ok"
            elif fail_count < len(days_list):
                status = "partial"
            else:
                status = "error"

            current_candidate_runs = int(room_state[2] or 0) if room_state else 0
            current_candidate_since = room_state[3] if room_state else None

            eligible_for_silence_check = (
                fail_count == 0
                and raw_count == 0
                and args.days >= args.silence_threshold_days
            )
            if eligible_for_silence_check:
                silent_candidate_runs = current_candidate_runs + 1
                silent_candidate_since = current_candidate_since or utc_now()
                mark_skip = silent_candidate_runs >= 2
                if not mark_skip and status == "ok":
                    status = "silent_candidate"
            else:
                silent_candidate_runs = 0
                silent_candidate_since = None
                mark_skip = False

            skip_reason = f"silent_over_{args.silence_threshold_days}_days"
            update_room_status(
                conn,
                args.chatroom_table,
                room_id,
                last_message_date=last_message_date,
                status=status,
                raw_count=raw_count,
                clean_count=clean_count,
                fail_count=fail_count,
                mark_skip=mark_skip,
                skip_reason=skip_reason,
                silent_candidate_runs=silent_candidate_runs,
                silent_candidate_since=silent_candidate_since,
            )

            summary["rooms"] += 1
            summary["raw_count"] += raw_count
            summary["clean_count"] += clean_count
            summary[status] = summary.get(status, 0) + 1
            if mark_skip:
                summary["marked_skip"] += 1

            if mark_skip:
                flag_text = f" skip=1({skip_reason})"
            elif status == "silent_candidate":
                flag_text = f" silent_candidate_runs={silent_candidate_runs}"
            else:
                flag_text = ""
            print(
                f"  done status={status} raw={raw_count} clean={clean_count} "
                f"fail={fail_count} last_message_date={last_message_date or '-'}{flag_text}"
            )
    finally:
        conn.close()

    print(
        "SUMMARY "
        f"rooms={summary['rooms']} ok={summary.get('ok', 0)} partial={summary.get('partial', 0)} "
        f"error={summary.get('error', 0)} silent_candidate={summary.get('silent_candidate', 0)} "
        f"marked_skip={summary['marked_skip']} "
        f"raw={summary['raw_count']} clean={summary['clean_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
