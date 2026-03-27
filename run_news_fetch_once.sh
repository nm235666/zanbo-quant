#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="/tmp/news_fetch.lock"
LOG_FILE="/tmp/news_fetch_cron.log"
FETCH_CMD="python3 -u /home/zanbo/zanbotest/fetch_news_rss.py --limit 15 --timeout 30"
# 每轮固定评分一批，逐轮吃掉历史未评分，避免单次任务跑太久
SCORE_CMD="timeout 240s python3 -u /home/zanbo/zanbotest/llm_score_news.py --limit 20 --retry 1 --sleep 0.1 --model GPT-5.4"

cd /home/zanbo/zanbotest
. /home/zanbo/zanbotest/runtime_env.sh

# 防止任务重叠执行
if ! flock -n "$LOCK_FILE" -c "$FETCH_CMD || true; $SCORE_CMD" >>"$LOG_FILE" 2>&1; then
  echo "[$(date -Iseconds)] skip: previous international news job still running (${APP_DB_LABEL})" >>"$LOG_FILE"
fi
