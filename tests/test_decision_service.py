#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.decision_service import service as decision_service


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE stock_codes (
            ts_code TEXT PRIMARY KEY,
            symbol TEXT,
            name TEXT,
            area TEXT,
            industry TEXT,
            market TEXT,
            list_date TEXT,
            delist_date TEXT,
            list_status TEXT
        );
        CREATE TABLE stock_scores_daily (
            score_date TEXT,
            ts_code TEXT,
            name TEXT,
            symbol TEXT,
            market TEXT,
            area TEXT,
            industry TEXT,
            industry_rank INTEGER,
            industry_count INTEGER,
            score_grade TEXT,
            industry_score_grade TEXT,
            total_score REAL,
            industry_total_score REAL,
            trend_score REAL,
            industry_trend_score REAL,
            financial_score REAL,
            industry_financial_score REAL,
            valuation_score REAL,
            industry_valuation_score REAL,
            capital_flow_score REAL,
            industry_capital_flow_score REAL,
            event_score REAL,
            industry_event_score REAL,
            news_score REAL,
            industry_news_score REAL,
            risk_score REAL,
            industry_risk_score REAL,
            latest_trade_date TEXT,
            latest_risk_date TEXT,
            score_payload_json TEXT,
            source TEXT,
            update_time TEXT
        );
        """
    )
    conn.commit()


class DecisionServiceTest(unittest.TestCase):
    def _mk_db(self) -> str:
        fd, path = tempfile.mkstemp(prefix="decision-", suffix=".db")
        os.close(fd)
        return path

    def test_board_stock_history_and_switch_flow(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            _init_schema(conn)
            conn.execute(
                """
                INSERT INTO stock_scores_daily (
                    score_date, ts_code, name, symbol, market, area, industry, industry_rank, industry_count,
                    score_grade, industry_score_grade, total_score, industry_total_score, trend_score,
                    industry_trend_score, financial_score, industry_financial_score, valuation_score,
                    industry_valuation_score, capital_flow_score, industry_capital_flow_score, event_score,
                    industry_event_score, news_score, industry_news_score, risk_score, industry_risk_score,
                    latest_trade_date, latest_risk_date, score_payload_json, source, update_time
                ) VALUES (
                    '2026-04-08', '000001.SZ', '平安银行', '000001', '主板', '深圳', '银行', 1, 8,
                    'A', 'A', 91.5, 88.2, 89.0, 86.0, 92.0, 90.0, 85.0, 83.0, 77.0, 74.0, 68.0, 63.0, 72.0, 70.0, 80.0, 78.0,
                    '2026-04-08', '2026-04-08', ?, 'unit_test', '2026-04-08T10:00:00Z'
                )
                """,
                (
                    json.dumps(
                        {
                            "score_summary": {
                                "trend": "趋势稳健",
                                "financial": "财务稳定",
                                "valuation": "估值合理",
                            }
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        with patch.dict(os.environ, {"DECISION_STRATEGY_LLM_ENABLED": "0"}, clear=False):
            with patch.object(decision_service, "query_stock_detail") as mock_detail:
                mock_detail.return_value = {
                    "profile": {"ts_code": "000001.SZ", "name": "平安银行", "industry": "银行", "market": "主板", "area": "深圳"},
                    "score": {"total_score": 91.5, "industry_total_score": 88.2, "score_grade": "A", "industry_score_grade": "A", "score_summary": {}},
                }

                board = decision_service.query_decision_board(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=5)
                self.assertEqual(board["summary"]["universe_size"], 1)
                self.assertEqual(board["market_regime"]["mode"], "aggressive")
                self.assertEqual(board["summary"]["top_score"], 91.5)
                self.assertEqual(board["shortlist"][0]["ts_code"], "000001.SZ")
                self.assertEqual(board["trade_plan"]["mode"], "aggressive")

                plan = decision_service.query_decision_trade_plan(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=5)
                self.assertEqual(plan["mode"], "aggressive")
                self.assertEqual(plan["position_plan"]["base_position"], 30)
                self.assertGreaterEqual(len(plan["checklist"]), 3)
                self.assertEqual(plan["priority_stocks"][0]["ts_code"], "000001.SZ")
                self.assertGreaterEqual(len(plan["intraday_plan"]), 3)
                self.assertIn("开盘前", [item["stage"] for item in plan["intraday_plan"]])
                self.assertIsInstance(plan["theme_links"], list)
                self.assertIn("approval_flow", plan)
                self.assertEqual(plan["approval_flow"]["state"], "pending")

                strategy_lab = decision_service.query_decision_strategy_lab(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=5)
                self.assertEqual(strategy_lab["title"], "策略实验台")
                self.assertEqual(strategy_lab["source_mode"], "preview")
                self.assertGreaterEqual(len(strategy_lab["strategies"]), 3)
                self.assertEqual(strategy_lab["summary"]["best_strategy"], strategy_lab["strategies"][0]["name"])
                self.assertIn("右侧趋势确认策略", [item["name"] for item in strategy_lab["strategies"]])
                self.assertIn("llm_feasibility_score", strategy_lab["strategies"][0])

                runs_empty = decision_service.query_decision_strategy_runs(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=10)
                self.assertEqual(runs_empty["total"], 0)

                generated = decision_service.run_decision_strategy_generation(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=5)
                self.assertEqual(generated["title"], "策略实验台")
                self.assertEqual(generated["source_mode"], "generated")
                self.assertIn("generated_run", generated)
                self.assertGreaterEqual(len(generated["strategies"]), 3)
                self.assertIn("llm_feasibility_score", generated["strategies"][0])

                runs = decision_service.query_decision_strategy_runs(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=10)
                self.assertEqual(runs["total"], 1)
                self.assertEqual(runs["items"][0]["run_version"], 1)
                self.assertIn("comparison_to_previous", runs["items"][0])

                latest_strategy = decision_service.query_decision_strategy_lab(
                    sqlite3_module=sqlite3,
                    db_path=db_path,
                    page=1,
                    page_size=5,
                    run_id=generated["generated_run"]["run_id"],
                )
                self.assertEqual(latest_strategy["run"]["run_version"], 1)
                self.assertEqual(latest_strategy["source_mode"], "stored")

                stock = decision_service.query_decision_stock(sqlite3_module=sqlite3, db_path=db_path, ts_code="000001.SZ")
                self.assertEqual(stock["score"]["total_score"], 91.5)
                self.assertTrue(stock["trade_plan"]["allow_entry"])
                self.assertIn("平安银行", stock["detail"]["profile"]["name"])

                history_empty = decision_service.query_decision_history(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=10)
                self.assertEqual(history_empty["total"], 0)

                switch_state = decision_service.get_decision_kill_switch(sqlite3_module=sqlite3, db_path=db_path)
                self.assertEqual(int(switch_state["allow_trading"]), 1)

                updated = decision_service.set_decision_kill_switch(
                    sqlite3_module=sqlite3,
                    db_path=db_path,
                    allow_trading=False,
                    reason="unit test pause",
                )
                self.assertEqual(int(updated["allow_trading"]), 0)
                self.assertEqual(updated["reason"], "unit test pause")

                snapshot = decision_service.run_decision_snapshot(sqlite3_module=sqlite3, db_path=db_path, snapshot_date="2026-04-08")
                self.assertTrue(snapshot["ok"])
                history = decision_service.query_decision_history(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=10)
                self.assertEqual(history["total"], 1)
                self.assertEqual(history["items"][0]["snapshot_date"], "2026-04-08")
                self.assertIn("summary", history["items"][0]["payload"])

                action = decision_service.record_decision_action(
                    sqlite3_module=sqlite3,
                    db_path=db_path,
                    action_type="confirm",
                    ts_code="000001.SZ",
                    stock_name="平安银行",
                    note="unit test confirm",
                    actor="tester",
                    snapshot_date="2026-04-08",
                    payload={"context": {"source": "unit_test"}},
                )
                self.assertEqual(action["action_type"], "confirm")
                actions = decision_service.query_decision_actions(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=10)
                self.assertEqual(actions["total"], 1)
                self.assertEqual(actions["items"][0]["ts_code"], "000001.SZ")
                self.assertEqual(actions["items"][0]["payload"]["context"]["source"], "unit_test")

                plan_with_action = decision_service.query_decision_trade_plan(sqlite3_module=sqlite3, db_path=db_path, page=1, page_size=5, ts_code="000001.SZ")
                self.assertEqual(plan_with_action["approval_flow"]["state"], "approved")
                self.assertGreaterEqual(len(plan_with_action["approval_flow"]["recent_actions"]), 1)

    def test_scheduled_job_uses_cn_date(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            _init_schema(conn)
            conn.commit()
        finally:
            conn.close()

        result = decision_service.run_decision_scheduled_job(sqlite3_module=sqlite3, db_path=db_path, job_key="decision_daily_snapshot")
        self.assertEqual(result["job_key"], "decision_daily_snapshot")
        self.assertRegex(result["snapshot_date"], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
