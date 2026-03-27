#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/news_archive.lock"
LOG_FILE="/tmp/news_archive.log"
CMD="python3 -u /home/zanbo/zanbotest/optimize_and_archive_news.py --retain-days 180 --batch-size 1000 --max-batches 50"

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

if ! flock -n "$LOCK_FILE" -c "$CMD" >>"$LOG_FILE" 2>&1; then
  echo "[$(date -Iseconds)] skip: previous archive job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
fi
