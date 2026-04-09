from __future__ import annotations

from .common import run_python_commands, run_python_script

NEWS_LLM_MODEL_CHAIN = "deepseek-chat|zhipu-news"


def run_news_stock_map_refresh(*, limit: int = 300, days: int = 7) -> dict:
    return run_python_script(
        "map_news_items_to_stocks.py",
        "--limit",
        str(limit),
        "--days",
        str(days),
        timeout_s=900,
        meta={"limit": limit, "days": days, "kind": "stock_map_refresh"},
    )


def run_news_sentiment_refresh(
    *,
    target: str = "news",
    model: str = NEWS_LLM_MODEL_CHAIN,
    limit: int = 20,
    retry: int = 0,
    sleep: float = 0.05,
) -> dict:
    return run_python_script(
        "llm_score_sentiment.py",
        "--target",
        target,
        "--model",
        model,
        "--limit",
        str(limit),
        "--retry",
        str(retry),
        "--sleep",
        str(sleep),
        timeout_s=300,
        meta={
            "target": target,
            "model": model,
            "limit": limit,
            "retry": retry,
            "sleep": sleep,
            "kind": "sentiment_refresh",
        },
    )


def run_cn_news_score_refresh(
    *,
    model: str = NEWS_LLM_MODEL_CHAIN,
    limit: int = 30,
    retry: int = 0,
    sleep: float = 0.05,
) -> dict:
    commands = [
        ("llm_score_news.py", "--model", model, "--source", "cn_sina_7x24", "--limit", str(limit), "--retry", str(retry), "--sleep", str(sleep)),
        ("llm_score_news.py", "--model", model, "--source", "cn_eastmoney_fastnews", "--limit", str(limit), "--retry", str(retry), "--sleep", str(sleep)),
    ]
    return run_python_commands(
        [{"script": script, "args": list(args)} for script, *args in commands]
    )


def run_intl_news_score_refresh(
    *,
    model: str = NEWS_LLM_MODEL_CHAIN,
    limit: int = 20,
    retry: int = 0,
    sleep: float = 0.05,
) -> dict:
    return run_python_script(
        "llm_score_news.py",
        "--model",
        model,
        "--limit",
        str(limit),
        "--retry",
        str(retry),
        "--sleep",
        str(sleep),
        timeout_s=300,
        meta={
            "model": model,
            "limit": limit,
            "retry": retry,
            "sleep": sleep,
            "kind": "intl_news_score_refresh",
        },
    )
