from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mcp_server import schemas


ROOT_DIR = Path(__file__).resolve().parents[2]


def check_cron_sync(_: schemas.EmptyArgs) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT_DIR / "scripts" / "scheduler" / "check_cron_sync.py")],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    lines = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
    summary: dict[str, object] = {"missing": None, "extra": None, "drift": None, "missing_keys": [], "extra_keys": [], "drift_keys": []}
    for line in lines:
        if line.startswith("missing="):
            parts = dict(piece.split("=", 1) for piece in line.split() if "=" in piece)
            for key in ("missing", "extra", "drift"):
                if key in parts:
                    try:
                        summary[key] = int(parts[key])
                    except Exception:
                        summary[key] = parts[key]
        if line.startswith("missing_keys:"):
            summary["missing_keys"] = [x for x in line.split(":", 1)[-1].split(",") if x]
        if line.startswith("extra_keys:"):
            summary["extra_keys"] = [x for x in line.split(":", 1)[-1].split(",") if x]
        if line.startswith("drift_keys:"):
            summary["drift_keys"] = [x for x in line.split(":", 1)[-1].split(",") if x]
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "summary": summary,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }

