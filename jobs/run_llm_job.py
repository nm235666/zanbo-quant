#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from jobs.llm_jobs import get_llm_job_target, run_llm_job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 LLM 节点巡检任务")
    parser.add_argument(
        "--job-key",
        required=True,
        help="任务标识，如 llm_provider_nodes_probe、multi_role_v3_stale_recovery、multi_role_v3_worker_guard",
    )
    parser.add_argument("--describe", action="store_true", help="仅输出任务映射，不执行")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = get_llm_job_target(args.job_key)
    if args.describe:
        print(json.dumps(target, ensure_ascii=False))
        return 0
    result = run_llm_job(args.job_key)
    print(json.dumps({**target, "ok": result.get("ok"), "meta": result.get("meta")}, ensure_ascii=False))
    if result.get("stdout"):
        print(result["stdout"])
    if result.get("stderr"):
        print(result["stderr"])
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
