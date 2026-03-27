#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/db_health_check.lock"
LOG_FILE="/tmp/db_health_check.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous db health check still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start db health check (${APP_DB_LABEL})" >>"$LOG_FILE"
python3 -u /home/zanbo/zanbotest/db_health_check.py >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end db health check (${APP_DB_LABEL})" >>"$LOG_FILE"
