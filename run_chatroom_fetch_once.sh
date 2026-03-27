#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/chatroom_fetch.lock"
LOG_FILE="/tmp/chatroom_fetch_cron.log"
FETCH_CMD="python3 -u /home/zanbo/zanbotest/fetch_chatroom_list_to_db.py --once"

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

if ! flock -n "$LOCK_FILE" -c "$FETCH_CMD" >>"$LOG_FILE" 2>&1; then
  echo "[$(date -Iseconds)] skip: previous chatroom fetch job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
fi
