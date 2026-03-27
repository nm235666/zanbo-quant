#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/minline_backfill_recent.lock"
LOG_FILE="/tmp/minline_backfill_recent.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous minline backfill job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

mapfile -t TRADE_DATES < <(python3 /home/zanbo/zanbotest/market_calendar.py --token 42e5d45b54aedf3a9f339ff8010327582ae8ad2819e18dca5c3457bb --count 2)
if [[ "${#TRADE_DATES[@]}" -eq 0 ]]; then
  echo "[$(date -Iseconds)] no trade dates resolved (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 1
fi

run_one_day() {
  local trade_date="$1"
  echo "[$(date -Iseconds)] start minline trade_date=$trade_date (${APP_DB_LABEL})" >>"$LOG_FILE"
  timeout 3600s python3 -u /home/zanbo/zanbotest/fetch_sina_minline_all_listed.py \
    --trade-date "$trade_date" \
    --workers 6 \
    --min-workers 2 \
    --max-workers 10 \
    --retry 2 \
    --batch-size 300 \
    --max-rounds 3 \
    --max-fail-per-stock 5 \
    --stagnation-rounds 2 >>"$LOG_FILE" 2>&1 || true
  echo "[$(date -Iseconds)] end minline trade_date=$trade_date (${APP_DB_LABEL})" >>"$LOG_FILE"
}

for trade_date in "${TRADE_DATES[@]}"; do
  run_one_day "$trade_date"
done
