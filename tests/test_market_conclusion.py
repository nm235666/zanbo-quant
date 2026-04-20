#!/usr/bin/env python3
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from backend.routes.market import _score_conflict_resolution, query_market_conclusion_from_conn


NOW = datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return list(self._rows)


class _FakeConn:
    def __init__(self, rows_by_table: dict[str, list[dict]]):
        self.rows_by_table = rows_by_table
        self.executed_sql: list[str] = []

    def execute(self, sql: str):
        self.executed_sql.append(sql)
        for table_name, rows in self.rows_by_table.items():
            if f"FROM {table_name}" in sql:
                return _FakeCursor(rows)
        raise AssertionError(f"unexpected SQL: {sql}")


class MarketConclusionScoringTest(unittest.TestCase):
    def test_single_source_returns_positive_composite(self):
        payload = _score_conflict_resolution(
            [
                {
                    "source": "theme_hotspots",
                    "direction": "看多",
                    "heat_level": "极高",
                    "theme_strength": 0.92,
                    "confidence": 0.88,
                    "published_at": "2026-04-20T11:00:00Z",
                }
            ],
            now=NOW,
        )
        self.assertEqual(payload["winner_source"], "theme_hotspots")
        self.assertEqual(payload["direction"], "看多")
        self.assertGreater(payload["confidence"], 0.7)
        self.assertFalse(payload["needs_review"])
        self.assertGreater(payload["score_breakdown"]["composite"], 0.0)

    def test_multi_source_uses_real_breakdown_and_consistency(self):
        payload = _score_conflict_resolution(
            [
                {
                    "source": "theme_hotspots",
                    "direction": "看多",
                    "heat_level": "高",
                    "theme_strength": 0.8,
                    "confidence": 0.7,
                    "published_at": "2026-04-20T10:00:00Z",
                },
                {
                    "source": "investment_signals",
                    "direction": "看多",
                    "signal_strength": 0.82,
                    "confidence": 0.76,
                    "updated_at": "2026-04-20T09:30:00Z",
                },
                {
                    "source": "news_daily_summaries",
                    "news_count": 16,
                    "summary_markdown": "市场整体偏多，看多科技与券商。",
                    "updated_at": "2026-04-20T09:00:00Z",
                },
                {
                    "source": "news_daily_summaries",
                    "news_count": 14,
                    "summary_markdown": "资金风格继续偏多，结论看多。",
                    "updated_at": "2026-04-20T08:00:00Z",
                },
            ],
            now=NOW,
        )
        self.assertEqual(payload["direction"], "看多")
        self.assertFalse(payload["needs_review"])
        self.assertEqual(payload["dissenting_sources"], [])
        self.assertGreater(payload["confidence"], 0.7)
        breakdown = {item["source"]: item for item in payload["score_breakdown"]["sources"]}
        self.assertIn("investment_signals", breakdown)
        self.assertIn("news_daily_summaries", breakdown)
        self.assertEqual(breakdown["news_daily_summaries"]["ai_consistency"], 1.0)
        self.assertGreater(breakdown["investment_signals"]["composite"], 0.0)

    def test_low_confidence_marks_needs_review_and_dissenting_sources(self):
        payload = _score_conflict_resolution(
            [
                {
                    "source": "investment_signals",
                    "direction": "看多",
                    "signal_strength": 0.05,
                    "confidence": 0.08,
                    "updated_at": "2026-04-15T08:00:00Z",
                },
                {
                    "source": "news_daily_summaries",
                    "news_count": 3,
                    "summary_markdown": "整体观点中性。",
                    "updated_at": "2026-04-18T06:00:00Z",
                },
                {
                    "source": "risk_scenarios",
                    "scenario_name": "回撤压力",
                    "pnl_impact": -0.01,
                    "max_drawdown": -0.02,
                    "var_95": -0.01,
                    "cvar_95": -0.015,
                    "updated_at": "2026-04-18T04:00:00Z",
                },
            ],
            now=NOW,
        )
        self.assertLess(payload["confidence"], 0.5)
        self.assertTrue(payload["needs_review"])
        self.assertIn("investment_signals", payload["dissenting_sources"])

    def test_risk_priority_can_win_over_bullish_sources(self):
        payload = _score_conflict_resolution(
            [
                {
                    "source": "theme_hotspots",
                    "direction": "看多",
                    "heat_level": "极高",
                    "theme_strength": 0.82,
                    "confidence": 0.75,
                    "published_at": "2026-04-20T11:00:00Z",
                },
                {
                    "source": "investment_signals",
                    "direction": "看多",
                    "signal_strength": 0.8,
                    "confidence": 0.72,
                    "updated_at": "2026-04-20T10:30:00Z",
                },
                {
                    "source": "risk_scenarios",
                    "scenario_name": "黑天鹅压力",
                    "pnl_impact": -0.08,
                    "max_drawdown": -0.18,
                    "var_95": -0.10,
                    "cvar_95": -0.14,
                    "updated_at": "2026-04-20T11:30:00Z",
                },
            ],
            now=NOW,
        )
        self.assertEqual(payload["winner_source"], "risk_scenarios")
        self.assertEqual(payload["direction"], "看空")
        self.assertFalse(payload["needs_review"])
        self.assertGreater(payload["confidence"], 0.7)

    def test_query_uses_postgres_windows_and_renamed_tables(self):
        conn = _FakeConn(
            {
                "theme_hotspot_tracker": [],
                "investment_signal_tracker": [],
                "news_daily_summaries": [],
                "stock_news_items": [],
                "macro_series": [],
                "risk_scenarios": [],
            }
        )
        payload = query_market_conclusion_from_conn(conn, lookback_hours=24, now=NOW)
        self.assertIn("conflict_resolution", payload)
        sql_blob = "\n".join(conn.executed_sql)
        self.assertIn("NOW() - INTERVAL '24 hours'", sql_blob)
        self.assertIn("FROM stock_news_items", sql_blob)
        self.assertIn("FROM macro_series", sql_blob)
        self.assertNotIn("datetime('now'", sql_blob)
        self.assertNotIn("FROM stock_news ", sql_blob)
        self.assertNotIn("FROM macro_indicators", sql_blob)


if __name__ == "__main__":
    unittest.main()
