#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/news_daily_summary.lock"
LOG_FILE="/tmp/news_daily_summary_cron.log"
BASE_DIR="/home/zanbo/zanbotest"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

SUMMARY_DATE="$(TZ=Asia/Shanghai date +%F)"

run_with_model() {
  local model="$1"
  echo "[$(date -Iseconds)] try model=$model summary_date=$SUMMARY_DATE" >>"$LOG_FILE"
  timeout 900s python3 -u /home/zanbo/zanbotest/llm_summarize_daily_important_news.py \
    --date "$SUMMARY_DATE" \
    --importance "极高,高,中" \
    --max-news 30 \
    --min-news 8 \
    --max-prompt-chars 9000 \
    --request-timeout 180 \
    --max-retries 2 \
    --retry-backoff 2 \
    --model "$model" >>"$LOG_FILE" 2>&1
}

job() {
  local ok=0

  if run_with_model "GPT-5.4"; then
    ok=1
  elif run_with_model "kimi2.5"; then
    ok=1
  elif run_with_model "deepseek-chat"; then
    ok=1
  fi

  if [[ "$ok" -eq 1 ]]; then
    echo "[$(date -Iseconds)] summary success summary_date=$SUMMARY_DATE" >>"$LOG_FILE"
  else
    echo "[$(date -Iseconds)] summary failed summary_date=$SUMMARY_DATE" >>"$LOG_FILE"
    return 1
  fi
}

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous daily summary job still running" >>"$LOG_FILE"
  exit 0
fi

job
