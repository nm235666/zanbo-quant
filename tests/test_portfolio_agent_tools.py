#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from mcp_server import config
from mcp_server.schemas import PortfolioOrderReviewsArgs, ReconcilePositionsArgs
from mcp_server.tools.business import generate_portfolio_order_reviews, reconcile_portfolio_positions
from services.portfolio_service.service import _ensure_portfolio_tables


class PortfolioAgentToolsTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(prefix="portfolio-agent-tools-", suffix=".db")
        os.close(fd)
        conn = sqlite3.connect(self.db_path)
        try:
            _ensure_portfolio_tables(conn)
            conn.execute("CREATE TABLE stock_daily_prices (ts_code TEXT, trade_date TEXT, close REAL)")
            conn.execute("CREATE TABLE decision_actions (id TEXT PRIMARY KEY, action_payload_json TEXT)")
            conn.execute("INSERT INTO decision_actions (id, action_payload_json) VALUES ('da1', '{}')")
            conn.execute(
                """
                INSERT INTO portfolio_orders
                    (id, ts_code, action_type, planned_price, executed_price, size, status,
                     decision_action_id, note, executed_at, created_at, updated_at)
                VALUES ('o1', '600519.SH', 'buy', 9.5, 10.0, 100, 'executed', 'da1', '', '2026-04-20T00:00:00Z', '2026-04-20T00:00:00Z', '2026-04-20T00:00:00Z')
                """
            )
            for idx, day in enumerate(["20260420", "20260421", "20260422", "20260423", "20260424", "20260427"]):
                conn.execute("INSERT INTO stock_daily_prices (ts_code, trade_date, close) VALUES ('600519.SH', ?, ?)", (day, 10.0 + idx))
            conn.commit()
        finally:
            conn.close()
        self.old_write = config.MCP_WRITE_ENABLED
        config.MCP_WRITE_ENABLED = True

    def tearDown(self):
        config.MCP_WRITE_ENABLED = self.old_write
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def test_reconcile_dry_run_and_write(self):
        with patch("mcp_server.tools.business.db.connect", self._connect), patch(
            "mcp_server.tools.business.db.apply_row_factory", lambda conn: None
        ), patch(
            "mcp_server.tools.business.db.using_postgres", lambda: False
        ):
            dry = reconcile_portfolio_positions(ReconcilePositionsArgs(dry_run=True, limit=50))
            write = reconcile_portfolio_positions(
                ReconcilePositionsArgs(
                    dry_run=False,
                    confirm=True,
                    actor="agent:test",
                    reason="approve",
                    idempotency_key="k1",
                    limit=50,
                )
            )
        self.assertTrue(dry["ok"])
        self.assertEqual(len(dry["planned_changes"]), 1)
        self.assertTrue(write["ok"])
        self.assertEqual(write["changed_count"], 1)
        conn = self._connect()
        try:
            row = conn.execute("SELECT quantity, avg_cost FROM portfolio_positions WHERE ts_code = '600519.SH'").fetchone()
        finally:
            conn.close()
        self.assertEqual(row["quantity"], 100)
        self.assertEqual(row["avg_cost"], 10.0)

    def test_order_review_dry_run_write_and_idempotent_skip(self):
        with patch("mcp_server.tools.business.db.connect", self._connect), patch(
            "mcp_server.tools.business.db.apply_row_factory", lambda conn: None
        ), patch(
            "mcp_server.tools.business.db.using_postgres", lambda: False
        ):
            dry = generate_portfolio_order_reviews(PortfolioOrderReviewsArgs(dry_run=True, horizon_days=5, limit=50))
            write = generate_portfolio_order_reviews(
                PortfolioOrderReviewsArgs(
                    dry_run=False,
                    confirm=True,
                    actor="agent:test",
                    reason="approve",
                    idempotency_key="k2",
                    horizon_days=5,
                    limit=50,
                )
            )
            dry_after = generate_portfolio_order_reviews(PortfolioOrderReviewsArgs(dry_run=True, horizon_days=5, limit=50))
        self.assertTrue(dry["ok"])
        self.assertEqual(len(dry["planned_changes"]), 1)
        self.assertTrue(write["ok"])
        self.assertEqual(write["changed_count"], 1)
        self.assertEqual(len(dry_after["planned_changes"]), 0)
        self.assertEqual(dry_after["skipped"][0]["reason"], "review_exists")


if __name__ == "__main__":
    unittest.main(verbosity=2)
