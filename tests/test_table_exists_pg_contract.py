#!/usr/bin/env python3
from __future__ import annotations

import unittest

import db_compat


class _FakeCursor:
    def __init__(self, one=None):
        self._one = one

    def fetchone(self):
        return self._one


class _SQLCaptureConn:
    def __init__(self, result=(1,)):
        self.sql_calls: list[tuple[str, tuple]] = []
        self._result = result

    def execute(self, sql: str, params=()):
        self.sql_calls.append((sql, tuple(params or ())))
        return _FakeCursor(self._result)


class _RaisingConn:
    def execute(self, sql: str, params=()):
        raise RuntimeError("boom")


class TableExistsPgContractTest(unittest.TestCase):
    def test_public_table_exists_pg_uses_qmark_placeholder(self):
        conn = _SQLCaptureConn()
        orig = db_compat.using_postgres
        db_compat.using_postgres = lambda: True  # type: ignore[assignment]
        try:
            ok = db_compat.table_exists(conn, "macro_regimes")
        finally:
            db_compat.using_postgres = orig  # type: ignore[assignment]

        self.assertTrue(ok)
        self.assertEqual(len(conn.sql_calls), 1)
        sql, params = conn.sql_calls[0]
        self.assertIn("information_schema.tables", sql)
        self.assertIn("table_name = ?", sql)
        self.assertNotIn("table_name = %s", sql)
        self.assertEqual(params, ("macro_regimes",))

    def test_public_table_exists_sqlite_queries_sqlite_master(self):
        conn = _SQLCaptureConn()
        orig = db_compat.using_postgres
        db_compat.using_postgres = lambda: False  # type: ignore[assignment]
        try:
            ok = db_compat.table_exists(conn, "portfolio_orders")
        finally:
            db_compat.using_postgres = orig  # type: ignore[assignment]

        self.assertTrue(ok)
        self.assertEqual(len(conn.sql_calls), 1)
        sql, params = conn.sql_calls[0]
        self.assertIn("sqlite_master", sql)
        self.assertIn("name=?", sql)
        self.assertEqual(params, ("portfolio_orders",))

    def test_public_table_exists_returns_false_on_exception(self):
        orig = db_compat.using_postgres
        db_compat.using_postgres = lambda: True  # type: ignore[assignment]
        try:
            ok = db_compat.table_exists(_RaisingConn(), "anything")
        finally:
            db_compat.using_postgres = orig  # type: ignore[assignment]
        self.assertFalse(ok)

    def test_public_apply_row_factory_pg_sets_row_sqlite_is_noop(self):
        class _Conn:
            def __init__(self):
                self.row_factory = None

        orig = db_compat.using_postgres

        pg_conn = _Conn()
        db_compat.using_postgres = lambda: True  # type: ignore[assignment]
        try:
            db_compat.apply_row_factory(pg_conn)
        finally:
            db_compat.using_postgres = orig  # type: ignore[assignment]
        self.assertIs(pg_conn.row_factory, db_compat.Row)

        sqlite_conn = _Conn()
        db_compat.using_postgres = lambda: False  # type: ignore[assignment]
        try:
            db_compat.apply_row_factory(sqlite_conn)
        finally:
            db_compat.using_postgres = orig  # type: ignore[assignment]
        self.assertIsNone(sqlite_conn.row_factory)


if __name__ == "__main__":
    unittest.main(verbosity=2)
