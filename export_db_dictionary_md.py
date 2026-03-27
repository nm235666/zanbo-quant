#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import db_compat as sqlite3


TABLE_DESCRIPTIONS = {
    "capital_flow_market": "市场级资金流数据，主要记录北向/南向等整体资金净流入情况。",
    "capital_flow_stock": "个股级资金流数据，用于观察单只股票主力/大单/中单/小单资金流向。",
    "chatroom_investment_analysis": "群聊投资倾向分析结果表，存储大模型对单个群的总结、投资标的提炼和最终看多/看空结论。",
    "chatroom_list_items": "群聊基础信息表，记录群 ID、备注名、成员数，以及是否继续纳入监控等状态。",
    "chatroom_stock_candidate_pool": "由群聊投资倾向分析聚合出来的候选池表，汇总哪些股票/主题被更多群看多或看空。",
    "company_governance": "研究用治理画像表，把股东结构、董事高管结构、增减持、质押等治理数据拼成公司治理快照。",
    "fx_daily": "汇率日线表，记录主要汇率对或指数的日频行情。",
    "macro_series": "宏观指标时间序列表，存储 CPI、PPI、社融、PMI 等指标的历史序列。",
    "news_daily_summaries": "新闻日报总结表，保存对当日重要新闻的 LLM 总结 Markdown。",
    "news_feed_items": "国际/国内财经快讯主表，保存抓取到的新闻原文信息及 LLM 评分结果。",
    "news_feed_items_archive": "新闻归档表，保存从主新闻表归档出去的历史新闻。",
    "rate_curve_points": "利率曲线关键点表，保存不同市场、不同期限的收益率或政策利率点位。",
    "risk_scenarios": "风险情景表，记录针对个股或资产做出的情景压力测试结果。",
    "spread_daily": "利差日频表，如中美 10Y 利差等衍生指标。",
    "stock_codes": "股票基础信息主表，是所有股票相关数据的主索引表。",
    "stock_daily_prices": "股票日线行情表，保存历史日线 OHLCV 数据。",
    "stock_events": "股票事件表，保存分红、回购、解禁、业绩预告等事件。",
    "stock_financials": "股票财务核心指标表，按报告期保存营收、利润、ROE、现金流等数据。",
    "stock_minline": "股票分钟线表，保存分时/分钟级价格与成交量数据。",
    "stock_news_items": "个股相关新闻表，保存与某只股票关联的新闻、评分和摘要。",
    "stock_scores_daily": "股票综合评分日快照表，包含总分、分项得分和行业内相对评分。",
    "stock_valuation_daily": "股票估值日频表，保存 PE/PB/PS/股息率/市值等估值快照。",
    "wechat_chatlog_clean_items": "清洗后的群聊消息表，过滤图片/链接等无效内容后，保留可分析文本及引用结构。",
}


COLUMN_DESCRIPTIONS = {
    "capital_flow_market": {
        "trade_date": "交易日期，格式通常为 YYYYMMDD。",
        "flow_type": "资金流类型，例如北向、南向。",
        "net_inflow": "净流入金额。",
        "buy_amount": "买入总金额。",
        "sell_amount": "卖出总金额。",
        "unit": "金额单位。",
        "source": "数据来源标识。",
        "update_time": "数据更新时间。",
    },
    "capital_flow_stock": {
        "ts_code": "Tushare 股票代码。",
        "trade_date": "交易日期。",
        "net_inflow": "个股总净流入金额。",
        "main_inflow": "主力资金净流入金额。",
        "super_large_inflow": "超大单净流入金额。",
        "large_inflow": "大单净流入金额。",
        "medium_inflow": "中单净流入金额。",
        "small_inflow": "小单净流入金额。",
        "source": "数据来源标识。",
        "update_time": "数据更新时间。",
    },
    "chatroom_investment_analysis": {
        "id": "主键 ID。",
        "room_id": "群聊唯一 ID。",
        "talker": "群聊展示名/查询名。",
        "analysis_date": "本次分析对应的消息最新日期。",
        "analysis_window_days": "分析窗口天数。",
        "message_count": "本次分析使用的消息条数。",
        "sender_count": "参与发言人数。",
        "latest_message_date": "本次分析覆盖到的最新消息日期。",
        "room_summary": "群聊内容摘要。",
        "targets_json": "提炼出的投资标的及其看多/看空 JSON。",
        "final_bias": "群整体最终投资倾向，仅看多或看空。",
        "model": "使用的大模型名称。",
        "prompt_version": "提示词版本。",
        "raw_output": "模型原始输出。",
        "created_at": "创建时间。",
        "update_time": "更新时间。",
    },
    "chatroom_list_items": {
        "room_id": "群聊唯一 ID。",
        "remark": "群备注名。",
        "nick_name": "群昵称。",
        "owner": "群主或拥有者标识。",
        "user_count": "群成员数量。",
        "source_url": "群列表来源接口。",
        "raw_csv_row": "原始 CSV 行内容。",
        "first_seen_at": "首次被抓到的时间。",
        "last_seen_at": "最近一次在群列表中出现的时间。",
        "update_time": "更新时间。",
        "skip_realtime_monitor": "是否跳过实时监控，1 表示跳过。",
        "skip_realtime_reason": "跳过实时监控的原因。",
        "skip_realtime_marked_at": "被标记为跳过监控的时间。",
        "last_message_date": "最近一条聊天记录日期。",
        "last_chatlog_backfill_at": "最近一次聊天记录补抓时间。",
        "last_chatlog_backfill_status": "最近一次聊天记录补抓状态。",
        "last_30d_raw_message_count": "最近 30 天原始消息条数。",
        "last_30d_clean_message_count": "最近 30 天清洗后消息条数。",
        "last_30d_fetch_fail_count": "最近 30 天拉取失败次数。",
        "silent_candidate_runs": "连续被判定为沉默群的次数。",
        "silent_candidate_since": "开始被判定为沉默候选群的时间。",
        "llm_chatroom_summary": "LLM 生成的群聊简介。",
        "llm_chatroom_tags_json": "LLM 打的分类标签 JSON。",
        "llm_chatroom_primary_category": "LLM 判断的主分类，如投资交易。",
        "llm_chatroom_activity_level": "群活跃度等级。",
        "llm_chatroom_risk_level": "群风险等级。",
        "llm_chatroom_confidence": "LLM 分类置信度。",
        "llm_chatroom_model": "用于打标签的模型。",
        "llm_chatroom_tagged_at": "最近一次打标签时间。",
        "llm_chatroom_prompt_version": "群聊标签提示词版本。",
        "llm_chatroom_raw_output": "群聊标签模型原始输出。",
    },
    "chatroom_stock_candidate_pool": {
        "id": "主键 ID。",
        "candidate_name": "候选标的名称，可能是股票、主题或资产。",
        "candidate_type": "候选类型，如股票、主题、标的。",
        "bullish_room_count": "看多该标的的群数量。",
        "bearish_room_count": "看空该标的的群数量。",
        "net_score": "净分值，通常为看多群数减看空群数。",
        "dominant_bias": "主导方向，看多或看空。",
        "mention_count": "总提及次数。",
        "room_count": "涉及该标的的群数量。",
        "latest_analysis_date": "最近一次相关分析日期。",
        "sample_reasons_json": "样例理由 JSON。",
        "source_room_ids_json": "来源群 ID 列表 JSON。",
        "source_talkers_json": "来源群名称列表 JSON。",
        "created_at": "创建时间。",
        "update_time": "更新时间。",
    },
    "company_governance": {
        "ts_code": "Tushare 股票代码。",
        "asof_date": "治理画像对应日期。",
        "holder_structure_json": "股东结构画像 JSON，包括前十大股东、股东户数、质押等。",
        "board_structure_json": "董事会/高管结构画像 JSON。",
        "mgmt_change_json": "高管或重要股东近期增减持等变化 JSON。",
        "incentive_plan_json": "股权激励计划或占位信息 JSON。",
        "governance_score": "治理综合评分。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "fx_daily": {
        "pair_code": "汇率对或指数代码，如 USDCNY、DXY。",
        "trade_date": "交易日期。",
        "open": "开盘价。",
        "high": "最高价。",
        "low": "最低价。",
        "close": "收盘价。",
        "pct_chg": "涨跌幅。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "macro_series": {
        "indicator_code": "指标代码。",
        "indicator_name": "指标中文/展示名称。",
        "freq": "频率，如日、周、月、季、年。",
        "period": "统计周期。",
        "value": "指标值。",
        "unit": "单位。",
        "source": "数据来源标识。",
        "publish_date": "发布日期。",
        "update_time": "更新时间。",
    },
    "news_daily_summaries": {
        "id": "主键 ID。",
        "summary_date": "日报日期。",
        "filter_importance": "汇总时采用的重要度筛选条件。",
        "source_filter": "汇总时采用的数据源筛选条件。",
        "news_count": "参与总结的新闻条数。",
        "model": "使用的总结模型。",
        "prompt_version": "提示词版本。",
        "summary_markdown": "新闻日报总结 Markdown 内容。",
        "created_at": "创建时间。",
    },
    "news_feed_items": {
        "id": "主键 ID。",
        "source": "新闻来源。",
        "title": "新闻标题。",
        "link": "新闻链接。",
        "guid": "源站唯一标识。",
        "summary": "原始摘要。",
        "category": "新闻分类。",
        "author": "作者。",
        "pub_date": "发布时间。",
        "fetched_at": "抓取时间。",
        "content_hash": "内容哈希，用于去重。",
        "llm_system_score": "LLM 评出的系统重要性评分。",
        "llm_finance_impact_score": "LLM 评出的财经影响评分。",
        "llm_finance_importance": "LLM 评出的财经重要程度等级。",
        "llm_impacts_json": "影响方向、资产、板块等结构化 JSON。",
        "llm_model": "评分所用模型。",
        "llm_scored_at": "评分时间。",
        "llm_prompt_version": "新闻评分提示词版本。",
        "llm_raw_output": "模型原始输出。",
    },
    "news_feed_items_archive": {
        "id": "原新闻主键 ID。",
        "source": "新闻来源。",
        "title": "新闻标题。",
        "link": "新闻链接。",
        "guid": "源站唯一标识。",
        "summary": "原始摘要。",
        "category": "新闻分类。",
        "author": "作者。",
        "pub_date": "发布时间。",
        "fetched_at": "抓取时间。",
        "content_hash": "内容哈希。",
        "llm_system_score": "系统重要性评分。",
        "llm_finance_impact_score": "财经影响评分。",
        "llm_finance_importance": "财经重要程度。",
        "llm_impacts_json": "结构化影响 JSON。",
        "llm_model": "评分模型。",
        "llm_scored_at": "评分时间。",
        "llm_prompt_version": "提示词版本。",
        "llm_raw_output": "模型原始输出。",
        "archived_at": "归档时间。",
    },
    "rate_curve_points": {
        "market": "市场标识，如 CN、US。",
        "curve_code": "曲线代码，如国债收益率、政策利率、Shibor。",
        "trade_date": "交易日期。",
        "tenor": "期限，如 1M、3M、10Y。",
        "value": "点位值。",
        "unit": "单位，通常为百分比。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "risk_scenarios": {
        "id": "主键 ID。",
        "ts_code": "Tushare 股票代码。",
        "scenario_date": "情景日期。",
        "scenario_name": "情景名称。",
        "horizon": "情景观察期限。",
        "pnl_impact": "预估盈亏影响。",
        "max_drawdown": "最大回撤估计。",
        "var_95": "95% VaR。",
        "cvar_95": "95% 条件 VaR。",
        "assumptions_json": "情景假设 JSON。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "spread_daily": {
        "spread_code": "利差代码，如 CN10Y_US10Y。",
        "trade_date": "交易日期。",
        "value": "利差值。",
        "unit": "单位，通常为 bp。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "stock_codes": {
        "ts_code": "Tushare 股票代码，主键。",
        "symbol": "纯数字股票代码。",
        "name": "股票简称。",
        "area": "所属地区。",
        "industry": "所属行业。",
        "market": "所属市场/板块。",
        "list_date": "上市日期。",
        "delist_date": "退市日期。",
        "list_status": "上市状态，L=上市，D=退市，P=暂停上市。",
    },
    "stock_daily_prices": {
        "ts_code": "Tushare 股票代码。",
        "trade_date": "交易日期。",
        "open": "开盘价。",
        "high": "最高价。",
        "low": "最低价。",
        "close": "收盘价。",
        "pre_close": "前收盘价。",
        "change": "涨跌额。",
        "pct_chg": "涨跌幅。",
        "vol": "成交量。",
        "amount": "成交额。",
    },
    "stock_events": {
        "id": "主键 ID。",
        "ts_code": "Tushare 股票代码。",
        "event_type": "事件类型，如分红、回购、解禁、业绩预告。",
        "event_date": "事件生效或对应日期。",
        "ann_date": "公告日期。",
        "title": "事件标题。",
        "detail_json": "事件详细结构化 JSON。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
        "event_key": "事件唯一键，用于幂等去重。",
    },
    "stock_financials": {
        "ts_code": "Tushare 股票代码。",
        "report_period": "报告期末日期。",
        "report_type": "报告类型，如年报、一季报、半年报、三季报。",
        "ann_date": "公告日期。",
        "revenue": "营业收入。",
        "op_profit": "营业利润。",
        "net_profit": "归母净利润。",
        "net_profit_excl_nr": "扣非净利润。",
        "roe": "净资产收益率。",
        "gross_margin": "毛利率。",
        "debt_to_assets": "资产负债率。",
        "operating_cf": "经营现金流。",
        "free_cf": "自由现金流。",
        "eps": "每股收益。",
        "bps": "每股净资产。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "stock_minline": {
        "ts_code": "Tushare 股票代码。",
        "trade_date": "交易日。",
        "minute_time": "分钟时间点。",
        "price": "该分钟成交价/最新价。",
        "avg_price": "均价。",
        "volume": "该分钟成交量。",
        "total_volume": "截至该分钟的累计成交量。",
        "source": "数据来源标识。",
    },
    "stock_news_items": {
        "id": "主键 ID。",
        "ts_code": "关联股票代码。",
        "company_name": "公司名称。",
        "source": "新闻来源。",
        "news_code": "新闻源内部编号。",
        "title": "新闻标题。",
        "summary": "新闻摘要。",
        "link": "原文链接。",
        "pub_time": "发布时间。",
        "comment_num": "评论数。",
        "relation_stock_tags_json": "关联股票标签 JSON。",
        "content_hash": "内容哈希，用于去重。",
        "fetched_at": "抓取时间。",
        "update_time": "更新时间。",
        "llm_system_score": "系统重要性评分。",
        "llm_finance_impact_score": "财经影响评分。",
        "llm_finance_importance": "财经重要程度。",
        "llm_impacts_json": "结构化影响 JSON。",
        "llm_summary": "个股新闻 LLM 摘要。",
        "llm_model": "评分/摘要模型。",
        "llm_scored_at": "评分时间。",
        "llm_prompt_version": "提示词版本。",
        "llm_raw_output": "模型原始输出。",
    },
    "stock_scores_daily": {
        "score_date": "评分日期。",
        "ts_code": "股票代码。",
        "name": "股票简称。",
        "symbol": "数字代码。",
        "market": "市场。",
        "area": "地区。",
        "industry": "行业。",
        "score_grade": "综合评分等级。",
        "total_score": "综合总分。",
        "trend_score": "趋势分。",
        "financial_score": "财务分。",
        "valuation_score": "估值分。",
        "capital_flow_score": "资金流分。",
        "event_score": "事件分。",
        "news_score": "新闻分。",
        "risk_score": "风险分。",
        "latest_trade_date": "使用到的最新行情日期。",
        "latest_report_period": "使用到的最新财报期。",
        "latest_valuation_date": "使用到的最新估值日期。",
        "latest_flow_date": "使用到的最新资金流日期。",
        "latest_event_date": "使用到的最新事件日期。",
        "latest_news_time": "使用到的最新新闻时间。",
        "latest_risk_date": "使用到的最新风险日期。",
        "score_payload_json": "评分细项明细 JSON。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
        "industry_score_grade": "行业内相对评分等级。",
        "industry_total_score": "行业内相对综合总分。",
        "industry_trend_score": "行业内相对趋势分。",
        "industry_financial_score": "行业内相对财务分。",
        "industry_valuation_score": "行业内相对估值分。",
        "industry_capital_flow_score": "行业内相对资金流分。",
        "industry_event_score": "行业内相对事件分。",
        "industry_news_score": "行业内相对新闻分。",
        "industry_risk_score": "行业内相对风险分。",
        "industry_rank": "行业内排名。",
        "industry_count": "行业样本数。",
    },
    "stock_valuation_daily": {
        "ts_code": "股票代码。",
        "trade_date": "交易日期。",
        "pe": "市盈率。",
        "pe_ttm": "滚动市盈率。",
        "pb": "市净率。",
        "ps": "市销率。",
        "ps_ttm": "滚动市销率。",
        "dv_ratio": "股息率。",
        "dv_ttm": "滚动股息率。",
        "total_mv": "总市值。",
        "circ_mv": "流通市值。",
        "source": "数据来源标识。",
        "update_time": "更新时间。",
    },
    "wechat_chatlog_clean_items": {
        "id": "主键 ID。",
        "talker": "群聊名称。",
        "query_date_start": "本次抓取请求的起始日期。",
        "query_date_end": "本次抓取请求的结束日期。",
        "message_date": "消息日期。",
        "message_time": "消息时间。",
        "sender_name": "发送人昵称。",
        "sender_id": "发送人 ID。",
        "message_type": "消息类型，如文本、引用、系统消息。",
        "content": "原始消息内容。",
        "content_clean": "清洗后的消息正文。",
        "is_quote": "是否为引用消息，1 表示是。",
        "quote_sender_name": "被引用消息发送人。",
        "quote_sender_id": "被引用消息发送人 ID。",
        "quote_time_text": "被引用消息时间文本。",
        "quote_content": "被引用的消息内容。",
        "raw_block": "抓取回来的原始消息块。",
        "source_url": "聊天记录来源接口。",
        "fetched_at": "抓取时间。",
        "update_time": "更新时间。",
        "message_key": "消息唯一键，用于去重。",
    },
}


TYPE_CN = {
    "text": "文本",
    "double precision": "双精度浮点",
    "bigint": "长整数",
    "integer": "整数",
    "numeric": "数值",
    "real": "浮点",
    "boolean": "布尔",
}


TABLE_ORDER = [
    "stock_codes",
    "stock_daily_prices",
    "stock_minline",
    "stock_valuation_daily",
    "stock_financials",
    "stock_events",
    "company_governance",
    "capital_flow_stock",
    "capital_flow_market",
    "stock_scores_daily",
    "stock_news_items",
    "news_feed_items",
    "news_feed_items_archive",
    "news_daily_summaries",
    "macro_series",
    "fx_daily",
    "rate_curve_points",
    "spread_daily",
    "risk_scenarios",
    "chatroom_list_items",
    "wechat_chatlog_clean_items",
    "chatroom_investment_analysis",
    "chatroom_stock_candidate_pool",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导出 PostgreSQL 主库数据字典 Markdown")
    parser.add_argument(
        "--output",
        default=str(Path("docs") / "database_dictionary.md"),
        help="输出 Markdown 文件路径",
    )
    return parser.parse_args()


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def fetch_schema(conn: sqlite3.Connection) -> dict[str, list[dict[str, str]]]:
    rows = conn.execute(
        """
        SELECT table_name, column_name, data_type, ordinal_position
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position
        """
    ).fetchall()
    schema: dict[str, list[dict[str, str]]] = defaultdict(list)
    for table_name, column_name, data_type, ordinal_position in rows:
        schema[str(table_name)].append(
            {
                "column_name": str(column_name),
                "data_type": str(data_type),
                "ordinal_position": int(ordinal_position),
            }
        )
    return dict(schema)


def fetch_row_counts(conn: sqlite3.Connection, tables: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in tables:
        try:
            counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        except Exception:
            counts[table] = -1
    return counts


def cn_type(value: str) -> str:
    return TYPE_CN.get(value, value)


def table_category(table_name: str) -> str:
    if table_name.startswith("stock_") or table_name == "stock_codes" or table_name == "company_governance":
        return "股票与公司数据"
    if table_name.startswith("news_"):
        return "新闻与 LLM 新闻分析"
    if table_name in {"macro_series", "fx_daily", "rate_curve_points", "spread_daily", "capital_flow_market", "capital_flow_stock", "risk_scenarios"}:
        return "宏观、资金流与风险"
    if table_name.startswith("chatroom_") or table_name.startswith("wechat_"):
        return "群聊与社群分析"
    return "其他"


def render_markdown(schema: dict[str, list[dict[str, str]]], counts: dict[str, int]) -> str:
    tables = sorted(schema.keys(), key=lambda x: (TABLE_ORDER.index(x) if x in TABLE_ORDER else 999, x))
    lines: list[str] = []
    lines.append("# 数据库数据字典")
    lines.append("")
    lines.append(f"- 生成时间：`{now_utc()}`")
    lines.append("- 数据库：`PostgreSQL 主库`")
    lines.append(f"- 表数量：`{len(tables)}`")
    lines.append("")
    lines.append("## 总览")
    lines.append("")
    lines.append("| 表名 | 中文用途 | 当前行数 | 归类 |")
    lines.append("| --- | --- | ---: | --- |")
    for table in tables:
        desc = TABLE_DESCRIPTIONS.get(table, "待补充说明")
        row_count = counts.get(table, -1)
        lines.append(f"| `{table}` | {desc} | {row_count if row_count >= 0 else '未知'} | {table_category(table)} |")
    lines.append("")
    lines.append("## 各表详解")
    lines.append("")
    for table in tables:
        lines.append(f"### `{table}`")
        lines.append("")
        lines.append(f"- 用途：{TABLE_DESCRIPTIONS.get(table, '待补充说明')}")
        row_count = counts.get(table, -1)
        lines.append(f"- 当前行数：`{row_count if row_count >= 0 else '未知'}`")
        lines.append(f"- 字段数：`{len(schema[table])}`")
        lines.append("")
        lines.append("| 字段名 | 类型 | 中文解读 |")
        lines.append("| --- | --- | --- |")
        desc_map = COLUMN_DESCRIPTIONS.get(table, {})
        for col in schema[table]:
            column_name = col["column_name"]
            lines.append(
                f"| `{column_name}` | {cn_type(col['data_type'])} | {desc_map.get(column_name, '待补充说明')} |"
            )
        lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append("- 本文档基于当前 PostgreSQL 主库实时导出，行数会随采集和归档变化。")
    lines.append("- 大量 `*_json` 字段保存的是结构化 JSON 文本，适合前端展示和 LLM 上下文拼装。")
    lines.append("- 日期字段目前以文本形式存储较多，常见格式为 `YYYYMMDD`、`YYYY-MM-DD` 或 ISO 时间字符串。")
    lines.append("- 若后续新增表或字段，可重新运行导出脚本自动更新本文档。")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect()
    try:
        schema = fetch_schema(conn)
        counts = fetch_row_counts(conn, list(schema.keys()))
    finally:
        conn.close()

    markdown = render_markdown(schema, counts)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
