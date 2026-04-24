#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from mcp_server.audit import AUDIT_TABLE
from services.agent_runtime import create_run, decide_run, get_run, run_next_once
from services.agent_runtime import store
from services.agent_runtime.executor import execute_tool_step


class AgentRuntimeTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(prefix="agent-runtime-", suffix=".db")
        os.close(fd)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _patch_db(self):
        return patch("services.agent_runtime.store.db.connect", self._connect)

    def test_create_run_dedupes_schedule_key(self):
        with self._patch_db():
            first = create_run(agent_key="funnel_progress_agent", schedule_key="20260424")
            second = create_run(agent_key="funnel_progress_agent", schedule_key="20260424")
        self.assertEqual(first["id"], second["id"])
        self.assertTrue(second["deduped"])

    def test_executor_records_step_and_mcp_audit(self):
        with self._patch_db(), patch("mcp_server.audit.db.connect", self._connect), patch(
            "mcp_server.tools.registry.call_tool", return_value={"ok": True, "value": 1}
        ):
            run = create_run(agent_key="funnel_progress_agent")
            out = execute_tool_step(
                run_id=run["id"],
                step_index=1,
                tool_name="system.health_snapshot",
                arguments={},
            )
            loaded = get_run(run["id"])

        self.assertTrue(out["ok"])
        self.assertGreater(out["audit_id"], 0)
        self.assertEqual(loaded["steps"][0]["tool_name"], "system.health_snapshot")
        conn = self._connect()
        try:
            row = conn.execute(f"SELECT tool_name, status FROM {AUDIT_TABLE} WHERE id = ?", (out["audit_id"],)).fetchone()
        finally:
            conn.close()
        self.assertEqual(row["tool_name"], "system.health_snapshot")
        self.assertEqual(row["status"], "success")

    def test_funnel_agent_auto_writes_only_allowlisted_tools(self):
        calls = []

        def fake_step(*, run_id, step_index, tool_name, arguments=None):
            calls.append((tool_name, dict(arguments or {})))
            if tool_name == "business.closure_gap_scan":
                return {
                    "ok": True,
                    "result": {
                        "ok": True,
                        "gaps": ["funnel_ingested_backlog"],
                        "funnel_by_state": {"ingested": 3, "confirmed": 1},
                    },
                }
            return {"ok": True, "result": {"ok": True, "changed_count": 1, "warnings": []}}

        with self._patch_db(), patch("services.agent_runtime.agents.execute_tool_step", side_effect=fake_step):
            run = create_run(agent_key="funnel_progress_agent")
            out = run_next_once(worker_id="test-worker")
            loaded = get_run(run["id"])

        self.assertTrue(out["ok"])
        self.assertEqual(loaded["status"], "succeeded")
        write_calls = [(name, args) for name, args in calls if args.get("dry_run") is False]
        self.assertEqual({name for name, _ in write_calls}, {"business.repair_funnel_score_align", "business.repair_funnel_review_refresh"})
        for _, args in write_calls:
            self.assertTrue(args["confirm"])
            self.assertEqual(args["actor"], "agent:funnel_progress_agent")
            self.assertTrue(args["reason"])
            self.assertTrue(args["idempotency_key"])

    def test_auto_write_disabled_keeps_repairs_dry_run(self):
        calls = []

        def fake_step(*, run_id, step_index, tool_name, arguments=None):
            calls.append((tool_name, dict(arguments or {})))
            if tool_name == "business.closure_gap_scan":
                return {"ok": True, "result": {"ok": True, "gaps": ["funnel_ingested_backlog"], "funnel_by_state": {"ingested": 2}}}
            return {"ok": True, "result": {"ok": True, "planned_changes": [{}]}}

        with self._patch_db(), patch.dict(os.environ, {"AGENT_AUTO_WRITE_ENABLED": "0"}), patch(
            "services.agent_runtime.agents.execute_tool_step", side_effect=fake_step
        ):
            run = create_run(agent_key="funnel_progress_agent")
            run_next_once(worker_id="test-worker")
            loaded = get_run(run["id"])

        self.assertEqual(loaded["status"], "succeeded")
        self.assertFalse([args for _, args in calls if args.get("dry_run") is False])
        self.assertIn("agent_auto_write_disabled", loaded["result"]["warnings"])

    def test_portfolio_agent_waits_for_approval_then_executes_pending_step(self):
        def fake_step(*, run_id, step_index, tool_name, arguments=None):
            if tool_name == "business.portfolio_closure_scan":
                return {"ok": True, "result": {"ok": True, "requires_position_reconcile": True, "executed_orders": 1, "positions": 0}}
            if tool_name == "business.reconcile_portfolio_positions":
                return {"ok": True, "result": {"ok": True, "dry_run": True, "planned_changes": [{"ts_code": "600519.SH"}], "warnings": []}}
            return {"ok": True, "result": {"ok": True}}

        with self._patch_db(), patch("services.agent_runtime.agents.execute_tool_step", side_effect=fake_step):
            run = create_run(agent_key="portfolio_reconcile_agent")
            run_next_once(worker_id="test-worker")
            waiting = get_run(run["id"])

        self.assertEqual(waiting["status"], "waiting_approval")
        pending = [s for s in waiting["steps"] if s["status"] == "pending_approval"]
        self.assertEqual(len(pending), 1)

        with self._patch_db(), patch("mcp_server.audit.db.connect", self._connect), patch(
            "mcp_server.tools.registry.call_tool", return_value={"ok": True, "changed_count": 1}
        ):
            decided = decide_run(run["id"], actor="admin", reason="approve reconcile", decision="approved")
            loaded = get_run(run["id"])

        self.assertTrue(decided["ok"])
        self.assertEqual(loaded["status"], "succeeded")
        self.assertEqual(loaded["result"]["changed_count"], 1)
        self.assertEqual([s for s in loaded["steps"] if s["status"] == "pending_approval"], [])

    def test_rejected_approval_does_not_execute_pending_step(self):
        with self._patch_db():
            run = create_run(agent_key="portfolio_review_agent")
            store.update_run(run["id"], status="waiting_approval", approval_required=True, result={"pending_write_steps": [{}]})
            store.insert_pending_step(
                run_id=run["id"],
                step_index=1,
                tool_name="business.generate_portfolio_order_reviews",
                args={"dry_run": False, "confirm": True},
            )
            decided = decide_run(run["id"], actor="admin", reason="not now", decision="rejected")
            loaded = get_run(run["id"])

        self.assertTrue(decided["ok"])
        self.assertEqual(loaded["status"], "cancelled")
        self.assertEqual(loaded["steps"][0]["status"], "pending_approval")


if __name__ == "__main__":
    unittest.main(verbosity=2)
