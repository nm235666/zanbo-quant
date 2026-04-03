# Multi-Role V2 Hotfix Prompt

```text
请按“前端可交付优先”的热修复方式处理 multi-role v2 问题。

硬约束：
- 不改公开 API 兼容性
- 不动 v1 主路径
- 不做跨模块重构
- 先保证 apps/web 页面可恢复使用

输出顺序必须是：
1. 任务理解（如何服务前端展示业务）
2. 影响范围（文件与接口）
3. 根因与证据（日志/DB/返回码）
4. 最小修复方案（一步步）
5. 验证命令与结果
6. 风险与回滚点

优先检查项：
- /api/llm/multi-role/v2/start|task|decision|retry-aggregate
- queued/running/aggregating 状态推进
- 聚合失败后的可恢复入口
- 当日复用命中逻辑

如果存在多个可行路径：
- 默认选择改动最小、对前端用户影响最小的方案
- 明确写出未覆盖风险
```
