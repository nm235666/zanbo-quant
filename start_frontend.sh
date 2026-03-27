#!/usr/bin/env bash
set -euo pipefail

cd /home/zanbo/zanbotest/frontend
python3 -m http.server 8080 --bind 0.0.0.0
