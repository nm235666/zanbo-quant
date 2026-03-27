#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/stock_news_backfill_missing.lock"
LOG_FILE="/tmp/stock_news_backfill_missing.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous stock news missing backfill still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start stock news missing backfill (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 3300s python3 -u /home/zanbo/zanbotest/backfill_stock_news_items.py \
  --missing-only \
  --limit-stocks 200 \
  --page-size 20 \
  --max-pages 2 \
  --retry 2 \
  --pause 0.2 >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end stock news missing backfill (${APP_DB_LABEL})" >>"$LOG_FILE"
