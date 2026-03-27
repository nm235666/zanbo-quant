#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import db_compat as sqlite3
from pathlib import Path

import requests

URL = "https://search-api-web.eastmoney.com/search/jsonp"

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://kuaixun.eastmoney.com/",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

TAG_RE = re.compile(r"<[^>]+>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="查询东方财富个股相关新闻")
    parser.add_argument("--name", default="", help="股票名称，如 恒立液压")
    parser.add_argument("--ts-code", default="", help="股票代码，如 601100.SH")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参，用于 ts_code -> 股票名）",
    )
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量，默认 20")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP 超时秒数")
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="输出格式，默认 text",
    )
    return parser.parse_args()


def resolve_name_from_ts_code(db_path: str, ts_code: str) -> str:
    db = Path(db_path).resolve()
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute(
            """
            SELECT name
            FROM stock_codes
            WHERE ts_code = ?
            LIMIT 1
            """,
            (ts_code.strip().upper(),),
        ).fetchone()
    finally:
        conn.close()
    if not row or not row[0]:
        raise ValueError(f"未在 stock_codes 中找到股票代码: {ts_code}")
    return str(row[0]).strip()


def unwrap_jsonp(text: str) -> dict:
    raw = text.strip()
    m = re.match(r"^[^(]+\((.*)\)\s*;?\s*$", raw, flags=re.S)
    if m:
        raw = m.group(1)
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("接口返回不是 JSON Object")
    return obj


def strip_html(text: str) -> str:
    return TAG_RE.sub("", str(text or "")).strip()


def build_params(keyword: str, page: int, page_size: int) -> dict:
    payload = {
        "uid": "",
        "keyword": keyword,
        "type": ["cmsArticleWebFast"],
        "client": "web",
        "clientVersion": "1.0",
        "clientType": "kuaixun",
        "param": {
            "cmsArticleWebFast": {
                "column": "102",
                "cmsColumnList": "",
                "pageIndex": max(page, 1),
                "pageSize": min(max(page_size, 1), 100),
            }
        },
    }
    return {
        "param": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        "cb": "jQuery1830_eastmoney_stock_news",
        "_": "1774486287210",
    }


def fetch_news(keyword: str, page: int, page_size: int, timeout: int) -> dict:
    resp = requests.get(
        URL,
        params=build_params(keyword, page, page_size),
        headers=DEFAULT_HEADERS,
        timeout=timeout,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return unwrap_jsonp(resp.text)


def normalize_items(obj: dict) -> tuple[int, list[dict]]:
    result = obj.get("result") or {}
    rows = result.get("cmsArticleWebFast") or []
    total = int(obj.get("hitsTotal") or 0)
    items = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                "title": strip_html(row.get("title")),
                "summary": strip_html(row.get("docuReader")),
                "pub_time": str(row.get("date") or "").strip(),
                "link": str(row.get("uniqueUrl") or "").strip(),
                "news_code": str(row.get("code") or "").strip(),
                "comment_num": row.get("commentNum"),
                "relation_stock_tags": row.get("relationStockTags") or [],
                "column": str(row.get("column") or "").strip(),
            }
        )
    return total, items


def main() -> int:
    args = parse_args()
    name = args.name.strip()
    ts_code = args.ts_code.strip().upper()

    if not name:
        if not ts_code:
            print("请传入 --name 或 --ts-code")
            return 1
        try:
            name = resolve_name_from_ts_code(args.db_path, ts_code)
        except Exception as exc:
            print(f"解析股票名称失败: {exc}")
            return 2

    try:
        obj = fetch_news(name, page=args.page, page_size=args.page_size, timeout=args.timeout)
        total, items = normalize_items(obj)
    except Exception as exc:
        print(f"查询失败: {exc}")
        return 3

    payload = {
        "keyword": name,
        "page": args.page,
        "page_size": args.page_size,
        "total": total,
        "items": items,
    }

    if args.output == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"关键词: {name}")
    if ts_code:
        print(f"股票代码: {ts_code}")
    print(f"总命中: {total}")
    print(f"当前页: {args.page}")
    print(f"返回条数: {len(items)}")
    print("")
    for idx, item in enumerate(items, 1):
        print(f"[{idx}] {item['title']}")
        print(f"时间: {item['pub_time']}")
        if item["summary"]:
            print(f"摘要: {item['summary']}")
        if item["link"]:
            print(f"链接: {item['link']}")
        if item["relation_stock_tags"]:
            print(f"关联标的: {', '.join(map(str, item['relation_stock_tags']))}")
        print("-" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
