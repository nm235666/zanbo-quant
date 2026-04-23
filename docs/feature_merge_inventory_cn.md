# 功能合并与去重 — 盘点矩阵

更新时间：2026-04-23  
对应计划：`feature-merge-dedup`（盘点 → L2 Hub 试点 → L1/L3 叙事合并）。

## Phase 0：路径 / API / 任务 / 重叠 / 难度 / Deep link

| 路径前缀或页面 | 主数据/API（典型） | 用户任务一句话 | 与谁重叠 | 合并难度 | 保留独立 URL |
| --- | --- | --- | --- | --- | --- |
| `/app/data/intelligence/*` | `fetchNews`、日报生成 API | 浏览与筛选新闻/日报 | 四页同属「读资讯」 | 低（Hub+Tab） | 是（子路径不变） |
| `/app/data/signals/*` | signals API | 看信号总览/主题/链/时间线 | 四页同属「看信号」 | 低 | 待定 Phase1 二批 |
| `/app/data/chatrooms/*` | chatrooms API | 群聊运维与投资倾向 | 四页同属「群聊」 | 中（含 room/sender 子路径） | 是 |
| `/app/data/stocks/list` vs `scores` vs `detail` | stocks API | 收敛标的 → 看评分 → 下钻 | 与评分总览部分重叠 | 中 | 是 |
| `/app/data/scoreboard` vs `/app/desk/board` | decision/scores API | 看榜单 vs 做动作 | 叙事相关非同一页 | 高（计划排除硬合并） | 是 |
| `/app/desk/workbench` vs `/app/lab/task-inbox` | 工作台聚合 / 任务 API | 今日待办 vs 研究任务队列 | 任务心智 | 中 | 是 |
| `/app/lab/multi-role` vs `/app/lab/roundtable` | LLM 多步会话 | 多角色论证 vs 首席圆桌 | 协作形态 | 中 | 是 |
| `/app/desk/funnel` vs `/app/data/chatrooms/candidates` | 漏斗 / 群聊候选 | 候选生命周期 vs 群聊汇总池 | 「候选」对象 | 高（需产品定对象模型） | 是 |
| `/app/desk/macro-regime` vs `/app/data/macro` | 状态机 vs 原始序列 | 配置语言 vs 查数 | 弱重叠 | 低（互链即可） | 是 |
| Admin `signals-audit/quality/state-timeline` | 治理配置 | 审计与纠偏 | 与用户侧信号浏览 | 不合并 | 是 |

## Phase 1 首域决策（业务缺省时默认）

- **首域**：资讯（`/app/data/intelligence` Hub）。
- **Tab 权限**：`global-news` / `cn-news` → `news_read`；`stock-news` → `stock_news_read`；`daily-summaries` → `daily_summary_read`；无权限 Tab 不渲染。
- **侧栏**：第二层由 4 条资讯入口合并为 1 条「资讯中心」→ `/app/data/intelligence`（`permission: news_read`；仅持 `stock_news_read` / `daily_summary_read` 的用户仍可直接访问对应子路径，侧栏可能不显示 Hub，由后续「多权限 OR 导航」增强）。

## Phase 2  backlog（分项评审，未在本次代码范围一次性做完）

| 项 | 建议方向 | 依赖 |
| --- | --- | --- |
| 工作台 + 收件箱 | 单页双 Tab 或侧栏只保留主入口 | 产品确认主入口 |
| 多角色 + 圆桌 | 共用壳 + 模式切换 | 会话状态是否隔离 |
| 漏斗 vs 群聊候选 | 统一「候选」状态枚举与文案 | 后端/数据契约 |
| 信号 / 群聊 Hub | 复制资讯 Hub 模式 | Phase1 验收通过后 |

### Phase2 小 PR 审计（本轮已核对代码，未再重复造入口）

- `ResearchWorkbenchPage` 已含指向 `/app/lab/task-inbox` 的「任务收件箱」链接。
- `MultiRoleResearchPage` 已含升级到 `/app/lab/roundtable` 的入口；圆桌页已有多角色关联说明。
- 漏斗与群聊候选的数据对齐仍依赖产品与后端契约；已补充运营说明 [docs/funnel_operating_model_cn.md](funnel_operating_model_cn.md)（评分对齐任务、复盘快照、双进池路径），群聊候选池卡片增加「带入候选漏斗」互链。

## Phase 3 数据去重

- 与 `docs/database_audit_report.md` 中新闻重复等问题对齐；前端 Hub 不替代 DB 去重。

## 验收口径（Phase 1 资讯）

- 侧栏 L2 资讯相关入口由 4 变为 1。
- `/app/data/intelligence/global-news` 等旧子路径仍可访问；`/app/data/intelligence` 重定向到首个有权限的子路径。
- `vue-tsc`、相关 Playwright、`run_minimal_regression.sh` 通过。
