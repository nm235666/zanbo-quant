#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from jobs.llm_jobs import get_llm_job_target


ROOT_DIR = Path(__file__).resolve().parents[1]


class LlmJobsTest(unittest.TestCase):
    def test_llm_job_target_shape(self):
        target = get_llm_job_target("llm_provider_nodes_probe")
        self.assertEqual(target["job_key"], "llm_provider_nodes_probe")
        self.assertEqual(target["category"], "maintenance")
        self.assertEqual(target["runner_type"], "llm_probe")
        self.assertIn("check_gpt_provider_nodes", target["target"])
        target2 = get_llm_job_target("multi_role_v3_stale_recovery")
        self.assertEqual(target2["job_key"], "multi_role_v3_stale_recovery")
        self.assertEqual(target2["runner_type"], "multi_role_maintenance")
        self.assertIn("reclaim_stale_multi_role_v3_jobs", target2["target"])

    def test_run_llm_job_describe(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "jobs" / "run_llm_job.py"),
                "--job-key",
                "llm_provider_nodes_probe",
                "--describe",
            ],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        payload = json.loads(lines[-1])
        self.assertEqual(payload["job_key"], "llm_provider_nodes_probe")
        self.assertEqual(payload["runner_type"], "llm_probe")


if __name__ == "__main__":
    unittest.main()
