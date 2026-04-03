# .codex 使用说明

这个目录的目标是：让新对话更快上手项目，并让日常任务始终围绕两条核心目标展开。

## 当前固定优先级

1. 第一核心目标：把前端展示业务做好
2. 第二核心目标：保证测试可用性

## 目录结构

- `config.toml`
  项目级配置、主目标、关键路径、推荐验证命令
- `agents/`
  面向不同任务形态的 agent 预设
- `skills/`
  可复用的工作流说明
- `templates/`
  可直接复制给新对话或任务对话的模板
- `checklists/`
  改动前、push 前、文档巡检时的检查单
- `prompts/`
  高频任务 prompt 模板

## 推荐使用方式

### 1. 新开一个对话 / 快速扫仓库

优先做法：
- 先看 `AGENTS.md`
- 再用 `skills/repo-scan/SKILL.md` 建立最小上下文

如果需要直接给新对话一段启动语，可使用：

```text
这是一个已有代码库项目，请先按仓库里的 AGENTS.md 理解项目工作方式。

项目根目录：
/home/zanbo/zanbotest

请先完成这几步，不要急着写代码：
1. 阅读 /home/zanbo/zanbotest/AGENTS.md
2. 按 AGENTS.md 的“参考文件”顺序快速建立项目认知
3. 用 5-10 条总结你对当前项目主链路的理解
4. 明确当前最高优先级：
   - 第一核心目标：把前端展示业务做好
   - 第二核心目标：保证测试可用性
5. 在开始任何实现前，先输出：
   - 你理解的任务
   - 涉及的文件和模块
   - 风险点
   - 最小实施计划
```

### 2. 开始一个具体任务

优先使用：
- `templates/task-kickoff.md`

如果要拆分最小提交单元：
- `templates/minimal-commit-plan.md`

### 3. 做前端页面类任务

结合使用：
- `skills/frontend-delivery/SKILL.md`
- `checklists/frontend-change-checklist.md`

### 4. 做测试 / 验证类任务

结合使用：
- `skills/testability-guard/SKILL.md`

### 5. 做文档巡检

结合使用：
- `skills/doc-freshness/SKILL.md`
- `checklists/doc-freshness-checklist.md`

### 6. 做代码审查

结合使用：
- `agents/reviewer.toml`

### 7. 在 git push 前

必须至少过一遍：
- `checklists/push-before-checklist.md`

### 8. 远端联调与故障分流

优先使用：
- `checklists/remote-deploy-smoke-checklist.md`
- `checklists/auth-permission-troubleshooting.md`
- `prompts/incident-404-401-diff.md`

### 9. QuantaAlpha 旁路运行

优先使用：
- `checklists/quantaalpha-runtime-checklist.md`

### 10. LLM 节点运维与稳定性

优先使用：
- `skills/llm-provider-ops/SKILL.md`
- `checklists/llm-pipeline-checklist.md`

### 11. 任务编排故障排查

优先使用：
- `skills/job-triage/SKILL.md`
- `checklists/scheduler-parity-checklist.md`

### 12. 数据质量巡检与修复

优先使用：
- `skills/data-quality-audit/SKILL.md`
- `prompts/backlog-drain.md`

### 13. 线上事故处理与复盘

优先使用：
- `agents/ops-sre.toml`
- `prompts/incident-rca.md`
- `templates/hotfix-kickoff.md`

## 推荐 agent 使用场景

- `frontend-first`
  当任务主要是页面、交互、展示、图表、仪表盘、路由、权限前端链路时使用

- `delivery-fast`
  当你希望“提速但不失焦”时使用；采用 2-4 个强相关改动的一次性交付节奏

- `reviewer`
  当需要做代码审查、PR review 或回归风险检查时使用

- `ops-sre`
  当出现线上故障、任务失败、超时/502、重试风暴、端口状态不一致时使用

## 推荐 skills 使用场景

- `repo-scan`
  新对话第一次进项目，或任务前快速扫模块边界和调用链

- `minimal-fix`
  明确要求最小改动修复

- `frontend-delivery`
  前端展示任务

- `testability-guard`
  测试可用性任务

- `doc-freshness`
  文档同步任务

- `llm-provider-ops`
  LLM 节点探活、节点优先级调整、fallback 稳定性排障

- `job-triage`
  定时任务/编排任务故障定位、止血、补跑

- `data-quality-audit`
  数据质量巡检、缺口定位、修复命令落地

## 最小闭环习惯

无论做什么任务，尽量维持这个节奏：

1. 先用 `AGENTS.md` 建立主链路认知
2. 再用 `.codex/templates/` 或对应 skill 明确任务边界
3. 实施时优先复用现有代码与组件
4. 完成后至少做最小验证
5. push 前检查文档是否最新

## 当前推荐最小验证

- 前端改动：
  `cd /home/zanbo/zanbotest/apps/web && npm run build`

- 常见 Python 改动：
  `cd /home/zanbo/zanbotest && python3 -m py_compile backend/server.py backend/routes/*.py job_registry.py`

- QuantaAlpha 调度入口：
  `cd /home/zanbo/zanbotest && python3 job_orchestrator.py dry-run quantaalpha_health_check`

- QuantaAlpha 接口可达性：
  `curl -i "http://127.0.0.1:8077/api/quant-factors/results?page=1&page_size=1"`

## 注意

- `.codex` 是项目辅助层，不替代 `AGENTS.md`
- 长期规则看 `AGENTS.md`
- 动态项目事实看 `docs/system_overview_cn.md`、`README_WEB.md`、源码和任务定义
