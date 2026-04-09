#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path("/home/zanbo/zanbotest")


class FrontendApiSmokeTest(unittest.TestCase):
    def test_rbac_public_routes_and_guard_contract(self):
        config = json.loads((ROOT / "config" / "rbac_dynamic.config.json").read_text(encoding="utf-8"))
        route_permissions = config.get("route_permissions") if isinstance(config, dict) else {}
        self.assertIsInstance(route_permissions, dict)
        self.assertEqual(route_permissions.get("/login"), "public")
        self.assertEqual(route_permissions.get("/upgrade"), "public")

        router_ts = (ROOT / "apps/web/src/app/router.ts").read_text(encoding="utf-8")
        self.assertIn("{ path: '/login'", router_ts)
        self.assertIn("{ path: '/upgrade'", router_ts)
        self.assertIn("permission: 'public'", router_ts)
        self.assertIn("if (!requiredPermission && auth.rbacDynamicEnforced && !staticPermission)", router_ts)

    def test_quant_api_strategy_contract(self):
        quant_api_ts = (ROOT / "apps/web/src/services/api/quantFactors.ts").read_text(encoding="utf-8")
        self.assertIn("VITE_QUANT_API_DEV_FALLBACK", quant_api_ts)
        self.assertIn("/api/quant-factors", quant_api_ts)
        self.assertNotIn(":8004/api/quant-factors", quant_api_ts)
        self.assertNotIn(":8005/api/quant-factors", quant_api_ts)
        self.assertNotIn(":8006/api/quant-factors", quant_api_ts)

    def test_retrieval_api_uses_hyphen_path_only(self):
        research_ts = (ROOT / "apps/web/src/services/api/research.ts").read_text(encoding="utf-8")
        news_ts = (ROOT / "apps/web/src/services/api/news.ts").read_text(encoding="utf-8")
        self.assertIn("/api/ai-retrieval/search", research_ts)
        self.assertIn("/api/ai-retrieval/search", news_ts)
        self.assertNotIn("/api/ai_retrieval/search", research_ts)
        self.assertNotIn("/api/ai_retrieval/search", news_ts)

        route_file = (ROOT / "backend/routes/ai_retrieval.py").read_text(encoding="utf-8")
        self.assertIn("legacy_path_hits", route_file)
        self.assertTrue(re.search(r"ai_retrieval", route_file))

    def test_decision_board_routes_and_api_exist(self):
        router_ts = (ROOT / "apps/web/src/app/router.ts").read_text(encoding="utf-8")
        nav_ts = (ROOT / "apps/web/src/app/navigation.ts").read_text(encoding="utf-8")
        decision_api_ts = (ROOT / "apps/web/src/services/api/decision.ts").read_text(encoding="utf-8")
        self.assertIn("/research/decision", router_ts)
        self.assertIn("/research/trade-plan", router_ts)
        self.assertIn("决策看板", nav_ts)
        self.assertIn("交易计划书", nav_ts)
        self.assertIn("/api/decision/board", decision_api_ts)
        self.assertIn("/api/decision/plan", decision_api_ts)
        self.assertIn("/api/decision/strategies", decision_api_ts)
        self.assertIn("/api/decision/strategy-runs", decision_api_ts)
        self.assertIn("/api/decision/actions", decision_api_ts)
        self.assertIn("/api/decision/kill-switch", decision_api_ts)
        self.assertIn("/api/decision/strategy-runs/run", decision_api_ts)
        self.assertIn("/api/decision/snapshot/run", decision_api_ts)
        trade_plan_ts = (ROOT / "apps/web/src/pages/research/DecisionTradePlanPage.vue").read_text(encoding="utf-8")
        self.assertIn("策略实验台", trade_plan_ts)
        self.assertIn("生成策略批次", trade_plan_ts)
        self.assertIn("版本", trade_plan_ts)
        self.assertIn("日内执行计划", trade_plan_ts)
        self.assertIn("产业链联动", trade_plan_ts)
        self.assertIn("LLM 辅助说明", trade_plan_ts)

    def test_signal_graph_routes_and_api_exist(self):
        router_ts = (ROOT / "apps/web/src/app/router.ts").read_text(encoding="utf-8")
        nav_ts = (ROOT / "apps/web/src/app/navigation.ts").read_text(encoding="utf-8")
        signals_api_ts = (ROOT / "apps/web/src/services/api/signals.ts").read_text(encoding="utf-8")
        graph_page_ts = (ROOT / "apps/web/src/pages/signals/SignalChainGraphPage.vue").read_text(encoding="utf-8")
        self.assertIn("/signals/graph", router_ts)
        self.assertIn("产业链图谱", nav_ts)
        self.assertIn("/api/signals/graph", signals_api_ts)
        self.assertIn("关系图", graph_page_ts)
        self.assertIn("双中心", graph_page_ts)
        self.assertIn("以此为中心", graph_page_ts)

    def test_quant_routes_exist_in_api_catalog(self):
        server_py = (ROOT / "backend/server.py").read_text(encoding="utf-8")
        self.assertIn('"quant_factors_mine_start": "/api/quant-factors/mine/start"', server_py)
        self.assertIn('"quant_factors_backtest_start": "/api/quant-factors/backtest/start"', server_py)
        self.assertIn('"quant_factors_task": "/api/quant-factors/task?task_id=<task_id>"', server_py)
        self.assertIn('"quant_factors_health": "/api/quant-factors/health"', server_py)


if __name__ == "__main__":
    unittest.main()
