#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import db_compat as sqlite3


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="清理新闻与聊天记录重复数据")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def count_duplicate_groups(conn) -> dict[str, int]:
    return {
        "news_feed_link_groups": conn.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT source, COALESCE(link,''), COUNT(*) c
              FROM news_feed_items
              GROUP BY source, COALESCE(link,'')
              HAVING COALESCE(link,'') <> '' AND COUNT(*) > 1
            ) t
            """
        ).fetchone()[0],
        "stock_news_link_groups": conn.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT ts_code, COALESCE(link,''), COUNT(*) c
              FROM stock_news_items
              GROUP BY ts_code, COALESCE(link,'')
              HAVING COALESCE(link,'') <> '' AND COUNT(*) > 1
            ) t
            """
        ).fetchone()[0],
        "chatlog_key_groups": conn.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT message_key, COUNT(*) c
              FROM wechat_chatlog_clean_items
              GROUP BY message_key
              HAVING COUNT(*) > 1
            ) t
            """
        ).fetchone()[0],
    }


def main() -> int:
    args = parse_args()
    conn = sqlite3.connect(ROOT / "stocks.db")
    try:
        before = count_duplicate_groups(conn)
        print("before", before)
        if args.dry_run:
            return 0

        conn.execute(
            """
            DELETE FROM news_feed_items
            WHERE id IN (
              SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                         PARTITION BY source, COALESCE(link,'')
                         ORDER BY COALESCE(pub_date,'' ) DESC, COALESCE(fetched_at,'') DESC, id DESC
                       ) AS rn
                FROM news_feed_items
                WHERE COALESCE(link,'') <> ''
              ) x
              WHERE x.rn > 1
            )
            """
        )

        conn.execute(
            """
            DELETE FROM stock_news_items
            WHERE id IN (
              SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                         PARTITION BY ts_code, COALESCE(link,'')
                         ORDER BY COALESCE(pub_time,'') DESC, COALESCE(update_time,'') DESC, id DESC
                       ) AS rn
                FROM stock_news_items
                WHERE COALESCE(link,'') <> ''
              ) x
              WHERE x.rn > 1
            )
            """
        )

        conn.execute(
            """
            DELETE FROM wechat_chatlog_clean_items
            WHERE id IN (
              SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                         PARTITION BY message_key
                         ORDER BY COALESCE(update_time,'' ) DESC, COALESCE(fetched_at,'') DESC, id DESC
                       ) AS rn
                FROM wechat_chatlog_clean_items
              ) x
              WHERE x.rn > 1
            )
            """
        )
        conn.commit()
        after = count_duplicate_groups(conn)
        print("after", after)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
