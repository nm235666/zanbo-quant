#!/usr/bin/env bash
set -euo pipefail

PIDFILE="/tmp/stock_backend_supervisor.pid"
LOG="/tmp/stock_backend.log"
SUP_LOG="/tmp/stock_backend_supervisor.log"

is_running() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null
}

start() {
  if is_running; then
    echo "backend supervisor already running: pid=$(cat "$PIDFILE")"
    return 0
  fi

  nohup bash -lc '
    echo $$ > /tmp/stock_backend_supervisor.pid
    while true; do
      cd /home/zanbo/zanbotest
      PORT=8001 python3 backend/server.py >> /tmp/stock_backend.log 2>&1
      code=$?
      echo "[$(date -Iseconds)] backend exited with code $code, restarting..." >> /tmp/stock_backend.log
      sleep 1
    done
  ' > "$SUP_LOG" 2>&1 < /dev/null &

  sleep 1
  if is_running; then
    echo "backend supervisor started: pid=$(cat "$PIDFILE")"
  else
    echo "backend supervisor failed to start"
    exit 1
  fi
}

stop() {
  if is_running; then
    kill "$(cat "$PIDFILE")" || true
    rm -f "$PIDFILE"
    echo "backend supervisor stopped"
  else
    echo "backend supervisor not running"
  fi
}

status() {
  if is_running; then
    echo "backend supervisor running: pid=$(cat "$PIDFILE")"
  else
    echo "backend supervisor not running"
  fi
  ss -ltnp | rg ':8001' || true
}

case "${1:-start}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  *) echo "usage: $0 {start|stop|restart|status}"; exit 1 ;;
esac
