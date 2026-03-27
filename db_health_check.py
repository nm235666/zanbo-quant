#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import db_compat as sqlite3


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="数据库健康巡检")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser.parse_args()


def fetch_scalar(conn, sql: str):
    return conn.execute(sql).fetchone()[0]


def main() -> int:
    args = parse_args()
    conn = sqlite3.connect(ROOT / "stocks.db")
    try:
        payload = {
            "daily_latest": fetch_scalar(conn, "SELECT MAX(trade_date) FROM stock_daily_prices"),
            "minline_latest": fetch_scalar(conn, "SELECT MAX(trade_date) FROM stock_minline"),
            "scores_latest": fetch_scalar(conn, "SELECT MAX(score_date) FROM stock_scores_daily"),
            "miss_events": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM stock_codes s WHERE s.list_status='L' "
                "AND NOT EXISTS (SELECT 1 FROM stock_events e WHERE e.ts_code=s.ts_code)",
            ),
            "miss_governance": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM stock_codes s WHERE s.list_status='L' "
                "AND NOT EXISTS (SELECT 1 FROM company_governance g WHERE g.ts_code=s.ts_code)",
            ),
            "miss_flow": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM stock_codes s WHERE s.list_status='L' "
                "AND NOT EXISTS (SELECT 1 FROM capital_flow_stock c WHERE c.ts_code=s.ts_code)",
            ),
            "miss_minline": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM stock_codes s WHERE s.list_status='L' "
                "AND NOT EXISTS (SELECT 1 FROM stock_minline m WHERE m.ts_code=s.ts_code)",
            ),
            "news_unscored": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM news_feed_items WHERE COALESCE(llm_finance_importance,'')=''",
            ),
            "stock_news_unscored": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM stock_news_items WHERE COALESCE(llm_finance_importance,'')=''",
            ),
            "news_dup_link": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM (SELECT source, COALESCE(link,''), COUNT(*) c "
                "FROM news_feed_items GROUP BY source, COALESCE(link,'') "
                "HAVING COALESCE(link,'')<>'' AND COUNT(*)>1) t",
            ),
            "stock_news_dup_link": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM (SELECT ts_code, COALESCE(link,''), COUNT(*) c "
                "FROM stock_news_items GROUP BY ts_code, COALESCE(link,'') "
                "HAVING COALESCE(link,'')<>'' AND COUNT(*)>1) t",
            ),
            "macro_publish_empty": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM macro_series WHERE COALESCE(publish_date,'')=''",
            ),
            "chatlog_dup_key": fetch_scalar(
                conn,
                "SELECT COUNT(*) FROM (SELECT message_key, COUNT(*) c FROM wechat_chatlog_clean_items "
                "GROUP BY message_key HAVING COUNT(*)>1) t",
            ),
        }
    finally:
        conn.close()

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}\t{value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
