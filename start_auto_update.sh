#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
INTERVAL_SECONDS="${1:-3600}"
LOG_FILE="/tmp/stock_auto_update.log"

cd "$ROOT"

echo "[$(date -Iseconds)] auto update started, interval=${INTERVAL_SECONDS}s" >> "$LOG_FILE"
while true; do
  echo "[$(date -Iseconds)] running auto_update_stocks_and_prices.py" >> "$LOG_FILE"
  python3 auto_update_stocks_and_prices.py --pause 0.02 >> "$LOG_FILE" 2>&1 || true
  sleep "$INTERVAL_SECONDS"
done
