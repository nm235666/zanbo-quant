# Remote Deploy Smoke Checklist

适用于“服务器本机正常、远端浏览器异常（404/401/403）”场景。

## 1. 先确认服务器链路

- `curl -i http://127.0.0.1:8077/api/health`
- `curl -i "http://127.0.0.1:8077/api/quant-factors/results?page=1&page_size=1"`
- `curl -i -X POST "http://127.0.0.1:8077/api/quant-factors/mine/start" -H 'Content-Type: application/json' -d '{"direction":"smoke"}'`

判断标准：
- `404`：路由或反向代理配置问题。
- `401/403`：路由已存在，进入认证/权限问题排查。
- `200`：接口可直接访问（通常仅健康检查）。

## 2. 确认反向代理目标

- 检查 `nginx_8077.conf` 是否将 `/api/` 转发到正确后端（当前应为 `8002`）。
- 重启网关后复测：
  - `./start_nginx_8077.sh`
  - `curl -i http://127.0.0.1:8077/api/health`

## 3. 确认远端前端请求地址

- 在远端浏览器 DevTools -> Network 查看失败请求：
  - Request URL
  - Status Code
  - Response Body
- 如果 URL 指向旧域名/旧端口，优先修复 `VITE_API_BASE_URL` 或网关入口。

## 4. 前端版本与缓存

- 若后端已更新但页面仍旧行为：
  - 重新部署前端产物
  - 浏览器强刷 `Ctrl+F5`
- 使用 Network 面板确认新 bundle 哈希已变化。

## 5. 最终验收

- 远端页面触发目标接口时，不再出现 `404`。
- 若返回 `401/403`，转交认证/权限清单处理。
