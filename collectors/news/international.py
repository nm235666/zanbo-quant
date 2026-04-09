from __future__ import annotations

from .common import run_python_commands

NEWS_LLM_MODEL_CHAIN = "deepseek-chat|zhipu-news"


def run_international_news_pipeline() -> dict:
    commands = [
        # 为了降低端到端延迟，国际资讯主链每轮改为小批快跑，
        # 依赖高频调度持续推进，而不是单轮大批处理。
        {"script": "fetch_news_rss.py", "args": ["--limit", "10", "--timeout", "30"]},
        {"script": "fetch_news_marketscreener.py", "args": ["--limit", "12", "--timeout", "30"]},
        {"script": "fetch_news_marketscreener_live.py", "args": ["--limit", "12", "--timeout", "30"]},
        {"script": "llm_score_news.py", "args": ["--model", NEWS_LLM_MODEL_CHAIN, "--limit", "8", "--retry", "0", "--sleep", "0.05"]},
        {
            "script": "llm_score_sentiment.py",
            "args": ["--target", "news", "--model", NEWS_LLM_MODEL_CHAIN, "--limit", "8", "--retry", "0", "--sleep", "0.05"],
        },
        {"script": "map_news_items_to_stocks.py", "args": ["--limit", "80", "--days", "3"]},
    ]
    return run_python_commands(commands)
