# 数据库数据字典

- 生成时间：`2026-03-27 14:46:17 UTC`
- 数据库：`PostgreSQL 主库`
- 表数量：`23`

## 总览

| 表名 | 中文用途 | 当前行数 | 归类 |
| --- | --- | ---: | --- |
| `stock_codes` | 股票基础信息主表，是所有股票相关数据的主索引表。 | 5814 | 股票与公司数据 |
| `stock_daily_prices` | 股票日线行情表，保存历史日线 OHLCV 数据。 | 1327993 | 股票与公司数据 |
| `stock_minline` | 股票分钟线表，保存分时/分钟级价格与成交量数据。 | 1757145 | 股票与公司数据 |
| `stock_valuation_daily` | 股票估值日频表，保存 PE/PB/PS/股息率/市值等估值快照。 | 125985 | 股票与公司数据 |
| `stock_financials` | 股票财务核心指标表，按报告期保存营收、利润、ROE、现金流等数据。 | 17631 | 股票与公司数据 |
| `stock_events` | 股票事件表，保存分红、回购、解禁、业绩预告等事件。 | 128529 | 股票与公司数据 |
| `company_governance` | 研究用治理画像表，把股东结构、董事高管结构、增减持、质押等治理数据拼成公司治理快照。 | 2744 | 股票与公司数据 |
| `capital_flow_stock` | 个股级资金流数据，用于观察单只股票主力/大单/中单/小单资金流向。 | 1256146 | 宏观、资金流与风险 |
| `capital_flow_market` | 市场级资金流数据，主要记录北向/南向等整体资金净流入情况。 | 476 | 宏观、资金流与风险 |
| `stock_scores_daily` | 股票综合评分日快照表，包含总分、分项得分和行业内相对评分。 | 16479 | 股票与公司数据 |
| `stock_news_items` | 个股相关新闻表，保存与某只股票关联的新闻、评分和摘要。 | 554 | 股票与公司数据 |
| `news_feed_items` | 国际/国内财经快讯主表，保存抓取到的新闻原文信息及 LLM 评分结果。 | 6740 | 新闻与 LLM 新闻分析 |
| `news_feed_items_archive` | 新闻归档表，保存从主新闻表归档出去的历史新闻。 | 50 | 新闻与 LLM 新闻分析 |
| `news_daily_summaries` | 新闻日报总结表，保存对当日重要新闻的 LLM 总结 Markdown。 | 3 | 新闻与 LLM 新闻分析 |
| `macro_series` | 宏观指标时间序列表，存储 CPI、PPI、社融、PMI 等指标的历史序列。 | 35329 | 宏观、资金流与风险 |
| `fx_daily` | 汇率日线表，记录主要汇率对或指数的日频行情。 | 1565 | 宏观、资金流与风险 |
| `rate_curve_points` | 利率曲线关键点表，保存不同市场、不同期限的收益率或政策利率点位。 | 188 | 宏观、资金流与风险 |
| `spread_daily` | 利差日频表，如中美 10Y 利差等衍生指标。 | 47 | 宏观、资金流与风险 |
| `risk_scenarios` | 风险情景表，记录针对个股或资产做出的情景压力测试结果。 | 27425 | 宏观、资金流与风险 |
| `chatroom_list_items` | 群聊基础信息表，记录群 ID、备注名、成员数，以及是否继续纳入监控等状态。 | 166 | 群聊与社群分析 |
| `wechat_chatlog_clean_items` | 清洗后的群聊消息表，过滤图片/链接等无效内容后，保留可分析文本及引用结构。 | 320945 | 群聊与社群分析 |
| `chatroom_investment_analysis` | 群聊投资倾向分析结果表，存储大模型对单个群的总结、投资标的提炼和最终看多/看空结论。 | 27 | 群聊与社群分析 |
| `chatroom_stock_candidate_pool` | 由群聊投资倾向分析聚合出来的候选池表，汇总哪些股票/主题被更多群看多或看空。 | 176 | 群聊与社群分析 |

## 各表详解

### `stock_codes`

- 用途：股票基础信息主表，是所有股票相关数据的主索引表。
- 当前行数：`5814`
- 字段数：`9`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码，主键。 |
| `symbol` | 文本 | 纯数字股票代码。 |
| `name` | 文本 | 股票简称。 |
| `area` | 文本 | 所属地区。 |
| `industry` | 文本 | 所属行业。 |
| `market` | 文本 | 所属市场/板块。 |
| `list_date` | 文本 | 上市日期。 |
| `delist_date` | 文本 | 退市日期。 |
| `list_status` | 文本 | 上市状态，L=上市，D=退市，P=暂停上市。 |

### `stock_daily_prices`

- 用途：股票日线行情表，保存历史日线 OHLCV 数据。
- 当前行数：`1327993`
- 字段数：`11`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `trade_date` | 文本 | 交易日期。 |
| `open` | 双精度浮点 | 开盘价。 |
| `high` | 双精度浮点 | 最高价。 |
| `low` | 双精度浮点 | 最低价。 |
| `close` | 双精度浮点 | 收盘价。 |
| `pre_close` | 双精度浮点 | 前收盘价。 |
| `change` | 双精度浮点 | 涨跌额。 |
| `pct_chg` | 双精度浮点 | 涨跌幅。 |
| `vol` | 双精度浮点 | 成交量。 |
| `amount` | 双精度浮点 | 成交额。 |

### `stock_minline`

- 用途：股票分钟线表，保存分时/分钟级价格与成交量数据。
- 当前行数：`1757145`
- 字段数：`8`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `trade_date` | 文本 | 交易日。 |
| `minute_time` | 文本 | 分钟时间点。 |
| `price` | 双精度浮点 | 该分钟成交价/最新价。 |
| `avg_price` | 双精度浮点 | 均价。 |
| `volume` | 双精度浮点 | 该分钟成交量。 |
| `total_volume` | 双精度浮点 | 截至该分钟的累计成交量。 |
| `source` | 文本 | 数据来源标识。 |

### `stock_valuation_daily`

- 用途：股票估值日频表，保存 PE/PB/PS/股息率/市值等估值快照。
- 当前行数：`125985`
- 字段数：`13`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | 股票代码。 |
| `trade_date` | 文本 | 交易日期。 |
| `pe` | 双精度浮点 | 市盈率。 |
| `pe_ttm` | 双精度浮点 | 滚动市盈率。 |
| `pb` | 双精度浮点 | 市净率。 |
| `ps` | 双精度浮点 | 市销率。 |
| `ps_ttm` | 双精度浮点 | 滚动市销率。 |
| `dv_ratio` | 双精度浮点 | 股息率。 |
| `dv_ttm` | 双精度浮点 | 滚动股息率。 |
| `total_mv` | 双精度浮点 | 总市值。 |
| `circ_mv` | 双精度浮点 | 流通市值。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `stock_financials`

- 用途：股票财务核心指标表，按报告期保存营收、利润、ROE、现金流等数据。
- 当前行数：`17631`
- 字段数：`17`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `report_period` | 文本 | 报告期末日期。 |
| `report_type` | 文本 | 报告类型，如年报、一季报、半年报、三季报。 |
| `ann_date` | 文本 | 公告日期。 |
| `revenue` | 双精度浮点 | 营业收入。 |
| `op_profit` | 双精度浮点 | 营业利润。 |
| `net_profit` | 双精度浮点 | 归母净利润。 |
| `net_profit_excl_nr` | 双精度浮点 | 扣非净利润。 |
| `roe` | 双精度浮点 | 净资产收益率。 |
| `gross_margin` | 双精度浮点 | 毛利率。 |
| `debt_to_assets` | 双精度浮点 | 资产负债率。 |
| `operating_cf` | 双精度浮点 | 经营现金流。 |
| `free_cf` | 双精度浮点 | 自由现金流。 |
| `eps` | 双精度浮点 | 每股收益。 |
| `bps` | 双精度浮点 | 每股净资产。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `stock_events`

- 用途：股票事件表，保存分红、回购、解禁、业绩预告等事件。
- 当前行数：`128529`
- 字段数：`10`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `event_type` | 文本 | 事件类型，如分红、回购、解禁、业绩预告。 |
| `event_date` | 文本 | 事件生效或对应日期。 |
| `ann_date` | 文本 | 公告日期。 |
| `title` | 文本 | 事件标题。 |
| `detail_json` | 文本 | 事件详细结构化 JSON。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |
| `event_key` | 文本 | 事件唯一键，用于幂等去重。 |

### `company_governance`

- 用途：研究用治理画像表，把股东结构、董事高管结构、增减持、质押等治理数据拼成公司治理快照。
- 当前行数：`2744`
- 字段数：`9`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `asof_date` | 文本 | 治理画像对应日期。 |
| `holder_structure_json` | 文本 | 股东结构画像 JSON，包括前十大股东、股东户数、质押等。 |
| `board_structure_json` | 文本 | 董事会/高管结构画像 JSON。 |
| `mgmt_change_json` | 文本 | 高管或重要股东近期增减持等变化 JSON。 |
| `incentive_plan_json` | 文本 | 股权激励计划或占位信息 JSON。 |
| `governance_score` | 双精度浮点 | 治理综合评分。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `capital_flow_stock`

- 用途：个股级资金流数据，用于观察单只股票主力/大单/中单/小单资金流向。
- 当前行数：`1256146`
- 字段数：`10`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `trade_date` | 文本 | 交易日期。 |
| `net_inflow` | 双精度浮点 | 个股总净流入金额。 |
| `main_inflow` | 双精度浮点 | 主力资金净流入金额。 |
| `super_large_inflow` | 双精度浮点 | 超大单净流入金额。 |
| `large_inflow` | 双精度浮点 | 大单净流入金额。 |
| `medium_inflow` | 双精度浮点 | 中单净流入金额。 |
| `small_inflow` | 双精度浮点 | 小单净流入金额。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 数据更新时间。 |

### `capital_flow_market`

- 用途：市场级资金流数据，主要记录北向/南向等整体资金净流入情况。
- 当前行数：`476`
- 字段数：`8`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `trade_date` | 文本 | 交易日期，格式通常为 YYYYMMDD。 |
| `flow_type` | 文本 | 资金流类型，例如北向、南向。 |
| `net_inflow` | 双精度浮点 | 净流入金额。 |
| `buy_amount` | 双精度浮点 | 买入总金额。 |
| `sell_amount` | 双精度浮点 | 卖出总金额。 |
| `unit` | 文本 | 金额单位。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 数据更新时间。 |

### `stock_scores_daily`

- 用途：股票综合评分日快照表，包含总分、分项得分和行业内相对评分。
- 当前行数：`16479`
- 字段数：`37`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `score_date` | 文本 | 评分日期。 |
| `ts_code` | 文本 | 股票代码。 |
| `name` | 文本 | 股票简称。 |
| `symbol` | 文本 | 数字代码。 |
| `market` | 文本 | 市场。 |
| `area` | 文本 | 地区。 |
| `industry` | 文本 | 行业。 |
| `score_grade` | 文本 | 综合评分等级。 |
| `total_score` | 双精度浮点 | 综合总分。 |
| `trend_score` | 双精度浮点 | 趋势分。 |
| `financial_score` | 双精度浮点 | 财务分。 |
| `valuation_score` | 双精度浮点 | 估值分。 |
| `capital_flow_score` | 双精度浮点 | 资金流分。 |
| `event_score` | 双精度浮点 | 事件分。 |
| `news_score` | 双精度浮点 | 新闻分。 |
| `risk_score` | 双精度浮点 | 风险分。 |
| `latest_trade_date` | 文本 | 使用到的最新行情日期。 |
| `latest_report_period` | 文本 | 使用到的最新财报期。 |
| `latest_valuation_date` | 文本 | 使用到的最新估值日期。 |
| `latest_flow_date` | 文本 | 使用到的最新资金流日期。 |
| `latest_event_date` | 文本 | 使用到的最新事件日期。 |
| `latest_news_time` | 文本 | 使用到的最新新闻时间。 |
| `latest_risk_date` | 文本 | 使用到的最新风险日期。 |
| `score_payload_json` | 文本 | 评分细项明细 JSON。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |
| `industry_score_grade` | 文本 | 行业内相对评分等级。 |
| `industry_total_score` | 双精度浮点 | 行业内相对综合总分。 |
| `industry_trend_score` | 双精度浮点 | 行业内相对趋势分。 |
| `industry_financial_score` | 双精度浮点 | 行业内相对财务分。 |
| `industry_valuation_score` | 双精度浮点 | 行业内相对估值分。 |
| `industry_capital_flow_score` | 双精度浮点 | 行业内相对资金流分。 |
| `industry_event_score` | 双精度浮点 | 行业内相对事件分。 |
| `industry_news_score` | 双精度浮点 | 行业内相对新闻分。 |
| `industry_risk_score` | 双精度浮点 | 行业内相对风险分。 |
| `industry_rank` | 长整数 | 行业内排名。 |
| `industry_count` | 长整数 | 行业样本数。 |

### `stock_news_items`

- 用途：个股相关新闻表，保存与某只股票关联的新闻、评分和摘要。
- 当前行数：`554`
- 字段数：`23`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `ts_code` | 文本 | 关联股票代码。 |
| `company_name` | 文本 | 公司名称。 |
| `source` | 文本 | 新闻来源。 |
| `news_code` | 文本 | 新闻源内部编号。 |
| `title` | 文本 | 新闻标题。 |
| `summary` | 文本 | 新闻摘要。 |
| `link` | 文本 | 原文链接。 |
| `pub_time` | 文本 | 发布时间。 |
| `comment_num` | 长整数 | 评论数。 |
| `relation_stock_tags_json` | 文本 | 关联股票标签 JSON。 |
| `content_hash` | 文本 | 内容哈希，用于去重。 |
| `fetched_at` | 文本 | 抓取时间。 |
| `update_time` | 文本 | 更新时间。 |
| `llm_system_score` | 长整数 | 系统重要性评分。 |
| `llm_finance_impact_score` | 长整数 | 财经影响评分。 |
| `llm_finance_importance` | 文本 | 财经重要程度。 |
| `llm_impacts_json` | 文本 | 结构化影响 JSON。 |
| `llm_summary` | 文本 | 个股新闻 LLM 摘要。 |
| `llm_model` | 文本 | 评分/摘要模型。 |
| `llm_scored_at` | 文本 | 评分时间。 |
| `llm_prompt_version` | 文本 | 提示词版本。 |
| `llm_raw_output` | 文本 | 模型原始输出。 |

### `news_feed_items`

- 用途：国际/国内财经快讯主表，保存抓取到的新闻原文信息及 LLM 评分结果。
- 当前行数：`6740`
- 字段数：`19`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `source` | 文本 | 新闻来源。 |
| `title` | 文本 | 新闻标题。 |
| `link` | 文本 | 新闻链接。 |
| `guid` | 文本 | 源站唯一标识。 |
| `summary` | 文本 | 原始摘要。 |
| `category` | 文本 | 新闻分类。 |
| `author` | 文本 | 作者。 |
| `pub_date` | 文本 | 发布时间。 |
| `fetched_at` | 文本 | 抓取时间。 |
| `content_hash` | 文本 | 内容哈希，用于去重。 |
| `llm_system_score` | 长整数 | LLM 评出的系统重要性评分。 |
| `llm_finance_impact_score` | 长整数 | LLM 评出的财经影响评分。 |
| `llm_finance_importance` | 文本 | LLM 评出的财经重要程度等级。 |
| `llm_impacts_json` | 文本 | 影响方向、资产、板块等结构化 JSON。 |
| `llm_model` | 文本 | 评分所用模型。 |
| `llm_scored_at` | 文本 | 评分时间。 |
| `llm_prompt_version` | 文本 | 新闻评分提示词版本。 |
| `llm_raw_output` | 文本 | 模型原始输出。 |

### `news_feed_items_archive`

- 用途：新闻归档表，保存从主新闻表归档出去的历史新闻。
- 当前行数：`50`
- 字段数：`20`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 原新闻主键 ID。 |
| `source` | 文本 | 新闻来源。 |
| `title` | 文本 | 新闻标题。 |
| `link` | 文本 | 新闻链接。 |
| `guid` | 文本 | 源站唯一标识。 |
| `summary` | 文本 | 原始摘要。 |
| `category` | 文本 | 新闻分类。 |
| `author` | 文本 | 作者。 |
| `pub_date` | 文本 | 发布时间。 |
| `fetched_at` | 文本 | 抓取时间。 |
| `content_hash` | 文本 | 内容哈希。 |
| `llm_system_score` | 长整数 | 系统重要性评分。 |
| `llm_finance_impact_score` | 长整数 | 财经影响评分。 |
| `llm_finance_importance` | 文本 | 财经重要程度。 |
| `llm_impacts_json` | 文本 | 结构化影响 JSON。 |
| `llm_model` | 文本 | 评分模型。 |
| `llm_scored_at` | 文本 | 评分时间。 |
| `llm_prompt_version` | 文本 | 提示词版本。 |
| `llm_raw_output` | 文本 | 模型原始输出。 |
| `archived_at` | 文本 | 归档时间。 |

### `news_daily_summaries`

- 用途：新闻日报总结表，保存对当日重要新闻的 LLM 总结 Markdown。
- 当前行数：`3`
- 字段数：`9`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `summary_date` | 文本 | 日报日期。 |
| `filter_importance` | 文本 | 汇总时采用的重要度筛选条件。 |
| `source_filter` | 文本 | 汇总时采用的数据源筛选条件。 |
| `news_count` | 长整数 | 参与总结的新闻条数。 |
| `model` | 文本 | 使用的总结模型。 |
| `prompt_version` | 文本 | 提示词版本。 |
| `summary_markdown` | 文本 | 新闻日报总结 Markdown 内容。 |
| `created_at` | 文本 | 创建时间。 |

### `macro_series`

- 用途：宏观指标时间序列表，存储 CPI、PPI、社融、PMI 等指标的历史序列。
- 当前行数：`35329`
- 字段数：`9`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `indicator_code` | 文本 | 指标代码。 |
| `indicator_name` | 文本 | 指标中文/展示名称。 |
| `freq` | 文本 | 频率，如日、周、月、季、年。 |
| `period` | 文本 | 统计周期。 |
| `value` | 双精度浮点 | 指标值。 |
| `unit` | 文本 | 单位。 |
| `source` | 文本 | 数据来源标识。 |
| `publish_date` | 文本 | 发布日期。 |
| `update_time` | 文本 | 更新时间。 |

### `fx_daily`

- 用途：汇率日线表，记录主要汇率对或指数的日频行情。
- 当前行数：`1565`
- 字段数：`9`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `pair_code` | 文本 | 汇率对或指数代码，如 USDCNY、DXY。 |
| `trade_date` | 文本 | 交易日期。 |
| `open` | 双精度浮点 | 开盘价。 |
| `high` | 双精度浮点 | 最高价。 |
| `low` | 双精度浮点 | 最低价。 |
| `close` | 双精度浮点 | 收盘价。 |
| `pct_chg` | 双精度浮点 | 涨跌幅。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `rate_curve_points`

- 用途：利率曲线关键点表，保存不同市场、不同期限的收益率或政策利率点位。
- 当前行数：`188`
- 字段数：`8`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `market` | 文本 | 市场标识，如 CN、US。 |
| `curve_code` | 文本 | 曲线代码，如国债收益率、政策利率、Shibor。 |
| `trade_date` | 文本 | 交易日期。 |
| `tenor` | 文本 | 期限，如 1M、3M、10Y。 |
| `value` | 双精度浮点 | 点位值。 |
| `unit` | 文本 | 单位，通常为百分比。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `spread_daily`

- 用途：利差日频表，如中美 10Y 利差等衍生指标。
- 当前行数：`47`
- 字段数：`6`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `spread_code` | 文本 | 利差代码，如 CN10Y_US10Y。 |
| `trade_date` | 文本 | 交易日期。 |
| `value` | 双精度浮点 | 利差值。 |
| `unit` | 文本 | 单位，通常为 bp。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `risk_scenarios`

- 用途：风险情景表，记录针对个股或资产做出的情景压力测试结果。
- 当前行数：`27425`
- 字段数：`12`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `ts_code` | 文本 | Tushare 股票代码。 |
| `scenario_date` | 文本 | 情景日期。 |
| `scenario_name` | 文本 | 情景名称。 |
| `horizon` | 文本 | 情景观察期限。 |
| `pnl_impact` | 双精度浮点 | 预估盈亏影响。 |
| `max_drawdown` | 双精度浮点 | 最大回撤估计。 |
| `var_95` | 双精度浮点 | 95% VaR。 |
| `cvar_95` | 双精度浮点 | 95% 条件 VaR。 |
| `assumptions_json` | 文本 | 情景假设 JSON。 |
| `source` | 文本 | 数据来源标识。 |
| `update_time` | 文本 | 更新时间。 |

### `chatroom_list_items`

- 用途：群聊基础信息表，记录群 ID、备注名、成员数，以及是否继续纳入监控等状态。
- 当前行数：`166`
- 字段数：`31`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `room_id` | 文本 | 群聊唯一 ID。 |
| `remark` | 文本 | 群备注名。 |
| `nick_name` | 文本 | 群昵称。 |
| `owner` | 文本 | 群主或拥有者标识。 |
| `user_count` | 长整数 | 群成员数量。 |
| `source_url` | 文本 | 群列表来源接口。 |
| `raw_csv_row` | 文本 | 原始 CSV 行内容。 |
| `first_seen_at` | 文本 | 首次被抓到的时间。 |
| `last_seen_at` | 文本 | 最近一次在群列表中出现的时间。 |
| `update_time` | 文本 | 更新时间。 |
| `skip_realtime_monitor` | 长整数 | 是否跳过实时监控，1 表示跳过。 |
| `skip_realtime_reason` | 文本 | 跳过实时监控的原因。 |
| `skip_realtime_marked_at` | 文本 | 被标记为跳过监控的时间。 |
| `last_message_date` | 文本 | 最近一条聊天记录日期。 |
| `last_chatlog_backfill_at` | 文本 | 最近一次聊天记录补抓时间。 |
| `last_chatlog_backfill_status` | 文本 | 最近一次聊天记录补抓状态。 |
| `last_30d_raw_message_count` | 长整数 | 最近 30 天原始消息条数。 |
| `last_30d_clean_message_count` | 长整数 | 最近 30 天清洗后消息条数。 |
| `last_30d_fetch_fail_count` | 长整数 | 最近 30 天拉取失败次数。 |
| `silent_candidate_runs` | 长整数 | 连续被判定为沉默群的次数。 |
| `silent_candidate_since` | 文本 | 开始被判定为沉默候选群的时间。 |
| `llm_chatroom_summary` | 文本 | LLM 生成的群聊简介。 |
| `llm_chatroom_tags_json` | 文本 | LLM 打的分类标签 JSON。 |
| `llm_chatroom_primary_category` | 文本 | LLM 判断的主分类，如投资交易。 |
| `llm_chatroom_activity_level` | 文本 | 群活跃度等级。 |
| `llm_chatroom_risk_level` | 文本 | 群风险等级。 |
| `llm_chatroom_confidence` | 长整数 | LLM 分类置信度。 |
| `llm_chatroom_model` | 文本 | 用于打标签的模型。 |
| `llm_chatroom_tagged_at` | 文本 | 最近一次打标签时间。 |
| `llm_chatroom_prompt_version` | 文本 | 群聊标签提示词版本。 |
| `llm_chatroom_raw_output` | 文本 | 群聊标签模型原始输出。 |

### `wechat_chatlog_clean_items`

- 用途：清洗后的群聊消息表，过滤图片/链接等无效内容后，保留可分析文本及引用结构。
- 当前行数：`320945`
- 字段数：`21`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `talker` | 文本 | 群聊名称。 |
| `query_date_start` | 文本 | 本次抓取请求的起始日期。 |
| `query_date_end` | 文本 | 本次抓取请求的结束日期。 |
| `message_date` | 文本 | 消息日期。 |
| `message_time` | 文本 | 消息时间。 |
| `sender_name` | 文本 | 发送人昵称。 |
| `sender_id` | 文本 | 发送人 ID。 |
| `message_type` | 文本 | 消息类型，如文本、引用、系统消息。 |
| `content` | 文本 | 原始消息内容。 |
| `content_clean` | 文本 | 清洗后的消息正文。 |
| `is_quote` | 长整数 | 是否为引用消息，1 表示是。 |
| `quote_sender_name` | 文本 | 被引用消息发送人。 |
| `quote_sender_id` | 文本 | 被引用消息发送人 ID。 |
| `quote_time_text` | 文本 | 被引用消息时间文本。 |
| `quote_content` | 文本 | 被引用的消息内容。 |
| `raw_block` | 文本 | 抓取回来的原始消息块。 |
| `source_url` | 文本 | 聊天记录来源接口。 |
| `fetched_at` | 文本 | 抓取时间。 |
| `update_time` | 文本 | 更新时间。 |
| `message_key` | 文本 | 消息唯一键，用于去重。 |

### `chatroom_investment_analysis`

- 用途：群聊投资倾向分析结果表，存储大模型对单个群的总结、投资标的提炼和最终看多/看空结论。
- 当前行数：`27`
- 字段数：`16`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `room_id` | 文本 | 群聊唯一 ID。 |
| `talker` | 文本 | 群聊展示名/查询名。 |
| `analysis_date` | 文本 | 本次分析对应的消息最新日期。 |
| `analysis_window_days` | 长整数 | 分析窗口天数。 |
| `message_count` | 长整数 | 本次分析使用的消息条数。 |
| `sender_count` | 长整数 | 参与发言人数。 |
| `latest_message_date` | 文本 | 本次分析覆盖到的最新消息日期。 |
| `room_summary` | 文本 | 群聊内容摘要。 |
| `targets_json` | 文本 | 提炼出的投资标的及其看多/看空 JSON。 |
| `final_bias` | 文本 | 群整体最终投资倾向，仅看多或看空。 |
| `model` | 文本 | 使用的大模型名称。 |
| `prompt_version` | 文本 | 提示词版本。 |
| `raw_output` | 文本 | 模型原始输出。 |
| `created_at` | 文本 | 创建时间。 |
| `update_time` | 文本 | 更新时间。 |

### `chatroom_stock_candidate_pool`

- 用途：由群聊投资倾向分析聚合出来的候选池表，汇总哪些股票/主题被更多群看多或看空。
- 当前行数：`176`
- 字段数：`15`

| 字段名 | 类型 | 中文解读 |
| --- | --- | --- |
| `id` | 长整数 | 主键 ID。 |
| `candidate_name` | 文本 | 候选标的名称，可能是股票、主题或资产。 |
| `candidate_type` | 文本 | 候选类型，如股票、主题、标的。 |
| `bullish_room_count` | 长整数 | 看多该标的的群数量。 |
| `bearish_room_count` | 长整数 | 看空该标的的群数量。 |
| `net_score` | 长整数 | 净分值，通常为看多群数减看空群数。 |
| `dominant_bias` | 文本 | 主导方向，看多或看空。 |
| `mention_count` | 长整数 | 总提及次数。 |
| `room_count` | 长整数 | 涉及该标的的群数量。 |
| `latest_analysis_date` | 文本 | 最近一次相关分析日期。 |
| `sample_reasons_json` | 文本 | 样例理由 JSON。 |
| `source_room_ids_json` | 文本 | 来源群 ID 列表 JSON。 |
| `source_talkers_json` | 文本 | 来源群名称列表 JSON。 |
| `created_at` | 文本 | 创建时间。 |
| `update_time` | 文本 | 更新时间。 |

## 说明

- 本文档基于当前 PostgreSQL 主库实时导出，行数会随采集和归档变化。
- 大量 `*_json` 字段保存的是结构化 JSON 文本，适合前端展示和 LLM 上下文拼装。
- 日期字段目前以文本形式存储较多，常见格式为 `YYYYMMDD`、`YYYY-MM-DD` 或 ISO 时间字符串。
- 若后续新增表或字段，可重新运行导出脚本自动更新本文档。
