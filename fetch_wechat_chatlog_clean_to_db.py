#!/usr/bin/env python3
"""
抓取微信群聊天记录，清洗后入库。

特性：
- 支持单日或日期范围查询
- 先获取原始聊天文本，再做结构化清洗
- 过滤无效消息：图片、动画表情、视频、纯链接
- 识别引用格式消息，并标记/拆分引用字段

示例：
  python3 fetch_wechat_chatlog_clean_to_db.py --date 2026-03-02 --talker "Vito吃瓜3.0"
  python3 fetch_wechat_chatlog_clean_to_db.py --start-date 2026-03-02 --end-date 2026-03-04 --talker "Vito吃瓜3.0"
"""

from __future__ import annotations

import argparse
import hashlib
import re
import db_compat as sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_BASE_URL = "http://192.168.5.29:7030/api/v1/chatlog"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_TABLE_NAME = "wechat_chatlog_clean_items"

HEADER_RE = re.compile(
    r"^(?P<sender>.+?)(?:\((?P<sender_id>[^()]*)\))?\s+(?P<msg_time>\d{2}:\d{2}:\d{2})$"
)
QUOTE_HEADER_RE = re.compile(
    r"^(?P<sender>.+?)(?:\((?P<sender_id>[^()]*)\))?\s+(?P<quote_time>(?:\d{2}-\d{2}\s+)?\d{2}:\d{2}:\d{2})$"
)
INVALID_EXACT_PATTERNS = [
    re.compile(r"^!\[图片\]\(.*\)$"),
    re.compile(r"^!\[动画表情\]\(.*\)$"),
    re.compile(r"^!\[视频\]\(.*\)$"),
]
PURE_LINK_RE = re.compile(r"^(https?://\S+)$", re.I)
LINK_CARD_RE = re.compile(r"^\[链接\|.*\]$", re.I)
MARKDOWN_LINK_RE = re.compile(r"^\[[^\]]+\]\((https?://.+)\)$", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取微信群聊天记录并清洗入库")
    parser.add_argument("--talker", required=True, help="群聊名称，例如 Vito吃瓜3.0")
    parser.add_argument("--date", default="", help="单日 YYYY-MM-DD")
    parser.add_argument("--start-date", default="", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--end-date", default="", help="结束日期 YYYY-MM-DD")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="chatlog API 地址")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--table-name", default=DEFAULT_TABLE_NAME, help="目标表名")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="HTTP 超时秒数")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_time_param(args: argparse.Namespace) -> tuple[str, str]:
    if args.date:
        return args.date.strip(), args.date.strip()
    if args.start_date and args.end_date and args.start_date != args.end_date:
        return args.start_date.strip(), args.end_date.strip()
    if args.start_date:
        date_value = args.start_date.strip()
        return date_value, date_value
    raise SystemExit("请提供 --date，或同时提供 --start-date/--end-date")


def build_request_url(base_url: str, start_date: str, end_date: str, talker: str) -> str:
    time_param = start_date if start_date == end_date else f"{start_date}~{end_date}"
    query = urllib.parse.urlencode({"time": time_param, "talker": talker})
    return f"{base_url}?{query}"


def fetch_chatlog_text(url: str, timeout_seconds: int) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/plain,text/html,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talker TEXT NOT NULL,
            query_date_start TEXT NOT NULL,
            query_date_end TEXT NOT NULL,
            message_date TEXT,
            message_time TEXT,
            sender_name TEXT,
            sender_id TEXT,
            message_key TEXT,
            message_type TEXT,
            content TEXT,
            content_clean TEXT,
            is_quote INTEGER DEFAULT 0,
            quote_sender_name TEXT,
            quote_sender_id TEXT,
            quote_time_text TEXT,
            quote_content TEXT,
            raw_block TEXT,
            source_url TEXT,
            fetched_at TEXT,
            update_time TEXT
        )
        """
    )
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if "message_key" not in cols:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN message_key TEXT")
    conn.execute(f"DROP INDEX IF EXISTS uq_{table_name}_msg")
    conn.execute(
        f"""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_{table_name}_msg
        ON {table_name}(message_key)
        """
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_talker_date ON {table_name}(talker, message_date)"
    )
    conn.commit()


def split_blocks(text: str) -> list[str]:
    normalized = str(text or "").replace("\r\n", "\n").strip()
    if not normalized:
        return []
    return [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]


def clean_content_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        value = line.rstrip()
        if not value:
            continue
        cleaned.append(value)
    return cleaned


def classify_invalid_message(content: str) -> str | None:
    text = str(content or "").strip()
    if not text:
        return "empty"
    for pattern in INVALID_EXACT_PATTERNS:
        if pattern.match(text):
            return "media"
    if LINK_CARD_RE.match(text):
        return "link"
    if MARKDOWN_LINK_RE.match(text):
        return "link"
    if text.startswith("[链接|") and "](" in text and text.endswith(")"):
        return "link"
    if PURE_LINK_RE.match(text):
        return "link"
    if text.startswith("http://") or text.startswith("https://"):
        return "link"
    return None


def parse_quote(lines: list[str]) -> tuple[bool, dict]:
    if len(lines) < 3:
        return False, {}
    if not lines[0].startswith("> "):
        return False, {}

    quoted_lines = []
    remainder_start = 0
    for idx, line in enumerate(lines):
        if line.startswith("> "):
            quoted_lines.append(line[2:])
        else:
            remainder_start = idx
            break
    else:
        remainder_start = len(lines)

    if len(quoted_lines) < 2 or remainder_start >= len(lines):
        return False, {}

    quote_header = quoted_lines[0].strip()
    match = QUOTE_HEADER_RE.match(quote_header)
    if not match:
        return False, {}

    quote_content = "\n".join([x.strip() for x in quoted_lines[1:] if x.strip()]).strip()
    current_content = "\n".join([x.strip() for x in lines[remainder_start:] if x.strip()]).strip()
    if not current_content:
        return False, {}

    return True, {
        "quote_sender_name": (match.group("sender") or "").strip(),
        "quote_sender_id": (match.group("sender_id") or "").strip(),
        "quote_time_text": (match.group("quote_time") or "").strip(),
        "quote_content": quote_content,
        "current_content": current_content,
    }


def parse_block(block: str, talker: str, start_date: str, end_date: str, source_url: str) -> dict | None:
    lines = clean_content_lines(block.splitlines())
    if len(lines) < 2:
        return None

    header = lines[0].strip()
    header_match = HEADER_RE.match(header)
    if not header_match:
        return None

    sender_name = (header_match.group("sender") or "").strip()
    sender_id = (header_match.group("sender_id") or "").strip()
    message_time = (header_match.group("msg_time") or "").strip()
    content_lines = lines[1:]
    is_quote, quote_info = parse_quote(content_lines)

    if is_quote:
        content_clean = quote_info["current_content"]
        quote_content = quote_info["quote_content"]
        message_type = "quote"
    else:
        content_clean = "\n".join(content_lines).strip()
        quote_content = ""
        message_type = "system" if sender_name == "系统消息" else "text"

    invalid_reason = classify_invalid_message(content_clean)
    if invalid_reason:
        return None

    message_key = hashlib.sha256(
        "|".join(
            [
                talker,
                start_date,
                message_time,
                sender_name,
                sender_id,
                content_clean,
            ]
        ).encode("utf-8", errors="ignore")
    ).hexdigest()

    return {
        "talker": talker,
        "query_date_start": start_date,
        "query_date_end": end_date,
        "message_date": start_date,
        "message_time": message_time,
        "sender_name": sender_name,
        "sender_id": sender_id,
        "message_key": message_key,
        "message_type": message_type,
        "content": "\n".join(content_lines).strip(),
        "content_clean": content_clean,
        "is_quote": 1 if is_quote else 0,
        "quote_sender_name": quote_info.get("quote_sender_name", "") if is_quote else "",
        "quote_sender_id": quote_info.get("quote_sender_id", "") if is_quote else "",
        "quote_time_text": quote_info.get("quote_time_text", "") if is_quote else "",
        "quote_content": quote_content,
        "raw_block": block,
        "source_url": source_url,
        "fetched_at": utc_now(),
        "update_time": utc_now(),
    }


def parse_chatlog_text(text: str, talker: str, start_date: str, end_date: str, source_url: str) -> list[dict]:
    items = []
    for block in split_blocks(text):
        item = parse_block(block, talker=talker, start_date=start_date, end_date=end_date, source_url=source_url)
        if item:
            items.append(item)
    return items


def replace_rows_for_window(
    conn: sqlite3.Connection,
    table_name: str,
    talker: str,
    query_date_start: str,
    query_date_end: str,
    items: list[dict],
) -> int:
    if not items:
        return 0
    conn.execute(
        f"DELETE FROM {table_name} WHERE talker = ? AND query_date_start = ? AND query_date_end = ?",
        (talker, query_date_start, query_date_end),
    )
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


def main() -> int:
    args = parse_args()
    start_date, end_date = resolve_time_param(args)
    url = build_request_url(args.base_url, start_date, end_date, args.talker)
    raw_text = fetch_chatlog_text(url, timeout_seconds=args.timeout_seconds)
    items = parse_chatlog_text(raw_text, talker=args.talker, start_date=start_date, end_date=end_date, source_url=url)

    conn = sqlite3.connect(Path(args.db_path))
    try:
        ensure_table(conn, args.table_name)
        upserted = replace_rows_for_window(
            conn,
            args.table_name,
            talker=args.talker,
            query_date_start=start_date,
            query_date_end=end_date,
            items=items,
        )
        total = conn.execute(f"SELECT COUNT(*) FROM {args.table_name} WHERE talker = ?", (args.talker,)).fetchone()[0]
        quotes = conn.execute(
            f"SELECT COUNT(*) FROM {args.table_name} WHERE talker = ? AND is_quote = 1",
            (args.talker,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(f"url={url}")
    print(f"clean_items={len(items)} upserted={upserted} talker_total={total} quote_items={quotes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
