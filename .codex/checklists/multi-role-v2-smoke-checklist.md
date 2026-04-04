# Multi-Role V2 Smoke Checklist

适用于 `/api/llm/multi-role/v2/*` 主链路的可交付验证。

## 启动前

- 目标是否是 `apps/web` 主前端可见问题？
- `ts_code + lookback + roles` 是否固定，避免误判复用命中？
- 是否确认当前 `8006` 进程已加载最新代码？

## API 主链路

- `POST /api/llm/multi-role/v2/start` 能正常返回 `job_id`
- `GET /api/llm/multi-role/v2/task?job_id=...` 能轮询到终态
- `POST /api/llm/multi-role/v2/decision` 三分支可用：`retry/degrade/abort`
- `POST /api/llm/multi-role/v2/retry-aggregate` 可在聚合失败后单独重试汇总

## 状态机检查

- `queued -> running -> done|done_with_warnings|error` 转换正确
- `pending_user_decision` 只在 `accept_auto_degrade=false` 且角色失败时出现
- 聚合失败后 `analysis_markdown` 应保留角色原文，不得返回空白
- `queue_position / queue_length / current_concurrent_jobs` 返回值合理

## 前端页面检查

- 页面：`/research/reports` 中多角色公司分析可完整走通
- 任务进行中能看到明确阶段文案，不是静默空白
- 聚合失败时出现“重试汇总”入口
- 点击“重试汇总”后结果有反馈成功或失败

## 验证命令

- `python3 -m py_compile backend/server.py backend/routes/stocks.py`
- `bash run_minimal_regression.sh`
- `cd /home/zanbo/zanbotest/apps/web && npm run build`

## 结束前

- 是否确认本次改动对前端展示业务的直接收益？
- 是否明确本次未覆盖的风险和后续处理项？
