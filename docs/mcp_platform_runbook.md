# MCP 平台运行手册

本项目的一期 Agent 化先落标准 MCP HTTP 工具底座。MCP 服务独立于现有前后端进程运行，建议由反代或内网穿透将 `/mcp` 路径映射到 MCP 服务。

## 访问入口

- 内网入口：`http://192.168.5.52:8077/mcp`
- 外网入口：`http://tianbo.asia:6273/mcp`
- 健康检查：`/mcp/health`

默认健康检查也需要 MCP token。所有请求都应带：

```text
Authorization: Bearer <MCP_ADMIN_TOKEN>
```

## 启动方式

```bash
cd /home/zanbo/zanbotest
export MCP_ADMIN_TOKEN='replace-with-strong-token'
./scripts/run_mcp_server.sh
```

默认监听：

```text
127.0.0.1:8765
```

可通过环境变量覆盖：

```bash
export MCP_HOST=127.0.0.1
export MCP_PORT=8765
export MCP_WRITE_ENABLED=1
export MCP_LAN_BASE_URL=http://192.168.5.52:8077
export MCP_PUBLIC_BASE_URL=http://tianbo.asia:6273
```

## 反代要求

两个入口都应将 `/mcp` 和 `/mcp/health` 转发到 MCP 服务，并保留 `Authorization` header。

示例：

```nginx
location /mcp {
    proxy_pass http://127.0.0.1:8765/mcp;
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /mcp/health {
    proxy_pass http://127.0.0.1:8765/mcp/health;
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

如果 `192.168.5.52:8077` 当前已经承载 Web 前端，则按路径拆分：`/mcp` 转 MCP 服务，其余路径保持原有 Web 转发。

## 首批工具

- `system.health_snapshot`
- `db.table_counts`
- `db.readonly_query`
- `jobs.list_definitions`
- `jobs.list_runs`
- `jobs.list_alerts`
- `jobs.trigger`
- `scheduler.check_cron_sync`
- `business.closure_gap_scan`
- `business.repair_funnel_score_align`
- `business.repair_funnel_review_refresh`
- `business.run_decision_snapshot`
- `business.reconcile_portfolio_positions`

写工具默认 `dry_run=true`。真实执行必须提供：

```json
{
  "dry_run": false,
  "confirm": true,
  "actor": "ops-user",
  "reason": "明确的执行原因",
  "idempotency_key": "稳定幂等键"
}
```

## JSON-RPC 示例

```bash
curl -s \
  -H "Authorization: Bearer ${MCP_ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  http://127.0.0.1:8765/mcp
```

```bash
curl -s \
  -H "Authorization: Bearer ${MCP_ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"business.closure_gap_scan","arguments":{}}}' \
  http://127.0.0.1:8765/mcp
```

## 审计

所有 `tools/call` 调用都会写入 `mcp_tool_audit_logs`，包含 tool name、参数、dry-run 状态、执行结果和错误信息。写工具执行前必须先确认审计表可写。
