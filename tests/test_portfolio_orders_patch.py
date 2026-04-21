#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

# Force sqlite mode before loading service/db modules.
os.environ["USE_POSTGRES"] = "0"

from backend.routes import portfolio as portfolio_routes
from services.portfolio_service import service as portfolio_service


class _FakeHandler:
    def __init__(self) -> None:
        self.status = 200
        self.payload: dict = {}

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self.status = status
        self.payload = payload


class PortfolioOrdersPatchTest(unittest.TestCase):
    def setUp(self) -> None:
        fd, db_path = tempfile.mkstemp(prefix="portfolio-orders-patch-", suffix=".db")
        os.close(fd)
        self.db_path = Path(db_path)

        self._orig_connect = portfolio_service._db.connect
        self._orig_using_postgres = portfolio_service._db.using_postgres

        portfolio_service._db.connect = lambda: sqlite3.connect(self.db_path, isolation_level=None)  # type: ignore[assignment]
        portfolio_service._db.using_postgres = lambda: False  # type: ignore[assignment]

        with sqlite3.connect(self.db_path, isolation_level=None) as conn:
            portfolio_service._ensure_portfolio_tables(conn)

    def tearDown(self) -> None:
        portfolio_service._db.connect = self._orig_connect  # type: ignore[assignment]
        portfolio_service._db.using_postgres = self._orig_using_postgres  # type: ignore[assignment]
        if self.db_path.exists():
            self.db_path.unlink()

    def _insert_order(self, order_id: str, status: str = "planned") -> None:
        now = "2026-04-20T00:00:00Z"
        with sqlite3.connect(self.db_path, isolation_level=None) as conn:
            conn.execute(
                """
                INSERT INTO portfolio_orders
                  (id, ts_code, action_type, planned_price, executed_price, size, status,
                   decision_action_id, note, executed_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    "600519.SH",
                    "buy",
                    10.0,
                    None,
                    100,
                    status,
                    "",
                    "",
                    None,
                    now,
                    now,
                ),
            )

    def _fetch_order(self, order_id: str) -> tuple[str, float | None, str | None]:
        with sqlite3.connect(self.db_path, isolation_level=None) as conn:
            row = conn.execute(
                "SELECT status, executed_price, executed_at FROM portfolio_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
        self.assertIsNotNone(row)
        return row[0], row[1], row[2]

    def test_planned_to_executed_updates_fields(self):
        order_id = "order-executed"
        self._insert_order(order_id, status="planned")
        handler = _FakeHandler()

        handled = portfolio_routes.dispatch_patch(
            handler,
            urlparse(f"/api/portfolio/orders/{order_id}"),
            {"status": "executed", "executed_price": 10.5, "executed_at": "2026-04-20T12:30:00Z"},
            {},
        )

        self.assertTrue(handled)
        self.assertEqual(handler.status, 200)
        self.assertTrue(handler.payload.get("ok"))

        status, executed_price, executed_at = self._fetch_order(order_id)
        self.assertEqual(status, "executed")
        self.assertEqual(executed_price, 10.5)
        self.assertEqual(executed_at, "2026-04-20T12:30:00Z")

    def test_planned_to_cancelled_updates_status(self):
        order_id = "order-cancelled"
        self._insert_order(order_id, status="planned")
        handler = _FakeHandler()

        handled = portfolio_routes.dispatch_patch(
            handler,
            urlparse(f"/api/portfolio/orders/{order_id}"),
            {"status": "cancelled"},
            {},
        )

        self.assertTrue(handled)
        self.assertEqual(handler.status, 200)
        self.assertTrue(handler.payload.get("ok"))

        status, executed_price, executed_at = self._fetch_order(order_id)
        self.assertEqual(status, "cancelled")
        self.assertIsNone(executed_price)
        self.assertIsNone(executed_at)

    def test_invalid_status_returns_400_with_valid_list(self):
        order_id = "order-invalid-status"
        self._insert_order(order_id, status="planned")
        handler = _FakeHandler()

        handled = portfolio_routes.dispatch_patch(
            handler,
            urlparse(f"/api/portfolio/orders/{order_id}"),
            {"status": "done"},
            {},
        )

        self.assertTrue(handled)
        self.assertEqual(handler.status, 400)
        self.assertFalse(handler.payload.get("ok"))
        self.assertIn("无效订单状态", str(handler.payload.get("error") or ""))
        self.assertEqual(handler.payload.get("valid"), sorted(portfolio_routes.VALID_ORDER_STATUSES))

    def test_invalid_executed_price_returns_400(self):
        order_id = "order-invalid-price"
        self._insert_order(order_id, status="planned")
        handler = _FakeHandler()

        handled = portfolio_routes.dispatch_patch(
            handler,
            urlparse(f"/api/portfolio/orders/{order_id}"),
            {"status": "executed", "executed_price": "abc"},
            {},
        )

        self.assertTrue(handled)
        self.assertEqual(handler.status, 400)
        self.assertFalse(handler.payload.get("ok"))
        self.assertIn("executed_price 必须是数字", str(handler.payload.get("error") or ""))

    def test_unknown_order_id_returns_404(self):
        handler = _FakeHandler()

        handled = portfolio_routes.dispatch_patch(
            handler,
            urlparse("/api/portfolio/orders/not-exists"),
            {"status": "executed", "executed_price": 10.5},
            {},
        )

        self.assertTrue(handled)
        self.assertEqual(handler.status, 404)
        self.assertFalse(handler.payload.get("ok"))
        self.assertIn("订单不存在", str(handler.payload.get("error") or ""))


if __name__ == "__main__":
    unittest.main()
