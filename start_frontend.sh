#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/zanbo/zanbotest"
cd "$ROOT/apps/web"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run build
cd "$ROOT"
PORT=8002 python3 backend/server.py
