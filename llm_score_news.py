#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import db_compat as sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_API_KEY = "sk-374806b2f1744b1aa84a6b27758b0bb6"
GPT54_BASE_URL = "https://ai.td.ee/v1"
GPT54_API_KEY = "sk-1dbff3b041575534c99ee9f95711c2c9e9977c94db51ba679b9bcf04aa329343"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"
KIMI_API_KEY = "sk-trh5tumfscY5vi5VBSFInnwU3pr906bFJC4Nvf53xdMr2z72"

IMPORTANCE_LEVELS = {"极高", "高", "中", "低", "极低"}


def normalize_model_name(model: str) -> str:
    raw = (model or "").strip()
    m = raw.lower().replace("_", "-")
    if m in {"kimi2.5", "kimi-2.5", "kimi k2.5", "kimi-k2", "kimi2", "kimi"}:
        return "kimi-k2.5"
    return raw or "GPT-5.4"


def normalize_temperature_for_model(model: str, temperature: float) -> float:
    m = normalize_model_name(model).lower()
    if m.startswith("kimi-k2.5") or m.startswith("kimi-k2"):
        return 1.0
    return temperature


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用大模型对新闻进行结构化评分并入库")
    parser.add_argument(
        "--db-path",
        default=str(Path(__file__).resolve().parent / "stock_codes.db"),
        help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）",
    )
    parser.add_argument("--model", default="GPT-5.4", help="模型名，如 deepseek-chat / GPT-5.4")
    parser.add_argument("--base-url", default=DEEPSEEK_BASE_URL, help="LLM Base URL")
    parser.add_argument("--api-key", default=DEEPSEEK_API_KEY, help="LLM API Key")
    parser.add_argument("--temperature", type=float, default=0.1, help="采样温度")
    parser.add_argument("--limit", type=int, default=30, help="本次最多评分条数")
    parser.add_argument("--source", default="", help="仅评分指定来源，如 mw_topstories")
    parser.add_argument("--force", action="store_true", help="强制重评（默认只评未评分）")
    parser.add_argument("--retry", type=int, default=2, help="单条新闻失败重试次数")
    parser.add_argument("--sleep", type=float, default=0.3, help="每条间隔秒数")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_provider(model: str, base_url: str, api_key: str) -> tuple[str, str]:
    m = normalize_model_name(model).lower()
    if m.startswith("gpt-5.4"):
        return GPT54_BASE_URL, GPT54_API_KEY
    if m.startswith("kimi-k2.5") or m.startswith("kimi"):
        return KIMI_BASE_URL, KIMI_API_KEY
    return base_url, api_key


def ensure_columns(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(news_feed_items)").fetchall()}
    need = [
        ("llm_system_score", "INTEGER"),
        ("llm_finance_impact_score", "INTEGER"),
        ("llm_finance_importance", "TEXT"),
        ("llm_impacts_json", "TEXT"),
        ("llm_model", "TEXT"),
        ("llm_scored_at", "TEXT"),
        ("llm_prompt_version", "TEXT"),
        ("llm_raw_output", "TEXT"),
    ]
    for name, typ in need:
        if name not in cols:
            conn.execute(f"ALTER TABLE news_feed_items ADD COLUMN {name} {typ}")
    conn.commit()


def fetch_news_rows(conn: sqlite3.Connection, limit: int, source: str, force: bool) -> list[sqlite3.Row]:
    where = []
    params: list[object] = []
    if source.strip():
        where.append("source = ?")
        params.append(source.strip().lower())
    if not force:
        where.append("llm_system_score IS NULL OR llm_finance_impact_score IS NULL OR llm_finance_importance IS NULL")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
    SELECT id, source, title, link, summary, category, author, pub_date
    FROM news_feed_items
    {where_sql}
    ORDER BY pub_date DESC, id DESC
    LIMIT ?
    """
    params.append(max(limit, 1))
    return conn.execute(sql, params).fetchall()


def build_prompt(news: dict) -> str:
    # 输出 JSON，便于程序稳定解析；规则与用户要求一致
    return (
        "你是一个专业的财经新闻事件分析系统。请对输入新闻进行结构化评分。\n\n"
        "评分任务：\n"
        "1) 系统评分（0-100）\n"
        "2) 财经影响评分（0-100）\n"
        "3) 财经重要程度（极高/高/中/低/极低）\n\n"
        "评分标准：\n"
        "- 事件级别、权威性、时效性、稀缺性、波及范围、持续性\n"
        "- 风险偏好、宏观预期、盈利预期、资产定价、行业轮动、影响持续性\n"
        "- 若信息不足，仍需审慎打分，不能拒答\n\n"
        "财经重要程度分档规则：\n"
        "- 系统评分或财经影响评分 >= 90：极高\n"
        "- 任一评分 >= 75：高\n"
        "- 任一评分 >= 50：中\n"
        "- 任一评分 >= 20：低\n"
        "- 否则：极低\n\n"
        "还需要给出可影响项（仅识别，不解释逻辑）：\n"
        "- macro: 经济增长/通胀/利率/汇率/流动性/风险偏好\n"
        "- markets: A股/港股/美股/债券/商品/黄金/原油/外汇\n"
        "- sectors: 金融/地产/科技/半导体/AI/消费/医药/能源/有色/军工/汽车/新能源/基建/航运\n"
        "- direction 仅允许: 利多/利空/中性\n\n"
        "请只输出 JSON，不要输出任何额外文字，格式如下：\n"
        "{\n"
        '  "system_score": 0,\n'
        '  "finance_impact_score": 0,\n'
        '  "finance_importance": "中",\n'
        '  "impacts": {\n'
        '    "macro": [{"item":"风险偏好","direction":"利空"}],\n'
        '    "markets": [{"item":"美股","direction":"利空"}],\n'
        '    "sectors": [{"item":"科技","direction":"利空"}]\n'
        "  }\n"
        "}\n\n"
        f"输入新闻：\n{json.dumps(news, ensure_ascii=False)}"
    )


def call_llm(base_url: str, api_key: str, model: str, temperature: float, prompt: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "你是严谨、克制、结构化的财经新闻评分引擎。"},
            {"role": "user", "content": prompt},
        ],
    }
    body = json.dumps(payload).encode("utf-8")

    header_candidates = [
        {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        {"Content-Type": "application/json", "Authorization": api_key},
        {"Content-Type": "application/json", "api-key": api_key},
        {"Content-Type": "application/json", "x-api-key": api_key},
    ]

    last_error = None
    for headers in header_candidates:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
            obj = json.loads(text)
            return obj["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {e.code} {e.reason} | {detail}"
            if e.code not in (401, 403):
                break
        except Exception as e:  # pragma: no cover
            last_error = str(e)

    raise RuntimeError(f"调用LLM失败: {last_error}")


def to_score(v) -> int:
    try:
        n = int(round(float(v)))
    except Exception:
        n = 0
    return max(0, min(100, n))


def fallback_importance(system_score: int, impact_score: int) -> str:
    x = max(system_score, impact_score)
    if x >= 90:
        return "极高"
    if x >= 75:
        return "高"
    if x >= 50:
        return "中"
    if x >= 20:
        return "低"
    return "极低"


def parse_llm_output(raw: str) -> dict:
    txt = (raw or "").strip()
    # 优先 JSON
    try:
        obj = json.loads(txt)
        ss = to_score(obj.get("system_score"))
        fi = to_score(obj.get("finance_impact_score"))
        imp = str(obj.get("finance_importance", "")).strip()
        if imp not in IMPORTANCE_LEVELS:
            imp = fallback_importance(ss, fi)
        impacts = obj.get("impacts", {})
        if not isinstance(impacts, dict):
            impacts = {}
        return {
            "system_score": ss,
            "finance_impact_score": fi,
            "finance_importance": imp,
            "impacts_json": json.dumps(impacts, ensure_ascii=False),
        }
    except Exception:
        pass

    # 兼容“系统评分：xx”格式
    def find_num(pattern: str) -> int:
        m = re.search(pattern, txt, flags=re.IGNORECASE)
        if not m:
            return 0
        return to_score(m.group(1))

    ss = find_num(r"系统评分[：:\s]*([0-9]+(?:\.[0-9]+)?)")
    fi = find_num(r"财经影响评分[：:\s]*([0-9]+(?:\.[0-9]+)?)")
    m_imp = re.search(r"财经重要程度[：:\s]*(极高|高|中|低|极低)", txt)
    imp = m_imp.group(1) if m_imp else fallback_importance(ss, fi)
    return {
        "system_score": ss,
        "finance_impact_score": fi,
        "finance_importance": imp,
        "impacts_json": json.dumps({}, ensure_ascii=False),
    }


def update_row(
    conn: sqlite3.Connection,
    row_id: int,
    parsed: dict,
    model: str,
    prompt_version: str,
    raw_output: str,
) -> None:
    conn.execute(
        """
        UPDATE news_feed_items
        SET
            llm_system_score = ?,
            llm_finance_impact_score = ?,
            llm_finance_importance = ?,
            llm_impacts_json = ?,
            llm_model = ?,
            llm_scored_at = ?,
            llm_prompt_version = ?,
            llm_raw_output = ?
        WHERE id = ?
        """,
        (
            parsed["system_score"],
            parsed["finance_impact_score"],
            parsed["finance_importance"],
            parsed["impacts_json"],
            model,
            now_utc_str(),
            prompt_version,
            raw_output,
            row_id,
        ),
    )


def main() -> int:
    args = parse_args()
    args.model = normalize_model_name(args.model)
    args.temperature = normalize_temperature_for_model(args.model, args.temperature)
    db_path = Path(args.db_path).resolve()
    if (not sqlite3.using_postgres()) and not db_path.exists():
        print(f"数据库不存在: {db_path}")
        return 1

    base_url, api_key = resolve_provider(args.model, args.base_url, args.api_key)
    prompt_version = "news_score_v1"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_columns(conn)
        rows = fetch_news_rows(conn, limit=args.limit, source=args.source, force=args.force)
        if not rows:
            print("没有待评分新闻。")
            return 0

        ok = 0
        fail = 0
        for i, r in enumerate(rows, start=1):
            news = {
                "id": r["id"],
                "source": r["source"],
                "title": r["title"] or "",
                "summary": r["summary"] or "",
                "category": r["category"] or "",
                "author": r["author"] or "",
                "pub_date": r["pub_date"] or "",
                "link": r["link"] or "",
            }
            print(f"[{i}/{len(rows)}] scoring id={r['id']} source={r['source']}")
            prompt = build_prompt(news)

            last_err = None
            for attempt in range(args.retry + 1):
                try:
                    raw = call_llm(
                        base_url=base_url,
                        api_key=api_key,
                        model=args.model,
                        temperature=args.temperature,
                        prompt=prompt,
                    )
                    parsed = parse_llm_output(raw)
                    update_row(
                        conn,
                        row_id=r["id"],
                        parsed=parsed,
                        model=args.model,
                        prompt_version=prompt_version,
                        raw_output=raw,
                    )
                    conn.commit()
                    ok += 1
                    print(
                        f"  -> 系统评分={parsed['system_score']}, 财经影响评分={parsed['finance_impact_score']}, 重要程度={parsed['finance_importance']}"
                    )
                    last_err = None
                    break
                except Exception as exc:
                    last_err = exc
                    if attempt < args.retry:
                        wait_s = 1.5 * (2**attempt)
                        print(f"  -> 重试 {attempt + 1}/{args.retry}: {exc}")
                        time.sleep(wait_s)
            if last_err is not None:
                fail += 1
                print(f"  -> 失败: {last_err}")
            time.sleep(max(args.sleep, 0.0))

        print(f"完成: success={ok}, failed={fail}, total={len(rows)}")
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
