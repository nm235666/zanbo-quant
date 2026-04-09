#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest

from services.signals_service.graph import query_signal_chain_graph


class SignalsGraphTest(unittest.TestCase):
    def _mk_db(self) -> str:
        fd, path = tempfile.mkstemp(prefix="signals-graph-", suffix=".db")
        os.close(fd)
        return path

    def _create_tables(self, conn: sqlite3.Connection):
        conn.execute(
            """
            CREATE TABLE stock_codes (
                ts_code TEXT PRIMARY KEY,
                name TEXT,
                industry TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE stock_scores_daily (
                ts_code TEXT,
                name TEXT,
                industry TEXT,
                score_date TEXT,
                total_score REAL,
                industry_total_score REAL,
                score_grade TEXT,
                industry_score_grade TEXT,
                trend_score REAL,
                news_score REAL,
                risk_score REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE theme_hotspot_tracker (
                theme_name TEXT,
                theme_group TEXT,
                direction TEXT,
                theme_strength REAL,
                confidence REAL,
                evidence_count INTEGER,
                intl_news_count INTEGER,
                domestic_news_count INTEGER,
                stock_news_count INTEGER,
                chatroom_count INTEGER,
                stock_link_count INTEGER,
                latest_evidence_time TEXT,
                heat_level TEXT,
                top_terms_json TEXT,
                top_stocks_json TEXT,
                source_summary_json TEXT,
                evidence_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE theme_stock_mapping (
                theme_name TEXT,
                ts_code TEXT,
                stock_name TEXT,
                relation_type TEXT,
                weight REAL,
                source TEXT,
                notes TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE signal_state_tracker (
                signal_scope TEXT,
                signal_key TEXT,
                current_state TEXT,
                prev_state TEXT,
                driver_type TEXT,
                driver_title TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE investment_signal_tracker (
                signal_key TEXT,
                signal_type TEXT,
                subject_name TEXT,
                ts_code TEXT,
                direction TEXT,
                signal_strength REAL,
                confidence REAL,
                evidence_count INTEGER,
                news_count INTEGER,
                stock_news_count INTEGER,
                chatroom_count INTEGER,
                signal_status TEXT,
                latest_signal_date TEXT,
                source_summary_json TEXT,
                evidence_json TEXT
            )
            """
        )

    def test_empty_state_returns_shell(self):
        db_path = self._mk_db()
        try:
            payload = query_signal_chain_graph(
                sqlite3_module=sqlite3,
                db_path=db_path,
                center_type="theme",
                center_key="AI算力",
                depth=2,
                limit=12,
            )
            self.assertTrue(payload["summary"]["empty"])
            self.assertEqual(len(payload["nodes"]), 1)
            self.assertEqual(payload["center"]["status"], "empty")
            self.assertEqual(payload["edges"], [])
            self.assertEqual(payload["center_type"], "theme")
        finally:
            os.unlink(db_path)

    def test_theme_center_builds_nodes_and_edges(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            self._create_tables(conn)
            conn.executemany(
                "INSERT INTO stock_codes (ts_code, name, industry) VALUES (?, ?, ?)",
                [
                    ("000001.SZ", "中科云图", "计算机"),
                    ("000002.SZ", "算力芯片", "计算机"),
                ],
            )
            conn.executemany(
                """
                INSERT INTO stock_scores_daily (
                    ts_code, name, industry, score_date, total_score, industry_total_score,
                    score_grade, industry_score_grade, trend_score, news_score, risk_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ("000001.SZ", "中科云图", "计算机", "2026-04-01", 88, 91, "A", "A", 86, 84, 18),
                    ("000002.SZ", "算力芯片", "计算机", "2026-04-01", 79, 82, "B", "B", 72, 70, 26),
                ],
            )
            conn.execute(
                """
                INSERT INTO theme_hotspot_tracker (
                    theme_name, theme_group, direction, theme_strength, confidence, evidence_count,
                    intl_news_count, domestic_news_count, stock_news_count, chatroom_count, stock_link_count,
                    latest_evidence_time, heat_level, top_terms_json, top_stocks_json, source_summary_json, evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "AI算力",
                    "科技",
                    "看多",
                    88,
                    76,
                    12,
                    2,
                    3,
                    4,
                    1,
                    2,
                    "2026-04-01T10:00:00",
                    "高热",
                    json.dumps([{"term": "算力"}, {"term": "模型"}], ensure_ascii=False),
                    json.dumps(["000001.SZ", "000002.SZ"], ensure_ascii=False),
                    json.dumps({"intl_news": 2, "domestic_news": 3}, ensure_ascii=False),
                    json.dumps([{"title": "算力需求提升"}], ensure_ascii=False),
                ),
            )
            conn.execute(
                """
                INSERT INTO theme_stock_mapping (
                    theme_name, ts_code, stock_name, relation_type, weight, source, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("AI算力", "000001.SZ", "中科云图", "主题映射", 1.6, "seed", "核心映射"),
            )
            conn.execute(
                """
                INSERT INTO theme_stock_mapping (
                    theme_name, ts_code, stock_name, relation_type, weight, source, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("AI算力", "000002.SZ", "算力芯片", "主题映射", 1.2, "seed", "核心映射"),
            )
            conn.execute(
                """
                INSERT INTO signal_state_tracker (
                    signal_scope, signal_key, current_state, prev_state, driver_type, driver_title
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("theme", "theme:AI算力", "活跃", "观察", "news", "AI 算力热度抬升"),
            )
            conn.execute(
                """
                INSERT INTO investment_signal_tracker (
                    signal_key, signal_type, subject_name, ts_code, direction, signal_strength, confidence,
                    evidence_count, news_count, stock_news_count, chatroom_count, signal_status, latest_signal_date,
                    source_summary_json, evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "theme:AI算力",
                    "theme",
                    "AI算力",
                    "",
                    "看多",
                    0.92,
                    0.81,
                    8,
                    4,
                    2,
                    1,
                    "活跃",
                    "2026-04-01",
                    json.dumps({"source_count": 4}, ensure_ascii=False),
                    json.dumps([{"title": "算力主题持续发酵"}], ensure_ascii=False),
                ),
            )
            conn.execute(
                """
                INSERT INTO investment_signal_tracker (
                    signal_key, signal_type, subject_name, ts_code, direction, signal_strength, confidence,
                    evidence_count, news_count, stock_news_count, chatroom_count, signal_status, latest_signal_date,
                    source_summary_json, evidence_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "stock:000001.SZ",
                    "stock",
                    "中科云图",
                    "000001.SZ",
                    "看多",
                    0.86,
                    0.74,
                    6,
                    2,
                    2,
                    0,
                    "观察",
                    "2026-04-01",
                    json.dumps({"source_count": 2}, ensure_ascii=False),
                    json.dumps([{"title": "订单预期增强"}], ensure_ascii=False),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        try:
            theme_payload = query_signal_chain_graph(
                sqlite3_module=sqlite3,
                db_path=db_path,
                center_type="theme",
                center_key="AI算力",
                depth=2,
                limit=12,
            )
            self.assertFalse(theme_payload["summary"].get("empty", False))
            self.assertEqual(theme_payload["center_type"], "theme")
            self.assertGreaterEqual(theme_payload["summary"]["node_count"], 4)
            self.assertGreaterEqual(theme_payload["summary"]["edge_count"], 2)
            self.assertEqual(theme_payload["summary"]["theme_count"], 1)
            self.assertEqual(theme_payload["summary"]["industry_count"], 1)
            self.assertGreaterEqual(theme_payload["summary"]["stock_count"], 2)

            industry_payload = query_signal_chain_graph(
                sqlite3_module=sqlite3,
                db_path=db_path,
                center_type="industry",
                center_key="计算机",
                depth=2,
                limit=12,
            )
            self.assertEqual(industry_payload["center_type"], "industry")
            self.assertGreaterEqual(industry_payload["summary"]["theme_count"], 1)
            self.assertGreaterEqual(industry_payload["summary"]["stock_count"], 2)
            self.assertTrue(any(edge["relation_key"] == "industry_theme" for edge in industry_payload["edges"]))
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
