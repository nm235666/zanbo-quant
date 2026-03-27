#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
LOCK_FILE="/tmp/chatroom_analysis_pipeline.lock"
LOG_FILE="/tmp/chatroom_analysis_pipeline.log"

cd "$BASE_DIR"
. /home/zanbo/zanbotest/runtime_env.sh

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[$(date -Iseconds)] skip: previous chatroom analysis pipeline still running (${APP_DB_LABEL})" >>"$LOG_FILE"
  exit 0
fi

echo "[$(date -Iseconds)] start chatroom analysis pipeline (${APP_DB_LABEL})" >>"$LOG_FILE"
timeout 1800s python3 -u /home/zanbo/zanbotest/llm_analyze_chatroom_investment_bias.py \
  --model GPT-5.4 \
  --days 7 \
  --limit 20 \
  --primary-category 投资交易 \
  --retry 2 \
  --sleep 0.5 >>"$LOG_FILE" 2>&1 || true
timeout 600s python3 -u /home/zanbo/zanbotest/build_chatroom_candidate_pool.py \
  --min-room-count 1 >>"$LOG_FILE" 2>&1 || true
echo "[$(date -Iseconds)] end chatroom analysis pipeline (${APP_DB_LABEL})" >>"$LOG_FILE"
