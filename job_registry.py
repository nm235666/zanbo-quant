#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PYTHON_BIN = sys.executable or "python3"


@dataclass(frozen=True)
class JobDefinition:
    job_key: str
    name: str
    category: str
    schedule_expr: str
    owner: str = "scheduler"
    description: str = ""
    commands: tuple[tuple[str, ...], ...] = field(default_factory=tuple)


def py_cmd(*parts: str) -> tuple[str, ...]:
    return (PYTHON_BIN, *parts)


DEFAULT_JOBS: tuple[JobDefinition, ...] = (
    JobDefinition(
        job_key="market_expectations_refresh",
        name="市场预期刷新",
        category="signals",
        schedule_expr="42 * * * *",
        description="拉取 Polymarket 市场预期数据并入库",
        commands=(
            py_cmd(str(ROOT_DIR / "fetch_market_expectations_polymarket.py"), "--limit", "150", "--min-volume", "1000"),
        ),
    ),
    JobDefinition(
        job_key="theme_hotspot_refresh",
        name="主题热点引擎刷新",
        category="signals",
        schedule_expr="32 * * * *",
        description="刷新 7d 与 1d 主题热点引擎结果",
        commands=(
            py_cmd(str(ROOT_DIR / "build_theme_hotspot_engine.py"), "--lookback-days", "7", "--min-strength", "6"),
            py_cmd(
                str(ROOT_DIR / "build_theme_hotspot_engine.py"),
                "--lookback-days",
                "1",
                "--target-table",
                "theme_hotspot_tracker_1d",
                "--snapshot-table",
                "theme_daily_snapshots",
                "--evidence-table",
                "theme_evidence_items",
                "--skip-snapshot",
                "--min-strength",
                "4",
            ),
        ),
    ),
    JobDefinition(
        job_key="signal_state_refresh",
        name="信号状态机刷新",
        category="signals",
        schedule_expr="38 * * * *",
        description="刷新主题/股票状态机及事件",
        commands=((PYTHON_BIN, str(ROOT_DIR / "build_signal_state_machine.py")),),
    ),
    JobDefinition(
        job_key="fx_daily_dual_source",
        name="汇率双源补齐",
        category="macro",
        schedule_expr="35 7 * * *",
        description="使用 AKShare 对关键 FX 品种做双源补齐",
        commands=(
            py_cmd(
                str(ROOT_DIR / "backfill_fx_daily_akshare.py"),
                "--pairs",
                "USDJPY,EURUSD,DXY,USDCNY",
                "--lookback-days",
                "365",
            ),
        ),
    ),
    JobDefinition(
        job_key="minline_akshare_patch",
        name="分钟线 AKShare 补洞",
        category="market_data",
        schedule_expr="5 8 * * *",
        description="使用 AKShare 对最近交易日分钟线补洞",
        commands=(
            py_cmd(str(ROOT_DIR / "backfill_stock_minline_akshare.py"), "--trade-date", "__TRADE_DATE_1__", "--skip-existing"),
            py_cmd(str(ROOT_DIR / "backfill_stock_minline_akshare.py"), "--trade-date", "__TRADE_DATE_2__", "--skip-existing"),
        ),
    ),
    JobDefinition(
        job_key="research_reports_refresh",
        name="标准投研报告刷新",
        category="reports",
        schedule_expr="46 * * * *",
        description="自动生成市场/主题/高分股票标准报告",
        commands=((PYTHON_BIN, str(ROOT_DIR / "generate_standard_research_report.py"), "--report-type", "market", "--subject-key", "market_overview", "--report-date", "__CN_DATE__", "--model", "auto_market_snapshot_v1"),),
    ),
    JobDefinition(
        job_key="chatroom_tagging_safe",
        name="群聊低风险标签刷新",
        category="chatrooms",
        schedule_expr="12 0 */3 * *",
        description="只更新监控群，并通过历史多数票稳定标签",
        commands=(
            py_cmd(
                str(ROOT_DIR / "llm_tag_chatrooms.py"),
                "--model",
                "GPT-5.4",
                "--days",
                "30",
                "--limit",
                "20",
                "--monitored-only",
                "--retag-days",
                "3",
                "--min-confidence",
                "78",
                "--history-window",
                "7",
                "--majority-threshold",
                "0.62",
                "--min-majority-count",
                "3",
                "--retry",
                "2",
                "--sleep",
                "0.3",
            ),
        ),
    ),
)


def get_default_jobs() -> list[JobDefinition]:
    return list(DEFAULT_JOBS)

