#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${DB_PATH:-${ROOT_DIR}/stock_codes.db}"
REPO_DIR="${REPO_DIR:-${ROOT_DIR}/external/strategy}"
REPORT_TYPE="${REPORT_TYPE:-strategy_repo}"
MODEL_NAME="${MODEL_NAME:-strategy_repo_sync_v1}"
INCLUDE_PREFIXES="${INCLUDE_PREFIXES:-港A美/机构日报,港A美/私人精选}"

echo "[strategy-pipeline] sync repo..."
STRATEGY_REPO_URL="${STRATEGY_REPO_URL:-git@github-wealth:WealthCodePro/Strategy.git}" \
STRATEGY_REPO_USE_SSH="${STRATEGY_REPO_USE_SSH:-0}" \
TARGET_DIR="${REPO_DIR}" \
bash "${ROOT_DIR}/scripts/sync_strategy_repo.sh"

echo "[strategy-pipeline] import reports..."
python3 "${ROOT_DIR}/jobs/import_strategy_reports.py" \
  --repo-dir "${REPO_DIR}" \
  --db-path "${DB_PATH}" \
  --report-type "${REPORT_TYPE}" \
  --model "${MODEL_NAME}" \
  --include-prefixes "${INCLUDE_PREFIXES}"

echo "[strategy-pipeline] done."
