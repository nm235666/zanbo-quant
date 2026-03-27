#!/usr/bin/env bash
set -euo pipefail

PID_FILE="/tmp/cn_eastmoney_10s.pid"
LOG_FILE="/tmp/cn_eastmoney_10s_watchdog.log"
START_CMD="/home/zanbo/zanbotest/start_cn_news_eastmoney_10s.sh"

is_running() {
  if [[ ! -f "$PID_FILE" ]]; then
    return 1
  fi
  local pid
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -z "$pid" ]]; then
    return 1
  fi
  kill -0 "$pid" 2>/dev/null
}

if is_running; then
  exit 0
fi

echo "[$(date -Iseconds)] eastmoney 10s loop not running, restarting" >>"$LOG_FILE"
"$START_CMD" >>"$LOG_FILE" 2>&1
