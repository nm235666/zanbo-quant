#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


DEFAULT_LLM_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_LLM_API_KEY = "sk-374806b2f1744b1aa84a6b27758b0bb6"
DEFAULT_LLM_MODEL = "GPT-5.4"
GPT54_BASE_URL = "https://ai.td.ee/v1"
GPT54_API_KEY = "sk-1dbff3b041575534c99ee9f95711c2c9e9977c94db51ba679b9bcf04aa329343"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"
KIMI_API_KEY = "sk-trh5tumfscY5vi5VBSFInnwU3pr906bFJC4Nvf53xdMr2z72"

TRANSIENT_HTTP_CODES = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524}


@dataclass(frozen=True)
class LLMRoute:
    model: str
    base_url: str
    api_key: str
    temperature: float


def normalize_model_name(model: str) -> str:
    raw = (model or "").strip()
    m = raw.lower().replace("_", "-")
    if m in {"kimi2.5", "kimi-2.5", "kimi k2.5", "kimi-k2", "kimi2", "kimi"}:
        return "kimi-k2.5"
    return raw or DEFAULT_LLM_MODEL


def normalize_temperature_for_model(model: str, temperature: float) -> float:
    m = normalize_model_name(model).lower()
    if m.startswith("kimi-k2.5") or m.startswith("kimi-k2"):
        return 1.0
    return temperature


def resolve_provider(model: str, base_url: str = "", api_key: str = "") -> tuple[str, str]:
    m = normalize_model_name(model).lower()
    if m.startswith("gpt-5.4"):
        return GPT54_BASE_URL, GPT54_API_KEY
    if m.startswith("kimi-k2.5") or m.startswith("kimi"):
        return KIMI_BASE_URL, KIMI_API_KEY
    return (base_url or DEFAULT_LLM_BASE_URL), (api_key or DEFAULT_LLM_API_KEY)


def build_route(model: str, base_url: str = "", api_key: str = "", temperature: float = 0.2) -> LLMRoute:
    normalized_model = normalize_model_name(model)
    resolved_base_url, resolved_api_key = resolve_provider(normalized_model, base_url, api_key)
    return LLMRoute(
        model=normalized_model,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        temperature=normalize_temperature_for_model(normalized_model, temperature),
    )


def sanitize_json_value(value):
    if isinstance(value, dict):
        return {str(k): sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_json_value(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_json_value(v) for v in value]
    if isinstance(value, float):
        if value != value:
            return None
        if value == float("inf") or value == float("-inf"):
            return None
    return value


def post_chat_completions(
    route: LLMRoute,
    payload: dict,
    timeout_s: int = 120,
    max_retries: int = 3,
) -> str:
    body = json.dumps(sanitize_json_value(payload), ensure_ascii=False, allow_nan=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {route.api_key}",
        "Connection": "close",
    }
    url = route.base_url.rstrip("/") + "/chat/completions"
    last_error = None

    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=max(timeout_s, 30)) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {exc.code} {exc.reason} | {detail}"
            if exc.code in TRANSIENT_HTTP_CODES and attempt < max_retries:
                time.sleep(1.5 * (2**attempt))
                continue
            raise RuntimeError(f"LLM接口错误: {last_error}") from exc
        except Exception as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(1.5 * (2**attempt))
                continue

    try:
        import requests  # type: ignore

        response = requests.post(
            url,
            json=sanitize_json_value(payload),
            headers={"Authorization": f"Bearer {route.api_key}", "Connection": "close"},
            timeout=max(timeout_s, 30),
        )
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code} {response.reason} | {response.text}")
        return response.text
    except Exception as exc:  # pragma: no cover
        if last_error:
            raise RuntimeError(f"{last_error}; fallback requests error: {exc}") from exc
        raise RuntimeError(str(exc)) from exc


def chat_completion_text(
    *,
    model: str,
    messages: list[dict],
    temperature: float = 0.2,
    base_url: str = "",
    api_key: str = "",
    timeout_s: int = 120,
    max_retries: int = 3,
    **extra_payload,
) -> str:
    route = build_route(model=model, base_url=base_url, api_key=api_key, temperature=temperature)
    payload = {
        "model": route.model,
        "temperature": route.temperature,
        "messages": messages,
    }
    payload.update(extra_payload)
    text = post_chat_completions(route=route, payload=payload, timeout_s=timeout_s, max_retries=max_retries)
    obj = json.loads(text)
    return obj["choices"][0]["message"]["content"]

