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
        self.assertIn("resolveDefaultLandingPath", router_ts)
        self.assertIn("resolveLanding: true", router_ts)

    def test_default_landing_resolver_and_upgrade_page_are_dynamic(self):
        navigation_ts = (ROOT / "apps/web/src/app/navigation.ts").read_text(encoding="utf-8")
        login_page = (ROOT / "apps/web/src/pages/auth/LoginPage.vue").read_text(encoding="utf-8")
        upgrade_page = (ROOT / "apps/web/src/pages/auth/UpgradePage.vue").read_text(encoding="utf-8")

        self.assertIn("export function resolveDefaultLandingPath", navigation_ts)
        self.assertIn("return '/intelligence/global-news'", navigation_ts)
        self.assertIn("resolveDefaultLandingPath", login_page)
        self.assertIn("authStore.permissionCatalog", upgrade_page)
        self.assertIn("auth.trend_quota", upgrade_page)
        self.assertIn("auth.multi_role_quota", upgrade_page)
        self.assertNotIn("每日最多 3 次", upgrade_page)

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
        scoreboard_page = (ROOT / "apps/web/src/pages/research/ScoreboardPage.vue").read_text(encoding="utf-8")
        rbac_config = json.loads((ROOT / "config" / "rbac_dynamic.config.json").read_text(encoding="utf-8"))
        self.assertIn("/research/decision", router_ts)
        self.assertIn("/research/scoreboard", router_ts)
        self.assertNotIn("/research/trade-plan", router_ts)
        self.assertIn("决策看板", nav_ts)
        self.assertIn("评分总览", nav_ts)
        self.assertNotIn("交易计划书", nav_ts)
        self.assertIn("/api/decision/board", decision_api_ts)
        self.assertIn("/api/decision/scores", decision_api_ts)
        self.assertIn("/api/decision/plan", decision_api_ts)
        self.assertIn("/api/decision/strategies", decision_api_ts)
        self.assertIn("/api/decision/strategy-runs", decision_api_ts)
        self.assertIn("/api/decision/actions", decision_api_ts)
        self.assertIn("/api/decision/kill-switch", decision_api_ts)
        self.assertIn("/api/decision/strategy-runs/run", decision_api_ts)
        self.assertIn("/api/decision/snapshot/run", decision_api_ts)
        self.assertIn("入选理由", scoreboard_page)
        self.assertEqual(rbac_config["route_permissions"].get("/research/scoreboard"), "research_advanced")

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

    def test_dashboard_contract_is_lightweight(self):
        dashboard_page = (ROOT / "apps/web/src/pages/dashboard/DashboardPage.vue").read_text(encoding="utf-8")
        dashboard_types = (ROOT / "apps/web/src/shared/types/api.ts").read_text(encoding="utf-8")
        server_py = (ROOT / "backend/server.py").read_text(encoding="utf-8")

        self.assertIn("快捷入口", dashboard_page)
        self.assertNotIn("API 端口 build_id 一致性", dashboard_page)
        self.assertNotIn("任务编排回放", dashboard_page)
        self.assertNotIn("api_stack_consistency", dashboard_types)
        self.assertNotIn("source_monitor", dashboard_types)
        self.assertNotIn("orchestrator_alerts", dashboard_types)
        self.assertIn('cache_get_json("api:dashboard:v2")', server_py)
        self.assertNotIn('"api_stack_consistency": query_api_stack_consistency()', server_py)

    def test_scoreboard_contract_types_exist(self):
        api_types = (ROOT / "apps/web/src/shared/types/api.ts").read_text(encoding="utf-8")
        route_file = (ROOT / "backend/routes/decision.py").read_text(encoding="utf-8")
        decision_service = (ROOT / "services/decision_service/service.py").read_text(encoding="utf-8")

        self.assertIn("export interface DecisionScoreboardPayload", api_types)
        self.assertIn("export interface ReasonPacket", api_types)
        self.assertIn("def query_decision_scoreboard", decision_service)
        self.assertIn('if parsed.path == "/api/decision/scores"', route_file)


if __name__ == "__main__":
    unittest.main()
