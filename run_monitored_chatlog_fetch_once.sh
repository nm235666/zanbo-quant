#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/monitored_chatlog_fetch.lock"
LOG_FILE="/tmp/monitored_chatlog_fetch.log"
FETCH_CMD="python3 -u /home/zanbo/zanbotest/fetch_monitored_chatlogs_once.py"

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

if ! flock -n "$LOCK_FILE" -c "$FETCH_CMD" >>"$LOG_FILE" 2>&1; then
  echo "[$(date -Iseconds)] skip: previous monitored chatlog fetch job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
fi
