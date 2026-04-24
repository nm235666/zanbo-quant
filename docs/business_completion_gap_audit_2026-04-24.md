# 业务完成度差距审计报告

审计日期：2026-04-24  
审计方式：只读代码、只读运行库查询、只读调度检查；未修改代码、数据库 schema、UI 或依赖。

## 1. 总体结论：真实完成度估计

本项目不是纯静态展示或简单 mock 项目。按当前运行配置，应以 PostgreSQL 主库为准，而不是本地历史 SQLite 文件。`runtime_env.sh` 默认启用 `USE_POSTGRES=1`，并连接 `postgresql://zanbo@/stockapp`。主库中存在大量真实数据和运行痕迹，包括行情、新闻、信号、群聊、研报、任务运行记录。

综合判断：

- UI/API 表面完成度：约 70%-80%。
- 数据采集与展示完成度：约 60%-70%。
- 投研决策闭环完成度：约 35%-45%。
- 组合执行、持仓、复盘闭环完成度：约 15%-25%。
- 全项目真实业务完成度：约 45%-55%。

核心差距不是“页面全是假”，而是“前半段采集、分析、展示较真实，后半段决策动作、执行、持仓、复盘、指标门禁明显断裂”。项目已经具备较多真实数据资产和运营任务，但尚未形成稳定的端到端投资业务闭环。

## 2. 主库证据摘要

当前 PostgreSQL 主库观察到：

| 对象 | 规模/状态 | 结论 |
|---|---:|---|
| 表数量 | 84 | 不是空项目 |
| `job_runs` | 106,976 | 有长期任务运行记录 |
| `stock_daily_prices` | 1,426,828 | 行情数据较充分 |
| `stock_minline` | 25,519,848 | 分钟线数据较充分 |
| `stock_scores_daily` | 104,507 | 评分数据存在 |
| `news_feed_items` | 85,431 | 新闻数据存在 |
| `stock_news_items` | 140,991 | 个股新闻数据存在 |
| `investment_signal_events` | 33,251 | 信号事件存在 |
| `wechat_chatlog_clean_items` | 304,552 | 群聊清洗数据存在 |
| `chatroom_stock_candidate_pool` | 764 | 群聊候选池存在 |
| `research_reports` | 310 | 研报产物存在 |
| `multi_role_v3_jobs` | 45 | 多角色任务存在 |
| `decision_actions` | 11 | 决策动作样本很少 |
| `funnel_candidates` | 324 | 候选漏斗存在但推进不足 |
| `portfolio_orders` | 66 | 多为 smoke/取消记录 |
| `portfolio_positions` | 0 | 持仓闭环未跑通 |
| `portfolio_reviews` | 0 | 交易复盘闭环未跑通 |

最新数据时间：

| 数据项 | 最新时间 |
|---|---|
| 最新行情日线 | 20260423 |
| 最新评分 | 20260423 |
| 最新新闻 | 2026-04-24T04:28:53Z |
| 最新个股新闻 | 2026-04-24 12:15:53 |
| 最新信号 | 2026-04-24T03:29:42Z |
| 最新主题 | 2026-04-24T12:15:53 |
| 最新任务运行 | 2026-04-24T04:34:05Z |
| 最新漏斗更新 | 2026-04-24T01:15:07Z |
| 最新决策动作 | 2026-04-19T20:21:11Z |

## 3. 已完成但可疑模块

### 3.1 数据采集与数据资产

该部分真实度较高。行情、新闻、个股新闻、宏观、信号、主题、群聊数据均有主库规模和近期更新时间支撑。任务运行记录量也很大，说明采集链路并非只靠静态文件或演示数据。

可疑点：

- 部分任务近期仍有失败告警。
- 数据存在不代表已被投研闭环充分消费。
- 部分表规模大，但其下游对决策、执行、复盘的影响仍有限。

### 3.2 决策看板与评分看板

前端页面不是纯静态 mock，`DecisionBoardPage.vue`、`ScoreboardPage.vue` 等页面使用 Vue Query 调用真实 API。后端 `backend/routes/decision.py` 和 `services/decision_service/service.py` 会读取评分、新闻、信号、群聊、多角色 trace 等数据构建看板和证据包。

可疑点：

- `decision_actions` 主库仅 11 条，最新动作停在 2026-04-19。
- 决策动作数量不足以证明日常投研工作流已真实跑起来。
- `confirm/reject/defer/watch` 会自动创建 portfolio order，但默认 `size=0`、`planned_price=None`，更像审计记录，不是可执行交易计划。

### 3.3 多角色分析

多角色 v3 有真实任务表和运行记录，主库中 `multi_role_v3_jobs` 状态分布为 approved/deferred/rejected/error，说明不是简单 mock。

可疑点：

- 服务内存在 `_apply_degrade_placeholder()`，节点失败后可生成“阶段降级占位”。
- 降级结果仍可能进入页面展示，容易让用户误以为已形成完整分析。
- 该模块更适合作为研究辅助，不宜直接视为稳定交易决策引擎。

### 3.4 权限、角色、订阅/配额

后端存在用户、角色、权限、配额相关表和逻辑：

- `app_auth_users`
- `app_auth_sessions`
- `app_auth_role_policies`
- `app_auth_usage_daily`
- trend/multi-role daily quota

可疑点：

- 若未配置 admin token 且无活跃用户，后端保护接口会开放，属于 Dev/LAN 默认策略。
- 权限主要影响页面/API 访问和 LLM 次数，对投资闭环的业务行为约束较弱。
- 订阅等级尚未明显影响候选、决策、执行、复盘等核心业务流程。

## 4. 明显空壳模块

### 4.1 组合持仓

`portfolio_positions` 主库为 0。前端持仓页提示“在决策工作台确认交易后，持仓将出现在这里”，但后端成交订单并不会写入或更新 `portfolio_positions`。

服务层 `update_order()` 只更新订单状态、成交价、成交时间，并把 execution status 写回 `decision_actions.action_payload_json`。它没有：

- 增减持仓数量。
- 重算平均成本。
- 更新市值。
- 计算浮动盈亏。
- 处理买卖、加仓、减仓、清仓。

结论：持仓模块目前是页面和表结构存在，但业务闭环未实现。

### 4.2 交易复盘

`portfolio_reviews` 主库为 0。前端复盘页允许人工录入复盘，但不是成交后自动触发，也不校验订单是否真实执行。

服务层 `add_review()` 只插入：

- `order_id`
- `review_tag`
- `review_note`
- `slippage`
- `latency_ms`

缺失：

- 自动计算收益。
- 自动计算滑点。
- 根据持仓/行情生成 T+N 复盘。
- 回写决策动作质量。
- 沉淀规则修正建议。

结论：复盘模块目前更像手工备注系统。

### 4.3 候选漏斗推进与复盘快照

`funnel_candidates` 有 324 条，但状态分布为：

| 状态 | 数量 |
|---|---:|
| `ingested` | 303 |
| `decision_ready` | 20 |
| `confirmed` | 1 |

来源分布为：

| 来源 | 数量 |
|---|---:|
| `historical_backfill` | 303 |
| `decision_daily_snapshot` | 20 |
| `portfolio_order` | 1 |

这说明候选池大量停留在初始进入状态，没有持续推进到增强、确认、执行、复盘。

此外，调度同步检查显示以下任务缺失：

- `chatroom_signal_accuracy_refresh`
- `funnel_ingested_score_align`
- `funnel_review_refresh`

并且 `decision_daily_snapshot` 存在 drift。

结论：漏斗状态机代码存在，但实际运营闭环不稳定。

### 4.4 组合订单

`portfolio_orders` 有 66 条，但状态分布为：

| 状态 | 数量 |
|---|---:|
| `cancelled` | 63 |
| `planned` | 3 |

最新订单 note 含 `R32 smoke`，说明不少记录来自 smoke 测试。

前端订单页的“执行”按钮只是弹窗录入成交价，然后 PATCH 订单状态。后端不会产生真实持仓，也不会驱动复盘。

结论：订单模块是“状态跟踪”，不是完整执行系统。

## 5. 关键业务链路断点

### 5.1 候选进入后无法稳定推进

当前大量候选停在 `ingested`。虽然 `services/funnel_service/service.py` 中有状态机和 `promote_ingested_when_score_present()`，但相关 cron 未安装，导致实际推进缺口明显。

断点：

`historical_backfill/signal -> funnel_candidates.ingested -> 停滞`

### 5.2 决策动作无法形成有效执行计划

决策动作 API 会记录 `decision_actions`，也会自动创建 `portfolio_orders`。但自动订单默认 `size=0` 且计划价为空。

断点：

`decision confirm -> portfolio_order(size=0, planned_price=null) -> 不可执行`

### 5.3 订单成交不更新持仓

订单 PATCH 到 `executed` 后，只更新订单本身和决策 payload 的 execution status。

断点：

`portfolio_order.executed -> portfolio_positions 无变化`

### 5.4 持仓不产生复盘

由于持仓为空，复盘也无自动来源。即使手工添加复盘，也不会自动归因或回写策略质量。

断点：

`position/price movement -> portfolio_review/funnel_review_snapshot 缺失`

### 5.5 指标门禁被样本不足绕过

`jobs/collect_daily_metrics.py` 中，当决策动作少于 20 条时，`sample_insufficient=True` 并跳过门禁阈值检查。

断点：

`daily metrics -> sample_insufficient -> 不阻断低质量闭环`

## 6. 页面/API/服务/数据库/任务/测试对应关系表

| 功能 | 前端页面 | API | 服务层 | 数据表 | 调度任务 | 测试覆盖 | 真实闭环判断 |
|---|---|---|---|---|---|---|---|
| 股票行情 | Stocks/Prices/Detail | `/api/stocks`, `/api/prices`, `/api/minline` | stock 查询逻辑 | `stock_codes`, `stock_daily_prices`, `stock_minline` | market data jobs | 有 smoke/合同测试 | 较真实 |
| 新闻资讯 | News/StockNews/DailySummaries | `/api/news`, `/api/stock-news` | news/stock_news service | `news_feed_items`, `stock_news_items`, `news_daily_summaries` | news jobs | 有服务测试 | 较真实 |
| 信号主题 | Signals pages | `/api/investment-signals`, `/api/theme-hotspots` | signals service | `investment_signal_*`, `theme_*` | signal/theme jobs | 部分测试 | 中高 |
| 群聊分析 | Chatrooms pages | `/api/chatrooms/*` | chatrooms service | `wechat_chatlog_clean_items`, `chatroom_*` | chatroom jobs | 部分测试 | 中，但任务失败需修 |
| 决策看板 | DecisionBoard/Scoreboard | `/api/decision/*` | decision_service | `decision_snapshots`, `decision_actions` | `decision_daily_snapshot` | 有服务测试 | 中，动作太少 |
| 候选漏斗 | CandidateFunnel | `/api/funnel/*` | funnel_service | `funnel_candidates`, `funnel_transitions` | `funnel_ingested_score_align`, `funnel_review_refresh` | 状态机测试 | 中低，调度缺失 |
| 多角色分析 | MultiRoleResearch | `/api/llm/multi-role/v3/*` | multi_role_v3 | `multi_role_v3_jobs` | worker guard/recovery | 有服务测试 | 中，存在降级占位 |
| 量化因子 | QuantFactors | `/api/quant-factors/*` | quantaalpha/quant service | `quantaalpha_runs`, `quantaalpha_factor_results` | quant jobs 部分 disabled | 合同/任务测试 | 中低，失败率高 |
| 组合订单 | Orders | `/api/portfolio/orders` | portfolio_service | `portfolio_orders` | 无完整执行任务 | 订单状态测试 | 低，状态记录为主 |
| 持仓 | Positions | `/api/portfolio/positions` | portfolio_service | `portfolio_positions` | 无 | in-memory paper account 测试，不集成 | 很低 |
| 复盘 | Review | `/api/portfolio/review` | portfolio_service | `portfolio_reviews` | 无完整自动复盘 | 轻量测试 | 很低 |
| 权限配额 | Login/UserAdmin/RolePolicies | `/api/auth/*` | backend auth | `app_auth_*` | 无核心业务任务 | 合同/页面测试 | 中 |
| 每日指标 | SourceMonitor/Metrics | `/api/metrics/summary` | metrics job | docs metrics artifact | `collect_daily_metrics` | 脚本级 | 中低，样本不足绕过 |

## 7. 测试覆盖判断

当前测试不是完全无用，但大量测试偏“接口存在、页面字符串存在、状态更新成功”，对真实业务闭环覆盖不足。

已覆盖较好的部分：

- 决策服务部分证据包、动作记录、看板流程。
- 漏斗状态机、状态转换、幂等与版本冲突。
- portfolio order 的创建、状态更新、取消。
- API 合同、写边界、路由存在性。
- 多角色服务基础行为。

明显缺失的测试：

- `decision confirm -> portfolio order -> execute -> portfolio_positions` 端到端测试。
- 成交后平均成本、数量、市值、浮盈亏更新测试。
- `portfolio_orders` 与 `portfolio_reviews` 的真实复盘联动测试。
- 漏斗从 `ingested` 到 `amplified/decision_ready/confirmed/executed/reviewed` 的定时任务联动测试。
- `collect_daily_metrics` 基于主库真实闭环数据的阈值门禁测试。
- 权限/订阅等级对核心投研功能的实际限制测试。

结论：测试能证明“代码没有完全断”，不能证明“业务闭环已完成”。

## 8. 最优先补齐的 5 条业务闭环

### 8.1 修复调度安装与漂移

优先补齐：

- `funnel_ingested_score_align`
- `funnel_review_refresh`
- `chatroom_signal_accuracy_refresh`
- `decision_daily_snapshot` drift

验收标准：

- `check_cron_sync.py` 不再报告 missing/drift。
- 任务能写入 `job_runs`。
- 对应业务表有新增或状态推进。

### 8.2 决策确认生成有效交易计划

当前 `confirm` 自动生成 `size=0` 的订单，业务意义不足。

最小补齐：

- `confirm` 必须携带仓位区间或目标仓位。
- 生成订单时写入非零 `size` 或可计算的目标金额。
- 计划价取最新行情或用户确认价。
- 缺少仓位/价格时，只允许保存为 watch/defer，不允许生成可执行订单。

### 8.3 订单成交更新持仓

最小补齐：

- `executed buy/add` 增加或重算持仓。
- `executed sell/reduce/close` 扣减持仓。
- 更新平均成本、数量、最后价格、市值、浮盈亏。
- 订单状态与持仓更新必须在同一业务事务中完成。

### 8.4 成交后自动生成复盘快照

最小补齐：

- 成交后创建待复盘记录。
- 基于 `stock_daily_prices` 写入 T+N 收益。
- 复盘结果回写 `decision_actions` 和 funnel 状态。
- 页面展示自动复盘与人工备注的区别。

### 8.5 每日指标真正约束闭环质量

最小补齐：

- 指标从主库读取。
- 样本不足时仍输出明确风险，而不是完全跳过门禁。
- 指标至少包含：
  - 决策动作数。
  - 有证据链动作数。
  - 生成订单数。
  - 成交订单数。
  - 持仓更新数。
  - 已复盘数。
  - 漏斗推进率。

## 9. 不建议现在重构的内容

当前不建议优先做：

- 大规模重构前端页面。
- 重写路由和导航。
- 重命名数据库表。
- 抽象新的服务层框架。
- 新增复杂依赖或交易引擎。
- 为了观感修改 UI。
- 扩展更多展示型分析页面。

原因：项目最大短板不是代码结构，而是业务闭环没有跑穿。继续增加页面会放大“看起来完成”的错觉。

## 10. 下一步最小实施计划

### 阶段 1：调度和主库事实校准

目标：让已有任务真实运行。

任务：

1. 修复 crontab missing/drift。
2. 确认漏斗推进任务能从 `ingested` 推进到下一状态。
3. 确认群聊准确率任务能写入 accuracy labels。
4. 在指标页暴露任务缺失/漂移状态。

验收：

- `funnel_candidates.ingested` 数量下降。
- `funnel_transitions` 有新的系统推进记录。
- `job_alerts` 中相关任务不再持续失败。

### 阶段 2：打通最小交易闭环

目标：让一次确认动作能产生真实持仓。

任务：

1. 决策确认时要求仓位/数量/计划价。
2. 生成有效 `portfolio_orders`。
3. 执行订单后更新 `portfolio_positions`。
4. 回写 `decision_actions.action_payload_json.execution_status`。

验收：

- 新增一条 confirm 动作。
- 新增一条 planned order。
- 执行后 order 变为 executed。
- `portfolio_positions` 从 0 变为非 0。

### 阶段 3：打通最小复盘闭环

目标：让成交动作能自动进入复盘。

任务：

1. 成交后生成待复盘记录。
2. T+N 后从行情表计算收益。
3. 写入复盘快照。
4. 回写漏斗状态到 reviewed 或等价状态。

验收：

- `portfolio_reviews` 或复盘快照表出现自动生成记录。
- 决策动作能看到 review conclusion。
- 每日指标能计算 closure_rate。

### 阶段 4：补端到端测试

目标：用测试防止闭环再次退化成状态记录。

必须新增的测试场景：

1. 候选进入并被评分推进。
2. 决策确认并生成有效订单。
3. 订单成交并更新持仓。
4. 成交后生成复盘。
5. 指标任务统计到该闭环。

## 11. 最终判断

这个项目已经过了“原型页面”阶段，但还没有到“真实投研交易业务系统”阶段。它更准确的状态是：

> 数据资产和分析界面较成熟，任务体系存在；但核心投资闭环仍停在候选、动作、订单记录层，尚未稳定穿透到持仓、复盘和质量门禁。

下一步不应继续堆页面，而应集中补齐一条最短闭环：

`候选 -> 证据 -> 决策确认 -> 有效订单 -> 成交 -> 持仓 -> 复盘 -> 指标门禁`

这条链路跑通后，项目真实完成度会有实质提升。
