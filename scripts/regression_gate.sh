#!/usr/bin/env bash
# regression_gate.sh — 回归门禁
#
# 用途：整合 smoke 全套 + 截图回归，任一失败则非零退出，阻断集成。
# 用法：
#   bash scripts/regression_gate.sh            # 运行完整门禁
#   bash scripts/regression_gate.sh --smoke-only   # 只跑 smoke（不含截图回归）
#   bash scripts/regression_gate.sh --screenshots-only  # 只跑截图回归
#
# 环境变量（可在 runtime_env.sh 中配置）：
#   PLAYWRIGHT_BASE_URL     后端地址（默认 http://127.0.0.1:8002）
#   SMOKE_ADMIN_USERNAME    管理员账号
#   SMOKE_ADMIN_PASSWORD
#   SMOKE_PRO_USERNAME      Pro 用户账号
#   SMOKE_PRO_PASSWORD

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEB_DIR="$REPO_ROOT/apps/web"
GATE_LOG="$REPO_ROOT/gate_results.log"

echo "========================================" | tee "$GATE_LOG"
echo "回归门禁 — $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$GATE_LOG"
echo "========================================" | tee -a "$GATE_LOG"

MODE="${1:-}"
SMOKE_OK=0
SCREENSHOTS_OK=0
OVERALL_OK=0

run_smoke() {
  echo "" | tee -a "$GATE_LOG"
  echo ">>> [Smoke] 运行 smoke:e2e:all ..." | tee -a "$GATE_LOG"
  cd "$WEB_DIR"
  if npm run smoke:e2e:all 2>&1 | tee -a "$GATE_LOG"; then
    echo ">>> [Smoke] ✓ PASSED" | tee -a "$GATE_LOG"
    SMOKE_OK=1
  else
    echo ">>> [Smoke] ✗ FAILED" | tee -a "$GATE_LOG"
    SMOKE_OK=0
  fi
}

run_screenshots() {
  echo "" | tee -a "$GATE_LOG"
  echo ">>> [Screenshots] 运行 smoke:e2e:screenshots ..." | tee -a "$GATE_LOG"
  cd "$WEB_DIR"
  if npm run smoke:e2e:screenshots 2>&1 | tee -a "$GATE_LOG"; then
    echo ">>> [Screenshots] ✓ PASSED" | tee -a "$GATE_LOG"
    SCREENSHOTS_OK=1
  else
    echo ">>> [Screenshots] ✗ FAILED" | tee -a "$GATE_LOG"
    SCREENSHOTS_OK=0
  fi
}

case "$MODE" in
  --smoke-only)
    run_smoke
    [ "$SMOKE_OK" -eq 1 ] && OVERALL_OK=1
    ;;
  --screenshots-only)
    run_screenshots
    [ "$SCREENSHOTS_OK" -eq 1 ] && OVERALL_OK=1
    ;;
  *)
    run_smoke
    run_screenshots
    [ "$SMOKE_OK" -eq 1 ] && [ "$SCREENSHOTS_OK" -eq 1 ] && OVERALL_OK=1
    ;;
esac

echo "" | tee -a "$GATE_LOG"
echo "========================================" | tee -a "$GATE_LOG"
if [ "$OVERALL_OK" -eq 1 ]; then
  echo "门禁结果: ✓ PASSED — 可进入下一交付环节" | tee -a "$GATE_LOG"
  echo "结果日志: $GATE_LOG"
  exit 0
else
  echo "门禁结果: ✗ BLOCKED — 高风险回归失败，禁止集成" | tee -a "$GATE_LOG"
  echo "Smoke:       $([ $SMOKE_OK -eq 1 ] && echo ✓ || echo ✗)" | tee -a "$GATE_LOG"
  echo "Screenshots: $([ $SCREENSHOTS_OK -eq 1 ] && echo ✓ || echo ✗)" | tee -a "$GATE_LOG"
  echo "结果日志: $GATE_LOG"
  exit 1
fi
