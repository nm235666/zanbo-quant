# Incident Prompt: 404 vs 401/403 快速分流

```text
请按“先分流、后定位”的方式处理当前接口异常，不要先改代码。

目标：
1) 先判断是 404（路由/网关）还是 401/403（认证/权限）
2) 给出最短修复路径和可执行命令
3) 最后给一组验收命令

必须执行的检查：
- 服务器本机：
  - curl -i http://127.0.0.1:8077/api/health
  - curl -i "http://127.0.0.1:8077/api/quant-factors/results?page=1&page_size=1"
- 远端浏览器：
  - DevTools Network 中失败请求的 Request URL / Status / Response Body
- 网关：
  - 检查 nginx_8077.conf 的 /api 转发目标

输出格式：
1. 结论：404 还是 401/403
2. 证据：关键命令输出要点
3. 修复动作：按优先级 1/2/3
4. 验收：3 条可复制命令
```
