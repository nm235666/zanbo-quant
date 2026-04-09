# 自研等价数据适配层与研究栈启动 SOP（生产版）

## 1. 目标
- 为 `/research/quant-factors` 的 `research_engine` 提供自研等价数据适配层与回测底座。
- 确保 `stock_daily_prices` 数据完整、worker 进程可用、任务可观测链路可验收。

## 2. 数据准备
- 研究栈数据来源统一为数据库：
  - 主表：`stock_daily_prices`
  - 辅助表：`stock_codes`、`stock_daily_price_rollups`
- 数据要求：
  - 交易日序列连续可用
  - 全A样本覆盖满足回测门槛
  - `open/high/low/close/vol/amount/pct_chg` 字段可读
- 不再需要下载或配置 Qlib 的 `cn_data.zip`、`daily_pv.h5`。

## 3. 环境变量
- 在 `runtime_env.sh` 或启动环境中配置：
  - `FACTOR_ENGINE_SWITCH_MODE=legacy|dual|research`
  - `QUANTAALPHA_EXECUTION_MODE=hybrid|worker|inline`
  - `FACTOR_RESEARCH_UNIVERSE_MAX_SYMBOLS=1800`（默认）
  - `FACTOR_RESEARCH_PIPELINE_TIMEOUT_SECONDS=180`（默认）

## 4. 启动顺序
1. 启动后端 API（8002）。
2. 启动 research worker：
   - `python3 /home/zanbo/zanbotest/jobs/run_quantaalpha_worker.py`
3. 打开健康检查：
   - `GET /api/quant-factors/health`
4. 在前端发起 `engine_profile=research` 的 `mine` + `backtest` 各一次。

## 5. 验收检查
- `research_stack.status == ok`
- `worker.alive == true`
- `queue.pending` 可收敛
- `queue.stale_recovered_recent` 可见（僵尸任务自动收敛计数）
- `task.engine_used == research_engine`（research 可用场景）
- `baseline_compare.baseline.name == alpha158_20`
- `artifacts.data_adapter.version == self_qlib_equiv_v1`
- `artifacts.data_adapter.factor_expr_version == alpha158_20_equiv_v1`

## 6. 常见问题
- `research_data_insufficient`：行情覆盖不足或样本不够，需先补数据。
- `insufficient_symbol_coverage`：当日有效股票池不足，回测会被拒绝。
- `可计算因子不足`：字段缺失或停牌过多，导致表达式计算覆盖率不足。
