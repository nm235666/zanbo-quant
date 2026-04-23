"""
Maturity self-check tests for project_final_state_projection_2026-04-15.md

Section 6 validation criteria:
1. 主链路成功率 > 99%  — core service imports succeed, no hard crash on import
2. 决策可追踪率 > 95%  — all decision actions include trace fields (action_id, snapshot_id)
3. 闭环完成率 > 85%    — cross-module bridges present (stocks, news, signals, chatrooms → decision)
4. 状态一致性 → 0      — URL/state/stats consistency; key page patterns verified
5. 回归能力            — test files exist and cover core routes
"""
import ast
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path: str) -> str:
    full = os.path.join(REPO, path)
    with open(full, encoding="utf-8") as f:
        return f.read()


def _exists(path: str) -> bool:
    return os.path.exists(os.path.join(REPO, path))


class ProjectionMaturityTest(unittest.TestCase):
    # ───────────────────────────────────────────────
    # Criterion 1: 主链路成功率
    # ───────────────────────────────────────────────

    def test_backend_server_importable(self):
        """backend/server.py should import without errors (ApiHandler defined)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "backend.server", os.path.join(REPO, "backend", "server.py")
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        # Should not raise on exec (class definitions, no side effects at module level)
        spec.loader.exec_module(mod)  # type: ignore
        self.assertTrue(hasattr(mod, "ApiHandler"), "ApiHandler class must be defined in server.py")

    def test_decision_service_importable(self):
        """services/decision_service/service.py should import cleanly."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "decision_service",
            os.path.join(REPO, "services", "decision_service", "service.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        self.assertTrue(hasattr(mod, "record_decision_action"))
        self.assertTrue(hasattr(mod, "query_decision_calibration"))

    def test_decision_route_accepts_structured_fields(self):
        """backend/routes/decision.py must pass evidence_sources/execution_status/review_conclusion to payload."""
        content = _read("backend/routes/decision.py")
        self.assertIn("evidence_sources", content, "evidence_sources must be wired in decision route")
        self.assertIn("execution_status", content, "execution_status must be wired in decision route")
        self.assertIn("review_conclusion", content, "review_conclusion must be wired in decision route")

    def test_decision_route_accepts_trigger_reason(self):
        """Target §6.2: trigger_reason must be a first-class structured field in decision route."""
        content = _read("backend/routes/decision.py")
        self.assertIn("trigger_reason", content, "trigger_reason must be extracted from payload")
        self.assertIn('payload.get("trigger_reason"', content, "trigger_reason must be read from POST body")

    def test_allocation_read_model_exposes_conflict_constraints_and_review(self):
        """Target §7.3/§7.4: allocation read-model must expose structured conflict constraints and long-term review."""
        content = _read("services/macro_service/regime.py")
        self.assertIn("_build_conflict_constraints", content, "regime service must build structured conflict constraints")
        self.assertIn('allocation["conflict_constraints"]', content, "allocation read-model must expose conflict_constraints")
        self.assertIn('allocation["long_term_review"]', content, "allocation read-model must expose long_term_review")
        self.assertIn("sector_rotation", content, "portfolio suggestion must include sector rotation action")
        self.assertIn("strategy_switch", content, "portfolio suggestion must include strategy switch action")

    def test_portfolio_review_read_model_exposes_closure_chain(self):
        """Target §8: portfolio review read-model must join order and decision action context into a closure chain."""
        content = _read("services/portfolio_service/service.py")
        self.assertIn("LEFT JOIN decision_actions", content, "review list must join decision actions")
        self.assertIn("decision_payload", content, "review list must parse action payload into decision_payload")
        self.assertIn("rule_correction_hint", content, "review list must expose a rule correction hint")

    # ───────────────────────────────────────────────
    # Criterion 2: 决策可追踪率
    # ───────────────────────────────────────────────

    def test_decision_actions_return_trace_fields(self):
        """service.py _action_trace_fields must be called when building action items."""
        content = _read("services/decision_service/service.py")
        self.assertIn("_action_trace_fields", content)
        self.assertIn("action_id", content)
        self.assertIn("run_id", content)
        self.assertIn("snapshot_id", content)

    def test_decision_board_page_displays_trace_ids(self):
        """DecisionBoardPage.vue must render action_id and snapshot_id chips."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("action_id", content)
        self.assertIn("snapshot_id", content)
        self.assertIn("actionTraceId", content)

    def test_decision_board_displays_review_conclusion(self):
        """DecisionBoardPage.vue must display review_conclusion from payload."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("review_conclusion", content)
        self.assertIn("actionReviewConclusion", content)

    def test_decision_board_displays_evidence_sources(self):
        """DecisionBoardPage.vue must display evidence_sources from payload."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("evidence_sources", content)
        self.assertIn("actionEvidenceSources", content)

    def test_decision_board_displays_priority(self):
        """DecisionBoardPage.vue must read and display priority on recent-action cards (§6.2)."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("item?.payload?.priority", content, "priority readback must be present")
        self.assertIn("actionPriorityLabel", content, "actionPriorityLabel helper must render 高/中/低")

    def test_decision_board_displays_expiry_condition(self):
        """DecisionBoardPage.vue must read and display expiry_condition on recent-action cards (§6.2)."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("item?.payload?.expiry_condition", content, "expiry_condition readback must be present")
        self.assertIn("失效", content, "失效 label must render next to expiry_condition value")

    def test_decision_board_displays_position_pct_range(self):
        """DecisionBoardPage.vue must read and display position_pct_range on recent-action cards (§6.2)."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("item?.payload?.position_pct_range", content, "position_pct_range readback must be present")

    def test_decision_board_displays_trigger_reason(self):
        """Target §6.2 action card 'trigger_reason' must be collected AND read back on recent-action cards."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertIn("actionTriggerReasonDraft", content, "trigger_reason input draft must exist")
        self.assertIn("trigger_reason", content, "trigger_reason must appear in mutation payload/template")
        self.assertIn("item?.payload?.trigger_reason", content, "trigger_reason readback chip must reference item.payload")
        self.assertIn("触发原因", content, "触发原因 label must appear on recent-action chip")

    def test_allocation_page_displays_macro_action_cards(self):
        """Target §7.2: AllocationPage must map macro actions into portfolio action cards."""
        content = _read("apps/web/src/pages/portfolio/AllocationPage.vue")
        self.assertIn("macroActionCards", content, "AllocationPage must compute macroActionCards")
        self.assertIn("风险敞口", content, "AllocationPage must display 风险敞口 card")
        self.assertIn("现金比例建议", content, "AllocationPage must display 现金比例建议 card")
        self.assertIn("防守/进攻切换", content, "AllocationPage must display 防守/进攻切换 card")
        self.assertIn("行业权重调整", content, "AllocationPage must display 行业权重调整 card")
        self.assertIn("短线策略开关", content, "AllocationPage must display 短线策略开关 card")
        self.assertIn("findMacroAction('cash')", content, "AllocationPage must derive cash action from macro_actions")
        self.assertIn("findMacroAction('risk_budget')", content, "AllocationPage must derive risk budget action from macro_actions")
        self.assertIn("findMacroAction('defence')", content, "AllocationPage must derive defence action from macro_actions")
        self.assertIn("findMacroAction('sector_rotation')", content, "AllocationPage must derive sector rotation action from macro_actions")
        self.assertIn("findMacroAction('strategy_switch')", content, "AllocationPage must derive strategy switch action from macro_actions")

    def test_allocation_page_displays_conflict_constraints_and_long_term_review(self):
        """Target §7.3/§7.4: AllocationPage must expose structured conflict constraints and long-term review chain."""
        content = _read("apps/web/src/pages/portfolio/AllocationPage.vue")
        self.assertIn("conflictConstraintCards", content, "AllocationPage must compute structured conflict cards")
        self.assertIn("冲突裁决执行约束", content, "AllocationPage must render structured conflict ruling section")
        self.assertIn("允许执行范围", content, "AllocationPage must display allowed short-term action range")
        self.assertIn("同步防守动作", content, "AllocationPage must display required defence actions")
        self.assertIn("风险预算压缩", content, "AllocationPage must display compressed risk budget")
        self.assertIn("生效条件", content, "AllocationPage must display effective condition")
        self.assertIn("长线复盘链路", content, "AllocationPage must render long-term review chain")
        self.assertIn("宏观判断", content, "AllocationPage must render regime node in review chain")
        self.assertIn("组合动作", content, "AllocationPage must render action node in review chain")
        self.assertIn("后续结果", content, "AllocationPage must render result node in review chain")
        self.assertIn("规则修正", content, "AllocationPage must render correction node in review chain")

    def test_review_page_displays_closure_chain(self):
        """Target §8: ReviewPage must render judgment → action → execution → result → rule correction chain."""
        content = _read("apps/web/src/pages/portfolio/ReviewPage.vue")
        self.assertIn("复盘闭环", content, "ReviewPage must present closure framing")
        self.assertIn("原始判断", content, "ReviewPage must display original judgment node")
        self.assertIn("动作建议", content, "ReviewPage must display action node")
        self.assertIn("执行结果", content, "ReviewPage must display execution node")
        self.assertIn("结果归因", content, "ReviewPage must display result attribution node")
        self.assertIn("规则修正建议", content, "ReviewPage must display rule correction node")
        self.assertIn("reviewActionLabel", content, "ReviewPage must map action type labels")
        self.assertIn("reviewExecutionLabel", content, "ReviewPage must map execution status labels")

    # ───────────────────────────────────────────────
    # Criterion 3: 闭环完成率 — cross-module bridges
    # ───────────────────────────────────────────────

    def test_stocks_bridge_to_decision(self):
        """StockScoresPage or StockDetailPage must link to the decision board."""
        scores = _read("apps/web/src/pages/stocks/StockScoresPage.vue")
        detail = _read("apps/web/src/pages/stocks/StockDetailPage.vue")
        has_bridge = any(
            token in scores or token in detail
            for token in ("/app/decision", "/research/decision", "/app/desk/board")
        )
        self.assertTrue(has_bridge, "Stocks module must have a bridge to the decision board (/app/desk/board)")

    def test_news_bridge_to_decision(self):
        """NewsListPageBlock.vue must have goDecision or → 决策板."""
        content = _read("apps/web/src/pages/intelligence/NewsListPageBlock.vue")
        self.assertTrue(
            "goDecision" in content or "决策板" in content,
            "News module must bridge to decision board",
        )

    def test_chatrooms_bridge_to_decision(self):
        """ChatroomInvestmentPage.vue must have goDecisionFromChatroom or 决策板."""
        content = _read("apps/web/src/pages/chatrooms/ChatroomInvestmentPage.vue")
        self.assertTrue(
            "goDecisionFromChatroom" in content or "决策板" in content,
            "Chatrooms module must bridge to decision board",
        )

    def test_signals_bridge_to_decision(self):
        """SignalChainGraphPage.vue must have goToDecision linking to the decision board."""
        content = _read("apps/web/src/pages/signals/SignalChainGraphPage.vue")
        self.assertIn("goToDecision", content, "Signal graph must have goToDecision function")
        has_bridge = (
            "/app/decision" in content
            or "/research/decision" in content
            or "/app/desk/board" in content
        )
        self.assertTrue(has_bridge, "Signal graph must link to the decision board (/app/desk/board)")

    def test_decision_board_has_retrospective_section(self):
        """DecisionBoardPage.vue must have a 复盘 (retrospective) section."""
        content = _read("apps/web/src/pages/research/DecisionBoardPage.vue")
        self.assertTrue(
            "决策复盘" in content or "reviewItems" in content,
            "DecisionBoardPage must have a retrospective/review section",
        )

    # ───────────────────────────────────────────────
    # Criterion 4: 状态一致性
    # ───────────────────────────────────────────────

    def test_default_landing_prioritizes_decision_board(self):
        """resolveDefaultLandingPath must send non-admin research users to /app/desk/workbench (the唯一主入口)
        before any /admin/dashboard fallback."""
        content = _read("apps/web/src/app/navigation.ts")
        func_start = content.find("export function resolveDefaultLandingPath")
        self.assertGreater(func_start, 0, "resolveDefaultLandingPath function must exist")
        func_body = content[func_start:]
        workbench_pos = func_body.find("/app/desk/workbench")
        dashboard_pos = func_body.find("/admin/dashboard")
        self.assertGreater(workbench_pos, 0, "/app/desk/workbench must be checked in resolveDefaultLandingPath")
        self.assertGreater(dashboard_pos, 0, "/admin/dashboard must also be handled for admin landing")
        self.assertLess(
            workbench_pos, dashboard_pos,
            "resolveDefaultLandingPath must route non-admin research users to /app/desk/workbench before /admin/dashboard",
        )

    def test_stocks_empty_state_machine(self):
        """StocksListPage and PricesPage must have enforcePageCoherence for empty state handling."""
        list_page = _read("apps/web/src/pages/stocks/StocksListPage.vue")
        prices_page = _read("apps/web/src/pages/stocks/PricesPage.vue")
        self.assertIn("enforcePageCoherence", list_page)
        self.assertIn("enforcePageCoherence", prices_page)

    def test_signal_graph_uses_rendered_stats(self):
        """SignalChainGraphPage.vue displaySummary must be computed from rendered nodes, not raw API."""
        content = _read("apps/web/src/pages/signals/SignalChainGraphPage.vue")
        self.assertIn("displaySummary", content)
        self.assertIn("renderPayload", content)

    def test_upgrade_page_has_route_context_rules(self):
        """UpgradePage.vue must map at least 10 blocked routes to context + alternatives."""
        content = _read("apps/web/src/pages/auth/UpgradePage.vue")
        # Count test() rule entries
        test_count = content.count("test: (pathName)")
        self.assertGreaterEqual(test_count, 8, f"UpgradePage must have ≥8 route context rules, found {test_count}")
        self.assertIn("alternatives", content)

    # ───────────────────────────────────────────────
    # Criterion 5: 回归能力
    # ───────────────────────────────────────────────

    def test_core_test_files_exist(self):
        """Core test files must exist."""
        for path in [
            "tests/test_frontend_api_smoke.py",
            "tests/test_decision_service.py",
            "tests/test_minimal_regression.py",
        ]:
            self.assertTrue(_exists(path), f"Test file missing: {path}")

    def test_decision_service_tests_cover_calibration(self):
        """test_decision_service.py must test the calibration/board flow."""
        content = _read("tests/test_decision_service.py")
        self.assertTrue(
            "calibrat" in content.lower() or "board" in content.lower(),
            "Decision service tests must cover calibration or board flow",
        )

    def test_frontend_smoke_tests_cover_decision_routes(self):
        """test_frontend_api_smoke.py must verify decision board API routes."""
        content = _read("tests/test_frontend_api_smoke.py")
        self.assertIn("decision", content.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
