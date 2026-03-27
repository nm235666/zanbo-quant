#!/usr/bin/env python3
from __future__ import annotations

import argparse
import db_compat as sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新闻表索引优化 + 自动归档")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--retain-days", type=int, default=180, help="主表保留天数（默认180）")
    parser.add_argument("--batch-size", type=int, default=1000, help="每批归档行数")
    parser.add_argument("--max-batches", type=int, default=50, help="单次最多归档批次数")
    parser.add_argument("--vacuum", action="store_true", help="归档后执行 VACUUM（耗时）")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cutoff_utc_str(retain_days: int) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(retain_days, 1))
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()[0]
        > 0
    )


def columns_info(conn: sqlite3.Connection, table: str) -> list[tuple]:
    return conn.execute(f"PRAGMA table_info({table})").fetchall()


def ensure_archive_table(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "news_feed_items"):
        raise RuntimeError("主表 news_feed_items 不存在")

    if not table_exists(conn, "news_feed_items_archive"):
        conn.execute(
            "CREATE TABLE news_feed_items_archive AS SELECT * FROM news_feed_items WHERE 0"
        )

    src_cols = columns_info(conn, "news_feed_items")
    arc_cols = {r[1] for r in columns_info(conn, "news_feed_items_archive")}
    for _, name, col_type, *_ in src_cols:
        if name not in arc_cols:
            conn.execute(f"ALTER TABLE news_feed_items_archive ADD COLUMN {name} {col_type or 'TEXT'}")
    if "archived_at" not in arc_cols:
        conn.execute("ALTER TABLE news_feed_items_archive ADD COLUMN archived_at TEXT")

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_news_archive_source_pub_date ON news_feed_items_archive(source, pub_date)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_news_archive_pub_date ON news_feed_items_archive(pub_date)"
    )
    cols = {r[1] for r in columns_info(conn, "news_feed_items_archive")}
    if "llm_finance_importance" in cols:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_news_archive_importance_pub_date "
            "ON news_feed_items_archive(llm_finance_importance, pub_date)"
        )
    # archive 去重约束（尽量避免重复归档）
    if "source" in cols and "content_hash" in cols:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uniq_news_archive_source_hash "
            "ON news_feed_items_archive(source, content_hash)"
        )
    conn.commit()


def ensure_main_indexes(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uniq_news_source_hash ON news_feed_items(source, content_hash)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_news_source_pub_date ON news_feed_items(source, pub_date)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_pub_date ON news_feed_items(pub_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_news_fetched_at ON news_feed_items(fetched_at)")
    cols = {r[1] for r in columns_info(conn, "news_feed_items")}
    if "llm_finance_importance" in cols:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_news_importance_pub_date "
            "ON news_feed_items(llm_finance_importance, pub_date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_news_source_importance_pub_date "
            "ON news_feed_items(source, llm_finance_importance, pub_date)"
        )
    conn.commit()


def archive_once(conn: sqlite3.Connection, cutoff: str, batch_size: int) -> int:
    ids = [
        r[0]
        for r in conn.execute(
            """
            SELECT id
            FROM news_feed_items
            WHERE COALESCE(NULLIF(pub_date,''), fetched_at) < ?
            ORDER BY COALESCE(NULLIF(pub_date,''), fetched_at) ASC, id ASC
            LIMIT ?
            """,
            (cutoff, batch_size),
        ).fetchall()
    ]
    if not ids:
        return 0

    src_cols = [r[1] for r in columns_info(conn, "news_feed_items")]
    common = [c for c in src_cols if c != "id"]  # archive 保留原 id，不冲突也可一起归档
    # 归档表也有 id，保留 id 便于追溯
    common = src_cols[:]  # include id
    col_csv = ", ".join(common)
    placeholders = ",".join(["?"] * len(ids))
    archived_at = now_utc_str()

    insert_sql = (
        f"INSERT OR IGNORE INTO news_feed_items_archive ({col_csv}, archived_at) "
        f"SELECT {col_csv}, ? FROM news_feed_items WHERE id IN ({placeholders})"
    )
    conn.execute(insert_sql, [archived_at, *ids])
    delete_sql = f"DELETE FROM news_feed_items WHERE id IN ({placeholders})"
    conn.execute(delete_sql, ids)
    conn.commit()
    return len(ids)


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return 1

    cutoff = cutoff_utc_str(args.retain_days)
    conn = sqlite3.connect(db_path)
    try:
        if not table_exists(conn, "news_feed_items"):
            print("news_feed_items 不存在，跳过")
            return 0

        ensure_main_indexes(conn)
        ensure_archive_table(conn)

        moved = 0
        for _ in range(max(args.max_batches, 1)):
            n = archive_once(conn, cutoff=cutoff, batch_size=max(args.batch_size, 1))
            if n == 0:
                break
            moved += n

        conn.execute("ANALYZE")
        conn.commit()

        if args.vacuum:
            conn.execute("VACUUM")
            conn.commit()

        main_rows = conn.execute("SELECT COUNT(*) FROM news_feed_items").fetchone()[0]
        arc_rows = conn.execute("SELECT COUNT(*) FROM news_feed_items_archive").fetchone()[0]
        print(
            f"完成: cutoff={cutoff}, archived={moved}, main_rows={main_rows}, archive_rows={arc_rows}, "
            f"vacuum={'yes' if args.vacuum else 'no'}"
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
