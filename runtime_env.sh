#!/usr/bin/env bash
set -euo pipefail

export USE_POSTGRES="${USE_POSTGRES:-1}"
export DATABASE_URL="${DATABASE_URL:-postgresql://zanbo@/stockapp}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
export APP_DB_LABEL="${APP_DB_LABEL:-PostgreSQL 主库}"
export LLM_PROVIDER_CONFIG_FILE="${LLM_PROVIDER_CONFIG_FILE:-/home/zanbo/zanbotest/config/llm_providers.json}"
export TUSHARE_TOKEN="${TUSHARE_TOKEN:-}"
export BACKEND_ADMIN_TOKEN="${BACKEND_ADMIN_TOKEN:-}"
export BACKEND_ALLOWED_ORIGINS="${BACKEND_ALLOWED_ORIGINS:-http://127.0.0.1:8077,http://localhost:8077,http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:4173,http://localhost:4173,http://tianbo.asia:6273,https://tianbo.asia:6273}"
export QLIB_DATA_DIR="${QLIB_DATA_DIR:-}"
export FACTOR_ENGINE_SWITCH_MODE="${FACTOR_ENGINE_SWITCH_MODE:-legacy}"
export QUANTAALPHA_EXECUTION_MODE="${QUANTAALPHA_EXECUTION_MODE:-hybrid}"
export FACTOR_RESEARCH_UNIVERSE_MAX_SYMBOLS="${FACTOR_RESEARCH_UNIVERSE_MAX_SYMBOLS:-1800}"
export FACTOR_RESEARCH_PIPELINE_TIMEOUT_SECONDS="${FACTOR_RESEARCH_PIPELINE_TIMEOUT_SECONDS:-180}"

QUANTAALPHA_VENV_PY="/home/zanbo/zanbotest/runtime/quantaalpha_venv/bin/python"
if [ -x "${QUANTAALPHA_VENV_PY}" ]; then
  export QUANTAALPHA_PYTHON_BIN="${QUANTAALPHA_PYTHON_BIN:-${QUANTAALPHA_VENV_PY}}"
else
  export QUANTAALPHA_PYTHON_BIN="${QUANTAALPHA_PYTHON_BIN:-python3}"
fi
