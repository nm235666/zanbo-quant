#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import db_compat as sqlite3
import requests

from query_stock_news_eastmoney import fetch_news as fetch_news_eastmoney
from query_stock_news_eastmoney import normalize_items as normalize_items_eastmoney

LOCAL_DEPS = Path(__file__).resolve().parent / ".deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

try:
    import akshare as ak  # type: ignore
except Exception:  # noqa: BLE001
    ak = None


SOURCE_AK = "akshare.stock_news_em"
SOURCE_FALLBACK = "eastmoney_stock_news"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量补齐 stock_news_items 个股新闻")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--table-name", default="stock_news_items", help="目标表名")
    parser.add_argument("--ts-code", default="", help="仅处理单只股票，如 000001.SZ")
    parser.add_argument("--start-from", default="", help="从指定 ts_code 开始续跑")
    parser.add_argument("--limit-stocks", type=int, default=0, help="最多处理多少只股票")
    parser.add_argument("--all-status", action="store_true", help="处理全部状态股票")
    parser.add_argument("--missing-only", action="store_true", help="仅处理当前没有个股新闻的股票")
    parser.add_argument("--page-size", type=int, default=20, help="每页抓取数量")
    parser.add_argument("--max-pages", type=int, default=2, help="每只股票最多抓几页")
    parser.add_argument("--timeout", type=int, default=25, help="单次 HTTP 超时秒数")
    parser.add_argument("--retry", type=int, default=2, help="单只股票失败重试次数")
    parser.add_argument("--pause", type=float, default=0.2, help="每只股票之间暂停秒数")
    parser.add_argument("--force", action="store_true", help="忽略 missing-only，强制重抓目标股票")
    parser.add_argument("--dry-run", action="store_true", help="只抓取解析，不入库")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_table(conn: sqlite3.Connection, table_name: str) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_code_time ON {table_name}(ts_code, pub_time)"
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_source_time ON {table_name}(source, pub_time)"
    )
    conn.commit()


def load_targets(
    conn: sqlite3.Connection,
    table_name: str,
    ts_code: str,
    start_from: str,
    limit_stocks: int,
    all_status: bool,
    missing_only: bool,
    force: bool,
) -> list[tuple[str, str, str]]:
    if ts_code.strip():
        rows = conn.execute(
            """
            SELECT ts_code, symbol, name
            FROM stock_codes
            WHERE ts_code = ?
            LIMIT 1
            """,
            (ts_code.strip().upper(),),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    where = []
    params: list[object] = []
    if not all_status:
        where.append("list_status='L'")
    if missing_only and not force:
        where.append(
            f"NOT EXISTS (SELECT 1 FROM {table_name} n WHERE n.ts_code = stock_codes.ts_code)"
        )
    if start_from.strip():
        where.append("ts_code >= ?")
        params.append(start_from.strip().upper())
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    limit_sql = f" LIMIT {int(limit_stocks)}" if limit_stocks > 0 else ""
    sql = f"""
    SELECT ts_code, symbol, name
    FROM stock_codes
    {where_sql}
    ORDER BY ts_code
    {limit_sql}
    """
    return [(r[0], r[1], r[2]) for r in conn.execute(sql, params).fetchall()]


def content_hash(ts_code: str, source: str, item: dict) -> str:
    raw = "||".join(
        [
            ts_code,
            source,
            str(item.get("news_code") or ""),
            str(item.get("title") or ""),
            str(item.get("pub_time") or ""),
            str(item.get("link") or ""),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def normalize_akshare_rows(rows) -> list[dict]:
    items: list[dict] = []
    if rows is None:
        return items
    try:
        records = rows.to_dict("records")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"AKShare 返回结果无法转 records: {exc}") from exc

    for row in records:
        if not isinstance(row, dict):
            continue
        title = str(
            row.get("标题")
            or row.get("新闻标题")
            or row.get("title")
            or ""
        ).strip()
        summary = str(
            row.get("摘要")
            or row.get("内容")
            or row.get("summary")
            or ""
        ).strip()
        pub_time = str(
            row.get("发布时间")
            or row.get("时间")
            or row.get("pub_time")
            or ""
        ).strip()
        link = str(
            row.get("新闻链接")
            or row.get("链接")
            or row.get("url")
            or row.get("link")
            or ""
        ).strip()
        news_code = str(
            row.get("新闻编码")
            or row.get("code")
            or row.get("资讯编码")
            or ""
        ).strip()
        if not title:
            continue
        items.append(
            {
                "title": title,
                "summary": summary,
                "pub_time": pub_time,
                "link": link,
                "news_code": news_code,
                "comment_num": None,
                "relation_stock_tags": [],
            }
        )
    return items


def fetch_news_akshare_direct(symbol: str) -> list[dict]:
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    inner_param = {
        "uid": "",
        "keyword": symbol,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": "default",
                "pageIndex": 1,
                "pageSize": 10,
                "preTag": "<em>",
                "postTag": "</em>",
            }
        },
    }
    params = {
        "cb": "jQuery35101792940631092459_1764599530165",
        "param": json.dumps(inner_param, ensure_ascii=False),
        "_": "1764599530176",
    }
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://so.eastmoney.com/news/s?keyword={symbol}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    text = resp.text.strip()
    prefix = "jQuery35101792940631092459_1764599530165("
    if text.startswith(prefix) and text.endswith(")"):
        text = text[len(prefix):-1]
    obj = json.loads(text)
    records = (obj.get("result") or {}).get("cmsArticleWebOld") or []
    items: list[dict] = []
    for row in records:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").replace("<em>", "").replace("</em>", "").strip()
        summary = str(row.get("content") or "").replace("<em>", "").replace("</em>", "").replace("\u3000", "").replace("\r\n", " ").strip()
        code = str(row.get("code") or "").strip()
        link = f"http://finance.eastmoney.com/a/{code}.html" if code else ""
        pub_time = str(row.get("date") or "").strip()
        if not title:
            continue
        items.append(
            {
                "title": title,
                "summary": summary,
                "pub_time": pub_time,
                "link": link,
                "news_code": code,
                "comment_num": None,
                "relation_stock_tags": [],
            }
        )
    return items


def fetch_news_akshare(company_name: str, symbol: str) -> list[dict]:
    if ak is None:
        return fetch_news_akshare_direct(symbol=str(symbol or "").strip())
    fn = getattr(ak, "stock_news_em", None)
    if fn is None:
        return fetch_news_akshare_direct(symbol=str(symbol or "").strip())
    try:
        rows = fn(symbol=str(symbol or "").strip())
    except TypeError:
        rows = fn(symbol=company_name)
    return normalize_akshare_rows(rows)


def fetch_news_fallback(company_name: str, page: int, page_size: int, timeout: int) -> list[dict]:
    payload = fetch_news_eastmoney(company_name, page=page, page_size=page_size, timeout=timeout)
    _total, items = normalize_items_eastmoney(payload)
    return items


def fetch_news_for_stock(company_name: str, symbol: str, page: int, page_size: int, timeout: int) -> tuple[str, list[dict]]:
    if page == 1:
        try:
            items = fetch_news_akshare(company_name=company_name, symbol=symbol)
            if items:
                return SOURCE_AK, items[:page_size]
        except Exception:
            pass
    return SOURCE_FALLBACK, fetch_news_fallback(company_name=company_name, page=page, page_size=page_size, timeout=timeout)


def upsert_rows(
    conn: sqlite3.Connection,
    table_name: str,
    ts_code: str,
    company_name: str,
    source: str,
    items: list[dict],
) -> tuple[int, int]:
    fetched_at = now_utc_str()
    inserted = 0
    skipped = 0
    for item in items:
        h = content_hash(ts_code, source, item)
        cur = conn.execute(
            f"""
            INSERT OR IGNORE INTO {table_name} (
                ts_code, company_name, source, news_code, title, summary, link, pub_time,
                comment_num, relation_stock_tags_json, content_hash, fetched_at, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts_code,
                company_name,
                source,
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


def process_one_stock(
    conn: sqlite3.Connection,
    table_name: str,
    ts_code: str,
    symbol: str,
    company_name: str,
    max_pages: int,
    page_size: int,
    timeout: int,
) -> dict:
    total_inserted = 0
    total_skipped = 0
    used_sources: list[str] = []
    page_counts: list[int] = []

    for page in range(1, max(max_pages, 1) + 1):
        source, items = fetch_news_for_stock(
            company_name=company_name,
            symbol=symbol,
            page=page,
            page_size=page_size,
            timeout=timeout,
        )
        used_sources.append(source)
        page_counts.append(len(items))
        if not items:
            break
        inserted, skipped = upsert_rows(
            conn=conn,
            table_name=table_name,
            ts_code=ts_code,
            company_name=company_name,
            source=source,
            items=items,
        )
        total_inserted += inserted
        total_skipped += skipped
        if page > 1 and inserted == 0 and skipped > 0:
            break

    stock_rows = conn.execute(
        f"SELECT COUNT(*) FROM {table_name} WHERE ts_code = ?",
        (ts_code,),
    ).fetchone()[0]
    return {
        "inserted": total_inserted,
        "skipped": total_skipped,
        "stock_rows": stock_rows,
        "sources": used_sources,
        "page_counts": page_counts,
    }


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn, args.table_name)
        targets = load_targets(
            conn=conn,
            table_name=args.table_name,
            ts_code=args.ts_code,
            start_from=args.start_from,
            limit_stocks=args.limit_stocks,
            all_status=args.all_status,
            missing_only=args.missing_only,
            force=args.force,
        )
        if not targets:
            print("没有可处理的股票。")
            return 0

        print(
            f"待处理股票数: {len(targets)}, missing_only={args.missing_only and not args.force}, "
            f"max_pages={args.max_pages}, page_size={args.page_size}, akshare={'yes' if ak else 'no'}"
        )
        total_inserted = 0
        total_skipped = 0
        failed = 0

        for idx, (ts_code, symbol, company_name) in enumerate(targets, start=1):
            last_exc = None
            for attempt in range(args.retry + 1):
                try:
                    if args.dry_run:
                        source, items = fetch_news_for_stock(
                            company_name=company_name,
                            symbol=symbol,
                            page=1,
                            page_size=args.page_size,
                            timeout=args.timeout,
                        )
                        print(
                            f"[{idx}/{len(targets)}] {ts_code} {company_name}: "
                            f"source={source} items={len(items)}"
                        )
                    else:
                        result = process_one_stock(
                            conn=conn,
                            table_name=args.table_name,
                            ts_code=ts_code,
                            symbol=symbol,
                            company_name=company_name,
                            max_pages=args.max_pages,
                            page_size=args.page_size,
                            timeout=args.timeout,
                        )
                        total_inserted += int(result["inserted"])
                        total_skipped += int(result["skipped"])
                        print(
                            f"[{idx}/{len(targets)}] {ts_code} {company_name}: "
                            f"inserted={result['inserted']} skipped={result['skipped']} "
                            f"stock_rows={result['stock_rows']} sources={','.join(result['sources'])} "
                            f"page_counts={result['page_counts']}"
                        )
                    last_exc = None
                    break
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    if attempt < args.retry:
                        time.sleep(1.0 * (2**attempt))
            if last_exc is not None:
                failed += 1
                print(f"[{idx}/{len(targets)}] {ts_code} {company_name}: 失败 -> {last_exc}")

            if args.pause > 0:
                time.sleep(args.pause)

        if args.dry_run:
            return 0

        final_rows = conn.execute(f"SELECT COUNT(*) FROM {args.table_name}").fetchone()[0]
        print(
            f"完成: failed={failed}, inserted={total_inserted}, skipped={total_skipped}, "
            f"table_rows={final_rows}"
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
