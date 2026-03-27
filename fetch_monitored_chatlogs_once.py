#!/usr/bin/env python3
from __future__ import annotations

import argparse
import db_compat as sqlite3
import time
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

from realtime_streams import publish_app_event
from fetch_wechat_chatlog_clean_to_db import (
    DEFAULT_BASE_URL,
    HEADER_RE,
    build_request_url,
    clean_content_lines,
    ensure_table as ensure_chatlog_table,
    fetch_chatlog_text,
    parse_chatlog_text,
    split_blocks,
)


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_CHATLOG_TABLE = "wechat_chatlog_clean_items"
DEFAULT_CHATROOM_TABLE = "chatroom_list_items"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取当前监控中的群聊聊天记录并入库")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="聊天记录 API 地址")
    parser.add_argument("--chatlog-table", default=DEFAULT_CHATLOG_TABLE, help="聊天记录表名")
    parser.add_argument("--chatroom-table", default=DEFAULT_CHATROOM_TABLE, help="群聊表名")
    parser.add_argument("--date", default="", help="抓取日期，默认今天（UTC）")
    parser.add_argument("--yesterday-and-today", action="store_true", help="抓取昨天和今天两个日期")
    parser.add_argument("--only-room", default="", help="只抓取指定群（remark/nick_name/room_id/talker）")
    parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 个唯一 talker，0 表示全部")
    parser.add_argument("--sleep", type=float, default=0.05, help="每个群之间暂停秒数")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="HTTP 超时秒数")
    parser.add_argument("--verbose", action="store_true", help="打印更多日志")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_text() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def yesterday_text() -> str:
    return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()


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


def fetch_monitored_talkers(
    conn: sqlite3.Connection,
    table_name: str,
    limit: int,
    only_room: str,
) -> list[dict]:
    rows = conn.execute(
        f"""
        SELECT room_id, remark, nick_name
        FROM {table_name}
        WHERE COALESCE(skip_realtime_monitor, 0) = 0
        ORDER BY COALESCE(remark, ''), COALESCE(nick_name, ''), room_id
        """
    ).fetchall()
    grouped: dict[str, dict] = {}
    target = only_room.strip()
    for row in rows:
        talker = choose_talker_name(row)
        if not talker:
            continue
        room_id = str(row["room_id"] or "").strip()
        remark = str(row["remark"] or "").strip()
        nick_name = str(row["nick_name"] or "").strip()
        if target and target not in {talker, room_id, remark, nick_name}:
            continue
        item = grouped.setdefault(talker, {"talker": talker, "room_ids": []})
        item["room_ids"].append(room_id)
    values = list(grouped.values())
    if limit and limit > 0:
        values = values[:limit]
    return values


def update_room_statuses(
    conn: sqlite3.Connection,
    table_name: str,
    room_ids: list[str],
    *,
    status: str,
    latest_message_date: str,
) -> None:
    if not room_ids:
        return
    placeholders = ",".join(["?"] * len(room_ids))
    now = utc_now()
    params: list[object] = [latest_message_date, now, status, *room_ids]
    conn.execute(
        f"""
        UPDATE {table_name}
        SET
            last_message_date = CASE
                WHEN ? <> '' THEN ?
                ELSE last_message_date
            END,
            last_chatlog_backfill_at = ?,
            last_chatlog_backfill_status = ?,
            update_time = ?
        WHERE room_id IN ({placeholders})
        """,
        [
            latest_message_date,
            latest_message_date,
            now,
            status,
            now,
            *room_ids,
        ],
    )
    conn.commit()


def main() -> int:
    args = parse_args()
    if args.yesterday_and_today:
        target_dates = [yesterday_text(), today_text()]
    else:
        target_dates = [(args.date or "").strip() or today_text()]
    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_chatlog_table(conn, args.chatlog_table)
        talkers = fetch_monitored_talkers(conn, args.chatroom_table, args.limit, args.only_room)
        if not talkers:
            print("没有需要抓取的监控中群聊。")
            return 0

        print(f"dates={','.join(target_dates)} monitored_talkers={len(talkers)}")
        success = 0
        failed = 0
        total_clean = 0
        for index, item in enumerate(talkers, start=1):
            talker = item["talker"]
            room_ids = item["room_ids"]
            room_success = True
            room_total_clean = 0
            latest_message_date = ""
            for target_date in target_dates:
                url = build_request_url(args.base_url, target_date, target_date, talker)
                try:
                    raw_text = fetch_chatlog_text(url, timeout_seconds=args.timeout_seconds)
                    raw_count = count_raw_message_blocks(raw_text)
                    parsed_items = parse_chatlog_text(
                        raw_text,
                        talker=talker,
                        start_date=target_date,
                        end_date=target_date,
                        source_url=url,
                    )
                    clean_count = replace_day_rows(conn, args.chatlog_table, talker, target_date, parsed_items)
                    room_total_clean += clean_count
                    if raw_count > 0:
                        latest_message_date = target_date
                    if args.verbose:
                        print(
                            f"[{index}/{len(talkers)}] {talker} {target_date}: ok raw={raw_count} clean={clean_count} rooms={len(room_ids)}"
                        )
                except urllib.error.URLError as exc:
                    room_success = False
                    update_room_statuses(
                        conn,
                        args.chatroom_table,
                        room_ids,
                        status=f"error: {exc}",
                        latest_message_date="",
                    )
                    print(f"[{index}/{len(talkers)}] {talker} {target_date}: fetch_failed -> {exc}")
                    break
                except Exception as exc:
                    room_success = False
                    update_room_statuses(
                        conn,
                        args.chatroom_table,
                        room_ids,
                        status=f"error: {exc}",
                        latest_message_date="",
                    )
                    print(f"[{index}/{len(talkers)}] {talker} {target_date}: unexpected_error -> {exc}")
                    break
            if room_success:
                update_room_statuses(
                    conn,
                    args.chatroom_table,
                    room_ids,
                    status="ok",
                    latest_message_date=latest_message_date,
                )
                success += 1
                total_clean += room_total_clean
            else:
                failed += 1
            if args.sleep > 0:
                time.sleep(args.sleep)
    finally:
        conn.close()

    print(f"done success={success} failed={failed} clean_rows={total_clean}")
    publish_app_event(
        event="chatlog_monitor_update",
        payload={
            "success_rooms": int(success),
            "failed_rooms": int(failed),
            "clean_rows": int(total_clean),
            "dates": target_dates,
        },
        producer="fetch_monitored_chatlogs_once.py",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
