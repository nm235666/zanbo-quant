#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/minline_intraday_focus.lock"
LOG_FILE="/tmp/minline_intraday_focus.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous intraday minline focus still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start intraday minline focus (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 1800s python3 -u /home/zanbo/zanbotest/run_minline_focus_once.py \
  --token 42e5d45b54aedf3a9f339ff8010327582ae8ad2819e18dca5c3457bb \
  --limit-scores 80 \
  --limit-candidates 40 \
  --max-targets 100 >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end intraday minline focus (${APP_DB_LABEL})" >>"$LOG_FILE"
