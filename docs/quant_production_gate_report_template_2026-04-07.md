# 因子挖掘生产切流双门槛验收模板

## 基本信息
- 验收周期：`YYYY-MM-DD ~ YYYY-MM-DD`（建议连续 7 天）
- 切流目标：`legacy -> dual -> research`
- 验收人：

## 门槛 A：稳定性
- 任务成功率（mine/backtest）：
- 假 running（>10 分钟）数量：
- `/api/quant-factors/mine/start` P95：
- `/api/quant-factors/task` P95：
- Worker 崩溃恢复次数：

判定：
- [ ] 通过（成功率 >= 98% 且假 running 为 0）
- [ ] 未通过

## 门槛 B：策略效果（对照 alpha158_20）
- 评测集数量：
- 中位 `delta_arr`：
- 中位 `delta_calmar`：
- 中位 `delta_mdd`：
- 不同方向通过率：

判定：
- [ ] 通过（中位 delta_arr > 0，delta_calmar > 0，delta_mdd <= 0.02）
- [ ] 未通过

## 结论
- [ ] 可切换 `FACTOR_ENGINE_SWITCH_MODE=research`
- [ ] 继续 `dual` 观察
- [ ] 回退 `legacy`

## 证据清单
- 健康接口截图/日志：`/api/quant-factors/health`
- 任务样本列表（task_id）：
- 结果样本列表（含 baseline_compare）：
- 异常回归记录（参数错误、数据缺失、回测失败）：
