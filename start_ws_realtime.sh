#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
cd "$ROOT"

nohup python3 "$ROOT/ws_realtime_server.py" --host 0.0.0.0 --port 8010 >/tmp/ws_realtime.log 2>&1 &
echo $!
