"""Round 32 T3 · Portfolio orders planned→executed/cancelled HTTP smoke.

Exercises the live backend at http://127.0.0.1:8002 end-to-end:
  1. Login as the pro smoke account to obtain a session token.
  2. Create a planned order via POST /api/portfolio/orders.
  3. Transition it to 'executed' via PATCH and verify fields persist.
  4. Create another planned order and transition to 'cancelled'.
  5. Cleanup: leave the created orders in the DB (they record test ts_code
     so rollback is not required; the service uses uuid ids).

Skipped when the backend is not reachable; the backend unit tests at
tests/test_portfolio_orders_patch.py already cover the service logic.
"""
from __future__ import annotations

import json
import os
import unittest
import urllib.error
import urllib.request


BACKEND = os.environ.get("SMOKE_BACKEND_URL", "http://127.0.0.1:8002").rstrip("/")
USERNAME = os.environ.get("SMOKE_PRO_USERNAME", "zanbo")
PASSWORD = os.environ.get("SMOKE_PRO_PASSWORD", "zanbo666")
TEST_TS_CODE = "000001.SZ"  # any valid format; backend does not require existence


def _req(method: str, path: str, *, token: str | None = None, payload: dict | None = None):
    body = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{BACKEND}{path}"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"error": raw}


class PortfolioOrdersFlowSmoke(unittest.TestCase):
    """Concrete HTTP-level smoke for the R32 planned→executed/cancelled flow."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            status, _ = _req("GET", "/api/health")
        except Exception as exc:  # pragma: no cover
            raise unittest.SkipTest(f"Backend not reachable at {BACKEND}: {exc}")
        if status != 200:
            raise unittest.SkipTest(f"Backend health not 200: {status}")

        status, body = _req("POST", "/api/auth/login", payload={"username": USERNAME, "password": PASSWORD})
        if status != 200 or not body.get("ok"):
            raise unittest.SkipTest(f"Login failed for smoke: status={status} body={body}")
        token = body.get("token")
        if not token:
            raise unittest.SkipTest("Login response missing token")
        cls.token = token

    def _create_planned_order(self, note: str) -> str:
        status, body = _req(
            "POST",
            "/api/portfolio/orders",
            token=self.token,
            payload={
                "ts_code": TEST_TS_CODE,
                "action_type": "buy",
                "planned_price": 10.0,
                "size": 100,
                "note": note,
            },
        )
        self.assertEqual(status, 200, f"create order failed: {body}")
        self.assertTrue(body.get("ok"), body)
        order_id = body.get("id") or body.get("order", {}).get("id")
        self.assertTrue(order_id, f"no id in create response: {body}")
        return str(order_id)

    def _fetch_order(self, order_id: str) -> dict:
        status, body = _req("GET", "/api/portfolio/orders?limit=200", token=self.token)
        self.assertEqual(status, 200)
        items = body.get("items") if isinstance(body, dict) else body
        self.assertIsInstance(items, list, f"expected list, got {type(items).__name__}; body={body}")
        for item in items:
            if str(item.get("id")) == order_id:
                return item
        self.fail(f"order {order_id} not found in list; size={len(items)}")
        return {}  # unreachable

    def test_planned_to_executed_flow(self):
        order_id = self._create_planned_order("R32 smoke · executed flow")
        self.addCleanup(self._mark_cancelled_safely, order_id)  # best-effort cleanup

        status, body = _req(
            "PATCH",
            f"/api/portfolio/orders/{order_id}",
            token=self.token,
            payload={
                "status": "executed",
                "executed_price": 10.5,
                "executed_at": "2026-04-20T12:00:00Z",
            },
        )
        self.assertEqual(status, 200, body)
        self.assertTrue(body.get("ok"), body)

        order = self._fetch_order(order_id)
        self.assertEqual(order.get("status"), "executed")
        self.assertAlmostEqual(float(order.get("executed_price")), 10.5, places=4)
        self.assertTrue(order.get("executed_at"))

    def test_planned_to_cancelled_flow(self):
        order_id = self._create_planned_order("R32 smoke · cancelled flow")
        status, body = _req(
            "PATCH",
            f"/api/portfolio/orders/{order_id}",
            token=self.token,
            payload={"status": "cancelled"},
        )
        self.assertEqual(status, 200, body)
        self.assertTrue(body.get("ok"), body)

        order = self._fetch_order(order_id)
        self.assertEqual(order.get("status"), "cancelled")

    def test_patch_rejects_invalid_status(self):
        order_id = self._create_planned_order("R32 smoke · invalid status")
        self.addCleanup(self._mark_cancelled_safely, order_id)

        status, body = _req(
            "PATCH",
            f"/api/portfolio/orders/{order_id}",
            token=self.token,
            payload={"status": "done"},  # not in VALID_ORDER_STATUSES
        )
        self.assertEqual(status, 400, body)
        self.assertFalse(body.get("ok", True))
        self.assertIn("valid", body)

    def test_patch_rejects_unknown_id(self):
        status, body = _req(
            "PATCH",
            "/api/portfolio/orders/does-not-exist-xyz",
            token=self.token,
            payload={"status": "executed", "executed_price": 1.0},
        )
        self.assertEqual(status, 404, body)

    def _mark_cancelled_safely(self, order_id: str) -> None:
        try:
            _req(
                "PATCH",
                f"/api/portfolio/orders/{order_id}",
                token=self.token,
                payload={"status": "cancelled"},
            )
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
