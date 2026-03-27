#!/usr/bin/env bash
set -euo pipefail

cd /home/zanbo/zanbotest
export USE_POSTGRES="${USE_POSTGRES:-1}"
export DATABASE_URL="${DATABASE_URL:-postgresql://zanbo@/stockapp}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
PORT=8006 python3 backend/server.py
