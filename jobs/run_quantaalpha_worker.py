#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db_compat as sqlite3

from services.quantaalpha_service import run_quantaalpha_worker_loop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 AI 因子挖掘 research worker")
    parser.add_argument("--once", action="store_true", help="仅处理一次任务后退出")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="无任务时轮询间隔（秒）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_quantaalpha_worker_loop(
        sqlite3_module=sqlite3,
        db_path=str(ROOT_DIR / "stock_codes.db"),
        poll_interval_seconds=max(0.2, float(args.poll_interval)),
        run_once=bool(args.once),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
