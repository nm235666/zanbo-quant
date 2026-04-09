#!/usr/bin/env bash
set -euo pipefail

cd /home/zanbo/zanbotest
python3 /home/zanbo/zanbotest/scripts/scheduler/check_cron_sync.py

