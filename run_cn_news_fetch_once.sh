#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/cn_news_fetch.lock"
LOG_FILE="/tmp/cn_news_fetch_cron.log"
FETCH_CMD="python3 -u /home/zanbo/zanbotest/fetch_cn_news_sina_7x24.py --limit 60 --timeout 30"
SCORE_CMD="timeout 90s python3 -u /home/zanbo/zanbotest/llm_score_news.py --source cn_sina_7x24 --limit 30 --retry 1 --sleep 0.05 --model GPT-5.4"

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

if ! flock -n "$LOCK_FILE" -c "$FETCH_CMD || true; $SCORE_CMD" >>"$LOG_FILE" 2>&1; then
  echo "[$(date -Iseconds)] skip: previous domestic news job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
fi
