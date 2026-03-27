#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
RUNNER="${BASE_DIR}/run_monitored_chatlog_fetch_once.sh"
CRON_EXPR="${1:-*/3 * * * *}"
CRON_CMD="/bin/bash ${RUNNER}"
CRON_LINE="${CRON_EXPR} ${CRON_CMD}"

tmp_file="$(mktemp)"
existing_file="$(mktemp)"

crontab -l 2>/dev/null | grep -vF "${CRON_CMD}" >"${existing_file}" || true
cat "${existing_file}" >"${tmp_file}"
echo "${CRON_LINE}" >>"${tmp_file}"
crontab "${tmp_file}"

rm -f "${tmp_file}" "${existing_file}"

echo "installed cron for PostgreSQL 主库: ${CRON_LINE}"
