# QuantaAlpha Runtime Checklist

适用于 QuantaAlpha 旁路集成的部署、联调与日常巡检。

## 1. 代码与目录

- 目录存在：`/home/zanbo/zanbotest/external/quantaalpha`
- 入口存在：`external/quantaalpha/launcher.py`
- 记录当前版本：
  - `cd /home/zanbo/zanbotest/external/quantaalpha && git rev-parse HEAD`

## 2. 后端接口可达

- `curl -i http://127.0.0.1:8077/api/health`
- `curl -i "http://127.0.0.1:8077/api/quant-factors/results?page=1&page_size=1"`

说明：
- `401/403` 表示路由已挂载（进入认证/权限）。
- `404` 表示路由或网关未生效。

## 3. 调度入口可用

- `python3 /home/zanbo/zanbotest/job_orchestrator.py dry-run quantaalpha_health_check`
- `python3 /home/zanbo/zanbotest/job_orchestrator.py dry-run quantaalpha_mine_daily`
- `python3 /home/zanbo/zanbotest/job_orchestrator.py dry-run quantaalpha_backtest_daily`

## 4. 实跑

- `python3 /home/zanbo/zanbotest/job_orchestrator.py run quantaalpha_health_check`
- 观察状态与告警：
  - `python3 /home/zanbo/zanbotest/job_orchestrator.py runs --job-key quantaalpha_health_check --limit 20`
  - `python3 /home/zanbo/zanbotest/job_orchestrator.py alerts --job-key quantaalpha_health_check --limit 20`

## 5. 结果与报告

- 检查 `quantaalpha_runs`、`quantaalpha_factor_results`、`quantaalpha_backtest_results` 是否有新增。
- 检查 `research_reports` 是否出现 `report_type=quant_backtest`。
- 前端在“因子挖掘工作台”可轮询任务并看到结果列表。

## 6. 回滚开关

- 若旁路异常影响联调，先关闭：
  - `ENABLE_QUANT_FACTORS=0`
- 保证不影响主链路（news/signals/research 既有路径）。
