#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
PID_FILE="/tmp/cn_eastmoney_10s.pid"
LOG_FILE="/tmp/cn_eastmoney_10s_supervisor.log"

mkdir -p /tmp

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE" || true)"
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "eastmoney 10s loop already running: pid=$old_pid"
    exit 0
  fi
fi

nohup bash -lc '
  echo $$ > /tmp/cn_eastmoney_10s.pid
  trap "rm -f /tmp/cn_eastmoney_10s.pid" EXIT
  while true; do
    /home/zanbo/zanbotest/run_cn_news_eastmoney_once.sh
    sleep 10
  done
' >>"$LOG_FILE" 2>&1 &

sleep 1
echo "eastmoney 10s loop started, pid=$(cat "$PID_FILE")"
