#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import psycopg2

from migrate_sqlite_to_postgres import create_table, recreate_indexes, user_tables

DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_DATABASE_URL = "postgresql://zanbo@/stockapp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="仅初始化 PostgreSQL 表结构")
    parser.add_argument("--sqlite-path", default=str(DEFAULT_SQLITE_PATH), help="用于读取表结构的 SQLite 数据库")
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL, help="PostgreSQL 连接串")
    parser.add_argument("--drop-existing", action="store_true", help="重建前删除现有同名表")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sqlite_path = Path(args.sqlite_path).resolve()
    if not sqlite_path.exists():
        raise SystemExit(f"SQLite 数据库不存在: {sqlite_path}")
    src = sqlite3.connect(sqlite_path)
    try:
        dst = psycopg2.connect(args.database_url)
        try:
            for table in user_tables(src):
                print(f"初始化表: {table}")
                create_table(dst, src, table, args.drop_existing)
                recreate_indexes(dst, src, table)
            print("PostgreSQL 表结构初始化完成")
        finally:
            dst.close()
    finally:
        src.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
