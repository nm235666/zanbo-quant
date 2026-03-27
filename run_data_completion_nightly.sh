#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/data_completion_nightly.lock"
LOG_FILE="/tmp/data_completion_nightly.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous nightly completion job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start nightly completion (${APP_DB_LABEL})" >>"$LOG_FILE"
python3 -u /home/zanbo/zanbotest/run_data_completion_batches.py \
  --token 42e5d45b54aedf3a9f339ff8010327582ae8ad2819e18dca5c3457bb \
  --governance-batch 50 \
  --events-batch 100 \
  --rounds 6 \
  --skip-flow \
  --skip-scores >>"$LOG_FILE" 2>&1 || true
python3 -u /home/zanbo/zanbotest/backfill_stock_scores_daily.py --truncate-date >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end nightly completion (${APP_DB_LABEL})" >>"$LOG_FILE"
