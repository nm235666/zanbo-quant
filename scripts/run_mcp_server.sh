#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

. "${ROOT_DIR}/runtime_env.sh"

if [[ -z "${MCP_ADMIN_TOKEN:-}" ]]; then
  echo "MCP_ADMIN_TOKEN is required before starting the MCP service." >&2
  exit 2
fi

exec python3 -m mcp_server.server
