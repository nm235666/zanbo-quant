#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from services.funnel_service import service as funnel_service


def _table_exists_sqlite(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return bool(row and int(row[0] or 0) > 0)


class FunnelServiceStatusTest(unittest.TestCase):
    def _mk_db(self) -> str:
        fd, path = tempfile.mkstemp(prefix="funnel-", suffix=".db")
        os.close(fd)
        return path

    def test_metrics_marks_degraded_when_upstream_ready_but_funnel_missing(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("CREATE TABLE stock_scores_daily (score_date TEXT)")
            conn.execute("INSERT INTO stock_scores_daily (score_date) VALUES ('2026-04-23')")
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            metrics = funnel_service.get_funnel_metrics()
            listing = funnel_service.list_candidates()

        self.assertEqual(metrics["status"], "degraded")
        self.assertIn("funnel_candidates", metrics["missing_inputs"])
        self.assertEqual(metrics["upstream_scores"]["latest_count"], 1)
        self.assertEqual(listing["status"], "degraded")
        self.assertEqual(listing["total"], 0)
        self.assertEqual(listing["upstream_scores"]["latest_score_date"], "2026-04-23")

    def test_metrics_ready_when_funnel_has_rows(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("CREATE TABLE stock_scores_daily (score_date TEXT)")
            conn.execute("INSERT INTO stock_scores_daily (score_date) VALUES ('2026-04-23')")
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES ('cid-1', '000001.SZ', '平安银行', 'decision_daily_snapshot', 'decision_action', 'test', 'snap:2026-04-23', 'decision_ready', 1, '2026-04-23T01:00:00Z', '2026-04-23T01:00:00Z')
                """
            )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            metrics = funnel_service.get_funnel_metrics()
            listing = funnel_service.list_candidates(limit=10, offset=0)

        self.assertEqual(metrics["status"], "ready")
        self.assertEqual(metrics["total"], 1)
        self.assertEqual(metrics.get("conversion_rate"), 0.0)
        self.assertIsNone(metrics.get("avg_days_to_decision"))
        self.assertEqual(listing["status"], "ready")
        self.assertEqual(listing["total"], 1)
        self.assertEqual(listing["items"][0]["ts_code"], "000001.SZ")
        self.assertEqual(int(listing["items"][0].get("state_version") or 0), 1)

    def test_list_and_detail_attach_evidence_when_requested(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """
                CREATE TABLE stock_scores_daily (
                    score_date TEXT,
                    ts_code TEXT
                )
                """
            )
            conn.execute("INSERT INTO stock_scores_daily (score_date, ts_code) VALUES ('2026-04-23', '000001.SZ')")
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES ('cid-evidence', '000001.SZ', '平安银行', 'test', 'researcher', 'test', '', 'ingested', 1, '2026-04-23T00:00:00Z', '2026-04-23T00:00:00Z')
                """
            )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        packet = {
            "ts_code": "000001.SZ",
            "evidence_status": "incomplete",
            "evidence_chain_complete": False,
            "missing_evidence": ["signals"],
            "warning_messages": ["缺少投资信号"],
        }
        summary = {
            "evidence_status": "incomplete",
            "evidence_chain_complete": False,
            "missing_evidence": ["signals"],
            "signal_count": 0,
        }

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite), patch.object(
            funnel_service, "build_stock_evidence_packet", return_value=packet
        ), patch.object(funnel_service, "summarize_evidence_packet", return_value=summary):
            plain = funnel_service.list_candidates(limit=10, offset=0)
            enriched = funnel_service.list_candidates(limit=10, offset=0, include_evidence=True)
            detail = funnel_service.get_candidate("cid-evidence")

        self.assertNotIn("evidence_summary", plain["items"][0])
        self.assertEqual(enriched["items"][0]["evidence_summary"]["missing_evidence"], ["signals"])
        self.assertEqual(detail["evidence_packet"]["ts_code"], "000001.SZ")
        self.assertEqual(detail["missing_evidence"], ["signals"])
        self.assertFalse(detail["evidence_chain_complete"])

    def test_metrics_avg_days_when_first_decision_transition_exists(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("CREATE TABLE stock_scores_daily (score_date TEXT)")
            conn.execute("INSERT INTO stock_scores_daily (score_date) VALUES ('2026-04-23')")
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE funnel_transitions (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    from_state TEXT NOT NULL DEFAULT '',
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    evidence_ref TEXT NOT NULL DEFAULT '',
                    trigger_source TEXT NOT NULL DEFAULT '',
                    operator TEXT NOT NULL DEFAULT '',
                    idempotency_key TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES (
                    'cid-avg', '000002.SZ', '万科A', 'test', 'researcher', '', '', 'ingested', 1,
                    '2026-04-01T00:00:00Z', '2026-04-01T00:00:00Z'
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_transitions (
                    id, candidate_id, from_state, to_state, reason, evidence_ref, trigger_source, operator, idempotency_key, created_at
                ) VALUES (
                    'tid-1', 'cid-avg', '', 'decision_ready', 'enter', '', 'researcher', 'u1', '', '2026-04-03T00:00:00Z'
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            metrics = funnel_service.get_funnel_metrics()

        self.assertEqual(metrics["status"], "ready")
        self.assertAlmostEqual(float(metrics["avg_days_to_decision"]), 2.0, places=1)
        self.assertEqual(metrics.get("conversion_rate"), 0.0)

    def test_promote_ingested_when_score_present(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """
                CREATE TABLE stock_scores_daily (
                    score_date TEXT,
                    ts_code TEXT
                )
                """
            )
            conn.execute("INSERT INTO stock_scores_daily (score_date, ts_code) VALUES ('2026-04-23', '000001.SZ')")
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE funnel_transitions (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    from_state TEXT NOT NULL DEFAULT '',
                    to_state TEXT NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    evidence_ref TEXT NOT NULL DEFAULT '',
                    trigger_source TEXT NOT NULL DEFAULT '',
                    operator TEXT NOT NULL DEFAULT '',
                    idempotency_key TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES (
                    'cid-promo', '000001.SZ', 'Ping', 't', 't', '', '', 'ingested', 1,
                    '2026-04-20T00:00:00Z', '2026-04-20T00:00:00Z'
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            out = funnel_service.promote_ingested_when_score_present(score_date="2026-04-23")

        self.assertTrue(out.get("ok"))
        self.assertEqual(out.get("promoted"), 1)
        self.assertEqual(out.get("scanned"), 1)
        conn2 = sqlite3.connect(db_path)
        try:
            row = conn2.execute("SELECT state FROM funnel_candidates WHERE id = 'cid-promo'").fetchone()
            self.assertEqual(str(row[0]), "amplified")
        finally:
            conn2.close()

    def test_list_candidates_ts_q_filter(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("CREATE TABLE stock_scores_daily (score_date TEXT)")
            conn.execute("INSERT INTO stock_scores_daily (score_date) VALUES ('2026-04-23')")
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES
                ('a', '000001.SZ', 'A', '', '', '', '', 'ingested', 1, '2026-04-20T00:00:00Z', '2026-04-20T00:00:00Z'),
                ('b', '600000.SH', 'B', '', '', '', '', 'ingested', 1, '2026-04-21T00:00:00Z', '2026-04-21T00:00:00Z')
                """
            )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            listing = funnel_service.list_candidates(ts_q="600", limit=50, offset=0)

        self.assertEqual(listing["total"], 1)
        self.assertEqual(len(listing["items"]), 1)
        self.assertEqual(listing["items"][0]["ts_code"], "600000.SH")

    def test_refresh_funnel_review_snapshots(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """
                CREATE TABLE funnel_candidates (
                    id TEXT PRIMARY KEY,
                    ts_code TEXT,
                    name TEXT,
                    source TEXT,
                    trigger_source TEXT,
                    reason TEXT,
                    evidence_ref TEXT,
                    state TEXT,
                    state_version INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                INSERT INTO funnel_candidates (
                    id, ts_code, name, source, trigger_source, reason, evidence_ref, state, state_version, created_at, updated_at
                ) VALUES (
                    'cid-rev', '000001.SZ', 'P', '', '', '', '', 'confirmed', 3,
                    '2026-04-01T00:00:00Z', '2026-04-01T12:00:00Z'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE stock_daily_prices (
                    ts_code TEXT,
                    trade_date TEXT,
                    close REAL
                )
                """
            )
            days = [
                ("20260401", 100.0),
                ("20260402", 101.0),
                ("20260403", 102.0),
                ("20260404", 103.0),
                ("20260405", 104.0),
                ("20260408", 110.0),
            ]
            for td, cl in days:
                conn.execute(
                    "INSERT INTO stock_daily_prices (ts_code, trade_date, close) VALUES (?, ?, ?)",
                    ("000001.SZ", td, cl),
                )
            conn.commit()
        finally:
            conn.close()

        def connect_override():
            return sqlite3.connect(db_path)

        def apply_row_factory(conn):
            conn.row_factory = sqlite3.Row

        with patch.object(funnel_service._db, "connect", side_effect=connect_override), patch.object(
            funnel_service._db, "apply_row_factory", side_effect=apply_row_factory
        ), patch.object(funnel_service._db, "table_exists", side_effect=_table_exists_sqlite):
            out = funnel_service.refresh_funnel_review_snapshots(horizon_days=5, limit=10)

        self.assertTrue(out.get("ok"))
        self.assertGreaterEqual(out.get("written", 0), 1)
        conn2 = sqlite3.connect(db_path)
        try:
            cnt = conn2.execute("SELECT COUNT(*) FROM funnel_review_snapshots WHERE candidate_id = 'cid-rev'").fetchone()[0]
            self.assertGreaterEqual(int(cnt), 1)
        finally:
            conn2.close()


if __name__ == "__main__":
    unittest.main()
