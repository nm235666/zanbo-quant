#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/news_dedupe.lock"
LOG_FILE="/tmp/news_dedupe.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous dedupe job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start dedupe (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 900s python3 -u /home/zanbo/zanbotest/cleanup_duplicate_items.py >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end dedupe (${APP_DB_LABEL})" >>"$LOG_FILE"
