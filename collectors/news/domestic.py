from __future__ import annotations

from .common import run_python_commands

NEWS_LLM_MODEL_CHAIN = "deepseek-chat|zhipu-news"


def run_cn_news_pipeline() -> dict:
    commands = [
        {"script": "fetch_cn_news_sina_7x24.py", "args": ["--limit", "60", "--timeout", "30"]},
        {"script": "llm_score_news.py", "args": ["--model", NEWS_LLM_MODEL_CHAIN, "--source", "cn_sina_7x24", "--limit", "20", "--retry", "0", "--sleep", "0.05"]},
        {"script": "llm_score_news.py", "args": ["--model", NEWS_LLM_MODEL_CHAIN, "--source", "cn_eastmoney_fastnews", "--limit", "20", "--retry", "0", "--sleep", "0.05"]},
        {"script": "llm_score_sentiment.py", "args": ["--target", "news", "--model", NEWS_LLM_MODEL_CHAIN, "--limit", "20", "--retry", "0", "--sleep", "0.05"]},
    ]
    return run_python_commands(commands)
