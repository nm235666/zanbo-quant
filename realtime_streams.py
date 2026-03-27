#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable

from db_compat import get_redis_client

NEWS_STREAM_KEY = "stream:news_events"
APP_STREAM_KEY = "stream:app_events"
WS_BROADCAST_CHANNEL = "channel:realtime_broadcast"
WS_LAST_STATUS_KEY = "realtime:last_status"
MAX_EVENT_ITEMS = 20


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_items(items: Iterable[dict], limit: int = MAX_EVENT_ITEMS) -> list[dict]:
    normalized: list[dict] = []
    for item in items:
        if len(normalized) >= max(limit, 1):
            break
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "source": str(item.get("source") or "").strip(),
                "title": str(item.get("title") or "").strip(),
                "link": str(item.get("link") or "").strip(),
                "guid": str(item.get("guid") or "").strip(),
                "summary": str(item.get("summary") or "").strip(),
                "author": str(item.get("author") or "").strip(),
                "pub_date": str(item.get("pub_date") or "").strip(),
                "scope": str(item.get("scope") or "").strip(),
            }
        )
    return normalized


def publish_news_batch(source: str, scope: str, items: Iterable[dict], producer: str = "") -> str:
    client = get_redis_client()
    if client is None:
        return ""

    normalized = _normalize_items(items)
    if not normalized:
        return ""

    payload = {
        "event": "news_batch",
        "source": source,
        "scope": scope,
        "producer": producer or "",
        "count": len(normalized),
        "created_at": now_utc_iso(),
        "items": normalized,
    }
    return client.xadd(
        NEWS_STREAM_KEY,
        {"event": "news_batch", "payload": json.dumps(payload, ensure_ascii=False)},
        maxlen=2000,
        approximate=True,
    )


def publish_ws_broadcast(message: dict) -> int:
    client = get_redis_client()
    if client is None:
        return 0
    payload = json.dumps(message, ensure_ascii=False, default=str)
    client.set(WS_LAST_STATUS_KEY, payload)
    return int(client.publish(WS_BROADCAST_CHANNEL, payload))


def publish_app_event(
    event: str,
    payload: dict,
    producer: str = "",
    stream_key: str = APP_STREAM_KEY,
) -> str:
    client = get_redis_client()
    if client is None:
        return ""
    body = {
        "event": str(event or "").strip() or "app_event",
        "producer": producer or "",
        "created_at": now_utc_iso(),
        "payload": payload if isinstance(payload, dict) else {},
    }
    return client.xadd(
        stream_key,
        {"event": body["event"], "payload": json.dumps(body, ensure_ascii=False, default=str)},
        maxlen=5000,
        approximate=True,
    )
