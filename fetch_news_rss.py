#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import db_compat as sqlite3
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from realtime_streams import publish_news_batch

RSS_SOURCES = {
    "dj_world_news": "https://feeds.content.dowjones.io/public/rss/RSSWorldNews",
    "dj_markets_main": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
    "dj_wsjd": "https://feeds.content.dowjones.io/public/rss/RSSWSJD",
    "dj_us_news": "https://feeds.content.dowjones.io/public/rss/RSSUSnews",
    "bbg_markets_news": "https://feeds.bloomberg.com/markets/news.rss?utm_source=chatgpt.com",
    "mw_topstories": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "mw_realtimeheadlines": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
    "mw_bulletins": "https://feeds.content.dowjones.io/public/rss/mw_bulletins",
    "mw_marketpulse": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取 Dow Jones / Bloomberg RSS 新闻并入库")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument(
        "--sources",
        default=(
            "dj_world_news,dj_markets_main,dj_wsjd,dj_us_news,bbg_markets_news,"
            "mw_topstories,mw_realtimeheadlines,mw_bulletins,mw_marketpulse"
        ),
        help=(
            "要抓取的数据源，逗号分隔（可选: dj_world_news,dj_markets_main,dj_wsjd,"
            "dj_us_news,bbg_markets_news,mw_topstories,mw_realtimeheadlines,mw_bulletins,mw_marketpulse）"
        ),
    )
    parser.add_argument("--limit", type=int, default=100, help="每个源最多入库条数")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP超时秒数")
    parser.add_argument("--user-agent", default="Mozilla/5.0 RSSFetcher/1.0", help="请求UA")
    parser.add_argument("--dry-run", action="store_true", help="只抓取不入库")
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


def parse_rss_dt(v: str) -> str:
    s = (v or "").strip()
    if not s:
        return ""
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return s


def text_of(parent: ET.Element, path: str) -> str:
    node = parent.find(path)
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def pick_item_fields(item: ET.Element) -> dict:
    # RSS 2.0 常见字段
    title = text_of(item, "title")
    link = text_of(item, "link")
    guid = text_of(item, "guid")
    summary = text_of(item, "description")
    category = text_of(item, "category")
    author = text_of(item, "author")
    pub_date = parse_rss_dt(text_of(item, "pubDate"))

    # 某些 feed 可能用 dc:creator
    if not author:
        for child in item:
            if child.tag.endswith("creator") and child.text:
                author = child.text.strip()
                break

    return {
        "title": title,
        "link": link,
        "guid": guid,
        "summary": summary,
        "category": category,
        "author": author,
        "pub_date": pub_date,
    }


def fetch_rss(url: str, timeout: int, user_agent: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def canonical_news_key(title: str, link: str, guid: str, pub_date: str) -> str:
    guid = (guid or "").strip()
    if guid:
        return guid.lower()

    link = (link or "").strip()
    if link:
        try:
            u = urllib.parse.urlsplit(link)
            q = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
            # 移除常见追踪参数，减少“同文不同URL”重复
            q = [
                (k, v)
                for (k, v) in q
                if (not k.lower().startswith("utm_")) and (k.lower() not in {"mod", "cmpid", "cid"})
            ]
            qstr = urllib.parse.urlencode(q, doseq=True)
            return urllib.parse.urlunsplit((u.scheme.lower(), u.netloc.lower(), u.path, qstr, ""))
        except Exception:
            return link.lower()
    return f"{(title or '').strip().lower()}|{(pub_date or '').strip()}"


def build_hash(title: str, link: str, guid: str, pub_date: str) -> str:
    raw = canonical_news_key(title=title, link=link, guid=guid, pub_date=pub_date).encode(
        "utf-8", errors="ignore"
    )
    return hashlib.sha256(raw).hexdigest()


def parse_items(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []
    items = []
    for item in channel.findall("item"):
        items.append(pick_item_fields(item))
    return items


def upsert_items(conn: sqlite3.Connection, source: str, items: list[dict], limit: int) -> tuple[int, int, list[dict]]:
    fetched_at = now_utc_str()
    inserted = 0
    skipped = 0
    inserted_items: list[dict] = []
    for it in items[: max(limit, 0)]:
        content_hash = build_hash(it["title"], it["link"], it["guid"], it["pub_date"])
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO news_feed_items (
                source, title, link, guid, summary, category, author, pub_date, fetched_at, content_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                it["title"],
                it["link"],
                it["guid"],
                it["summary"],
                it["category"],
                it["author"],
                it["pub_date"],
                fetched_at,
                content_hash,
            ),
        )
        if cur.rowcount == 1:
            inserted += 1
            inserted_items.append({**it, "source": source, "scope": "international"})
        else:
            skipped += 1
    conn.commit()
    return inserted, skipped, inserted_items


def normalize_title(text: str) -> str:
    s = (text or "").lower().strip()
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def cleanup_bulletin_duplicates(conn: sqlite3.Connection, hour_window: int = 6) -> int:
    """
    清理 MarketWatch bulletin 与完整文章的重复：
    - 仅处理 source = mw_bulletins
    - 若在时间窗口内存在非 bulletin、且标题高度包含的记录，则删除 bulletin
    """
    rows = conn.execute(
        """
        SELECT id, title, pub_date
        FROM news_feed_items
        WHERE source = 'mw_bulletins' AND title IS NOT NULL AND TRIM(title) <> '' AND pub_date IS NOT NULL
        ORDER BY id
        """
    ).fetchall()
    others = conn.execute(
        """
        SELECT id, title, pub_date
        FROM news_feed_items
        WHERE source <> 'mw_bulletins' AND title IS NOT NULL AND TRIM(title) <> '' AND pub_date IS NOT NULL
        """
    ).fetchall()

    deleted = 0

    def parse_iso_utc(s: str) -> datetime | None:
        v = (s or "").strip()
        if not v:
            return None
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            return None

    for rid, title, pub_date in rows:
        t1 = normalize_title(title)
        if len(t1) < 24:
            continue
        dt1 = parse_iso_utc(pub_date)
        if dt1 is None:
            continue
        for cid, ctitle, cpub_date in others:
            dt2 = parse_iso_utc(cpub_date)
            if dt2 is None:
                continue
            if abs((dt1 - dt2).total_seconds()) > hour_window * 3600:
                continue
            t2 = normalize_title(ctitle)
            if len(t2) < 24:
                continue
            short, long_ = (t1, t2) if len(t1) <= len(t2) else (t2, t1)
            if len(short) >= 24 and short in long_:
                conn.execute("DELETE FROM news_feed_items WHERE id = ?", (rid,))
                deleted += 1
                break

    if deleted:
        conn.commit()
    return deleted


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}", file=sys.stderr)
        return 1

    sources = [x.strip().lower() for x in args.sources.split(",") if x.strip()]
    if not sources:
        print("未指定 sources", file=sys.stderr)
        return 2

    invalid = [s for s in sources if s not in RSS_SOURCES]
    if invalid:
        print(f"不支持的数据源: {', '.join(invalid)}", file=sys.stderr)
        return 3

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn)

        total_fetched = 0
        total_inserted = 0
        total_skipped = 0

        for source in sources:
            url = RSS_SOURCES[source]
            try:
                xml_bytes = fetch_rss(url=url, timeout=args.timeout, user_agent=args.user_agent)
                items = parse_items(xml_bytes)
            except Exception as exc:
                print(f"[{source}] 抓取失败: {exc}", file=sys.stderr)
                continue

            total_fetched += len(items)
            if args.dry_run:
                print(f"[{source}] 抓取 {len(items)} 条（dry-run，不入库）")
                continue

            inserted, skipped, inserted_items = upsert_items(conn, source, items, args.limit)
            total_inserted += inserted
            total_skipped += skipped
            print(
                f"[{source}] 抓取 {len(items)} 条，尝试入库 {min(len(items), args.limit)} 条，"
                f"新增 {inserted} 条，跳过重复 {skipped} 条"
            )
            if inserted_items:
                publish_news_batch(
                    source=source,
                    scope="international",
                    items=inserted_items,
                    producer="fetch_news_rss.py",
                )

        cleaned = cleanup_bulletin_duplicates(conn)
        if cleaned:
            print(f"额外清理 bulletin 近似重复: {cleaned} 条")

        if args.dry_run:
            print(f"完成(dry-run): fetched={total_fetched}")
        else:
            total_rows = conn.execute("SELECT COUNT(*) FROM news_feed_items").fetchone()[0]
            print(
                f"完成: fetched={total_fetched}, inserted={total_inserted}, skipped={total_skipped}, "
                f"table_rows={total_rows}"
            )
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
