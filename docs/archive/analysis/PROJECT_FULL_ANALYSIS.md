# Zanbo Quant 投研系统 - 项目全景分析报告

**生成时间**：2026-04-06  
**分析范围**：项目全目录递归扫描  
**分析文件数**：200+ 个核心文件  
**项目规模**：中大型（约 5万+ 行代码）

---

## 第一部分：项目整体目录概览

```
/home/zanbo/zanbotest/
├── AGENTS.md                     # Agent 开发指南（主链路规则）
├── README_WEB.md                 # 运行部署说明
├── PROJECT_ANALYSIS_REPORT.md    # 项目分析报告
├── SQLITE_RETIRED.md             # SQLite 退役说明

# ========== 前端应用 ==========
├── apps/web/                     # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── app/                  # 路由、权限、导航
│   │   ├── pages/                # 页面组件
│   │   ├── services/api/         # API 服务
│   │   ├── stores/               # Pinia 状态管理
│   │   └── shared/               # 共享组件、工具
│   ├── package.json
│   └── vite.config.ts

# ========== 后端核心 ==========
├── backend/
│   ├── server.py                 # 主 API 服务（334KB，核心入口）
│   └── routes/                   # 路由模块
│       ├── stocks.py
│       ├── signals.py
│       ├── news.py
│       ├── chatrooms.py
│       ├── system.py
│       ├── ai_retrieval.py
│       └── quant_factors.py

# ========== 业务服务层 ==========
├── services/
│   ├── ai_retrieval_service.py   # AI 检索服务
│   ├── agent_service/            # LLM Agent 服务
│   │   ├── multi_role_v3.py     # 多角色分析 v3/v4
│   │   ├── graph/               # LangGraph 图编排
│   │   └── context/             # 上下文构建
│   ├── chatrooms_service/        # 群聊服务
│   ├── signals_service/          # 信号服务
│   ├── stock_news_service/       # 个股新闻服务
│   ├── stock_detail_service/     # 股票详情服务
│   ├── quantaalpha_service/      # 因子挖掘服务
│   ├── reporting/                # 报告服务
│   ├── execution/                # 执行层（风控、模拟账户）
│   ├── notifications/            # 通知服务
│   └── system/                   # 系统服务

# ========== 任务系统 ==========
├── job_registry.py               # 任务定义注册表
├── job_orchestrator.py           # 任务调度编排器
├── jobs/                         # 任务执行入口
│   ├── llm_jobs.py
│   ├── news_jobs.py
│   ├── chatroom_jobs.py
│   ├── stock_news_jobs.py
│   ├── macro_jobs.py
│   ├── market_jobs.py
│   ├── quantaalpha_jobs.py
│   └── run_*.py                  # 各任务运行器

# ========== 数据采集（fetch_*.py） ==========
├── fetch_news_rss.py             # RSS 国际新闻
├── fetch_cn_news_eastmoney.py    # 东方财富国内新闻
├── fetch_cn_news_sina_7x24.py    # 新浪 7x24 快讯
├── fetch_stock_news_eastmoney_to_db.py  # 个股新闻
├── fetch_chatroom_list_to_db.py  # 群聊列表
├── fetch_monitored_chatlogs_once.py     # 群聊记录
├── fetch_wechat_chatlog_clean_to_db.py  # 微信聊天记录
├── fetch_market_expectations_polymarket.py  # Polymarket 预期
├── fetch_all_stock_codes.py      # 股票代码
├── fetch_sina_minline_all_listed.py     # 分钟线
└── ...（约 15 个采集脚本）

# ========== 数据回填（backfill_*.py） ==========
├── backfill_stock_financials.py
├── backfill_stock_events.py
├── backfill_company_governance.py
├── backfill_macro_series.py
├── backfill_fx_daily.py
├── backfill_capital_flow_stock.py
├── backfill_stock_news_items.py
├── backfill_wechat_chatlogs_30d.py
├── backfill_stock_scores_daily.py
├── backfill_risk_scenarios.py
└── ...（约 20 个回填脚本）

# ========== 数据构建（build_*.py） ==========
├── build_investment_signal_tracker.py    # 投资信号
├── build_theme_hotspot_engine.py         # 主题热点
├── build_signal_state_machine.py         # 信号状态机
├── build_chatroom_candidate_pool.py      # 群聊候选池
└── build_stock_daily_price_rollups.py    # 价格汇总

# ========== LLM 能力 ==========
├── llm_gateway.py                # LLM 网关（fallback、限流）
├── llm_provider_config.py        # Provider 配置
├── manage_llm_providers.py       # Provider 管理
├── llm_score_news.py             # 新闻评分
├── llm_score_stock_news.py       # 个股新闻评分
├── llm_summarize_daily_important_news.py  # 日报总结
├── llm_tag_chatrooms.py          # 群聊标签
├── llm_analyze_chatroom_investment_bias.py  # 投资倾向
├── llm_score_chatroom_sentiment.py
├── llm_resolve_stock_aliases.py  # 别名归一
└── ...（约 12 个 LLM 脚本）

# ========== 实时服务 ==========
├── realtime_streams.py           # Redis 事件流
├── stream_news_worker.py         # 新闻流 Worker
├── ws_realtime_server.py         # WebSocket 服务

# ========== 基础设施 ==========
├── db_compat.py                  # 数据库兼容层
├── runtime_secrets.py            # 运行时密钥
├── runtime_env.sh                # 运行时环境
├── market_calendar.py            # 交易日历

# ========== 配置与文档 ==========
├── config/                       # 配置文件
│   ├── llm_providers.json        # LLM Provider 配置
│   └── rbac_dynamic.config.json  # 动态权限配置
├── docs/                         # 文档
│   ├── system_overview_cn.md
│   ├── database_dictionary.md
│   ├── database_audit_report.md
│   └── ...（约 20 个文档）
├── tests/                        # 测试
└── collectors/                   # 采集器模块
    ├── news/
    ├── chatrooms/
    ├── stock_news/
    ├── macro/
    └── market/
```

---

## 第二部分：逐文件分析

### 2.1 前端核心文件

#### **apps/web/package.json**
- **文件作用**：前端依赖配置
- **技术栈**：Vue 3.5 + TypeScript 5.9 + Vite 8 + TailwindCSS 4
- **核心依赖**：Pinia（状态管理）、Vue Router、TanStack Query、ECharts、Lightweight Charts
- **是否核心**：是（前端构建入口）

#### **apps/web/src/app/router.ts**
- **文件作用**：前端路由定义与权限守卫
- **主要功能**：
  - 定义 30+ 页面路由
  - 权限验证（RBAC 动态权限）
  - 登录状态检查
  - 路由级权限映射
- **关键路由**：dashboard、stocks/*、signals/*、research/*、chatrooms/*、system/*
- **是否核心**：是（前端主链路入口）

#### **apps/web/src/app/permissions.ts**
- **文件作用**：权限定义与验证
- **权限模型**：role-based + effective permissions 组合
- **是否核心**：是

### 2.2 后端核心文件

#### **backend/server.py**
- **文件作用**：主 API 服务端（334KB，单文件较大）
- **主要功能**：
  - HTTP 服务启动（ThreadingHTTPServer）
  - 路由分发与中间件
  - CORS 处理
  - LLM 多角色分析 API
  - 股票、新闻、群聊、信号等全量 API
  - 服务依赖注入
- **关键端点**：
  - `/api/health` - 健康检查
  - `/api/stocks/*` - 股票相关
  - `/api/news/*` - 新闻相关
  - `/api/llm/multi-role/v3/*` - 多角色分析
  - `/api/investment-signals` - 投资信号
  - `/api/chatrooms/*` - 群聊
- **与其他文件关系**：
  - 导入所有 backend/routes/ 模块
  - 导入所有 services/ 模块
  - 依赖 db_compat、job_orchestrator、llm_gateway
- **是否核心**：是（系统主入口）

#### **backend/routes/stocks.py**
- **文件作用**：股票相关 API 路由
- **主要功能**：
  - 股票列表查询
  - 股票详情（价格、财务、估值、治理、风险）
  - 分钟线/K 线数据
- **是否核心**：是

#### **backend/routes/signals.py**
- **文件作用**：投资信号相关 API 路由
- **主要功能**：
  - 投资信号查询（7d/1d 口径）
  - 主题热点查询
  - 信号状态时间线
  - 投研报告查询
- **是否核心**：是

#### **backend/routes/system.py**
- **文件作用**：系统管理 API（45KB）
- **主要功能**：
  - LLM Provider 管理
  - 任务调度管理
  - 用户权限管理
  - 数据库审计
  - 系统配置
- **是否核心**：是

### 2.3 服务层核心文件

#### **services/ai_retrieval_service.py**
- **文件作用**：AI 检索服务（RAG）
- **主要功能**：
  - 向量嵌入生成
  - 语义检索
  - 混合检索（BM25 + 向量）
  - 检索指标统计
- **关键配置**：AI_RETRIEVAL_ENABLED、AI_RETRIEVAL_SHADOW_MODE
- **是否核心**：是（AI 检索主链路）

#### **services/agent_service/multi_role_v3.py**
- **文件作用**：多角色分析 v3/v4 核心实现
- **主要功能**：
  - 异步任务创建与管理
  - LangGraph 图编排（v4 引擎）
  - 六阶段分析流程（Analyst → Bull/Bear → Research Manager → Trader → 风控 → Portfolio Manager）
  - 用户决策审批
  - SSE 流式输出
- **关键状态**：queued/running/pending_user_decision/approved/rejected/deferred/done_with_warnings/error
- **是否核心**：是（核心研究能力）

#### **services/signals_service/service.py**
- **文件作用**：投资信号服务
- **主要功能**：
  - 信号查询与聚合
  - 主题热点分析
  - 信号状态机
  - 信号质量规则
- **是否核心**：是

### 2.4 任务系统核心文件

#### **job_registry.py**
- **文件作用**：任务定义单一真源
- **主要功能**：
  - 定义 30+ 定时任务
  - 任务分类（news/stock_news/chatrooms/macro/signals/audit）
  - 调度表达式（cron 格式）
  - 命令模板
- **关键任务**：
  - 新闻采集（每 2-5 分钟）
  - 信号刷新（每小时）
  - 群聊分析（每小时）
  - 个股新闻评分（每 10 分钟）
- **是否核心**：是

#### **job_orchestrator.py**
- **文件作用**：任务调度编排
- **主要功能**：
  - 任务定义同步
  - 任务执行记录
  - 告警管理
  - 交易日门禁
  - 分布式锁（Redis）
- **数据表**：job_definitions、job_runs、job_alerts
- **是否核心**：是

### 2.5 数据采集核心文件

#### **fetch_news_rss.py**
- **文件作用**：RSS 国际新闻采集
- **数据源**：Dow Jones、Bloomberg、MarketWatch
- **主要功能**：
  - RSS 解析
  - 去重（content_hash）
  - 实时流推送
- **是否核心**：是

#### **fetch_cn_news_eastmoney.py / fetch_cn_news_sina_7x24.py**
- **文件作用**：国内财经新闻采集
- **数据源**：东方财富、新浪
- **是否核心**：是

#### **build_investment_signal_tracker.py**
- **文件作用**：投资信号主构建器
- **主要功能**：
  - 聚合新闻、个股新闻、群聊候选池
  - 生成 30d/7d/1d 信号表
  - 信号快照与事件记录
  - 信号强度计算
- **输出表**：investment_signal_tracker、investment_signal_tracker_7d、investment_signal_tracker_1d
- **是否核心**：是

### 2.6 LLM 核心文件

#### **llm_gateway.py**
- **文件作用**：LLM 统一网关
- **主要功能**：
  - Provider fallback 机制
  - 限流控制（Redis + 本地双限流）
  - 延迟与成功率指标
  - 多模型路由
- **支持模型**：deepseek-chat、gpt-5.4、kimi-k2.5 等
- **是否核心**：是

#### **llm_provider_config.py**
- **文件作用**：LLM Provider 配置管理
- **配置文件**：config/llm_providers.json
- **主要功能**：
  - Provider 优先级
  - 模型路由策略
  - 多角色 v3 策略
  - 嵌入模型配置
- **是否核心**：是

### 2.7 基础设施文件

#### **db_compat.py**
- **文件作用**：数据库兼容层（SQLite → PostgreSQL）
- **主要功能**：
  - SQL 方言转换
  - 连接管理
  - Redis 缓存
  - Row 工厂
- **核心类**：CompatCursor、CompatPostgresConnection、Row
- **是否核心**：是（数据访问基础）

#### **realtime_streams.py**
- **文件作用**：实时事件流
- **主要功能**：
  - Redis Stream / PubSub
  - 新闻批次发布
  - 应用事件发布
- **是否核心**：是

---

## 第三部分：模块级归纳

### 3.1 前端模块

| 模块 | 职责 | 关键文件 | 依赖关系 |
|------|------|----------|----------|
| **app** | 路由、权限、导航 | router.ts、permissions.ts、navigation.ts | → stores/auth |
| **pages** | 页面组件 | 30+ 页面 Vue 文件 | → services/api、shared |
| **services/api** | API 客户端 | stocks.ts、news.ts、signals.ts 等 | → http.ts |
| **stores** | 状态管理 | auth.ts、ui.ts、realtime.ts | → services/api |
| **shared** | 共享组件 | ui/、charts/、query/、realtime/ | → 各页面 |

### 3.2 后端模块

| 模块 | 职责 | 关键文件 | 依赖关系 |
|------|------|----------|----------|
| **backend/server** | HTTP 服务、路由分发 | server.py | → routes/*、services/* |
| **backend/routes** | API 端点实现 | stocks.py、signals.py、news.py、chatrooms.py、system.py | → services/* |
| **services/agent** | LLM 多角色分析 | agent_service/、multi_role_v3.py | → llm_gateway |
| **services/signals** | 投资信号 | signals_service/ | → db_compat |
| **services/retrieval** | AI 检索 | ai_retrieval_service.py | → llm_provider_config |
| **services/chatrooms** | 群聊分析 | chatrooms_service/ | → db_compat |
| **services/news** | 新闻服务 | stock_news_service/ | → db_compat |

### 3.3 任务调度模块

| 模块 | 职责 | 关键文件 | 依赖关系 |
|------|------|----------|----------|
| **job_registry** | 任务定义 | job_registry.py | → 独立 |
| **job_orchestrator** | 调度执行 | job_orchestrator.py | → job_registry、db_compat |
| **jobs** | 任务执行器 | jobs/*.py | → collectors、services |

### 3.4 数据采集模块

| 模块 | 职责 | 关键文件 | 依赖关系 |
|------|------|----------|----------|
| **collectors/news** | 新闻采集 | collectors/news/、fetch_news_*.py | → db_compat |
| **collectors/chatrooms** | 群聊采集 | collectors/chatrooms/、fetch_chatroom*.py | → db_compat |
| **backfill** | 历史补数 | backfill_*.py | → db_compat |
| **build** | 数据构建 | build_*.py | → db_compat |

### 3.5 LLM 模块

| 模块 | 职责 | 关键文件 | 依赖关系 |
|------|------|----------|----------|
| **llm_gateway** | 网关与限流 | llm_gateway.py | → llm_provider_config |
| **llm_provider_config** | Provider 配置 | llm_provider_config.py | → config/llm_providers.json |
| **llm_scoring** | 评分与分析 | llm_score*.py、llm_analyze*.py | → llm_gateway |
| **agent_service** | 多角色分析 | services/agent_service/ | → llm_gateway |

### 3.6 模块调用关系图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端 (Vue 3)                         │
│    apps/web/src: router → pages → services/api → stores      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────┐
│                    后端 (backend/server.py)                  │
│              routes/* → services/* → db_compat               │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼─────┐ ┌────────▼────────┐
│  job_orchestrator │  llm_gateway │  realtime_streams │
│  + jobs/       │  + agent_svc  │  + ws_server      │
└───────┬───────┘ └──────┬─────┘ └────────┬────────┘
        │                │                │
        ▼                ▼                ▼
   ┌────────┐      ┌──────────┐     ┌──────────┐
   │PostgreSQL│      │LLM APIs  │     │  Redis   │
   └────────┘      └──────────┘     └──────────┘
```

---

## 第四部分：项目整体总结

### 4.1 项目主要目标

**Zanbo Quant** 是一个围绕 **A 股市场**的**本地化投研系统**，核心目标是：

1. **数据采集与整合**：聚合股票行情、财经新闻、群聊观点、宏观数据
2. **AI 分析能力**：通过 LLM 进行新闻评分、公司研究、群聊观点提炼
3. **投资信号生成**：融合多源数据生成可追踪的投资信号
4. **研究支持**：多角色 AI 分析、趋势研判、因子挖掘

### 4.2 核心功能

| 功能域 | 核心能力 |
|--------|----------|
| **股票数据** | 基础资料、日线/分钟线行情、财务指标、估值、治理画像、资金流 |
| **新闻系统** | RSS 国际新闻、国内快讯、个股新闻、自动评分、情绪识别、日报总结 |
| **群聊分析** | 聊天记录抓取、投资倾向分析、别名归一、候选池生成 |
| **投资信号** | 多源信号聚合、主题热点、信号时间线、状态机追踪 |
| **LLM 研究** | 多角色公司分析（v4 LangGraph）、趋势分析、向量检索 |
| **系统管理** | 任务调度、Provider 管理、权限控制、数据库审计 |

### 4.3 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3.5 + TypeScript 5.9 + Vite 8 + TailwindCSS 4 + Pinia |
| **后端** | Python 3.10 + 原生 HTTP (ThreadingHTTPServer) |
| **数据库** | PostgreSQL（主库）、SQLite（兼容/退役中） |
| **缓存** | Redis（限流、缓存、实时流） |
| **LLM** | DeepSeek、GPT-5.4、Kimi K2.5 + LangGraph (v4) |
| **部署** | Shell 脚本 + cron 定时任务 |
| **向量检索** | OpenAI Embeddings + 混合检索 |

### 4.4 主要架构与设计模式

#### 架构特点

1. **单体后端 + 拆分路由**：server.py 为主入口，routes/ 拆分不同领域
2. **服务层抽象**：services/ 按领域封装业务逻辑
3. **任务调度系统**：registry + orchestrator + jobs 三层结构
4. **数据库兼容层**：db_compat.py 屏蔽 SQLite/PostgreSQL 差异
5. **LLM 网关**：统一入口 + fallback + 限流 + 指标
6. **实时流**：Redis Stream + WebSocket 推送

#### 设计模式

- **依赖注入**：services 通过 deps 字典注入依赖
- **异步任务**：多角色分析采用 job + worker 模式
- **管道模式**：数据采集 → 清洗 → 评分 → 聚合 → 信号
- **策略模式**：LLM Provider 多策略路由

### 4.5 关键执行流程

#### 新闻线
```
RSS/国内新闻采集 → 去重清洗 → 入库 → LLM 评分/摘要 → 股票映射 → 投资信号
```

#### 群聊线
```
群列表抓取 → 聊天记录拉取 → 清洗 → LLM 投资倾向分析 → 别名归一 → 候选池 → 投资信号
```

#### 信号线
```
新闻 + 个股新闻 + 群聊候选池 → 主题映射 → 信号聚合 → 7d/1d 口径 → 快照/事件记录 → 前端展示
```

#### 多角色分析线
```
前端发起 → 创建异步任务 → worker 消费 → LangGraph 六阶段执行 → SSE 流式回显 → 用户决策
```

### 4.6 重要入口文件

| 入口 | 文件路径 | 用途 |
|------|----------|------|
| **前端主入口** | apps/web/src/main.ts | Vue 应用启动 |
| **前端路由** | apps/web/src/app/router.ts | 页面路由定义 |
| **后端主入口** | backend/server.py | HTTP 服务 |
| **任务注册** | job_registry.py | 定时任务定义 |
| **任务调度** | job_orchestrator.py | 任务执行编排 |
| **LLM 网关** | llm_gateway.py | LLM 统一调用 |
| **数据库兼容** | db_compat.py | 数据库访问 |
| **一键启动** | start_all.sh | 全系统启动 |

### 4.7 潜在风险、问题与可优化点

#### 风险点

1. **后端单文件过大**：server.py 334KB，维护成本高
2. **SQLite 退役过渡**：部分脚本可能仍存在 SQLite 依赖
3. **并发能力**：原生 HTTP server 非生产级，无异步支持
4. **LLM 依赖**：多角色分析强依赖外部 API，成本与稳定性风险
5. **数据一致性**：多任务并行写入可能存在竞争条件

#### 问题

1. **测试覆盖不足**：tests/ 目录测试用例有限
2. **文档同步**：代码与文档可能不同步（AGENTS.md 要求严格同步）
3. **错误处理**：部分脚本错误处理不够完善
4. **配置分散**：配置分散在多个 JSON 文件和环境变量中

#### 可优化点

1. **架构层面**：
   - 后端拆分为微服务或至少按领域拆分模块
   - 引入 FastAPI/Flask 替代原生 HTTP server
   - 引入异步框架（asyncio）提升并发

2. **数据层面**：
   - 统一数仓（ClickHouse/Doris）替代 PostgreSQL 分析查询
   - 向量数据库（Milvus/Pinecone）替代文件嵌入存储

3. **工程层面**：
   - 完善 CI/CD 流程
   - 增加集成测试覆盖
   - 引入类型检查（mypy）和代码格式化（ruff/black）

4. **运维层面**：
   - 增加健康检查与自愈机制
   - 完善监控告警（Prometheus + Grafana）
   - 日志聚合与链路追踪

---

## 附录：文件清单统计

### 按类型统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python 脚本 | 150+ | 采集、构建、服务、任务 |
| Shell 脚本 | 40+ | 启动、调度、运维 |
| Vue 组件 | 30+ | 页面、共享组件 |
| TypeScript | 20+ | 服务、状态、工具 |
| 配置文件 | 10+ | JSON、环境变量 |
| 文档 | 20+ | Markdown 文档 |

### 核心数据表（30+ 张）

```
# 股票与公司
stock_codes, stock_daily_prices, stock_minline, stock_financials
stock_valuation_daily, stock_events, company_governance, stock_scores_daily
stock_news_items

# 宏观与资金
macro_series, fx_daily, rate_curve_points, spread_daily
capital_flow_market, capital_flow_stock, risk_scenarios

# 新闻
news_feed_items, news_feed_items_archive, news_daily_summaries

# 群聊
chatroom_list_items, wechat_chatlog_clean_items
chatroom_investment_analysis, chatroom_stock_candidate_pool

# 信号
investment_signal_tracker, investment_signal_tracker_7d, investment_signal_tracker_1d
investment_signal_daily_snapshots, investment_signal_events
theme_stock_mapping, stock_alias_dictionary

# 任务与系统
job_definitions, job_runs, job_alerts
multi_role_v3_jobs, multi_role_v3_job_runs
```

---

*文档结束*
