#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
cd "$ROOT"

nohup python3 "$ROOT/stream_news_worker.py" >/tmp/stream_news_worker.log 2>&1 &
echo $!
