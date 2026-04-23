#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from jobs.funnel_jobs import run_funnel_job


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run funnel maintenance jobs")
    parser.add_argument(
        "--job-key",
        required=True,
        help="funnel_ingested_score_align | funnel_review_refresh",
    )
    args = parser.parse_args(argv)
    result = run_funnel_job(args.job_key)
    print(json.dumps(result, ensure_ascii=False, default=str))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
