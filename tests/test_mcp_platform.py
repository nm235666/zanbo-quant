#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from mcp_server import config
from mcp_server.auth import verify_request
from mcp_server.audit import AUDIT_TABLE, ensure_audit_table, record_tool_audit
from mcp_server.schemas import JobTriggerArgs
from mcp_server.server import MCPHandler
from mcp_server.tools.common import require_write_allowed
from mcp_server.tools.db_tools import readonly_query
from mcp_server.schemas import ReadonlyQueryArgs


class MCPAuthTest(unittest.TestCase):
    def test_token_and_origin_required(self):
        old_token = config.MCP_ADMIN_TOKEN
        try:
            config.MCP_ADMIN_TOKEN = "secret"
            ok = verify_request(authorization="Bearer secret", origin="http://192.168.5.52:8077")
            self.assertTrue(ok.ok)

            bad_origin = verify_request(authorization="Bearer secret", origin="http://evil.example")
            self.assertFalse(bad_origin.ok)
            self.assertEqual(bad_origin.status, 403)

            bad_token = verify_request(authorization="Bearer nope", origin="http://tianbo.asia:6273")
            self.assertFalse(bad_token.ok)
            self.assertEqual(bad_token.status, 401)
        finally:
            config.MCP_ADMIN_TOKEN = old_token


class MCPReadonlyQueryTest(unittest.TestCase):
    def test_readonly_query_blocks_mutation_and_sensitive_tables(self):
        with self.assertRaisesRegex(ValueError, "only_select_allowed"):
            readonly_query(ReadonlyQueryArgs(sql="DELETE FROM portfolio_orders", limit=10))

        with self.assertRaisesRegex(ValueError, "table_not_allowlisted|sensitive"):
            readonly_query(ReadonlyQueryArgs(sql="SELECT * FROM app_auth_users LIMIT 10", limit=10))

    def test_readonly_query_adds_bounded_limit(self):
        fd, path = tempfile.mkstemp(prefix="mcp-readonly-", suffix=".db")
        os.close(fd)
        conn = sqlite3.connect(path)
        try:
            conn.execute("CREATE TABLE portfolio_orders (id TEXT, status TEXT)")
            conn.execute("INSERT INTO portfolio_orders (id, status) VALUES ('o1', 'planned')")
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            c = sqlite3.connect(path)
            c.row_factory = sqlite3.Row
            return c

        with patch("mcp_server.tools.db_tools.db.connect", connect_override), patch(
            "mcp_server.tools.db_tools.db.apply_row_factory", lambda conn: None
        ):
            result = readonly_query(ReadonlyQueryArgs(sql="SELECT id, status FROM portfolio_orders", limit=20))
        self.assertTrue(result["ok"])
        self.assertIn("LIMIT 20", result["sql"])
        self.assertEqual(result["items"][0]["id"], "o1")


class MCPWriteGuardAuditTest(unittest.TestCase):
    def test_write_guard_requires_confirm_reason_and_idempotency(self):
        old_write_enabled = config.MCP_WRITE_ENABLED
        config.MCP_WRITE_ENABLED = True
        self.addCleanup(lambda: setattr(config, "MCP_WRITE_ENABLED", old_write_enabled))

        with self.assertRaisesRegex(ValueError, "confirm_required"):
            require_write_allowed(
                JobTriggerArgs(job_key="decision_daily_snapshot", dry_run=False, actor="ops", reason="run", idempotency_key="k")
            )
        with self.assertRaisesRegex(ValueError, "reason_required"):
            require_write_allowed(
                JobTriggerArgs(
                    job_key="decision_daily_snapshot",
                    dry_run=False,
                    confirm=True,
                    actor="ops",
                    reason="",
                    idempotency_key="k",
                )
            )

        require_write_allowed(
            JobTriggerArgs(
                job_key="decision_daily_snapshot",
                dry_run=False,
                confirm=True,
                actor="ops",
                reason="manual repair",
                idempotency_key="k",
            )
        )

    def test_write_disabled_still_allows_dry_run(self):
        old_write_enabled = config.MCP_WRITE_ENABLED
        try:
            config.MCP_WRITE_ENABLED = False
            require_write_allowed(JobTriggerArgs(job_key="decision_daily_snapshot", dry_run=True))
            with self.assertRaisesRegex(ValueError, "mcp_write_disabled"):
                require_write_allowed(
                    JobTriggerArgs(
                        job_key="decision_daily_snapshot",
                        dry_run=False,
                        confirm=True,
                        actor="ops",
                        reason="manual repair",
                        idempotency_key="k",
                    )
                )
        finally:
            config.MCP_WRITE_ENABLED = old_write_enabled

    def test_audit_table_records_tool_call(self):
        fd, path = tempfile.mkstemp(prefix="mcp-audit-", suffix=".db")
        os.close(fd)

        def connect_override():
            return sqlite3.connect(path)

        with patch("mcp_server.audit.db.connect", connect_override):
            conn = connect_override()
            try:
                ensure_audit_table(conn)
            finally:
                conn.close()
            audit_id = record_tool_audit(
                request_id="r1",
                actor="ops",
                tool_name="jobs.trigger",
                args={"job_key": "decision_daily_snapshot"},
                dry_run=True,
                status="success",
                result={"ok": True},
            )
        self.assertGreater(audit_id, 0)
        conn = sqlite3.connect(path)
        try:
            row = conn.execute(f"SELECT tool_name, status FROM {AUDIT_TABLE} WHERE id = ?", (audit_id,)).fetchone()
            self.assertEqual(row[0], "jobs.trigger")
            self.assertEqual(row[1], "success")
        finally:
            conn.close()


class MCPJsonRpcTest(unittest.TestCase):
    def test_initialize_and_tool_call_shape(self):
        handler = object.__new__(MCPHandler)
        init = MCPHandler._handle_rpc(handler, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "zanbo-mcp")

        with patch("mcp_server.server.call_tool", return_value={"ok": True}), patch(
            "mcp_server.server.record_tool_audit", return_value=42
        ):
            called = MCPHandler._handle_rpc(
                handler,
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "system.health_snapshot", "arguments": {"dry_run": True}},
                },
            )
        self.assertEqual(called["result"]["structuredContent"]["audit_id"], 42)
        self.assertEqual(called["result"]["content"][0]["type"], "text")


if __name__ == "__main__":
    unittest.main(verbosity=2)
