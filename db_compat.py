#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sqlite3 as _sqlite3
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote_plus

try:
    import psycopg2
    from psycopg2 import OperationalError as PostgresOperationalError
    from psycopg2.extras import execute_values
except Exception:  # pragma: no cover
    psycopg2 = None
    PostgresOperationalError = Exception
    execute_values = None

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

SQLITE_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
DEFAULT_POSTGRES_DB = os.getenv("POSTGRES_DB", "stockapp")
DEFAULT_POSTGRES_USER = os.getenv("POSTGRES_USER", "zanbo")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{quote_plus(DEFAULT_POSTGRES_USER)}@/" f"{quote_plus(DEFAULT_POSTGRES_DB)}",
).strip()
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0").strip()
USE_POSTGRES = os.getenv("USE_POSTGRES", "1").strip().lower() not in {"0", "false", "no"}


class Row(dict):
    def __init__(self, keys: Iterable[str], values: Iterable[Any]):
        self._keys = list(keys)
        self._values = tuple(values)
        super().__init__(zip(self._keys, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)

    def keys(self):  # pragma: no cover
        return list(self._keys)


Connection = Any
OperationalError = PostgresOperationalError if psycopg2 is not None else _sqlite3.OperationalError


class CompatCursor:
    def __init__(self, cursor, row_factory=None, pragma_columns: list[str] | None = None):
        self._cursor = cursor
        self._row_factory = row_factory
        self._pragma_columns = pragma_columns

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def _columns(self):
        if self._pragma_columns is not None:
            return self._pragma_columns
        if not self._cursor.description:
            return []
        return [col[0] for col in self._cursor.description]

    def _convert_row(self, row):
        if row is None:
            return None
        if self._row_factory is Row:
            return Row(self._columns(), row)
        return row

    def fetchone(self):
        return self._convert_row(self._cursor.fetchone())

    def fetchall(self):
        return [self._convert_row(row) for row in self._cursor.fetchall()]

    def __iter__(self):  # pragma: no cover
        for row in self._cursor:
            yield self._convert_row(row)

    def close(self):
        self._cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def execute(self, sql: str, params: Iterable[Any] = ()):
        kind, new_sql, pragma_columns = _rewrite_sql(sql)
        self._cursor.execute(_replace_qmarks(new_sql), tuple(params or ()))
        self._pragma_columns = pragma_columns if kind == "pragma" else None
        return self

    def executemany(self, sql: str, seq_of_params):
        kind, new_sql, pragma_columns = _rewrite_sql(sql)
        self._cursor.executemany(_replace_qmarks(new_sql), list(seq_of_params))
        self._pragma_columns = pragma_columns if kind == "pragma" else None
        return self


class CompatPostgresConnection:
    def __init__(self, raw_conn):
        self._conn = raw_conn
        self.row_factory = None

    def cursor(self):  # pragma: no cover
        return CompatCursor(self._conn.cursor(), row_factory=self.row_factory)

    def execute(self, sql: str, params: Iterable[Any] = ()):
        kind, new_sql, pragma_columns = _rewrite_sql(sql)
        cur = self._conn.cursor()
        cur.execute(_replace_qmarks(new_sql), tuple(params or ()))
        return CompatCursor(cur, row_factory=self.row_factory, pragma_columns=pragma_columns if kind == "pragma" else None)

    def executemany(self, sql: str, seq_of_params):
        kind, new_sql, pragma_columns = _rewrite_sql(sql)
        cur = self._conn.cursor()
        cur.executemany(_replace_qmarks(new_sql), list(seq_of_params))
        return CompatCursor(cur, row_factory=self.row_factory, pragma_columns=pragma_columns if kind == "pragma" else None)

    def commit(self):
        self._conn.commit()

    def rollback(self):  # pragma: no cover
        self._conn.rollback()

    def close(self):
        self._conn.close()


def _replace_qmarks(sql: str) -> str:
    out: list[str] = []
    in_single = False
    in_double = False
    i = 0
    marker = "__DBC_QMARK__"
    while i < len(sql):
        ch = sql[i]
        if ch == "'" and not in_double:
            if in_single and i + 1 < len(sql) and sql[i + 1] == "'":
                out.append("''")
                i += 2
                continue
            in_single = not in_single
            out.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
            i += 1
            continue
        if ch == "%":
            out.append("%%")
        elif ch == "?" and not in_single and not in_double:
            out.append(marker)
        else:
            out.append(ch)
        i += 1
    return "".join(out).replace(marker, "%s")


def _rewrite_sql(sql: str) -> tuple[str, str, list[str] | None]:
    text = sql.strip()
    lower = re.sub(r"\s+", " ", text.lower())

    if lower.startswith("pragma foreign_keys") or lower.startswith("pragma journal_mode") or lower.startswith("pragma synchronous"):
        return ("pragma_noop", "SELECT 1", ["1"])

    if lower == "select name from sqlite_master where type='table' order by name":
        return (
            "sqlite_master",
            "SELECT table_name AS name FROM information_schema.tables WHERE table_schema = current_schema() ORDER BY table_name",
            None,
        )

    if "from sqlite_master" in lower and "count(*)" in lower and "type='table'" in lower:
        name_match = re.search(r"name\s*=\s*'([^']+)'", text, flags=re.I)
        if name_match:
            table_name = name_match.group(1)
            return (
                "sqlite_master",
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = '{table_name}'",
                None,
            )
        return (
            "sqlite_master",
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = ?",
            None,
        )

    pragma_match = re.match(r"(?is)^pragma\s+table_info\(([^)]+)\)\s*$", text)
    if pragma_match:
        table_name = pragma_match.group(1).strip().strip("'\"")
        pragma_sql = f"""
        SELECT
            ordinal_position - 1 AS cid,
            column_name AS name,
            data_type AS type,
            CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull,
            column_default AS dflt_value,
            CASE WHEN EXISTS (
                SELECT 1
                FROM information_schema.key_column_usage kcu
                JOIN information_schema.table_constraints tc
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND kcu.table_schema = current_schema()
                  AND kcu.table_name = '{table_name}'
                  AND kcu.column_name = c.column_name
            ) THEN 1 ELSE 0 END AS pk
        FROM information_schema.columns c
        WHERE table_schema = current_schema() AND table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        return ("pragma", pragma_sql, ["cid", "name", "type", "notnull", "dflt_value", "pk"])

    if lower.startswith("insert or ignore into "):
        m = re.match(r"(?is)^insert\s+or\s+ignore\s+into\s+(.+?)\s+values\s*(.+)$", text)
        if m:
            return ("normal", f"INSERT INTO {m.group(1)} VALUES {m.group(2)} ON CONFLICT DO NOTHING", None)
        return ("normal", re.sub(r"(?is)^insert\s+or\s+ignore", "INSERT", text) + " ON CONFLICT DO NOTHING", None)

    if lower.startswith("insert or replace into "):
        m = re.match(r"(?is)^insert\s+or\s+replace\s+into\s+(.+?)\s+values\s*(.+)$", text)
        if m:
            return ("normal", f"INSERT INTO {m.group(1)} VALUES {m.group(2)} ON CONFLICT DO NOTHING", None)
        return ("normal", re.sub(r"(?is)^insert\s+or\s+replace", "INSERT", text) + " ON CONFLICT DO NOTHING", None)

    if lower.startswith("create table if not exists "):
        ddl = text
        ddl = re.sub(r"(?i)\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b", "BIGSERIAL PRIMARY KEY", ddl)
        ddl = re.sub(r"(?i)\bINT\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b", "BIGSERIAL PRIMARY KEY", ddl)
        ddl = re.sub(r"(?i)\bAUTOINCREMENT\b", "", ddl)
        return ("normal", ddl, None)

    text = re.sub(
        r"strftime\('%Y%m%d',\s*'now',\s*'-([0-9]+) day'\)",
        lambda m: f"to_char(CURRENT_TIMESTAMP - INTERVAL '{m.group(1)} day', 'YYYYMMDD')",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"datetime\('now',\s*'-([0-9]+) day'\)",
        lambda m: f"(CURRENT_TIMESTAMP - INTERVAL '{m.group(1)} day')",
        text,
        flags=re.I,
    )
    text = re.sub(r"\bifnull\(", "COALESCE(", text, flags=re.I)
    return ("normal", text, None)


def connect(path: str | Path | None = None):
    if USE_POSTGRES and DATABASE_URL and psycopg2 is not None:
        raw = psycopg2.connect(DATABASE_URL)
        raw.autocommit = True
        return CompatPostgresConnection(raw)
    sqlite_path = Path(path or SQLITE_DB_PATH)
    conn = _sqlite3.connect(sqlite_path)
    return conn


def connect_sqlite(path: str | Path | None = None):
    sqlite_path = Path(path or SQLITE_DB_PATH)
    conn = _sqlite3.connect(sqlite_path)
    conn.row_factory = _sqlite3.Row
    return conn


def using_postgres() -> bool:
    return bool(USE_POSTGRES and DATABASE_URL and psycopg2 is not None)


def db_label() -> str:
    if using_postgres():
        return DATABASE_URL
    return str(SQLITE_DB_PATH)


def assert_database_ready() -> None:
    if using_postgres():
        conn = connect()
        try:
            conn.execute("SELECT 1").fetchone()
        finally:
            conn.close()
        return
    if not SQLITE_DB_PATH.exists():
        raise SystemExit(f"数据库不存在: {SQLITE_DB_PATH}")


def get_redis_client():
    if redis is None or not REDIS_URL:
        return None
    try:
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def cache_get_json(key: str):
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if not raw:
            return None
        return json.loads(raw)
    except Exception:
        return None


def cache_set_json(key: str, value: Any, ttl_seconds: int):
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False, default=str))
        return True
    except Exception:
        return False


def table_exists(conn, table_name: str) -> bool:
    # Source SQL must use '?'; _replace_qmarks converts to '%s' for psycopg2.
    # Writing literal '%s' here would be double-escaped to '%%s' and never
    # match — R32/R33 same-family bug governance, now centralised here.
    try:
        if using_postgres():
            row = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
                (table_name,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            ).fetchone()
        return bool(row and int(row[0] or 0) > 0)
    except Exception:
        return False


def apply_row_factory(conn) -> None:
    # Enable dict-shaped rows on PG (via CompatCursor). SQLite raw connections
    # use a different row_factory contract (cursor, tuple) that Row doesn't
    # satisfy, so leave them untouched.
    if using_postgres():
        try:
            conn.row_factory = Row
        except Exception:
            pass


__all__ = [
    "connect",
    "connect_sqlite",
    "using_postgres",
    "db_label",
    "assert_database_ready",
    "cache_get_json",
    "cache_set_json",
    "get_redis_client",
    "table_exists",
    "apply_row_factory",
    "execute_values",
    "Row",
    "Connection",
    "OperationalError",
    "DATABASE_URL",
    "REDIS_URL",
    "SQLITE_DB_PATH",
]
