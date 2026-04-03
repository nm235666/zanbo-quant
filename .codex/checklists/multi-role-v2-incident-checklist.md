# Multi-Role V2 Incident Checklist

适用于“85% 卡住、长期 queued、Not Found、401/403、聚合失败无恢复入口”等事故排障。

## 先判影响面

- 是否影响主前端页面可交付？
- 是否仅个别 job_id 受影响，还是全量请求受影响？
- 是否已出现用户可见报错：`Not Found`、`AUTH_REQUIRED`、`pending_user_decision` 无法继续？

## 先查接口再查代码

- `GET /api/health` 是否正常
- `POST /api/llm/multi-role/v2/start` 是否正常返回
- `GET /api/llm/multi-role/v2/task?job_id=...` 是否状态推进
- `POST /api/llm/multi-role/v2/retry-aggregate` 是否存在（排除旧进程代码）

## 关键命令

- `tail -f /tmp/stock_backend_multi_role.log`
- `rg -n "<job_id>|multi-role-v2|queued|running|aggregating|pending_user_decision|done_with_warnings|error" /tmp/stock_backend_multi_role.log`
- `python3 - <<'PY' ... select status, role_runs_json, aggregator_run_json from multi_role_analysis_history where job_id=? ... PY`

## 高概率根因分流

- `queued` 长期不动：执行线程丢失或旧进程未加载新逻辑
- `retry-aggregate` 返回 `404`：后端进程未重启到新版本
- `401/403`：登录态或权限缺失，不是路由不存在
- 聚合长期慢：provider 串行兜底 + 上游超时
- 结果不复用：`ts_code/lookback/roles` 不一致或当日判定口径不匹配

## 止血动作

- 重启 `8006` 多角色后端并确认新路由生效
- 对失联 `queued/running` 任务转失败并提示重试
- 必要时降低并发、启用队列保护，避免雪崩重试

## 复盘输出

- 现象、时间线、根因、证据、止血方案、永久修复、回滚点
- 明确“对前端展示业务的影响”和“恢复确认方式”
