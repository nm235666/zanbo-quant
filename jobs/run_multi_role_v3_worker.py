#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db_compat as sqlite3
from backend import server as backend_server
from services.agent_service.multi_role_v3 import ensure_multi_role_v3_tables, run_multi_role_v3_worker_loop


def build_runtime():
    return {
        "build_context": lambda *, ts_code, lookback: backend_server.build_multi_role_context(ts_code=ts_code, lookback=lookback),
        "llm_call": lambda *, node_key, prompt, strong, timeout_s: backend_server._multi_role_v3_call_llm(
            node_key=node_key,
            prompt=prompt,
            strong=strong,
            timeout_s=timeout_s,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Multi-Role V3 independent worker loop")
    parser.add_argument("--once", action="store_true", help="Process at most one queued job and exit")
    parser.add_argument("--poll-seconds", type=float, default=float(os.getenv("MULTI_ROLE_V3_WORKER_POLL_SECONDS", "1.0") or 1.0))
    args = parser.parse_args(argv)

    conn = sqlite3.connect(backend_server.DB_PATH)
    try:
        ensure_multi_role_v3_tables(conn)
    finally:
        conn.close()

    runtime = build_runtime()
    run_multi_role_v3_worker_loop(
        sqlite3_module=sqlite3,
        db_path=backend_server.DB_PATH,
        runtime=runtime,
        once=bool(args.once),
        poll_seconds=max(0.2, float(args.poll_seconds or 1.0)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
