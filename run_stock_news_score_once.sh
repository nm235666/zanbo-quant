#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/stock_news_score.lock"
LOG_FILE="/tmp/stock_news_score.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous stock news scoring job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start stock news scoring (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 480s python3 -u /home/zanbo/zanbotest/llm_score_stock_news.py \
  --model GPT-5.4 \
  --limit 80 \
  --retry 2 \
  --sleep 0.2 >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end stock news scoring (${APP_DB_LABEL})" >>"$LOG_FILE"
