# Push Before Checklist

在 `git push` 前至少过一遍这个清单。

## 代码与范围

- 是否只改了和任务相关的文件？
- 是否避免了无关重构？
- 是否保持公开接口兼容？
- 是否保持数据库 schema 不变（除非任务明确要求）？

## 前端展示业务

- 本次改动是否真正改善了前端展示、交互或信息表达？
- 如果是前端任务，页面主路径是否可用？
- 如果不是前端任务，是否至少没有伤害前端主链路？

## 测试可用性

- 跑了什么验证？
- 没跑什么验证？
- 剩余风险是什么？

推荐验证：
- 前端改动：`cd /home/zanbo/zanbotest/apps/web && npm run build`
- Python 改动：`cd /home/zanbo/zanbotest && python3 -m py_compile backend/server.py backend/routes/*.py job_registry.py`

## 文档新鲜度

- `AGENTS.md` 是否仍然准确？
- `README_WEB.md` 是否仍然准确？
- `docs/system_overview_cn.md` 是否仍然准确？
- 若任务影响 SQLite/运行主库认知，`SQLITE_RETIRED.md` 是否需要更新？
- 是否有模块专项文档需要同步？

## 提交说明

- 能否清楚说明“改了什么 / 没改什么 / 风险点”？
- 是否能给出简明 diff 摘要？
- 是否能说明对“前端展示业务”和“测试可用性”的影响？
