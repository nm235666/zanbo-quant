#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import socket
import struct
import threading
import time
from datetime import datetime, timezone

from db_compat import get_redis_client
from realtime_streams import WS_BROADCAST_CHANNEL, WS_LAST_STATUS_KEY

WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ClientRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: set[socket.socket] = set()

    def add(self, conn: socket.socket) -> None:
        with self._lock:
            self._clients.add(conn)

    def remove(self, conn: socket.socket) -> None:
        with self._lock:
            self._clients.discard(conn)
        try:
            conn.close()
        except Exception:
            pass

    def count(self) -> int:
        with self._lock:
            return len(self._clients)

    def broadcast_text(self, text: str) -> None:
        with self._lock:
            clients = list(self._clients)
        dead: list[socket.socket] = []
        frame = encode_ws_text_frame(text)
        for conn in clients:
            try:
                conn.sendall(frame)
            except Exception:
                dead.append(conn)
        for conn in dead:
            self.remove(conn)


def encode_ws_text_frame(text: str) -> bytes:
    payload = text.encode("utf-8")
    header = bytearray([0x81])
    n = len(payload)
    if n < 126:
        header.append(n)
    elif n < 65536:
        header.append(126)
        header.extend(struct.pack("!H", n))
    else:
        header.append(127)
        header.extend(struct.pack("!Q", n))
    return bytes(header) + payload


def recv_exact(conn: socket.socket, size: int) -> bytes:
    buf = bytearray()
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf.extend(chunk)
    return bytes(buf)


def read_ws_frame(conn: socket.socket) -> tuple[int, bytes]:
    hdr = recv_exact(conn, 2)
    opcode = hdr[0] & 0x0F
    masked = bool(hdr[1] & 0x80)
    length = hdr[1] & 0x7F
    if length == 126:
        length = struct.unpack("!H", recv_exact(conn, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", recv_exact(conn, 8))[0]
    mask = recv_exact(conn, 4) if masked else b""
    payload = recv_exact(conn, length) if length else b""
    if masked:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return opcode, payload


def parse_http_request(conn: socket.socket) -> tuple[str, dict[str, str]]:
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            raise ConnectionError("empty request")
        data += chunk
        if len(data) > 65536:
            raise ConnectionError("request too large")
    raw = data.decode("utf-8", errors="ignore")
    lines = raw.split("\r\n")
    request_line = lines[0]
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            break
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        headers[k.strip().lower()] = v.strip()
    return request_line, headers


def send_http_json(conn: socket.socket, status_code: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    reason = {200: "OK", 400: "Bad Request", 404: "Not Found"}.get(status_code, "OK")
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        "Content-Type: application/json; charset=utf-8",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    conn.sendall("\r\n".join(headers).encode("utf-8") + body)


def websocket_accept(key: str) -> str:
    raw = (key + WS_MAGIC).encode("utf-8")
    return base64.b64encode(hashlib.sha1(raw).digest()).decode("ascii")


def pubsub_loop(registry: ClientRegistry, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        client = get_redis_client()
        if client is None:
            time.sleep(1.0)
            continue
        pubsub = client.pubsub(ignore_subscribe_messages=True)
        try:
            pubsub.subscribe(WS_BROADCAST_CHANNEL)
            last_status = client.get(WS_LAST_STATUS_KEY)
            if last_status:
                registry.broadcast_text(last_status)
            while not stop_event.is_set():
                msg = pubsub.get_message(timeout=1.0)
                if not msg:
                    continue
                data = msg.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="ignore")
                if not isinstance(data, str):
                    continue
                registry.broadcast_text(data)
        except Exception as exc:
            print(f"ws pubsub 异常: {exc}")
            time.sleep(1.0)
        finally:
            try:
                pubsub.close()
            except Exception:
                pass


def handle_client(conn: socket.socket, addr, registry: ClientRegistry) -> None:
    try:
        request_line, headers = parse_http_request(conn)
        parts = request_line.split()
        path = parts[1] if len(parts) >= 2 else "/"

        if headers.get("upgrade", "").lower() != "websocket":
            if path in {"/health", "/ws/health", "/ws/realtime/health"}:
                send_http_json(
                    conn,
                    200,
                    {"status": "ok", "service": "ws_realtime", "clients": registry.count(), "ts": now_utc_iso()},
                )
            else:
                send_http_json(conn, 404, {"error": "Not Found"})
            return

        ws_key = headers.get("sec-websocket-key", "")
        if not ws_key:
            send_http_json(conn, 400, {"error": "Missing Sec-WebSocket-Key"})
            return

        accept = websocket_accept(ws_key)
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n"
            "\r\n"
        )
        conn.sendall(response.encode("utf-8"))
        registry.add(conn)
        registry.broadcast_text(
            json.dumps(
                {
                    "channel": "system",
                    "event": "welcome",
                    "payload": {"message": "realtime connected", "clients": registry.count(), "ts": now_utc_iso()},
                },
                ensure_ascii=False,
            )
        )

        while True:
            opcode, payload = read_ws_frame(conn)
            if opcode == 0x8:
                break
            if opcode == 0x9:
                pong = bytearray([0x8A, len(payload)]) + payload
                conn.sendall(bytes(pong))
            elif opcode == 0x1:
                # 当前只做广播，不处理前端命令。
                continue
    except Exception:
        pass
    finally:
        registry.remove(conn)
        print(f"ws client closed: {addr}")


def main() -> int:
    parser = argparse.ArgumentParser(description="轻量 WebSocket 实时广播服务")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args()

    registry = ClientRegistry()
    stop_event = threading.Event()
    t = threading.Thread(target=pubsub_loop, args=(registry, stop_event), daemon=True)
    t.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen(128)
        print(f"ws realtime server listening on {args.host}:{args.port}")
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, registry), daemon=True)
                thread.start()
        except KeyboardInterrupt:
            print("收到中断，退出")
        finally:
            stop_event.set()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
