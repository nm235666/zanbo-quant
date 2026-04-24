from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from . import config
from .audit import record_tool_audit
from .auth import origin_allowed, verify_request
from .tools import MCPToolError, call_tool, list_tools


JSONRPC_VERSION = "2.0"


def _json_dumps(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")


def _rpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _rpc_error(request_id: Any, code: int, message: str, data: Any = None) -> dict[str, Any]:
    payload = {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}
    if data is not None:
        payload["error"]["data"] = data
    return payload


class MCPHandler(BaseHTTPRequestHandler):
    server_version = "ZanboMCP/1.0"

    def _origin(self) -> str:
        return str(self.headers.get("Origin", "") or "").strip().rstrip("/")

    def _send_json(self, payload: Any, *, status: int = 200) -> None:
        body = _json_dumps(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        origin = self._origin()
        if origin and origin_allowed(origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Mcp-Session-Id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _reject_if_unauthorized(self) -> bool:
        auth = verify_request(authorization=str(self.headers.get("Authorization", "")), origin=self._origin())
        if auth.ok:
            return False
        self._send_json({"ok": False, "error": auth.error}, status=auth.status)
        return True

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self._origin() and not origin_allowed(self._origin()):
            self._send_json({"ok": False, "error": "origin_not_allowed"}, status=403)
            return
        self.send_response(204)
        origin = self._origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Mcp-Session-Id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/mcp/health":
            if not config.MCP_HEALTH_PUBLIC and self._reject_if_unauthorized():
                return
            self._send_json(
                {
                    "ok": True,
                    "service": "zanbo-mcp",
                    "mcp_path": "/mcp",
                    "lan_base_url": config.MCP_LAN_BASE_URL,
                    "public_base_url": config.MCP_PUBLIC_BASE_URL,
                    "write_enabled": config.MCP_WRITE_ENABLED,
                }
            )
            return
        self._send_json({"ok": False, "error": "not_found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/mcp":
            self._send_json({"ok": False, "error": "not_found"}, status=404)
            return
        if self._reject_if_unauthorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            request = json.loads(raw or "{}")
        except Exception as exc:
            self._send_json(_rpc_error(None, -32700, "parse_error", str(exc)), status=400)
            return
        response = self._handle_rpc(request)
        self._send_json(response)

    def _handle_rpc(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = request.get("id")
        method = str(request.get("method") or "").strip()
        params = request.get("params") if isinstance(request.get("params"), dict) else {}
        if method == "initialize":
            return _rpc_result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "zanbo-mcp", "version": "1.0.0"},
                },
            )
        if method == "tools/list":
            return _rpc_result(request_id, {"tools": list_tools()})
        if method == "tools/call":
            name = str(params.get("name") or "").strip()
            arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            actor = str(arguments.get("actor") or "").strip()
            dry_run = bool(arguments.get("dry_run", True))
            audit_id = 0
            try:
                result = call_tool(name, arguments)
                audit_id = record_tool_audit(
                    request_id=str(request_id or ""),
                    actor=actor,
                    tool_name=name,
                    args=arguments,
                    dry_run=dry_run,
                    status="success",
                    result=result,
                )
                if isinstance(result, dict):
                    result.setdefault("audit_id", audit_id)
                return _rpc_result(
                    request_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, default=str)}],
                        "structuredContent": result,
                    },
                )
            except MCPToolError as exc:
                audit_id = record_tool_audit(
                    request_id=str(request_id or ""),
                    actor=actor,
                    tool_name=name,
                    args=arguments,
                    dry_run=dry_run,
                    status="error",
                    result={"audit_id": audit_id},
                    error_text=str(exc),
                )
                return _rpc_error(request_id, -32000, str(exc), {"audit_id": audit_id})
        if method == "notifications/initialized":
            return _rpc_result(request_id, {})
        return _rpc_error(request_id, -32601, f"method_not_found:{method}")

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return


def main() -> int:
    server = ThreadingHTTPServer((config.MCP_HOST, config.MCP_PORT), MCPHandler)
    print(f"MCP server running on http://{config.MCP_HOST}:{config.MCP_PORT}/mcp", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
