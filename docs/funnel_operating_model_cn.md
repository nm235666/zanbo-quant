# 候选漏斗运行机制（运营说明）

## 两条进池路径

| 路径 | 典型入口 | 初始状态 | 说明 |
|------|-----------|----------|------|
| **手工 / API 创建** | 漏斗页「新建候选」、`POST /api/funnel/candidates` | `ingested`（已进入） | 默认进入最左阶段，由研究员或任务再推进。 |
| **决策同步** | 决策看板动作、`sync_decision_action_to_funnel`；短名单 `_sync_shortlist_to_funnel` | 常为 `decision_ready` / `confirmed` / `deferred` 等 | 与「一格一格从已进入走」**并列**，不经过「已进入」堆积。 |

## 自动推进（评分对齐）

- **任务 key**：`funnel_ingested_score_align`（见 [job_registry.py](../job_registry.py)）。
- **行为**：对仍为 **`ingested`** 的标的，若 **`stock_scores_daily`** 在**有效 `score_date`**（默认取库内最新 `score_date`）下存在该 **`ts_code`** 行，则调用状态机 **`ingested → amplified`**。
- **审计字段**：
  - `trigger_source`：`system_rule`
  - `operator`：`scheduler`
  - `reason`：`score_row_present:{score_date}`
  - `evidence_ref`：`stock_scores_daily:{score_date}:{ts_code}`
  - `idempotency_key`：`funnel:ingested_to_amplified:{candidate_id}:{score_date}`（同日重复跑为幂等）。
- **手工触发**：`python3 jobs/run_funnel_job.py --job-key funnel_ingested_score_align` 或经 `/api/jobs/trigger?job_key=funnel_ingested_score_align`（需具备任务触发权限）。

## 复盘快照（与推进解耦）

- **表**：`funnel_review_snapshots`（由任务首次创建）。
- **任务 key**：`funnel_review_refresh`。
- **行为**：对 **`confirmed` / `executed` / `reviewed`** 的标的，在存在 **`stock_daily_prices`** 时，按标的 `updated_at` 日期锚定，计算 **T+N（默认 5）** 收盘到收盘收益率并写入快照；**不修改**漏斗主状态。
- **查询**：`GET /api/funnel/review-snapshots?candidate_id={id}`。

## 列表 API

- `GET /api/funnel/candidates` 支持 `state`、`q`（代码/名称子串）、`limit`（≤200）、`offset` 分页。

## 与群聊候选池

- **群聊候选池**为讨论线索聚合视图；**漏斗**为单标的生命周期。二者对象模型不同；若需「从群聊一键带入漏斗」，请使用漏斗页新建并填写 `ts_code`（可从群聊池跳转时带 `prefill_ts` 查询参数）。
