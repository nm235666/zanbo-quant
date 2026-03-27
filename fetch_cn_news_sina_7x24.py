#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import re
import db_compat as sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from realtime_streams import publish_news_batch

SOURCE = "cn_sina_7x24"
URL = "https://finance.sina.com.cn/7x24/"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

ITEM_RE = re.compile(
    r'<div\s+newsdata-id="(?P<id>\d+)"\s+newsdata-time="(?P<day>\d{8})">\s*'
    r"<div>(?P<clock>\d{2}:\d{2}:\d{2})</div>\s*"
    r'<a[^>]*href="(?P<link>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.S,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取新浪 7x24 国内财经新闻并入库")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--tag", default="0", help="新浪 7x24 tag 参数，默认 0")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP 超时秒数")
    parser.add_argument("--limit", type=int, default=100, help="本次最多入库条数")
    parser.add_argument("--dry-run", action="store_true", help="只抓取解析，不入库")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news_feed_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT,
            link TEXT,
            guid TEXT,
            summary TEXT,
            category TEXT,
            author TEXT,
            pub_date TEXT,
            fetched_at TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            UNIQUE(source, content_hash)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_news_source_pub_date ON news_feed_items(source, pub_date)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_fetched_at ON news_feed_items(fetched_at)")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uniq_news_source_hash ON news_feed_items(source, content_hash)"
    )
    conn.commit()


def to_utc_iso(day: str, clock: str) -> str:
    # 新浪页面时间是北京时间，转为 UTC 存储
    dt_cn = datetime.strptime(day + clock, "%Y%m%d%H:%M:%S").replace(
        tzinfo=timezone(timedelta(hours=8))
    )
    return dt_cn.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_items(page_html: str) -> list[dict]:
    out: list[dict] = []
    for m in ITEM_RE.finditer(page_html):
        news_id = m.group("id")
        day = m.group("day")
        clock = m.group("clock")
        link = m.group("link").strip()
        title_raw = m.group("title")
        title = html.unescape(re.sub(r"<[^>]+>", "", title_raw)).strip()
        if not title:
            continue
        guid = f"sina7x24_{news_id}"
        pub_date = to_utc_iso(day=day, clock=clock)
        out.append(
            {
                "source": SOURCE,
                "title": title,
                "link": link,
                "guid": guid,
                "summary": "",
                "category": "国内财经快讯",
                "author": "新浪财经",
                "pub_date": pub_date,
            }
        )
    return out


def content_hash(item: dict) -> str:
    raw = f"{item['guid']}||{item['title']}||{item['pub_date']}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def upsert(conn: sqlite3.Connection, items: list[dict], limit: int) -> tuple[int, int, list[dict]]:
    fetched_at = now_utc_str()
    inserted = 0
    skipped = 0
    inserted_items: list[dict] = []
    for it in items[: max(limit, 0)]:
        h = content_hash(it)
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO news_feed_items (
                source, title, link, guid, summary, category, author, pub_date, fetched_at, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                it["source"],
                it["title"],
                it["link"],
                it["guid"],
                it["summary"],
                it["category"],
                it["author"],
                it["pub_date"],
                fetched_at,
                h,
            ),
        )
        if cur.rowcount == 1:
            inserted += 1
            inserted_items.append({**it, "scope": "domestic"})
        else:
            skipped += 1
    conn.commit()
    return inserted, skipped, inserted_items


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return 1

    try:
        resp = requests.get(
            URL,
            params={"tag": args.tag},
            headers=DEFAULT_HEADERS,
            timeout=args.timeout,
        )
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except Exception as exc:
        print(f"抓取失败: {exc}")
        return 2

    items = parse_items(resp.text)
    print(f"抓取并解析到 {len(items)} 条")
    if args.dry_run:
        for it in items[:5]:
            print(f"- {it['pub_date']} | {it['title'][:80]}")
        return 0

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn)
        inserted, skipped, inserted_items = upsert(conn, items, args.limit)
        total = conn.execute("SELECT COUNT(*) FROM news_feed_items").fetchone()[0]
        print(
            f"完成: source={SOURCE}, fetched={len(items)}, try_insert={min(len(items), args.limit)}, "
            f"inserted={inserted}, skipped={skipped}, table_rows={total}"
        )
        if inserted_items:
            publish_news_batch(
                source=SOURCE,
                scope="domestic",
                items=inserted_items,
                producer="fetch_cn_news_sina_7x24.py",
            )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
