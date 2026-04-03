# Doc Freshness Checklist

当你改了代码，先问自己这些问题：

## 如果改了前端页面/入口/权限

检查：
- `apps/web/src/app/router.ts`
- `docs/system_overview_cn.md`
- `README_WEB.md`（若影响启动/入口说明）

## 如果改了 API / 路由 / 鉴权

检查：
- `backend/server.py`
- `backend/routes/`
- `README_WEB.md`
- `docs/system_overview_cn.md`

## 如果改了任务 / 调度 / 运行方式

检查：
- `job_registry.py`
- `job_orchestrator.py`
- `docs/system_overview_cn.md`
- `docs/command_line_reference.md`

## 如果改了数据库运行认知 / 迁移方式

检查：
- `README_WEB.md`
- `SQLITE_RETIRED.md`
- `docs/database_dictionary.md`

## 如果改了项目执行规则

检查：
- `AGENTS.md`
- `.codex/config.toml`
- `.codex/skills/`
- `.codex/checklists/`

## 最终判断

在准备 `git push` 前，明确回答：
- 哪些文档已同步更新？
- 哪些文档无需更新，为什么？
- 还有没有已知的文档与代码不一致之处？
