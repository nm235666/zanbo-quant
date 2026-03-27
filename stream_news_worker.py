#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time

from realtime_streams import APP_STREAM_KEY, NEWS_STREAM_KEY, publish_ws_broadcast
from db_compat import get_redis_client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="消费新闻 Redis Stream，并广播给 WebSocket")
    parser.add_argument("--news-stream-key", default=NEWS_STREAM_KEY, help="新闻 Redis Stream key")
    parser.add_argument("--app-stream-key", default=APP_STREAM_KEY, help="业务 Redis Stream key")
    parser.add_argument("--start-id", default="$", help="首次消费起点，默认 $ 表示仅看新消息")
    parser.add_argument("--block-ms", type=int, default=15000, help="XREAD 阻塞毫秒数")
    parser.add_argument("--idle-sleep", type=float, default=1.0, help="Redis 不可用时的等待秒数")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    last_ids = {
        args.news_stream_key: args.start_id,
        args.app_stream_key: args.start_id,
    }
    print(
        f"stream worker 启动: news_stream={args.news_stream_key}, app_stream={args.app_stream_key}, start_id={args.start_id}"
    )

    while True:
        client = get_redis_client()
        if client is None:
            print("Redis 不可用，等待重试...")
            time.sleep(max(args.idle_sleep, 0.5))
            continue

        try:
            entries = client.xread(
                last_ids,
                block=max(args.block_ms, 1000),
                count=20,
            )
            if not entries:
                continue

            for stream_name, stream_entries in entries:
                for entry_id, fields in stream_entries:
                    last_ids[stream_name] = entry_id
                    raw = fields.get("payload") or "{}"
                    try:
                        payload = json.loads(raw)
                    except Exception:
                        payload = {"event": "stream_parse_error", "raw": raw}
                    is_news_stream = stream_name == args.news_stream_key
                    message = {
                        "channel": "news" if is_news_stream else "app",
                        "event": payload.get("event") or fields.get("event") or ("news_batch" if is_news_stream else "app_event"),
                        "entry_id": entry_id,
                        "payload": payload,
                    }
                    publish_ws_broadcast(message)
                    if is_news_stream:
                        count = payload.get("count") if isinstance(payload, dict) else "?"
                        source = payload.get("source") if isinstance(payload, dict) else ""
                        print(f"broadcast news entry={entry_id} source={source} count={count}")
                    else:
                        evt = payload.get("event") if isinstance(payload, dict) else "app_event"
                        print(f"broadcast app entry={entry_id} event={evt}")
        except KeyboardInterrupt:
            print("收到中断，退出")
            return 0
        except Exception as exc:
            print(f"stream worker 异常: {exc}")
            time.sleep(max(args.idle_sleep, 0.5))


if __name__ == "__main__":
    raise SystemExit(main())
