#!/usr/bin/env python3
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChatroomCandidatePoolBuilderTest(unittest.TestCase):
    def _mk_db(self) -> str:
        fd, path = tempfile.mkstemp(prefix="chatroom-pool-", suffix=".db")
        os.close(fd)
        return path

    def test_signal_predictions_are_merged_into_candidate_pool(self):
        db_path = self._mk_db()
        conn = sqlite3.connect(db_path)
        try:
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
                INSERT INTO stock_codes (ts_code, symbol, name)
                VALUES ('002850.SZ', '002850', '科达利');

                CREATE TABLE chatroom_investment_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id TEXT,
                    talker TEXT,
                    analysis_date TEXT,
                    targets_json TEXT,
                    update_time TEXT
                );

                CREATE TABLE chatroom_stock_signal_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    talker TEXT,
                    room_id TEXT,
                    signal_date TEXT,
                    signal_time TEXT,
                    ts_code TEXT,
                    stock_name TEXT,
                    direction TEXT,
                    source_content TEXT,
                    room_strength_label TEXT,
                    validation_status TEXT,
                    target_trade_date TEXT,
                    return_1d REAL,
                    verdict TEXT
                );
                INSERT INTO chatroom_stock_signal_predictions (
                    talker, room_id, signal_date, signal_time, ts_code, stock_name, direction,
                    source_content, room_strength_label, validation_status, target_trade_date, return_1d, verdict
                ) VALUES (
                    '资讯共享二', '46208217091@chatroom', '2026-03-29', '23:13:18',
                    '002850.SZ', '科达利', '看多', '优先宁德、璞泰来，其次亿纬、科达利',
                    'normal', 'evaluated', '20260330', 10.0, 'hit'
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

        env = {**os.environ, "USE_POSTGRES": "0"}
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "build_chatroom_candidate_pool.py"),
                "--db-path",
                db_path,
                "--window-days",
                "7",
                "--signal-window-days",
                "30",
            ],
            cwd=str(ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute(
                """
                SELECT candidate_name, candidate_type, ts_code, dominant_bias, mention_count,
                       room_count, latest_analysis_date, sample_reasons_json
                FROM chatroom_stock_candidate_pool
                WHERE ts_code = '002850.SZ'
                """
            ).fetchone()
        finally:
            conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "科达利")
        self.assertEqual(row[1], "股票")
        self.assertEqual(row[3], "看多")
        self.assertEqual(row[4], 1)
        self.assertEqual(row[5], 1)
        self.assertEqual(row[6], "2026-03-29")
        self.assertIn("chatroom_stock_signal_predictions", row[7])


if __name__ == "__main__":
    unittest.main()
