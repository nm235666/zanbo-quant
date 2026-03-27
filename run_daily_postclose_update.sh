#!/usr/bin/env bash
set -euo pipefail

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

LOG_FILE="/tmp/stock_postclose_update.log"
LOCK_FILE="/tmp/stock_postclose_update.lock"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] another postclose update is still running, skip" >> "$LOG_FILE"
  exit 0
fi

run_step() {
  local name="$1"
  shift
  echo "[$(date -Iseconds)] START $name" >> "$LOG_FILE"
  if "$@" >> "$LOG_FILE" 2>&1; then
    echo "[$(date -Iseconds)] OK    $name" >> "$LOG_FILE"
  else
    echo "[$(date -Iseconds)] FAIL  $name" >> "$LOG_FILE"
  fi
}

echo "[$(date -Iseconds)] ===== postclose update begin (${APP_DB_LABEL}) =====" >> "$LOG_FILE"

run_step "stocks_and_prices" python3 auto_update_stocks_and_prices.py --pause 0.02
run_step "valuation_daily" python3 backfill_stock_valuation_daily.py --lookback-days 5 --pause 0.02
run_step "capital_flow_stock" python3 backfill_capital_flow_stock.py --lookback-days 5 --pause 0.02
run_step "capital_flow_market" python3 backfill_capital_flow_market.py --lookback-days 5 --pause 0.02
run_step "fx_daily" python3 backfill_fx_daily.py --lookback-days 10 --pause 0.02
run_step "rate_curve_points" python3 backfill_rate_curve_points.py --lookback-days 10 --pause 0.02
run_step "spread_daily" python3 backfill_spread_daily.py --lookback-days 10
run_step "risk_scenarios" python3 backfill_risk_scenarios.py --lookback-bars 120
run_step "financials_fast" python3 fast_backfill_stock_financials.py --recent-periods 4 --pause 0.02
run_step "financials_missing" python3 backfill_missing_stock_financials.py --recent-periods 4 --pause 0.05
run_step "stock_events_daily" python3 update_daily_stock_events.py
run_step "stock_scores_daily" python3 backfill_stock_scores_daily.py --truncate-date

echo "[$(date -Iseconds)] ===== postclose update end (${APP_DB_LABEL}) =====" >> "$LOG_FILE"
