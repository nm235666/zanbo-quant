#!/usr/bin/env bash
set -euo pipefail

export USE_POSTGRES="${USE_POSTGRES:-1}"
export DATABASE_URL="${DATABASE_URL:-postgresql://zanbo@/stockapp}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
export APP_DB_LABEL="${APP_DB_LABEL:-PostgreSQL 主库}"
