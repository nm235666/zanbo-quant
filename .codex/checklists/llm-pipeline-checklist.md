# LLM Pipeline Checklist

用于检查 LLM 相关流水线是否可安全运行。

## Provider 层

- `config/llm_providers.json` 中是否有可用主节点？
- 是否存在明显失效节点（401/403/404/固定 model_not_found）？
- 是否启用了失败阈值，避免单次超时误停用？
- 模型名大小写是否已验证（如 `gpt-5.4` vs `GPT-5.4`）？
- base_url 是否已确认路径（`/v1`）？

## Gateway 层

- fallback 链是否符合当前策略？
- 是否记录 attempts / used_model 便于审计？
- 参数是否与目标网关兼容（temperature/max_tokens）？

## Job 层

- 评分/分析任务是否存在并发风暴风险？
- 是否有“直到清空”任务的退出条件？
- 是否有失败队列和重试上限？

## 日报链路专项

- 日报列表加载失败时，先区分“接口不可达”与“空数据”与“权限问题”
- 日报总结失败时，先看 provider 配置是否完整（尤其 `api_key`）
- 若报 `LLM 提供商未配置完整`，检查 `config/llm_providers.json` 对应节点是否 `enabled=true`
- 若报 `LLM 提供商未配置完整`，检查 `api_key` 或 `api_key_env` 是否真实可用
- 若报 `LLM 提供商未配置完整`，检查模型名与节点键是否一致（如 `GPT-5.4` / `gpt-5.4`）
- 日报链路至少做一次 `--limit 1` smoke，不直接全量重跑
- 失败重试前确认是否会覆盖已有成功结果
- 日报相关改动后，至少执行 `python3 -m py_compile backend/server.py backend/routes/*.py`
- 日报相关改动后，至少执行 `bash run_minimal_regression.sh`

## 验证

- 先跑 `--limit 1` 验证链路
- 再跑小批量验证
- 最后恢复并发任务

## 发布前结论

- 是否允许恢复全量补分/分析任务？
- 是否需要降并发或临时切模型？
