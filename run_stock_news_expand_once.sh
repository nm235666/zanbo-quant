#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/stock_news_expand.lock"
LOG_FILE="/tmp/stock_news_expand.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous stock news expansion still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start stock news expansion (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 1800s python3 -u /home/zanbo/zanbotest/run_stock_news_expand_focus.py \
  --limit-scores 100 \
  --limit-candidates 50 \
  --max-targets 120 \
  --page-size 20 \
  --score-after-fetch >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end stock news expansion (${APP_DB_LABEL})" >>"$LOG_FILE"
