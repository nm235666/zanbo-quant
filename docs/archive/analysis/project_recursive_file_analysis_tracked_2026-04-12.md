# 项目递归逐文件分析（Tracked Files）

> 生成时间: 2026-04-12 UTC

> 分析范围: `git ls-files`（共 484 个文件）。

> 说明: 工作区实际文件远大于该数量（含 `.venv/.deps/runtime/.git` 等第三方与运行产物）；这些目录在模块归纳中单独标注，不逐文件展开源码分析。


## 1. 项目整体目录概览

- `(root)`: 164 files
- `apps`: 99 files
- `services`: 65 files
- `.codex`: 33 files
- `docs`: 31 files
- `tests`: 26 files
- `jobs`: 20 files
- `collectors`: 15 files
- `backend`: 11 files
- `skills`: 8 files
- `scripts`: 6 files
- `config`: 3 files
- `external`: 1 files
- `logs`: 1 files
- `runtime`: 1 files


## 2. 逐文件分析

### `.codex/agents/delivery-fast.toml`
- 文件路径: `.codex/agents/delivery-fast.toml`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: name, description, prompt, Cycle template, 5. Close with
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/agents/frontend-first.toml`
- 文件路径: `.codex/agents/frontend-first.toml`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: name, description, prompt, Default workflow, 2. Do a fast scan (timebox
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/agents/ops-sre.toml`
- 文件路径: `.codex/agents/ops-sre.toml`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: name, description, prompt, Priority, Focus areas
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/agents/reviewer.toml`
- 文件路径: `.codex/agents/reviewer.toml`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: name, description, prompt, Review changes with this priority, Rules
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/auth-permission-troubleshooting.md`
- 文件路径: `.codex/checklists/auth-permission-troubleshooting.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Auth / Permission Troubleshooting Checklist / 1. 先分清 401 与 403 / 2. 401 排查
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/doc-freshness-checklist.md`
- 文件路径: `.codex/checklists/doc-freshness-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Doc Freshness Checklist / 如果改了前端页面/入口/权限 / 如果改了 API / 路由 / 鉴权
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/frontend-change-checklist.md`
- 文件路径: `.codex/checklists/frontend-change-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Frontend Change Checklist / 变更前 / 变更中
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/llm-pipeline-checklist.md`
- 文件路径: `.codex/checklists/llm-pipeline-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: LLM Pipeline Checklist / Provider 层 / Gateway 层
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/multi-role-v2-incident-checklist.md`
- 文件路径: `.codex/checklists/multi-role-v2-incident-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Multi-Role V2 Incident Checklist / 先判影响面 / 先查接口再查代码
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/multi-role-v2-smoke-checklist.md`
- 文件路径: `.codex/checklists/multi-role-v2-smoke-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Multi-Role V2 Smoke Checklist / 启动前 / API 主链路
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/push-before-checklist.md`
- 文件路径: `.codex/checklists/push-before-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Push Before Checklist / 代码与范围 / 前端展示业务
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/quantaalpha-runtime-checklist.md`
- 文件路径: `.codex/checklists/quantaalpha-runtime-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: QuantaAlpha Runtime Checklist / 1. 代码与目录 / 2. 后端接口可达
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/remote-deploy-smoke-checklist.md`
- 文件路径: `.codex/checklists/remote-deploy-smoke-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Remote Deploy Smoke Checklist / 1. 先确认服务器链路 / 2. 确认反向代理目标
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/checklists/scheduler-parity-checklist.md`
- 文件路径: `.codex/checklists/scheduler-parity-checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Scheduler Parity Checklist / 定义一致性 / 安装一致性
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/commands.md`
- 文件路径: `.codex/commands.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: .codex 使用说明 / 当前固定优先级 / 目录结构
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/config.toml`
- 文件路径: `.codex/config.toml`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: name, root, primary_goal, secondary_goal, summary
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/prompts/backend-safe-change.md`
- 文件路径: `.codex/prompts/backend-safe-change.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Backend Safe Change Prompt
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/prompts/backlog-drain.md`
- 文件路径: `.codex/prompts/backlog-drain.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Backlog Drain Prompt
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/prompts/incident-404-401-diff.md`
- 文件路径: `.codex/prompts/incident-404-401-diff.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Incident Prompt: 404 vs 401/403 快速分流
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/prompts/incident-rca.md`
- 文件路径: `.codex/prompts/incident-rca.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Incident RCA Prompt
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/prompts/multi-role-v2-hotfix.md`
- 文件路径: `.codex/prompts/multi-role-v2-hotfix.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Multi-Role V2 Hotfix Prompt
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/data-quality-audit/SKILL.md`
- 文件路径: `.codex/skills/data-quality-audit/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Data Quality Audit / Goal / Scope
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/doc-freshness/SKILL.md`
- 文件路径: `.codex/skills/doc-freshness/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Doc Freshness / Priority / Check these files first
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/frontend-delivery/SKILL.md`
- 文件路径: `.codex/skills/frontend-delivery/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Frontend Delivery / Goal / Read first
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/job-triage/SKILL.md`
- 文件路径: `.codex/skills/job-triage/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Job Triage / Goal / Scope
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/llm-provider-ops/SKILL.md`
- 文件路径: `.codex/skills/llm-provider-ops/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: LLM Provider Ops / Goal / Scope
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/minimal-fix/SKILL.md`
- 文件路径: `.codex/skills/minimal-fix/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Minimal Fix / Goal / Read first
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/multi-role-runtime-ops/SKILL.md`
- 文件路径: `.codex/skills/multi-role-runtime-ops/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Multi-Role Runtime Ops / Goal / Scope
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/repo-scan/SKILL.md`
- 文件路径: `.codex/skills/repo-scan/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Repo Scan / Goal / Read order
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/skills/testability-guard/SKILL.md`
- 文件路径: `.codex/skills/testability-guard/SKILL.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Testability Guard / Goal / Read first
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/templates/hotfix-kickoff.md`
- 文件路径: `.codex/templates/hotfix-kickoff.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Hotfix Kickoff Template
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/templates/minimal-commit-plan.md`
- 文件路径: `.codex/templates/minimal-commit-plan.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Minimal Commit Plan Template
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.codex/templates/task-kickoff.md`
- 文件路径: `.codex/templates/task-kickoff.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Task Kickoff Template
- 与其他文件或模块的关系: 提供 AI 协作规范/模板，对代码运行无直接依赖
- 是否是核心文件: 否

### `.gitignore`
- 文件路径: `.gitignore`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `AGENTS.md`
- 文件路径: `AGENTS.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant 投研系统 - Agent 指南 / 快速读取顺序 / 目录
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `PROJECT_ANALYSIS_REPORT.md`
- 文件路径: `PROJECT_ANALYSIS_REPORT.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `PROJECT_FULL_ANALYSIS.md`
- 文件路径: `PROJECT_FULL_ANALYSIS.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `README_WEB.md`
- 文件路径: `README_WEB.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 前后端分离投研系统运行说明 / 目录结构 / 文档导航（主链）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `SQLITE_RETIRED.md`
- 文件路径: `SQLITE_RETIRED.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: SQLite 已退役
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/.gitignore`
- 文件路径: `apps/web/.gitignore`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/.vscode/extensions.json`
- 文件路径: `apps/web/.vscode/extensions.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置键: recommendations
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/README.md`
- 文件路径: `apps/web/README.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant Vue Frontend / Run dev / Build
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/index.html`
- 文件路径: `apps/web/index.html`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/package-lock.json`
- 文件路径: `apps/web/package-lock.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置/数据文件（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/package.json`
- 文件路径: `apps/web/package.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置键: name, private, version, type, scripts, dependencies, devDependencies
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/public/favicon.svg`
- 文件路径: `apps/web/public/favicon.svg`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/public/icons.svg`
- 文件路径: `apps/web/public/icons.svg`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/App.vue`
- 文件路径: `apps/web/src/App.vue`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 页面/组件模板、交互逻辑、样式
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/app/navigation.config.json`
- 文件路径: `apps/web/src/app/navigation.config.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置键: version, source, groups
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/app/navigation.ts`
- 文件路径: `apps/web/src/app/navigation.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: normalizeNavGroups, resolveNavigationGroups, resolveDefaultLandingPath, NAV_CONFIG_VERSION, NAV_CONFIG_SOURCE
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/app/permissionGroups.ts`
- 文件路径: `apps/web/src/app/permissionGroups.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: uniquePermissions, PERMISSION_GROUP_VERSION
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/app/permissions.ts`
- 文件路径: `apps/web/src/app/permissions.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: hasPermissionByEffective
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/app/router.ts`
- 文件路径: `apps/web/src/app/router.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: router
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `apps/web/src/env.d.ts`
- 文件路径: `apps/web/src/env.d.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 以前端路由、类型、请求封装或状态逻辑为主
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/main.ts`
- 文件路径: `apps/web/src/main.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 以前端路由、类型、请求封装或状态逻辑为主
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `apps/web/src/pages/auth/LoginPage.vue`
- 文件路径: `apps/web/src/pages/auth/LoginPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/auth/UpgradePage.vue`
- 文件路径: `apps/web/src/pages/auth/UpgradePage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/chatrooms/ChatlogPage.vue`
- 文件路径: `apps/web/src/pages/chatrooms/ChatlogPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/chatrooms/ChatroomCandidatesPage.vue`
- 文件路径: `apps/web/src/pages/chatrooms/ChatroomCandidatesPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/chatrooms/ChatroomInvestmentPage.vue`
- 文件路径: `apps/web/src/pages/chatrooms/ChatroomInvestmentPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/chatrooms/ChatroomsOverviewPage.vue`
- 文件路径: `apps/web/src/pages/chatrooms/ChatroomsOverviewPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/dashboard/DashboardPage.vue`
- 文件路径: `apps/web/src/pages/dashboard/DashboardPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑、样式（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/intelligence/CnNewsPage.vue`
- 文件路径: `apps/web/src/pages/intelligence/CnNewsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/intelligence/DailySummariesPage.vue`
- 文件路径: `apps/web/src/pages/intelligence/DailySummariesPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/intelligence/GlobalNewsPage.vue`
- 文件路径: `apps/web/src/pages/intelligence/GlobalNewsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/intelligence/NewsListPageBlock.vue`
- 文件路径: `apps/web/src/pages/intelligence/NewsListPageBlock.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/intelligence/StockNewsPage.vue`
- 文件路径: `apps/web/src/pages/intelligence/StockNewsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/macro/MacroPage.vue`
- 文件路径: `apps/web/src/pages/macro/MacroPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/DecisionBoardPage.vue`
- 文件路径: `apps/web/src/pages/research/DecisionBoardPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/DecisionTradePlanPage.vue`
- 文件路径: `apps/web/src/pages/research/DecisionTradePlanPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/MultiRoleResearchPage.vue`
- 文件路径: `apps/web/src/pages/research/MultiRoleResearchPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/QuantFactorsPage.vue`
- 文件路径: `apps/web/src/pages/research/QuantFactorsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/ReportsPage.vue`
- 文件路径: `apps/web/src/pages/research/ReportsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/research/TrendAnalysisPage.vue`
- 文件路径: `apps/web/src/pages/research/TrendAnalysisPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalAuditPage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalAuditPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalChainGraphPage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalChainGraphPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalQualityConfigPage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalQualityConfigPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalStateTimelinePage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalStateTimelinePage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalTimelinePage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalTimelinePage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/SignalsOverviewPage.vue`
- 文件路径: `apps/web/src/pages/signals/SignalsOverviewPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/signals/ThemesPage.vue`
- 文件路径: `apps/web/src/pages/signals/ThemesPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/stocks/PricesPage.vue`
- 文件路径: `apps/web/src/pages/stocks/PricesPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/stocks/StockDetailPage.vue`
- 文件路径: `apps/web/src/pages/stocks/StockDetailPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/stocks/StockScoresPage.vue`
- 文件路径: `apps/web/src/pages/stocks/StockScoresPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/stocks/StocksListPage.vue`
- 文件路径: `apps/web/src/pages/stocks/StocksListPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/DatabaseAuditPage.vue`
- 文件路径: `apps/web/src/pages/system/DatabaseAuditPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/InviteAdminPage.vue`
- 文件路径: `apps/web/src/pages/system/InviteAdminPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/JobsOpsPage.vue`
- 文件路径: `apps/web/src/pages/system/JobsOpsPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/LlmProvidersPage.vue`
- 文件路径: `apps/web/src/pages/system/LlmProvidersPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/RolePoliciesPage.vue`
- 文件路径: `apps/web/src/pages/system/RolePoliciesPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/SourceMonitorPage.vue`
- 文件路径: `apps/web/src/pages/system/SourceMonitorPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/pages/system/UserAdminPage.vue`
- 文件路径: `apps/web/src/pages/system/UserAdminPage.vue`
- 文件作用: 前端页面
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 由 router.ts 注册路由，调用 services/api 与 stores，复用 shared 组件
- 是否是核心文件: 是

### `apps/web/src/services/api/auth.ts`
- 文件路径: `apps/web/src/services/api/auth.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchAuthStatus, clearAuthStatusCache, loginWithToken, loginWithPassword
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/chatrooms.ts`
- 文件路径: `apps/web/src/services/api/chatrooms.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchChatrooms, triggerChatroomFetch, fetchWechatChatlog, fetchChatroomInvestment
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/dashboard.ts`
- 文件路径: `apps/web/src/services/api/dashboard.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchDashboard, fetchSourceMonitor, fetchDatabaseAudit, fetchDbHealth
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/decision.ts`
- 文件路径: `apps/web/src/services/api/decision.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchDecisionBoard, fetchDecisionScoreboard, fetchDecisionStock, fetchDecisionPlan
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/macro.ts`
- 文件路径: `apps/web/src/services/api/macro.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchMacroIndicators, fetchMacroSeries
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/news.ts`
- 文件路径: `apps/web/src/services/api/news.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchNews, fetchNewsSources, fetchStockNews, fetchStockNewsSources
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/quantFactors.ts`
- 文件路径: `apps/web/src/services/api/quantFactors.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: startQuantMine, startQuantAutoResearch, startQuantBacktest, fetchQuantTask
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/research.ts`
- 文件路径: `apps/web/src/services/api/research.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchResearchReports, searchAiRetrieval
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/signals.ts`
- 文件路径: `apps/web/src/services/api/signals.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchInvestmentSignals, fetchSignalTimeline, fetchThemeHotspots, fetchSignalChainGraph
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/stocks.ts`
- 文件路径: `apps/web/src/services/api/stocks.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: fetchStockFilters, fetchStocks, fetchStockDetail, fetchStockPrices
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/api/system.ts`
- 文件路径: `apps/web/src/services/api/system.ts`
- 文件作用: 前端 API 封装
- 主要功能/逻辑: 核心导出/函数: _candidateBases, _callLlmProvidersApi, fetchSignalQualityConfig, saveSignalQualityRules
- 与其他文件或模块的关系: 被页面与 store 调用，通过 http.ts 访问 backend/routes/*
- 是否是核心文件: 否

### `apps/web/src/services/authToken.ts`
- 文件路径: `apps/web/src/services/authToken.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: readAdminToken, setAdminToken, clearAdminToken
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/services/http.ts`
- 文件路径: `apps/web/src/services/http.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 核心导出/函数: http
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `apps/web/src/shared/charts/MinuteKlineChart.vue`
- 文件路径: `apps/web/src/shared/charts/MinuteKlineChart.vue`
- 文件作用: 前端图表组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/charts/TrendAreaChart.vue`
- 文件路径: `apps/web/src/shared/charts/TrendAreaChart.vue`
- 文件作用: 前端图表组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/markdown/MarkdownBlock.vue`
- 文件路径: `apps/web/src/shared/markdown/MarkdownBlock.vue`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/query/client.ts`
- 文件路径: `apps/web/src/shared/query/client.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: queryClient
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/realtime/useRealtimeBus.ts`
- 文件路径: `apps/web/src/shared/realtime/useRealtimeBus.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: useRealtimeBus
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 是

### `apps/web/src/shared/taskPersistence/taskPersistence.ts`
- 文件路径: `apps/web/src/shared/taskPersistence/taskPersistence.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: canUseSessionStorage, safeParseStorage, readStorageMap, writeStorageMap, TASK_SNAPSHOT_TTL_MS
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/taskPersistence/usePersistedTaskRunner.ts`
- 文件路径: `apps/web/src/shared/taskPersistence/usePersistedTaskRunner.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: formatAgo, usePersistedTaskRunner, restoreTaskSnapshot, persistTaskSnapshot
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/types/api.ts`
- 文件路径: `apps/web/src/shared/types/api.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 以前端路由、类型、请求封装或状态逻辑为主
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/AppDialogHost.vue`
- 文件路径: `apps/web/src/shared/ui/AppDialogHost.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/AppShell.vue`
- 文件路径: `apps/web/src/shared/ui/AppShell.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/AppToastContainer.vue`
- 文件路径: `apps/web/src/shared/ui/AppToastContainer.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑、样式
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/DataTable.vue`
- 文件路径: `apps/web/src/shared/ui/DataTable.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/DetailDrawer.vue`
- 文件路径: `apps/web/src/shared/ui/DetailDrawer.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/InfoCard.vue`
- 文件路径: `apps/web/src/shared/ui/InfoCard.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/MetricGrid.vue`
- 文件路径: `apps/web/src/shared/ui/MetricGrid.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/PageSection.vue`
- 文件路径: `apps/web/src/shared/ui/PageSection.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/StatCard.vue`
- 文件路径: `apps/web/src/shared/ui/StatCard.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/StatePanel.vue`
- 文件路径: `apps/web/src/shared/ui/StatePanel.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/ui/StatusBadge.vue`
- 文件路径: `apps/web/src/shared/ui/StatusBadge.vue`
- 文件作用: 前端共享 UI 组件
- 主要功能/逻辑: 页面/组件模板、交互逻辑
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/confirm.ts`
- 文件路径: `apps/web/src/shared/utils/confirm.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: confirmDangerAction, promptInputAction, infoNoticeAction
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/dialog.ts`
- 文件路径: `apps/web/src/shared/utils/dialog.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: closeDialog, openAppDialog, confirmAppDialog, cancelAppDialog, appDialogState
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/export.ts`
- 文件路径: `apps/web/src/shared/utils/export.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: safeFilename, inlineComputedStyles, blobToDataUrl, stripExternalStyleUrls
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/finance.ts`
- 文件路径: `apps/web/src/shared/utils/finance.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: importanceOptions, parseJsonObject, parseJsonArray, parseImpactTags
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/format.ts`
- 文件路径: `apps/web/src/shared/utils/format.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: formatNumber, formatPercent, formatDateTime, formatDate
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/shared/utils/urlState.ts`
- 文件路径: `apps/web/src/shared/utils/urlState.ts`
- 文件作用: 前端共享能力/工具
- 主要功能/逻辑: 核心导出/函数: readQueryString, readQueryNumber, buildCleanQuery
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/src/stores/auth.ts`
- 文件路径: `apps/web/src/stores/auth.ts`
- 文件作用: 前端状态管理
- 主要功能/逻辑: 核心导出/函数: useAuthStore
- 与其他文件或模块的关系: 被页面组件消费，协调鉴权/实时状态与 API 结果
- 是否是核心文件: 是

### `apps/web/src/stores/realtime.ts`
- 文件路径: `apps/web/src/stores/realtime.ts`
- 文件作用: 前端状态管理
- 主要功能/逻辑: 核心导出/函数: useRealtimeStore
- 与其他文件或模块的关系: 被页面组件消费，协调鉴权/实时状态与 API 结果
- 是否是核心文件: 否

### `apps/web/src/stores/ui.ts`
- 文件路径: `apps/web/src/stores/ui.ts`
- 文件作用: 前端状态管理
- 主要功能/逻辑: 核心导出/函数: useUiStore
- 与其他文件或模块的关系: 被页面组件消费，协调鉴权/实时状态与 API 结果
- 是否是核心文件: 否

### `apps/web/src/styles.css`
- 文件路径: `apps/web/src/styles.css`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/tsconfig.app.json`
- 文件路径: `apps/web/tsconfig.app.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置/数据文件
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/tsconfig.json`
- 文件路径: `apps/web/tsconfig.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置键: files, references
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/tsconfig.node.json`
- 文件路径: `apps/web/tsconfig.node.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置/数据文件
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `apps/web/vite.config.ts`
- 文件路径: `apps/web/vite.config.ts`
- 文件作用: 前端应用代码
- 主要功能/逻辑: 以前端路由、类型、请求封装或状态逻辑为主
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `audit_database_report.py`
- 文件路径: `audit_database_report.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc, fetch_scalar, fetch_tables, fetch_row_count, fetch_samples ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `auto_update_once.sh`
- 文件路径: `auto_update_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | python3 auto_update_stocks_and_prices.py --pause 0.02
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `auto_update_stocks_and_prices.py`
- 文件路径: `auto_update_stocks_and_prices.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_today, ensure_tables, upsert_stock_codes, get_start_date, load_listed_set ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backend/__init__.py`
- 文件路径: `backend/__init__.py`
- 文件作用: 后端入口/基础
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backend/routes/__init__.py`
- 文件路径: `backend/routes/__init__.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/ai_retrieval.py`
- 文件路径: `backend/routes/ai_retrieval.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: _normalize_path, dispatch_post, dispatch_get
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/chatrooms.py`
- 文件路径: `backend/routes/chatrooms.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: dispatch_get
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/decision.py`
- 文件路径: `backend/routes/decision.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: dispatch_get, dispatch_post
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/news.py`
- 文件路径: `backend/routes/news.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: dispatch_get
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/quant_factors.py`
- 文件路径: `backend/routes/quant_factors.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: _normalize_profile, _normalize_engine_profile, dispatch_post, dispatch_get
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/signals.py`
- 文件路径: `backend/routes/signals.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: dispatch_get
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/stocks.py`
- 文件路径: `backend/routes/stocks.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: _safe_bool, _resolve_roles_from_payload, dispatch_get（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/routes/system.py`
- 文件路径: `backend/routes/system.py`
- 文件作用: 后端路由层
- 主要功能/逻辑: 主要函数: dispatch_post（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 由 backend/server.py 挂载，调用 services/* 访问数据库与外部能力
- 是否是核心文件: 是

### `backend/server.py`
- 文件路径: `backend/server.py`
- 文件作用: 后端入口/基础
- 主要功能/逻辑: 主要函数: _resolve_build_id（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `backend_supervisor.sh`
- 文件路径: `backend_supervisor.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | PIDFILE="/tmp/stock_backend_supervisor.pid" | LOG="/tmp/stock_backend.log"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `backfill_capital_flow_market.py`
- 文件路径: `backfill_capital_flow_market.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, to_float ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_capital_flow_stock.py`
- 文件路径: `backfill_capital_flow_stock.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, load_code_set ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_capital_flow_stock_akshare.py`
- 文件路径: `backfill_capital_flow_stock_akshare.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_target_codes, ts_to_parts, market_for_ak ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_company_governance.py`
- 文件路径: `backfill_company_governance.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_codes, fetch_with_retry, normalize_text ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_fx_daily.py`
- 文件路径: `backfill_fx_daily.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, mid ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_fx_daily_akshare.py`
- 文件路径: `backfill_fx_daily_akshare.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, safe_float ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_listed_3y_prices.py`
- 文件路径: `backfill_listed_3y_prices.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, yyyymmdd_utc_today, default_start_date_by_lookback, ensure_price_table, load_listed_codes, chunked_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_logic_view_cache.py`
- 文件路径: `backfill_logic_view_cache.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, iter_rows, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_macro_series.py`
- 文件路径: `backfill_macro_series.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, normalize_period, iter_numeric_fields, to_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_macro_series_akshare.py`
- 文件路径: `backfill_macro_series_akshare.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, safe_float, normalize_period, normalize_publish_date ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_missing_stock_financials.py`
- 文件路径: `backfill_missing_stock_financials.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, get_recent_periods, load_code_scope, build_missing_map, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_rate_curve_points.py`
- 文件路径: `backfill_rate_curve_points.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, upsert_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_risk_scenarios.py`
- 文件路径: `backfill_risk_scenarios.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_codes, fetch_price_rows, compute_stats ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_spread_daily.py`
- 文件路径: `backfill_spread_daily.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, upsert_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_events.py`
- 文件路径: `backfill_stock_events.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_target_codes, fetch_with_retry, normalize_text ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_financials.py`
- 文件路径: `backfill_stock_financials.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_target_codes, fetch_with_retry, safe_num ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_minline_akshare.py`
- 文件路径: `backfill_stock_minline_akshare.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, ensure_table, load_target_codes, ts_to_symbol, existing_rows, fetch_akshare_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_news_items.py`
- 文件路径: `backfill_stock_news_items.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, load_targets, content_hash, normalize_akshare_rows ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_scores_daily.py`
- 文件路径: `backfill_stock_scores_daily.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, to_json_safe, ensure_table, resolve_score_date, build_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_stock_valuation_daily.py`
- 文件路径: `backfill_stock_valuation_daily.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, utc_today, calc_start, ensure_table, load_code_set ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `backfill_wechat_chatlogs_30d.py`
- 文件路径: `backfill_wechat_chatlogs_30d.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, today_utc, daterange_days, table_columns, ensure_chatroom_columns ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `build_chatroom_candidate_pool.py`
- 文件路径: `build_chatroom_candidate_pool.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: normalize_text, parse_args, now_utc_str, cutoff_date_str, ensure_table, load_stock_aliases ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `build_frontend_nextgen.sh`
- 文件路径: `build_frontend_nextgen.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest/apps/web | npm run build
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `build_investment_signal_tracker.py`
- 文件路径: `build_investment_signal_tracker.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, today_utc_str, cutoff_news_time, cutoff_stock_news_time, ensure_table ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `build_signal_state_machine.py`
- 文件路径: `build_signal_state_machine.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, table_exists, ensure_tables, parse_json_text, load_current_signals ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `build_stock_daily_price_rollups.py`
- 文件路径: `build_stock_daily_price_rollups.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, resolve_latest_trade_date, calc_start_date, build_window_rollups ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `build_theme_hotspot_engine.py`
- 文件路径: `build_theme_hotspot_engine.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, today_utc_str, cutoff_news_time, cutoff_stock_news_time, normalize_text ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `check_gpt_provider_nodes.py`
- 文件路径: `check_gpt_provider_nodes.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_iso, _short, _strip_v1, build_base_url_candidates, build_model_candidates ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `clean_governance_json_nan.py`
- 文件路径: `clean_governance_json_nan.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, sanitize_json_value, clean_json_text, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `cleanup_duplicate_items.py`
- 文件路径: `cleanup_duplicate_items.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, _norm_text, _date_key, _news_semantic_keys, _stock_news_semantic_keys, _score_value ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `collectors/__init__.py`
- 文件路径: `collectors/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/chatrooms/__init__.py`
- 文件路径: `collectors/chatrooms/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/chatrooms/pipelines.py`
- 文件路径: `collectors/chatrooms/pipelines.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_chatroom_analysis_pipeline, run_chatroom_sentiment_refresh, run_monitored_chatlog_fetch, run_chatroom_list_refresh
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/macro/__init__.py`
- 文件路径: `collectors/macro/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/macro/pipelines.py`
- 文件路径: `collectors/macro/pipelines.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_macro_series_akshare_refresh, run_macro_context_refresh
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/market/__init__.py`
- 文件路径: `collectors/market/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/market/pipelines.py`
- 文件路径: `collectors/market/pipelines.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_market_expectations_refresh, run_market_news_refresh
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/__init__.py`
- 文件路径: `collectors/news/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/common.py`
- 文件路径: `collectors/news/common.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: _normalize_meta, run_python_script, run_python_commands
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/daily_summary.py`
- 文件路径: `collectors/news/daily_summary.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_daily_summary_refresh
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/domestic.py`
- 文件路径: `collectors/news/domestic.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_cn_news_pipeline
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/enrichment.py`
- 文件路径: `collectors/news/enrichment.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_news_stock_map_refresh, run_news_sentiment_refresh, run_cn_news_score_refresh, run_intl_news_score_refresh
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/news/international.py`
- 文件路径: `collectors/news/international.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: run_international_news_pipeline
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/stock_news/__init__.py`
- 文件路径: `collectors/stock_news/__init__.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `collectors/stock_news/pipelines.py`
- 文件路径: `collectors/stock_news/pipelines.py`
- 文件作用: 数据采集管道
- 主要功能/逻辑: 主要函数: _enforce_news_priority, run_stock_news_score_refresh, run_stock_news_backfill_missing, run_stock_news_expand_focus
- 与其他文件或模块的关系: 被 fetch/backfill/run 脚本复用，向数据库写入原始与清洗数据
- 是否是核心文件: 否

### `config/llm_providers.json`
- 文件路径: `config/llm_providers.json`
- 文件作用: 配置文件
- 主要功能/逻辑: JSON 配置/数据文件（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被后端服务、RBAC、LLM provider 管理逻辑读取
- 是否是核心文件: 否

### `config/rbac_dynamic.config.json`
- 文件路径: `config/rbac_dynamic.config.json`
- 文件作用: 配置文件
- 主要功能/逻辑: JSON 配置键: schema_version, version, source, permission_catalog, route_permissions, navigation_groups
- 与其他文件或模块的关系: 被后端服务、RBAC、LLM provider 管理逻辑读取
- 是否是核心文件: 否

### `config/tushare_token.txt`
- 文件路径: `config/tushare_token.txt`
- 文件作用: 配置文件
- 主要功能/逻辑: 文本内容摘要: 42e5d45b54aedf3a9f339ff8010327582ae8ad2819e18dca5c3457bb
- 与其他文件或模块的关系: 被后端服务、RBAC、LLM provider 管理逻辑读取
- 是否是核心文件: 否

### `create_fixed_mailbox_remote.sh`
- 文件路径: `create_fixed_mailbox_remote.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | SSH_USER="zanbo" | SSH_HOST="192.168.5.58"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `create_research_tables.py`
- 文件路径: `create_research_tables.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, create_tables（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `db_compat.py`
- 文件路径: `db_compat.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: _replace_qmarks, _rewrite_sql, connect, connect_sqlite, using_postgres, db_label ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `db_health_check.py`
- 文件路径: `db_health_check.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, fetch_scalar, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `deploy_api_stack.sh`
- 文件路径: `deploy_api_stack.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT_DIR="/home/zanbo/zanbotest" | BUILD_ID="${1:-deploy-$(date -u +%Y%m%dT%H%M%SZ)}"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `docs/Opportunitiesforsomeideas/Newfeatures&ideas`
- 文件路径: `docs/Opportunitiesforsomeideas/Newfeatures&ideas`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（需结合业务上下文）（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/Opportunitiesforsomeideas/总览版.md`
- 文件路径: `docs/Opportunitiesforsomeideas/总览版.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 投研自动化总览版 / 1. 这三份文件各自是什么 / 1.1 [我和ai的金融对话沟通.txt](/home/zanbo/zanbotest/docs/Opportunitiesforsomeideas/我和ai的金融对话沟通.txt)
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/Opportunitiesforsomeideas/我和ai的金融对话沟通.txt`
- 文件路径: `docs/Opportunitiesforsomeideas/我和ai的金融对话沟通.txt`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文本内容摘要: User: 其实，我在构思一个自己的网站，但是呢，目前很多东西没有做完，然后，但是我又不知道该怎么开始和结束。 Kimi: 卡在中间状态是最消耗人的——**既回（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/Opportunitiesforsomeideas/投研自动化落地方案.md`
- 文件路径: `docs/Opportunitiesforsomeideas/投研自动化落地方案.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 投研自动化落地方案 / 1. 我们要解决什么 / 2. 现有基础
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/ai_retrieval_gateway_2026-04-06.md`
- 文件路径: `docs/ai_retrieval_gateway_2026-04-06.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: AI Retrieval Gateway（2026-04-06） / 新增能力 / 运行开关
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/command_line_reference.md`
- 文件路径: `docs/command_line_reference.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 项目命令行命令总表 / 通用用法 / 启动与服务（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/database_audit_report.md`
- 文件路径: `docs/database_audit_report.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 数据库审核报告 / 总览 / 分主题详查（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/database_dictionary.md`
- 文件路径: `docs/database_dictionary.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 数据库数据字典 / 总览 / 各表详解（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/er-diagram.md`
- 文件路径: `docs/er-diagram.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant 数据库 ER 图 / 一、ER 图总览（按模块划分） / 二、核心股票数据模块（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/frontend-optimization-plan.md`
- 文件路径: `docs/frontend-optimization-plan.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant 前端页面优化诊断与整改路线图 / 1. 审计范围与依据 / 1.1 真实页面入口
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/frontend-optimization-priorities.md`
- 文件路径: `docs/frontend-optimization-priorities.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/job_observability_baseline_2026-04-02.md`
- 文件路径: `docs/job_observability_baseline_2026-04-02.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 调度观测基线（制定日期：2026-04-02） / 目标 / 覆盖任务
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/migration_completion_definition.md`
- 文件路径: `docs/migration_completion_definition.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 改造迁移完成定义（收口基线） / 目标 / 完成判定
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/navigation-permission-refactor-plan.md`
- 文件路径: `docs/navigation-permission-refactor-plan.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 导航重构与权限系统改造方案 / 执行进展（2026-04-05） / 目录（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/navigation_permission_smoke_checklist_2026-04-05.md`
- 文件路径: `docs/navigation_permission_smoke_checklist_2026-04-05.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 导航与权限轻量收口验收清单（2026-04-05） / 1. 构建与静态检查 / 2. 配置一致性校验
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/notifications_itchat_experimental.md`
- 文件路径: `docs/notifications_itchat_experimental.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 个人微信通知通道（ItChat）实验说明 / 背景 / 能力位置
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/pr_review_checklist.md`
- 文件路径: `docs/pr_review_checklist.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 改造期 PR 评审清单 / 必查项 / 回归项
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/project_flowchart.mmd`
- 文件路径: `docs/project_flowchart.mmd`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/quant_production_gate_report_template_2026-04-07.md`
- 文件路径: `docs/quant_production_gate_report_template_2026-04-07.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 因子挖掘生产切流双门槛验收模板 / 基本信息 / 门槛 A：稳定性
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/quant_research_qlib_sop_2026-04-07.md`
- 文件路径: `docs/quant_research_qlib_sop_2026-04-07.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 自研等价数据适配层与研究栈启动 SOP（生产版） / 1. 目标 / 2. 数据准备
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/rbac_dynamic_protocol_retirement_2026-04-05.md`
- 文件路径: `docs/rbac_dynamic_protocol_retirement_2026-04-05.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: RBAC 动态协议退役计划（2026-04-05） / 背景 / 新增字段
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/repo_structure_rules.md`
- 文件路径: `docs/repo_structure_rules.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 仓库结构约束 / 新代码落点 / 兼容策略
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/reporting_protocol_retirement_plan_2026-04-02.md`
- 文件路径: `docs/reporting_protocol_retirement_plan_2026-04-02.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Reporting 字段退场计划（制定日期：2026-04-02） / 背景 / 时间里程碑
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/scheduler_matrix_2026-04-06.md`
- 文件路径: `docs/scheduler_matrix_2026-04-06.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 定时任务调度矩阵（UTC/CST 双时区） / 业务时段矩阵 / 实时资讯链（自然日）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/script_layering_cli_cn.md`
- 文件路径: `docs/script_layering_cli_cn.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 脚本分层与 CLI 规范（v1） / 1. 分层约定 / 2. CLI 统一参数（建议）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/system_er_diagram_2026-04-05.md`
- 文件路径: `docs/system_er_diagram_2026-04-05.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant 当前系统 ER 图（2026-04-05） / 数据来源与口径 / 使用建议（前端/测试）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/system_overview_cn.md`
- 文件路径: `docs/system_overview_cn.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 系统全景总览 / 1. 目前系统已经具备的能力 / 1.1 股票基础与行情
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/web_frontend_rectify_smoke_checklist_2026-04-04.md`
- 文件路径: `docs/web_frontend_rectify_smoke_checklist_2026-04-04.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Web 前端整改回归清单（2026-04-04） / 1. 构建与静态检查 / 2. 页面主链路（手动 smoke）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/web_fullsite_test_report_2026-04-04.md`
- 文件路径: `docs/web_fullsite_test_report_2026-04-04.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/web_fullsite_test_report_2026-04-05.md`
- 文件路径: `docs/web_fullsite_test_report_2026-04-05.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `docs/web_fullsite_test_report_2026-04-06_full_regression.md`
- 文件路径: `docs/web_fullsite_test_report_2026-04-06_full_regression.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant Web 全量重测报告（2026-04-06 UTC） / 测试目标理解 / 涉及模块
- 与其他文件或模块的关系: 约束实现与运维流程，反向指导代码变更
- 是否是核心文件: 否

### `export_db_dictionary_md.py`
- 文件路径: `export_db_dictionary_md.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc, fetch_schema（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `external/quantaalpha`
- 文件路径: `external/quantaalpha`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（可能为二进制或编码不可读）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `fast_backfill_listed_prices.py`
- 文件路径: `fast_backfill_listed_prices.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_today, calc_start, ensure_table, load_listed_set, upsert_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fast_backfill_stock_financials.py`
- 文件路径: `fast_backfill_stock_financials.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, load_code_set, safe_num, choose_ann_date ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_all_stock_codes.py`
- 文件路径: `fetch_all_stock_codes.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_chatroom_list_to_db.py`
- 文件路径: `fetch_chatroom_list_to_db.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, ensure_table, fetch_csv_text, parse_rows, upsert_rows ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_cn_news_eastmoney.py`
- 文件路径: `fetch_cn_news_eastmoney.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, unwrap_jsonp, to_utc_iso, parse_items ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_cn_news_sina_7x24.py`
- 文件路径: `fetch_cn_news_sina_7x24.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, to_utc_iso, parse_items, content_hash ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_market_expectations_polymarket.py`
- 文件路径: `fetch_market_expectations_polymarket.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, table_exists, ensure_tables, to_float, resolve_themes ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_monitored_chatlogs_once.py`
- 文件路径: `fetch_monitored_chatlogs_once.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, today_text, yesterday_text, choose_talker_name, count_raw_message_blocks ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_news_marketscreener.py`
- 文件路径: `fetch_news_marketscreener.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, clean_text, fetch_html, parse_items ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_news_marketscreener_live.py`
- 文件路径: `fetch_news_marketscreener_live.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, clean_text, fetch_html, extract_live_block ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_news_rss.py`
- 文件路径: `fetch_news_rss.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, parse_rss_dt, text_of, pick_item_fields ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_sina_minline_all_listed.py`
- 文件路径: `fetch_sina_minline_all_listed.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, ts_to_sina_symbol, ensure_table, load_listed_codes, fetch_sina_raw, classify_error ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_sina_minline_one.py`
- 文件路径: `fetch_sina_minline_one.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, ts_to_sina_symbol, ensure_table, fetch_sina_data, upsert_minline, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_stock_news_eastmoney_to_db.py`
- 文件路径: `fetch_stock_news_eastmoney_to_db.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, _clean_text, _clean_link, _pub_day, _candidate_signatures ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `fetch_wechat_chatlog_clean_to_db.py`
- 文件路径: `fetch_wechat_chatlog_clean_to_db.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, utc_now, resolve_time_param, build_request_url, fetch_chatlog_text, ensure_table ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `generate_standard_research_report.py`
- 文件路径: `generate_standard_research_report.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, today_utc_str, parse_json_text, ensure_table, fmt ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `init_postgres_schema.py`
- 文件路径: `init_postgres_schema.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `install_all_crons.sh`
- 文件路径: `install_all_crons.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | TMP_EXISTING="$(mktemp)"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `install_chatroom_daily_cron.sh`
- 文件路径: `install_chatroom_daily_cron.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | RUNNER="${BASE_DIR}/run_chatroom_fetch_once.sh"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `install_monitored_chatlog_cron.sh`
- 文件路径: `install_monitored_chatlog_cron.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | RUNNER="${BASE_DIR}/run_monitored_chatlog_fetch_once.sh"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `install_monitored_chatlog_midnight_cron.sh`
- 文件路径: `install_monitored_chatlog_midnight_cron.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | RUNNER="${BASE_DIR}/run_monitored_chatlog_backfill_midnight.sh"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `job_orchestrator.py`
- 文件路径: `job_orchestrator.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: utc_now, cn_today, resolve_recent_trade_dates, expand_command, ensure_tables, sync_job_definitions ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `job_registry.py`
- 文件路径: `job_registry.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: py_cmd, bash_cmd（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `jobs/__init__.py`
- 文件路径: `jobs/__init__.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/chatroom_jobs.py`
- 文件路径: `jobs/chatroom_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_chatroom_job_target, run_chatroom_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/decision_jobs.py`
- 文件路径: `jobs/decision_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_decision_job_target, run_decision_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/llm_jobs.py`
- 文件路径: `jobs/llm_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: _list_multi_role_v3_worker_pids, ensure_multi_role_v3_workers, get_llm_job_target, run_llm_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/macro_jobs.py`
- 文件路径: `jobs/macro_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_macro_job_target, run_macro_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/market_jobs.py`
- 文件路径: `jobs/market_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_market_job_target, run_market_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/news_jobs.py`
- 文件路径: `jobs/news_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: cn_today, get_news_job_target, run_news_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/quantaalpha_jobs.py`
- 文件路径: `jobs/quantaalpha_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_quantaalpha_job_target, run_quantaalpha_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/registry_adapter.py`
- 文件路径: `jobs/registry_adapter.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: list_job_specs
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_chatroom_job.py`
- 文件路径: `jobs/run_chatroom_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_decision_job.py`
- 文件路径: `jobs/run_decision_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_llm_job.py`
- 文件路径: `jobs/run_llm_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_macro_job.py`
- 文件路径: `jobs/run_macro_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_market_job.py`
- 文件路径: `jobs/run_market_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_multi_role_v3_worker.py`
- 文件路径: `jobs/run_multi_role_v3_worker.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: build_runtime, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_news_job.py`
- 文件路径: `jobs/run_news_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_quantaalpha_job.py`
- 文件路径: `jobs/run_quantaalpha_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_quantaalpha_worker.py`
- 文件路径: `jobs/run_quantaalpha_worker.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/run_stock_news_job.py`
- 文件路径: `jobs/run_stock_news_job.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `jobs/stock_news_jobs.py`
- 文件路径: `jobs/stock_news_jobs.py`
- 文件作用: 任务调度执行
- 主要功能/逻辑: 主要函数: get_stock_news_job_target, run_stock_news_job
- 与其他文件或模块的关系: 由 job_registry.py / job_orchestrator.py 调度，调用 collectors/services
- 是否是核心文件: 否

### `llm_analyze_chatroom_investment_bias.py`
- 文件路径: `llm_analyze_chatroom_investment_bias.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, build_room_filter_sql, fetch_candidate_rooms, room_display_name ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_analyze_stock_trend.py`
- 文件路径: `llm_analyze_stock_trend.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_gateway.py`
- 文件路径: `llm_gateway.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: _normalize_base_url, _build_provider_signature, _rate_window, _redis_key, _state_redis_key, _metrics_redis_key ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `llm_multi_role_company_review.py`
- 文件路径: `llm_multi_role_company_review.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, resolve_company, load_role_profiles, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_provider_config.py`
- 文件路径: `llm_provider_config.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: _env, _normalize_model_key, _safe_float, _safe_int, _safe_bool, _resolve_api_key_from_item ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `llm_resolve_stock_aliases.py`
- 文件路径: `llm_resolve_stock_aliases.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_alias_table, candidate_is_theme_like, fetch_unresolved_candidates, build_prompt ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_score_chatroom_sentiment.py`
- 文件路径: `llm_score_chatroom_sentiment.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, fetch_rows, build_prompt, call_llm ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_score_news.py`
- 文件路径: `llm_score_news.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, fetch_news_rows, build_prompt, call_llm ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_score_sentiment.py`
- 文件路径: `llm_score_sentiment.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, fetch_rows, build_prompt, call_llm ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_score_stock_news.py`
- 文件路径: `llm_score_stock_news.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, fetch_rows, build_prompt, build_batch_prompt ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_summarize_daily_important_news.py`
- 文件路径: `llm_summarize_daily_important_news.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, today_utc_date, ensure_summary_table, fetch_news_rows, build_prompt ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `llm_tag_chatrooms.py`
- 文件路径: `llm_tag_chatrooms.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, build_room_filter_sql, fetch_candidate_rooms, room_display_name ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `logs/backend.out`
- 文件路径: `logs/backend.out`
- 文件作用: 其他文件
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `loop_score_unscored_news.py`
- 文件路径: `loop_score_unscored_news.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, count_unscored, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `manage_llm_providers.py`
- 文件路径: `manage_llm_providers.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: resolve_path, ensure_parent, default_payload, load_payload, save_payload, normalize_key ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `map_news_items_to_stocks.py`
- 文件路径: `map_news_items_to_stocks.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_columns, fetch_target_rows, cutoff_time, normalize_text ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `market_calendar.py`
- 文件路径: `market_calendar.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: beijing_today, recent_open_trade_dates, resolve_trade_date, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `migrate_sqlite_to_postgres.py`
- 文件路径: `migrate_sqlite_to_postgres.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, qident, map_sqlite_type, user_tables, table_sql, create_table ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `nginx_8077.conf`
- 文件路径: `nginx_8077.conf`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 配置项: location, proxy_pass http, proxy_pass http, location, proxy_pass http
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `optimize_and_archive_news.py`
- 文件路径: `optimize_and_archive_news.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, cutoff_utc_str, table_exists, columns_info, ensure_archive_table ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `query_stock_news_eastmoney.py`
- 文件路径: `query_stock_news_eastmoney.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, resolve_name_from_ts_code, unwrap_jsonp, strip_html, build_params, fetch_news ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `realtime_streams.py`
- 文件路径: `realtime_streams.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: now_utc_iso, _normalize_items, publish_news_batch, publish_ws_broadcast, publish_app_event
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `retire_sqlite.sh`
- 文件路径: `retire_sqlite.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | DB_BASENAME="stock_codes.db"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `roles_config.example.json`
- 文件路径: `roles_config.example.json`
- 文件作用: 配置/元数据
- 主要功能/逻辑: JSON 配置键: 宏观经济分析师, 企业治理分析师
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `run_chatroom_analysis_pipeline_once.sh`
- 文件路径: `run_chatroom_analysis_pipeline_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_chatroom_fetch_once.sh`
- 文件路径: `run_chatroom_fetch_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_chatroom_sentiment_once.sh`
- 文件路径: `run_chatroom_sentiment_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_chatroom_tagging_safe_once.sh`
- 文件路径: `run_chatroom_tagging_safe_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_cn_news_eastmoney_once.sh`
- 文件路径: `run_cn_news_eastmoney_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | LOCK_FILE="/tmp/cn_eastmoney_fetch.lock" | LOG_FILE="/tmp/cn_eastmoney_fetch.log"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_cn_news_fetch_once.sh`
- 文件路径: `run_cn_news_fetch_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_daily_postclose_update.sh`
- 文件路径: `run_daily_postclose_update.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_data_completion_batches.py`
- 文件路径: `run_data_completion_batches.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: utc_now, parse_args, query_scalar, progress_snapshot, log_line, run_step ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `run_data_completion_nightly.sh`
- 文件路径: `run_data_completion_nightly.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_data_completion_once.sh`
- 文件路径: `run_data_completion_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_database_audit_once.sh`
- 文件路径: `run_database_audit_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_db_health_check_once.sh`
- 文件路径: `run_db_health_check_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_frontend_api_smoke.sh`
- 文件路径: `run_frontend_api_smoke.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | python3 -m unittest tests/test_frontend_api_smoke.py
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_fx_daily_akshare_once.sh`
- 文件路径: `run_fx_daily_akshare_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_investment_signal_tracker_once.sh`
- 文件路径: `run_investment_signal_tracker_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_job_always.sh`
- 文件路径: `run_job_always.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | if [[ $# -lt 1 ]]; then | echo "usage: $0 <job_key>" >&2
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_job_if_trade_day.sh`
- 文件路径: `run_job_if_trade_day.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | if [[ $# -lt 1 ]]; then | echo "usage: $0 <job_key>" >&2
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_logic_view_cache_once.sh`
- 文件路径: `run_logic_view_cache_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_macro_series_akshare_once.sh`
- 文件路径: `run_macro_series_akshare_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_market_expectations_once.sh`
- 文件路径: `run_market_expectations_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_minimal_regression.sh`
- 文件路径: `run_minimal_regression.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | python3 -m unittest tests/test_minimal_regression.py
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_minline_akshare_patch_once.sh`
- 文件路径: `run_minline_akshare_patch_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_minline_backfill_recent.sh`
- 文件路径: `run_minline_backfill_recent.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_minline_focus_once.py`
- 文件路径: `run_minline_focus_once.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, latest_score_date, load_targets, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `run_minline_intraday_focus_once.sh`
- 文件路径: `run_minline_intraday_focus_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_monitored_chatlog_backfill_midnight.sh`
- 文件路径: `run_monitored_chatlog_backfill_midnight.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_monitored_chatlog_fetch_once.sh`
- 文件路径: `run_monitored_chatlog_fetch_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_archive_once.sh`
- 文件路径: `run_news_archive_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_daily_summary_once.sh`
- 文件路径: `run_news_daily_summary_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_dedupe_once.sh`
- 文件路径: `run_news_dedupe_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_fetch_once.sh`
- 文件路径: `run_news_fetch_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_sentiment_once.sh`
- 文件路径: `run_news_sentiment_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_news_stock_map_once.sh`
- 文件路径: `run_news_stock_map_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_research_reports_once.sh`
- 文件路径: `run_research_reports_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_scheduler_consistency_check.sh`
- 文件路径: `run_scheduler_consistency_check.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | python3 /home/zanbo/zanbotest/scripts/scheduler/check_cron_sync.py
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_signal_state_machine_once.sh`
- 文件路径: `run_signal_state_machine_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_stock_news_backfill_missing_once.sh`
- 文件路径: `run_stock_news_backfill_missing_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_stock_news_expand_focus.py`
- 文件路径: `run_stock_news_expand_focus.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, latest_score_date, load_targets, run_cmd, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `run_stock_news_expand_once.sh`
- 文件路径: `run_stock_news_expand_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_stock_news_score_once.sh`
- 文件路径: `run_stock_news_score_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `run_theme_hotspot_engine_once.sh`
- 文件路径: `run_theme_hotspot_engine_once.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `runtime/quantaalpha_runtime.env`
- 文件路径: `runtime/quantaalpha_runtime.env`
- 文件作用: 配置/元数据
- 主要功能/逻辑: 无法确定（需结合业务上下文）
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `runtime_env.sh`
- 文件路径: `runtime_env.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | export USE_POSTGRES="${USE_POSTGRES:-1}" | export DATABASE_URL="${DATABASE_URL:-postgresql://zanbo@/stockapp}"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `runtime_secrets.py`
- 文件路径: `runtime_secrets.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: env_str, env_csv, _load_token_from_file, resolve_tushare_token
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `script_cli.py`
- 文件路径: `script_cli.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: add_common_cli_flags, now_utc_text, log_step
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `scripts/check_navigation_config_alignment.py`
- 文件路径: `scripts/check_navigation_config_alignment.py`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 主要函数: _read_frontend_config, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `scripts/check_rbac_dynamic_config.py`
- 文件路径: `scripts/check_rbac_dynamic_config.py`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 主要函数: main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `scripts/scheduler/check_cron_sync.py`
- 文件路径: `scripts/scheduler/check_cron_sync.py`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 主要函数: _parse_allowed, _matches_cron, _next_trigger, _load_enabled_jobs, _expected_line, _current_crontab_lines ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `scripts/scheduler/render_crontab.py`
- 文件路径: `scripts/scheduler/render_crontab.py`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 主要函数: _load_enabled_jobs, _runner_for_category, render_lines, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `scripts/setup_quantaalpha_runtime.sh`
- 文件路径: `scripts/setup_quantaalpha_runtime.sh`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" | VENV_DIR="${ROOT_DIR}/runtime/quantaalpha_venv"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `scripts/smoke_navigation_permissions.py`
- 文件路径: `scripts/smoke_navigation_permissions.py`
- 文件作用: 运维/校验脚本
- 主要功能/逻辑: 主要函数: _has_permission, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `seed_signal_quality_rules.py`
- 文件路径: `seed_signal_quality_rules.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_tables, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `seed_stock_alias_dictionary.py`
- 文件路径: `seed_stock_alias_dictionary.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `seed_theme_stock_mapping.py`
- 文件路径: `seed_theme_stock_mapping.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, now_utc_str, ensure_table, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `serve_spa.py`
- 文件路径: `serve_spa.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `services/__init__.py`
- 文件路径: `services/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/__init__.py`
- 文件路径: `services/agent_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/backend_runtime.py`
- 文件路径: `services/agent_service/backend_runtime.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_backend_runtime_deps
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/context/__init__.py`
- 文件路径: `services/agent_service/context/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/context/company_context_builder.py`
- 文件路径: `services/agent_service/context/company_context_builder.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_company_context, summarize_context_dimensions
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/contracts.py`
- 文件路径: `services/agent_service/contracts.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要类: DecisionConfidence, ReviewBlock, RoleOutput, AgentAnalysisResult
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/features/__init__.py`
- 文件路径: `services/agent_service/features/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/features/trend_features.py`
- 文件路径: `services/agent_service/features/trend_features.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_trend_features, summarize_feature_dimensions
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/graph/__init__.py`
- 文件路径: `services/agent_service/graph/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/graph/company_research_graph.py`
- 文件路径: `services/agent_service/graph/company_research_graph.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: run_company_research_graph
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/graph/trend_analysis_graph.py`
- 文件路径: `services/agent_service/graph/trend_analysis_graph.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: run_trend_analysis_graph
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/multi_role_v3.py`
- 文件路径: `services/agent_service/multi_role_v3.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _now_iso, _loads, _safe_json, _extract_json_blob, _to_list, _coerce_confidence ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/outputs/__init__.py`
- 文件路径: `services/agent_service/outputs/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/outputs/markdown_report.py`
- 文件路径: `services/agent_service/outputs/markdown_report.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: extract_section, _extract_legacy_numbered_block, infer_decision_confidence, build_risk_review, build_portfolio_view
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/roles/__init__.py`
- 文件路径: `services/agent_service/roles/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/roles/catalog.py`
- 文件路径: `services/agent_service/roles/catalog.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/runtime_ops.py`
- 文件路径: `services/agent_service/runtime_ops.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_trend_features, call_llm_trend, build_multi_role_context, build_multi_role_prompt, call_llm_multi_role, split_multi_role_analysis ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/agent_service/service.py`
- 文件路径: `services/agent_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _extract_max_drawdown_from_context, _build_pretrade_signal_payload, _maybe_attach_risk_check, _maybe_notify, run_trend_analysis, run_multi_role_analysis
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/ai_retrieval_service.py`
- 文件路径: `services/ai_retrieval_service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _now_iso, _safe_int, _safe_float, _safe_bool, _normalize_scene, _normalize_query ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/chatrooms_service/__init__.py`
- 文件路径: `services/chatrooms_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/chatrooms_service/service.py`
- 文件路径: `services/chatrooms_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: query_wechat_chatlog, query_chatroom_overview, fetch_single_chatroom_now, query_chatroom_investment_analysis（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/decision_service/__init__.py`
- 文件路径: `services/decision_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/decision_service/service.py`
- 文件路径: `services/decision_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _utc_now, _today_cn, _table_exists, _as_float, _clamp, _parse_json ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/execution/__init__.py`
- 文件路径: `services/execution/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/execution/paper_account/__init__.py`
- 文件路径: `services/execution/paper_account/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/execution/paper_account/models.py`
- 文件路径: `services/execution/paper_account/models.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _utc_now
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/execution/risk_rules/__init__.py`
- 文件路径: `services/execution/risk_rules/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/execution/risk_rules/basic.py`
- 文件路径: `services/execution/risk_rules/basic.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: max_position_check, max_drawdown_check, volatility_check, liquidity_check, pre_trade_check
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/market_contracts/__init__.py`
- 文件路径: `services/market_contracts/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/market_contracts/events.py`
- 文件路径: `services/market_contracts/events.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要类: MarketEvent
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/news_priority_guard.py`
- 文件路径: `services/news_priority_guard.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _pending_news_unscored_count, _run_news_score_batch, ensure_news_scored_before_stock_news
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/__init__.py`
- 文件路径: `services/notifications/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/channels/__init__.py`
- 文件路径: `services/notifications/channels/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/channels/wechat_personal.py`
- 文件路径: `services/notifications/channels/wechat_personal.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _build_text, send_wechat_personal_message
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/channels/wecom.py`
- 文件路径: `services/notifications/channels/wecom.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: send_wecom_markdown
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/contracts.py`
- 文件路径: `services/notifications/contracts.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要类: NotificationPayload
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/notifications/service.py`
- 文件路径: `services/notifications/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: notify_with_wecom, notify_with_wechat_personal, notify, build_notification_payload
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/quantaalpha_service/__init__.py`
- 文件路径: `services/quantaalpha_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/quantaalpha_service/research_data_adapter.py`
- 文件路径: `services/quantaalpha_service/research_data_adapter.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _safe_div, _pearson_corr, _rank, _spearman_corr, _window, _val ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/quantaalpha_service/service.py`
- 文件路径: `services/quantaalpha_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _utc_now, _parse_utc, _safe_json, _ensure_tables, _pick_active_llm, _pearson_corr ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/__init__.py`
- 文件路径: `services/reporting/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/backend_runtime.py`
- 文件路径: `services/reporting/backend_runtime.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_reporting_runtime_deps
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/contracts.py`
- 文件路径: `services/reporting/contracts.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_reporting_protocol_meta
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/daily_summaries.py`
- 文件路径: `services/reporting/daily_summaries.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: enrich_summary_item, query_daily_summaries, start_daily_summary_generation, get_daily_summary_task
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/exporters/__init__.py`
- 文件路径: `services/reporting/exporters/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/exporters/image_exporter.py`
- 文件路径: `services/reporting/exporters/image_exporter.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_image_export_meta
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/renderers/__init__.py`
- 文件路径: `services/reporting/renderers/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/renderers/html_renderer.py`
- 文件路径: `services/reporting/renderers/html_renderer.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: render_html_document
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/renderers/markdown_renderer.py`
- 文件路径: `services/reporting/renderers/markdown_renderer.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: render_markdown_document
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/report_queries.py`
- 文件路径: `services/reporting/report_queries.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _parse_json_text, _top_market_expectations_for_theme, _market_expectations_for_report, query_research_reports
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/runtime_ops.py`
- 文件路径: `services/reporting/runtime_ops.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: query_news_daily_summaries, get_daily_summary_by_date, generate_daily_summary, cleanup_async_jobs, serialize_async_daily_summary_job, create_async_daily_summary_job ...
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/service.py`
- 文件路径: `services/reporting/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_report_payload
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/reporting/templates/README.md`
- 文件路径: `services/reporting/templates/README.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Reporting Templates
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/signals_service/__init__.py`
- 文件路径: `services/signals_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/signals_service/admin.py`
- 文件路径: `services/signals_service/admin.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: query_signal_audit, query_signal_quality_config, save_signal_quality_rules, save_signal_mapping_blocklist
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/signals_service/graph.py`
- 文件路径: `services/signals_service/graph.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _table_exists, _as_float, _clamp, _parse_json, _normalize_center_type, _latest_score_date ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/signals_service/queries.py`
- 文件路径: `services/signals_service/queries.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _top_market_expectations_for_theme, query_investment_signals, query_investment_signal_timeline, query_theme_hotspots（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/signals_service/service.py`
- 文件路径: `services/signals_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: build_signals_service_deps, build_signals_runtime_deps
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/stock_detail_service/__init__.py`
- 文件路径: `services/stock_detail_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/stock_detail_service/assembler.py`
- 文件路径: `services/stock_detail_service/assembler.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: parse_json_text, safe_float, round_or_none, percentile_rank, latest_macro_row, build_financial_summary ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/stock_detail_service/service.py`
- 文件路径: `services/stock_detail_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: query_stock_detail, build_stock_detail_runtime_deps
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/stock_news_service/__init__.py`
- 文件路径: `services/stock_news_service/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/stock_news_service/service.py`
- 文件路径: `services/stock_news_service/service.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: query_stock_news, query_stock_news_sources, fetch_stock_news_now, score_stock_news_now, build_fetch_response, build_score_response ...
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/system/__init__.py`
- 文件路径: `services/system/__init__.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `services/system/llm_providers_admin.py`
- 文件路径: `services/system/llm_providers_admin.py`
- 文件作用: 后端业务服务层
- 主要功能/逻辑: 主要函数: _safe_bool, _resolve_config_path, _default_payload, _load_payload, _save_payload, _as_nodes ...（长文件已提炼关键逻辑）
- 与其他文件或模块的关系: 被 backend/routes 或 jobs 调用，承接核心业务逻辑与查询拼装
- 是否是核心文件: 是

### `skills/README.md`
- 文件路径: `skills/README.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Skills
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `skills/__init__.py`
- 文件路径: `skills/__init__.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `skills/strategies/README.md`
- 文件路径: `skills/strategies/README.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: strategies 模板
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `skills/strategies/__init__.py`
- 文件路径: `skills/strategies/__init__.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 以脚本入口/过程逻辑为主（含数据库/采集/调度操作）
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `skills/strategies/daily_summary_template.md`
- 文件路径: `skills/strategies/daily_summary_template.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 日报模板 / 市场摘要 / 重点新闻
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `skills/strategies/multi_role_research_template.md`
- 文件路径: `skills/strategies/multi_role_research_template.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 多角色研究模板 / 标的信息 / 角色结论
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `skills/strategies/template_loader.py`
- 文件路径: `skills/strategies/template_loader.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: load_strategy_template_text
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `skills/strategies/trend_analysis_template.md`
- 文件路径: `skills/strategies/trend_analysis_template.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 趋势分析模板 / 标的与行情概览 / 趋势结构
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `start_all.sh`
- 文件路径: `start_all.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | cd "$ROOT"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_auto_update.sh`
- 文件路径: `start_auto_update.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | INTERVAL_SECONDS="${1:-3600}"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_backend.sh`
- 文件路径: `start_backend.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_backend_llm.sh`
- 文件路径: `start_backend_llm.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_backend_llm2.sh`
- 文件路径: `start_backend_llm2.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_backend_macro.sh`
- 文件路径: `start_backend_macro.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_backend_multi_role.sh`
- 文件路径: `start_backend_multi_role.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest | . /home/zanbo/zanbotest/runtime_env.sh
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_cn_news_eastmoney_10s.sh`
- 文件路径: `start_cn_news_eastmoney_10s.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | PID_FILE="/tmp/cn_eastmoney_10s.pid"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_frontend.sh`
- 文件路径: `start_frontend.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | cd "$ROOT/apps/web"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_frontend_nextgen_dev.sh`
- 文件路径: `start_frontend_nextgen_dev.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest/apps/web | npm run dev
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_frontend_nextgen_preview.sh`
- 文件路径: `start_frontend_nextgen_preview.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | cd /home/zanbo/zanbotest/apps/web | npm run preview
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_nginx_8077.sh`
- 文件路径: `start_nginx_8077.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | RUNTIME_DIR="${BASE_DIR}/nginx_runtime"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_stream_news_worker.sh`
- 文件路径: `start_stream_news_worker.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | cd "$ROOT"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `start_ws_realtime.sh`
- 文件路径: `start_ws_realtime.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | cd "$ROOT"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `stream_news_worker.py`
- 文件路径: `stream_news_worker.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `tests/test_agent_service.py`
- 文件路径: `tests/test_agent_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: AgentServiceContractTest, _ConnStub
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_chatroom_jobs.py`
- 文件路径: `tests/test_chatroom_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: ChatroomJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_chatrooms_service.py`
- 文件路径: `tests/test_chatrooms_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: _ConnStub, _CursorStub, _SQLiteStub, ChatroomsServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_decision_service.py`
- 文件路径: `tests/test_decision_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要函数: _init_schema
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_execution_risk.py`
- 文件路径: `tests/test_execution_risk.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: ExecutionRiskTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_frontend_api_smoke.py`
- 文件路径: `tests/test_frontend_api_smoke.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: FrontendApiSmokeTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_llm_gateway_rate_limit.py`
- 文件路径: `tests/test_llm_gateway_rate_limit.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: LlmGatewayRateLimitTests
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_llm_jobs.py`
- 文件路径: `tests/test_llm_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: LlmJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_llm_providers_admin.py`
- 文件路径: `tests/test_llm_providers_admin.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: LlmProvidersAdminTests
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_macro_jobs.py`
- 文件路径: `tests/test_macro_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: MacroJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_market_jobs.py`
- 文件路径: `tests/test_market_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: MarketJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_minimal_regression.py`
- 文件路径: `tests/test_minimal_regression.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: MinimalRegressionTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_news_jobs.py`
- 文件路径: `tests/test_news_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: NewsJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_notifications_service.py`
- 文件路径: `tests/test_notifications_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: NotificationsServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_notifications_wechat_personal.py`
- 文件路径: `tests/test_notifications_wechat_personal.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: NotificationsWechatPersonalTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_quantaalpha_jobs.py`
- 文件路径: `tests/test_quantaalpha_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: QuantaAlphaJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_quantaalpha_service.py`
- 文件路径: `tests/test_quantaalpha_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: QuantaAlphaServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_reporting_queries.py`
- 文件路径: `tests/test_reporting_queries.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: _ConnStub, _CursorStub, _SQLiteStub, ReportingQueriesTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_reporting_runtime_ops.py`
- 文件路径: `tests/test_reporting_runtime_ops.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: _Publisher, ReportingRuntimeOpsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_reporting_service.py`
- 文件路径: `tests/test_reporting_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: ReportingServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_signals_graph.py`
- 文件路径: `tests/test_signals_graph.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: SignalsGraphTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_signals_queries.py`
- 文件路径: `tests/test_signals_queries.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要函数: _resolve_signal_table
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_signals_service.py`
- 文件路径: `tests/test_signals_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: SignalsServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_stock_detail_service.py`
- 文件路径: `tests/test_stock_detail_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要函数: _init_schema
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_stock_news_jobs.py`
- 文件路径: `tests/test_stock_news_jobs.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: StockNewsJobsTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `tests/test_stock_news_service.py`
- 文件路径: `tests/test_stock_news_service.py`
- 文件作用: 测试文件
- 主要功能/逻辑: 主要类: StockNewsServiceTest
- 与其他文件或模块的关系: 验证对应 services/jobs/routes 的主路径行为
- 是否是核心文件: 否

### `un_news_score_backlog_parallel.sh`
- 文件路径: `un_news_score_backlog_parallel.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | LOCK_FILE="/tmp/un_news_score_backlog_parallel.lock"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `un_sentiment_backlog_parallel.sh`
- 文件路径: `un_sentiment_backlog_parallel.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | BASE_DIR="/home/zanbo/zanbotest" | LOCK_FILE="/tmp/un_sentiment_backlog_parallel.lock"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `update_daily_stock_events.py`
- 文件路径: `update_daily_stock_events.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: parse_args, china_today, main
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 否

### `watch_cn_news_eastmoney_10s.sh`
- 文件路径: `watch_cn_news_eastmoney_10s.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | PID_FILE="/tmp/cn_eastmoney_10s.pid" | LOG_FILE="/tmp/cn_eastmoney_10s_watchdog.log"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `watch_realtime_services.sh`
- 文件路径: `watch_realtime_services.sh`
- 文件作用: 运行/部署脚本
- 主要功能/逻辑: 关键命令: set -euo pipefail | ROOT="/home/zanbo/zanbotest" | LOG="/tmp/realtime_services_watchdog.log"
- 与其他文件或模块的关系: 编排 Python 脚本与服务进程，服务部署/巡检链路
- 是否是核心文件: 否

### `ws_realtime_server.py`
- 文件路径: `ws_realtime_server.py`
- 文件作用: 根目录 Python 脚本
- 主要功能/逻辑: 主要函数: now_utc_iso, encode_ws_text_frame, recv_exact, read_ws_frame, parse_http_request, send_http_json ...
- 与其他文件或模块的关系: 通常调用 db_compat、services、collectors 或 jobs 形成业务处理链
- 是否是核心文件: 是

### `前端美化建议报告.md`
- 文件路径: `前端美化建议报告.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: Zanbo Quant 前端美化建议报告 / 一、当前页面现状（浏览器视角） / 1.1 整体印象
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `新浪接口.txt`
- 文件路径: `新浪接口.txt`
- 文件作用: 其他文件
- 主要功能/逻辑: 文本内容摘要: import requests code = "sh600114"
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否

### `新闻评分积压问题分析.md`
- 文件路径: `新闻评分积压问题分析.md`
- 文件作用: 文档/规范
- 主要功能/逻辑: 文档主题: 新闻未评分积压问题分析报告 / 一、当前积压状况 / 1.1 整体数据
- 与其他文件或模块的关系: 与同目录模块协同，关系需结合调用方进一步确认
- 是否是核心文件: 否


## 3. 模块级归纳

### `apps/web`
- 模块职责: 前端 Web 应用（Vue3+TS）
- 文件数量: 99
- 关键文件: `apps/web/.gitignore`, `apps/web/.vscode/extensions.json`, `apps/web/README.md`, `apps/web/index.html`, `apps/web/package-lock.json`, `apps/web/package.json`, `apps/web/public/favicon.svg`, `apps/web/public/icons.svg`
- 模块依赖关系: 依赖 `backend/routes` 提供 API，核心由 `stores` 管理状态，`shared` 提供复用组件/工具。

### `backend`
- 模块职责: 后端 API 入口与路由层
- 文件数量: 11
- 关键文件: `backend/__init__.py`, `backend/routes/__init__.py`, `backend/routes/ai_retrieval.py`, `backend/routes/chatrooms.py`, `backend/routes/decision.py`, `backend/routes/news.py`, `backend/routes/quant_factors.py`, `backend/routes/signals.py`
- 模块依赖关系: 作为 HTTP 入口调用 `services`，并与 `jobs`/数据库共享业务模型。

### `services`
- 模块职责: 后端业务服务层
- 文件数量: 65
- 关键文件: `services/__init__.py`, `services/agent_service/__init__.py`, `services/agent_service/backend_runtime.py`, `services/agent_service/context/__init__.py`, `services/agent_service/context/company_context_builder.py`, `services/agent_service/contracts.py`, `services/agent_service/features/__init__.py`, `services/agent_service/features/trend_features.py`
- 模块依赖关系: 被 `backend/routes` 与 `jobs` 共同复用，是业务规则集中层。

### `jobs`
- 模块职责: 任务调度与任务执行
- 文件数量: 20
- 关键文件: `jobs/__init__.py`, `jobs/chatroom_jobs.py`, `jobs/decision_jobs.py`, `jobs/llm_jobs.py`, `jobs/macro_jobs.py`, `jobs/market_jobs.py`, `jobs/news_jobs.py`, `jobs/quantaalpha_jobs.py`
- 模块依赖关系: 依赖 `job_registry.py` 调度定义，执行时调用 `collectors` 与 `services`。

### `collectors`
- 模块职责: 数据采集与清洗管道
- 文件数量: 15
- 关键文件: `collectors/__init__.py`, `collectors/chatrooms/__init__.py`, `collectors/chatrooms/pipelines.py`, `collectors/macro/__init__.py`, `collectors/macro/pipelines.py`, `collectors/market/__init__.py`, `collectors/market/pipelines.py`, `collectors/news/__init__.py`
- 模块依赖关系: 被根目录 `fetch_/backfill_/build_` 脚本调用，写入数据库供 `services` 查询。

### `tests`
- 模块职责: 自动化测试
- 文件数量: 26
- 关键文件: `tests/test_agent_service.py`, `tests/test_chatroom_jobs.py`, `tests/test_chatrooms_service.py`, `tests/test_decision_service.py`, `tests/test_execution_risk.py`, `tests/test_frontend_api_smoke.py`, `tests/test_llm_gateway_rate_limit.py`, `tests/test_llm_jobs.py`
- 模块依赖关系: 覆盖 services/jobs/api 主路径，是回归保障主入口。

### `docs`
- 模块职责: 文档与规范
- 文件数量: 31
- 关键文件: `docs/Opportunitiesforsomeideas/Newfeatures&ideas`, `docs/Opportunitiesforsomeideas/总览版.md`, `docs/Opportunitiesforsomeideas/我和ai的金融对话沟通.txt`, `docs/Opportunitiesforsomeideas/投研自动化落地方案.md`, `docs/ai_retrieval_gateway_2026-04-06.md`, `docs/command_line_reference.md`, `docs/database_audit_report.md`, `docs/database_dictionary.md`
- 模块依赖关系: 定义主链规则、部署方式、数据字典，与实现保持同步。

### `scripts`
- 模块职责: 工具与一致性检查脚本
- 文件数量: 6
- 关键文件: `scripts/check_navigation_config_alignment.py`, `scripts/check_rbac_dynamic_config.py`, `scripts/scheduler/check_cron_sync.py`, `scripts/scheduler/render_crontab.py`, `scripts/setup_quantaalpha_runtime.sh`, `scripts/smoke_navigation_permissions.py`
- 模块依赖关系: 对导航、RBAC、调度一致性做校验，辅助 CI/运维。

### `config`
- 模块职责: 运行配置
- 文件数量: 3
- 关键文件: `config/llm_providers.json`, `config/rbac_dynamic.config.json`, `config/tushare_token.txt`
- 模块依赖关系: 被 LLM provider、RBAC、数据源配置读取。

### `.codex`
- 模块职责: 协作规范与AI辅助资产
- 文件数量: 33
- 关键文件: `.codex/agents/delivery-fast.toml`, `.codex/agents/frontend-first.toml`, `.codex/agents/ops-sre.toml`, `.codex/agents/reviewer.toml`, `.codex/checklists/auth-permission-troubleshooting.md`, `.codex/checklists/doc-freshness-checklist.md`, `.codex/checklists/frontend-change-checklist.md`, `.codex/checklists/llm-pipeline-checklist.md`
- 模块依赖关系: 提供协作流程模板和检查清单，辅助开发治理。

### `(root)`
- 模块职责: 根目录脚本与启动入口
- 文件数量: 164
- 关键文件: `.gitignore`, `AGENTS.md`, `PROJECT_ANALYSIS_REPORT.md`, `PROJECT_FULL_ANALYSIS.md`, `README_WEB.md`, `SQLITE_RETIRED.md`, `audit_database_report.py`, `auto_update_once.sh`
- 模块依赖关系: 包含启动脚本、一次性任务脚本与系统入口文件，连接所有模块。


### 非源码目录说明（未逐文件展开）

- `.venv/`, `.deps/`: Python 依赖与虚拟环境目录（文件规模大，非项目业务源码）。
- `runtime/`, `logs/`, `tmp/`, `nginx_runtime/`, `__pycache__/`: 运行产物、缓存和临时数据。
- `.git/`: 版本控制内部对象目录。

## 4. 项目整体总结

- 主要目标: 构建面向 A 股投研的本地化系统，强调前端展示完整性与后端可用性。
- 核心功能: 资讯采集、信号/主题分析、个股与宏观数据查询、决策研究、多角色 LLM 研究、任务调度与实时推送。
- 技术栈: Python（后端/任务/采集）、Vue 3 + TypeScript + Vite（前端）、PostgreSQL + Redis、Shell 运维脚本。
- 主要架构模式: 单体后端 + 分层路由（routes）+ 服务层（services）+ 调度层（jobs）+ 采集层（collectors）+ 前端 store 驱动展示。
- 关键执行流程: 数据采集/回填 -> 入库与派生构建 -> jobs 编排 -> services 查询/计算 -> backend API 输出 -> web 页面展示与实时刷新。
- 重要入口文件: `backend/server.py`、`apps/web/src/main.ts`、`apps/web/src/app/router.ts`、`job_registry.py`、`job_orchestrator.py`、`start_all.sh`。
- 潜在风险、问题或可优化点:
  1. 根目录脚本数量多且职责分散，存在重复与维护成本上升风险。
  2. 文档与实现存在时效差风险（需持续执行文档新鲜度检查）。
  3. 多数据源采集链路稳定性依赖外部接口，需强化重试与监控。
  4. 前端页面较多，接口兼容变更容易引发回归，需保持 smoke 覆盖。
- 无法确定项说明: 对纯占位/不可读文本文件，统一标记“无法确定”，并按目录与命名给出推测关系。