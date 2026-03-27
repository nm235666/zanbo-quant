#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import db_compat as sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_API_KEY = "sk-374806b2f1744b1aa84a6b27758b0bb6"
GPT54_BASE_URL = "https://ai.td.ee/v1"
GPT54_API_KEY = "sk-1dbff3b041575534c99ee9f95711c2c9e9977c94db51ba679b9bcf04aa329343"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"
KIMI_API_KEY = "sk-trh5tumfscY5vi5VBSFInnwU3pr906bFJC4Nvf53xdMr2z72"

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "stock_codes.db"
PROMPT_VERSION = "chatroom_tag_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用大模型为群聊总结并打分类标签")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="PostgreSQL 主库兼容参数（默认走 PostgreSQL；仅兼容保留旧 db-path 传参）")
    parser.add_argument("--model", default="GPT-5.4", help="模型名，如 GPT-5.4 / kimi-k2.5 / deepseek-chat")
    parser.add_argument("--base-url", default=DEEPSEEK_BASE_URL, help="LLM Base URL")
    parser.add_argument("--api-key", default=DEEPSEEK_API_KEY, help="LLM API Key")
    parser.add_argument("--temperature", type=float, default=0.2, help="采样温度")
    parser.add_argument("--days", type=int, default=30, help="取最近多少天聊天记录用于打标")
    parser.add_argument("--limit", type=int, default=20, help="本次最多处理多少个群")
    parser.add_argument("--only-room", default="", help="只处理指定群聊（remark/nick_name/room_id/talker）")
    parser.add_argument("--include-skipped", action="store_true", help="是否包含已停监控群")
    parser.add_argument("--force", action="store_true", help="强制重跑，默认只处理未打标或标签过旧的群")
    parser.add_argument("--max-messages", type=int, default=120, help="每个群最多送入模型的消息条数")
    parser.add_argument("--max-chars", type=int, default=12000, help="每个群送入模型的最大字符数")
    parser.add_argument("--sleep", type=float, default=0.3, help="每个群之间暂停秒数")
    parser.add_argument("--retry", type=int, default=2, help="单个群失败重试次数")
    parser.add_argument("--verbose", action="store_true", help="打印更多上下文")
    return parser.parse_args()


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_model_name(model: str) -> str:
    raw = (model or "").strip()
    m = raw.lower().replace("_", "-")
    if m in {"kimi2.5", "kimi-2.5", "kimi k2.5", "kimi-k2", "kimi2", "kimi"}:
        return "kimi-k2.5"
    return raw or "GPT-5.4"


def resolve_provider(model: str, base_url: str, api_key: str) -> tuple[str, str]:
    m = normalize_model_name(model).lower()
    if m.startswith("gpt-5.4"):
        return GPT54_BASE_URL, GPT54_API_KEY
    if m.startswith("kimi-k2.5") or m.startswith("kimi"):
        return KIMI_BASE_URL, KIMI_API_KEY
    return base_url, api_key


def normalize_temperature_for_model(model: str, temperature: float) -> float:
    m = normalize_model_name(model).lower()
    if m.startswith("kimi-k2.5") or m.startswith("kimi-k2"):
        return 1.0
    return temperature


def ensure_columns(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(chatroom_list_items)").fetchall()}
    need = [
        ("llm_chatroom_summary", "TEXT"),
        ("llm_chatroom_tags_json", "TEXT"),
        ("llm_chatroom_primary_category", "TEXT"),
        ("llm_chatroom_activity_level", "TEXT"),
        ("llm_chatroom_risk_level", "TEXT"),
        ("llm_chatroom_confidence", "INTEGER"),
        ("llm_chatroom_model", "TEXT"),
        ("llm_chatroom_tagged_at", "TEXT"),
        ("llm_chatroom_prompt_version", "TEXT"),
        ("llm_chatroom_raw_output", "TEXT"),
    ]
    for name, typ in need:
        if name not in cols:
            conn.execute(f"ALTER TABLE chatroom_list_items ADD COLUMN {name} {typ}")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_chatroom_list_items_llm_tagged_at ON chatroom_list_items(llm_chatroom_tagged_at)"
    )
    conn.commit()


def build_room_filter_sql(only_room: str, include_skipped: bool, force: bool) -> tuple[str, list[object]]:
    where = []
    params: list[object] = []
    if only_room.strip():
        value = only_room.strip()
        where.append("(c.remark = ? OR c.nick_name = ? OR c.room_id = ? OR l.talker = ?)")
        params.extend([value, value, value, value])
    if not include_skipped:
        where.append("COALESCE(c.skip_realtime_monitor, 0) = 0")
    if not force:
        where.append(
            "("
            "c.llm_chatroom_tagged_at IS NULL "
            "OR c.llm_chatroom_prompt_version IS NULL "
            "OR c.llm_chatroom_prompt_version <> ?"
            ")"
        )
        params.append(PROMPT_VERSION)
    return (" WHERE " + " AND ".join(where) if where else ""), params


def fetch_candidate_rooms(conn: sqlite3.Connection, args: argparse.Namespace) -> list[sqlite3.Row]:
    where_sql, params = build_room_filter_sql(args.only_room, args.include_skipped, args.force)
    sql = f"""
    SELECT
        c.room_id,
        c.remark,
        c.nick_name,
        c.user_count,
        c.last_message_date,
        COUNT(l.id) AS message_count,
        MAX(l.message_date) AS max_message_date
    FROM chatroom_list_items c
    JOIN wechat_chatlog_clean_items l
      ON l.talker = COALESCE(NULLIF(c.remark, ''), NULLIF(c.nick_name, ''), c.room_id)
    {where_sql}
    GROUP BY c.room_id, c.remark, c.nick_name, c.user_count, c.last_message_date
    ORDER BY MAX(l.message_date) DESC, COUNT(l.id) DESC
    LIMIT ?
    """
    return conn.execute(sql, [*params, max(args.limit, 1)]).fetchall()


def room_display_name(row: sqlite3.Row) -> str:
    return str(row["remark"] or row["nick_name"] or row["room_id"] or "").strip()


def fetch_recent_messages(
    conn: sqlite3.Connection,
    talker: str,
    days: int,
    max_messages: int,
) -> list[sqlite3.Row]:
    start_date = (datetime.now(timezone.utc).date() - timedelta(days=max(days - 1, 0))).isoformat()
    sql = """
    SELECT
        message_date,
        message_time,
        sender_name,
        message_type,
        content_clean,
        is_quote,
        quote_sender_name,
        quote_content
    FROM wechat_chatlog_clean_items
    WHERE talker = ?
      AND COALESCE(message_date, '') >= ?
    ORDER BY message_date DESC, message_time DESC, id DESC
    LIMIT ?
    """
    rows = conn.execute(sql, (talker, start_date, max_messages)).fetchall()
    return list(reversed(rows))


def build_message_digest(rows: list[sqlite3.Row], max_chars: int) -> str:
    parts: list[str] = []
    remaining = max_chars
    for row in rows:
        content = str(row["content_clean"] or "").strip()
        if not content:
            continue
        sender = str(row["sender_name"] or "未知发送人").strip()
        message_type = str(row["message_type"] or "text").strip()
        msg = f"[{row['message_date']} {row['message_time']}] {sender} ({message_type}): {content}"
        if int(row["is_quote"] or 0) == 1:
            quote_sender = str(row["quote_sender_name"] or "").strip()
            quote_content = str(row["quote_content"] or "").strip()
            if quote_sender or quote_content:
                msg += f" | 引用 {quote_sender}: {quote_content}"
        if len(msg) > remaining:
            if remaining > 50:
                parts.append(msg[:remaining])
            break
        parts.append(msg)
        remaining -= len(msg) + 1
        if remaining <= 0:
            break
    return "\n".join(parts)


def build_prompt(room: dict) -> str:
    return (
        "你是一个专业的信息分析助手，需要根据一个微信群最近的聊天记录，为该群做“分类标签”和“内容摘要”。\n"
        "请基于聊天内容本身判断，不要臆测。\n\n"
        "任务要求：\n"
        "1. 判断群聊主要主题与用途。\n"
        "2. 给出适合检索和筛选的分类标签。\n"
        "3. 判断群聊活跃度和风险等级。\n"
        "4. 输出一段简洁摘要，说明这个群大致在聊什么。\n\n"
        "标签输出要求：\n"
        "- primary_category: 只能从以下中选择一个：投资交易、财经资讯、技术交流、课程培训、电商团购、生活社交、行业社群、游戏娱乐、本地组织、其他\n"
        "- topic_tags: 3到8个中文短标签，例如 A股、短线交易、量化、逆向、安全、团购、海鲜、AI、课程、八卦\n"
        "- style_tags: 1到5个标签，例如 高活跃、低活跃、消息密集、问答型、观点输出、广告导向、资讯转发、实战讨论、闲聊\n"
        "- risk_level: 只能是 低 / 中 / 高\n"
        "- activity_level: 只能是 低 / 中 / 高\n"
        "- confidence: 0到100 的整数\n"
        "- summary: 80字以内中文总结\n\n"
        "只输出 JSON，不要输出任何多余文字，格式如下：\n"
        "{\n"
        '  "primary_category": "投资交易",\n'
        '  "topic_tags": ["A股", "短线交易", "龙虎榜"],\n'
        '  "style_tags": ["高活跃", "实战讨论", "观点输出"],\n'
        '  "risk_level": "中",\n'
        '  "activity_level": "高",\n'
        '  "confidence": 88,\n'
        '  "summary": "这是一个以A股短线和题材交易为主的高活跃讨论群。"\n'
        "}\n\n"
        f"输入数据：\n{json.dumps(room, ensure_ascii=False)}"
    )


def call_llm(base_url: str, api_key: str, model: str, temperature: float, prompt: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "你是严谨、克制、结构化的信息标签引擎。"},
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
            with urllib.request.urlopen(req, timeout=180) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
            obj = json.loads(text)
            return obj["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {e.code} {e.reason} | {detail}"
            if e.code not in (401, 403):
                break
        except Exception as e:
            last_error = str(e)
    raise RuntimeError(f"调用LLM失败: {last_error}")


def extract_json_text(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return "{}"
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.S)
    return match.group(0) if match else text


def clamp_confidence(value: object) -> int:
    try:
        n = int(round(float(value)))
    except Exception:
        n = 0
    return max(0, min(100, n))


def normalize_tag_list(value: object, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text and text not in result:
            result.append(text)
        if len(result) >= limit:
            break
    return result


def parse_llm_output(raw: str) -> dict:
    text = extract_json_text(raw)
    obj = json.loads(text)
    primary_category = str(obj.get("primary_category") or "其他").strip() or "其他"
    risk_level = str(obj.get("risk_level") or "中").strip() or "中"
    activity_level = str(obj.get("activity_level") or "中").strip() or "中"
    summary = str(obj.get("summary") or "").strip()[:200]
    topic_tags = normalize_tag_list(obj.get("topic_tags"), 8)
    style_tags = normalize_tag_list(obj.get("style_tags"), 5)
    merged_tags = []
    for tag in topic_tags + style_tags:
        if tag not in merged_tags:
            merged_tags.append(tag)
    return {
        "primary_category": primary_category,
        "topic_tags": topic_tags,
        "style_tags": style_tags,
        "tags_json": json.dumps(
            {
                "topic_tags": topic_tags,
                "style_tags": style_tags,
                "all_tags": merged_tags,
            },
            ensure_ascii=False,
        ),
        "risk_level": risk_level,
        "activity_level": activity_level,
        "confidence": clamp_confidence(obj.get("confidence")),
        "summary": summary,
    }


def update_room_tagging(
    conn: sqlite3.Connection,
    room_id: str,
    parsed: dict,
    model: str,
    raw_output: str,
) -> None:
    conn.execute(
        """
        UPDATE chatroom_list_items
        SET
            llm_chatroom_summary = ?,
            llm_chatroom_tags_json = ?,
            llm_chatroom_primary_category = ?,
            llm_chatroom_activity_level = ?,
            llm_chatroom_risk_level = ?,
            llm_chatroom_confidence = ?,
            llm_chatroom_model = ?,
            llm_chatroom_tagged_at = ?,
            llm_chatroom_prompt_version = ?,
            llm_chatroom_raw_output = ?
        WHERE room_id = ?
        """,
        (
            parsed["summary"],
            parsed["tags_json"],
            parsed["primary_category"],
            parsed["activity_level"],
            parsed["risk_level"],
            parsed["confidence"],
            model,
            now_utc_str(),
            PROMPT_VERSION,
            raw_output,
            room_id,
        ),
    )
    conn.commit()


def main() -> int:
    args = parse_args()
    model = normalize_model_name(args.model)
    base_url, api_key = resolve_provider(model, args.base_url, args.api_key)
    temperature = normalize_temperature_for_model(model, args.temperature)

    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row
    try:
        ensure_columns(conn)
        rooms = fetch_candidate_rooms(conn, args)
        if not rooms:
            print("没有需要处理的群聊。")
            return 0

        print(f"待处理群聊数: {len(rooms)} | 模型: {model}")
        for idx, room in enumerate(rooms, start=1):
            talker = room_display_name(room)
            room_id = str(room["room_id"] or "")
            recent_messages = fetch_recent_messages(conn, talker, args.days, args.max_messages)
            if not recent_messages:
                print(f"[{idx}/{len(rooms)}] {talker}: skip, 最近{args.days}天没有聊天记录")
                continue

            digest = build_message_digest(recent_messages, args.max_chars)
            payload = {
                "room_id": room_id,
                "talker": talker,
                "user_count": room["user_count"],
                "message_count_in_db_window": room["message_count"],
                "latest_message_date": room["max_message_date"],
                "recent_messages_sample": digest,
            }
            prompt = build_prompt(payload)

            if args.verbose:
                print(f"[{idx}/{len(rooms)}] {talker}: messages={len(recent_messages)} digest_chars={len(digest)}")
            else:
                print(f"[{idx}/{len(rooms)}] {talker}: 分析中...")

            last_error = None
            parsed = None
            raw_output = ""
            for _ in range(max(args.retry, 0) + 1):
                try:
                    raw_output = call_llm(base_url, api_key, model, temperature, prompt)
                    parsed = parse_llm_output(raw_output)
                    break
                except Exception as exc:
                    last_error = exc
                    time.sleep(1.0)
            if parsed is None:
                print(f"  失败: {last_error}")
                continue

            update_room_tagging(conn, room_id, parsed, model, raw_output)
            print(
                f"  完成 category={parsed['primary_category']} "
                f"activity={parsed['activity_level']} risk={parsed['risk_level']} "
                f"tags={','.join(json.loads(parsed['tags_json'])['all_tags'][:5])}"
            )
            if args.sleep > 0:
                time.sleep(args.sleep)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
