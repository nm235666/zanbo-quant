#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
LOG="/tmp/realtime_services_watchdog.log"

is_running() {
  local pattern="$1"
  pgrep -f "$pattern" >/dev/null 2>&1
}

ts() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

mkdir -p /tmp

if ! is_running "ws_realtime_server.py"; then
  nohup python3 "$ROOT/ws_realtime_server.py" --host 0.0.0.0 --port 8010 >/tmp/ws_realtime.log 2>&1 &
  echo "[$(ts)] restarted ws_realtime_server.py" >>"$LOG"
fi

if ! is_running "stream_news_worker.py"; then
  nohup python3 "$ROOT/stream_news_worker.py" >/tmp/stream_news_worker.log 2>&1 &
  echo "[$(ts)] restarted stream_news_worker.py" >>"$LOG"
fi
