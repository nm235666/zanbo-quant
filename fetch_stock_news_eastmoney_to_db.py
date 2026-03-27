#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import db_compat as sqlite3
from datetime import datetime, timezone
from pathlib import Path

from realtime_streams import publish_app_event
from query_stock_news_eastmoney import (
    fetch_news,
    normalize_items,
    resolve_name_from_ts_code,
)

SOURCE = "eastmoney_stock_news"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取东方财富个股新闻并入库")
    parser.add_argument("--name", default="", help="股票名称，如 恒立液压")
    parser.add_argument("--ts-code", default="", help="股票代码，如 601100.SH")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP 超时秒数")
    parser.add_argument("--dry-run", action="store_true", help="只抓取解析，不入库")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT NOT NULL,
            company_name TEXT NOT NULL,
            source TEXT NOT NULL,
            news_code TEXT,
            title TEXT NOT NULL,
            summary TEXT,
            link TEXT,
            pub_time TEXT,
            comment_num INTEGER,
            relation_stock_tags_json TEXT,
            llm_system_score INTEGER,
            llm_finance_impact_score INTEGER,
            llm_finance_importance TEXT,
            llm_impacts_json TEXT,
            llm_summary TEXT,
            llm_model TEXT,
            llm_scored_at TEXT,
            llm_prompt_version TEXT,
            llm_raw_output TEXT,
            content_hash TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            update_time TEXT,
            UNIQUE(ts_code, source, content_hash)
        )
        """
    )
    cols = {r[1] for r in conn.execute("PRAGMA table_info(stock_news_items)").fetchall()}
    need = [
        ("llm_system_score", "INTEGER"),
        ("llm_finance_impact_score", "INTEGER"),
        ("llm_finance_importance", "TEXT"),
        ("llm_impacts_json", "TEXT"),
        ("llm_summary", "TEXT"),
        ("llm_model", "TEXT"),
        ("llm_scored_at", "TEXT"),
        ("llm_prompt_version", "TEXT"),
        ("llm_raw_output", "TEXT"),
    ]
    for name, typ in need:
        if name not in cols:
            conn.execute(f"ALTER TABLE stock_news_items ADD COLUMN {name} {typ}")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_stock_news_code_time ON stock_news_items(ts_code, pub_time)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_stock_news_source_time ON stock_news_items(source, pub_time)"
    )
    conn.commit()


def content_hash(ts_code: str, item: dict) -> str:
    raw = f"{ts_code}||{item.get('news_code','')}||{item.get('title','')}||{item.get('pub_time','')}".encode(
        "utf-8",
        errors="ignore",
    )
    return hashlib.sha256(raw).hexdigest()


def upsert(conn: sqlite3.Connection, ts_code: str, company_name: str, items: list[dict]) -> tuple[int, int]:
    fetched_at = now_utc_str()
    inserted = 0
    skipped = 0
    for item in items:
        h = content_hash(ts_code, item)
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO stock_news_items (
                ts_code, company_name, source, news_code, title, summary, link, pub_time,
                comment_num, relation_stock_tags_json, content_hash, fetched_at, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts_code,
                company_name,
                SOURCE,
                item.get("news_code", ""),
                item.get("title", ""),
                item.get("summary", ""),
                item.get("link", ""),
                item.get("pub_time", ""),
                item.get("comment_num"),
                json.dumps(item.get("relation_stock_tags") or [], ensure_ascii=False),
                h,
                fetched_at,
                fetched_at,
            ),
        )
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    conn.commit()
    return inserted, skipped


def main() -> int:
    args = parse_args()
    ts_code = args.ts_code.strip().upper()
    company_name = args.name.strip()
    db_path = Path(args.db_path).resolve()

    if not company_name:
        if not ts_code:
            print("请传入 --name 或 --ts-code")
            return 1
        try:
            company_name = resolve_name_from_ts_code(str(db_path), ts_code)
        except Exception as exc:
            print(f"解析股票名称失败: {exc}")
            return 2

    if not ts_code:
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute(
                """
                SELECT ts_code
                FROM stock_codes
                WHERE name = ?
                ORDER BY CASE list_status WHEN 'L' THEN 0 ELSE 1 END, ts_code
                LIMIT 1
                """,
                (company_name,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            print(f"未在 stock_codes 中找到公司: {company_name}")
            return 3
        ts_code = str(row[0]).strip().upper()

    try:
        payload = fetch_news(company_name, page=args.page, page_size=args.page_size, timeout=args.timeout)
        total, items = normalize_items(payload)
    except Exception as exc:
        print(f"抓取失败: {exc}")
        return 4

    print(f"股票: {company_name} ({ts_code})")
    print(f"总命中: {total}")
    print(f"本页返回: {len(items)}")

    if args.dry_run:
        for item in items[:5]:
            print(f"- {item['pub_time']} | {item['title']}")
        return 0

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn)
        inserted, skipped = upsert(conn, ts_code, company_name, items)
        table_rows = conn.execute(
            "SELECT COUNT(*) FROM stock_news_items WHERE ts_code = ?",
            (ts_code,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(
        f"完成: source={SOURCE}, inserted={inserted}, skipped={skipped}, "
        f"stock_rows={table_rows}, page={args.page}, page_size={args.page_size}"
    )
    publish_app_event(
        event="stock_news_update",
        payload={
            "ts_code": ts_code,
            "company_name": company_name,
            "inserted": int(inserted),
            "skipped": int(skipped),
            "stock_rows": int(table_rows),
            "page_size": int(args.page_size),
        },
        producer="fetch_stock_news_eastmoney_to_db.py",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
