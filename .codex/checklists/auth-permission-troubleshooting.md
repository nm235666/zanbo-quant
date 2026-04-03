# Auth / Permission Troubleshooting Checklist

适用于接口返回 `401 AUTH_REQUIRED` 或 `403 AUTH_PERMISSION_DENIED_*`。

## 1. 先分清 401 与 403

- `401`：未登录、会话失效、或未携带 token。
- `403`：已登录但权限不足。

## 2. 401 排查

- 前端重新登录后重试。
- 检查请求头是否携带：
  - 会话 token（前端登录态）
  - 或 `X-Admin-Token`（系统管理调用）
- 服务器上检查：
  - `echo "$BACKEND_ADMIN_TOKEN"`
  - 确认后端进程加载了期望环境变量。

## 3. 403 排查

- 查看当前账号角色与有效权限：
  - `GET /api/auth/status`
  - `GET /api/auth/permissions`
- 对照路由权限要求（示例）：
  - `/api/quant-factors/*` 需要 `research_advanced`（或 admin）。

## 4. 典型错误码提示

- `AUTH_REQUIRED`：先登录。
- `AUTH_PERMISSION_DENIED_*`：补角色权限或切 admin 账号。
- `AUTH_PERMISSION_DENIED_QUANT_FACTORS`：缺少因子模块权限。

## 5. 验收

- 触发接口时不再返回 `401/403`。
- 前端与 curl 行为一致（避免“curl 可用，页面不可用”）。
