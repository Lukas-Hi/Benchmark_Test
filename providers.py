#!/usr/bin/env python3
"""
Entscheider-Benchmark: Provider-Konfiguration und API-Caller
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo
"""

import json
import asyncio
import aiohttp

from models import (
    ANTHROPIC_KEY, OPENAI_KEY, GOOGLE_KEY, OPENROUTER_KEY,
    TEMPERATURE, MAX_TOKENS, log,
)
from prompts import SYSTEM_PROMPT


# ============================================
# Modellkatalog
# ============================================

MODELS = {
    # --- Frontier ---
    "Claude Opus 4.6": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-6",
        "openrouter_id": "anthropic/claude-opus-4-6",
    },
    "Claude Opus 4.5": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-5",
        "openrouter_id": "anthropic/claude-opus-4-5",
    },
    "GPT-5.2": {
        "provider": "openrouter",
        "model_id": "gpt-5.2",
        "openrouter_id": "openai/gpt-5.2",
    },
    "GPT-5.2 Pro": {
        "provider": "openrouter",
        "model_id": "gpt-5.2-pro",
        "openrouter_id": "openai/gpt-5.2-pro",
    },
    "Gemini 3 Pro": {
        "provider": "google",
        "model_id": "gemini-3-pro-preview",
        "openrouter_id": "google/gemini-3-pro-preview",
    },
    "Gemini 2.5 Pro": {
        "provider": "google",
        "model_id": "gemini-2.5-pro",
        "openrouter_id": "google/gemini-2.5-pro",
    },
    "Grok 4.1": {
        "provider": "openrouter",
        "model_id": "x-ai/grok-4.1",
        "openrouter_id": "x-ai/grok-4.1",
    },
    # --- Mid-Tier ---
    "Claude Sonnet 4.5": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-5-20250929",
        "openrouter_id": "anthropic/claude-sonnet-4-5",
    },
    "Claude Haiku 4.5": {
        "provider": "anthropic",
        "model_id": "claude-haiku-4-5-20251001",
        "openrouter_id": "anthropic/claude-haiku-4-5",
    },
    "GPT-5.2 Chat": {
        "provider": "openrouter",
        "model_id": "gpt-5.2-chat",
        "openrouter_id": "openai/gpt-5.2-chat",
    },
    "Gemini 2.5 Flash": {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "openrouter_id": "google/gemini-2.5-flash",
    },
    "Mistral Large 3": {
        "provider": "openrouter",
        "model_id": "mistralai/mistral-large-3",
        "openrouter_id": "mistralai/mistral-large-3",
    },
    "DeepSeek V3.2": {
        "provider": "openrouter",
        "model_id": "deepseek/deepseek-v3.2",
        "openrouter_id": "deepseek/deepseek-v3.2",
    },
    "Llama 3.3 70B": {
        "provider": "openrouter",
        "model_id": "meta-llama/llama-3.3-70b-instruct",
        "openrouter_id": "meta-llama/llama-3.3-70b-instruct",
    },
    # --- Coding ---
    "GPT-5.2-Codex": {
        "provider": "openrouter",
        "model_id": "gpt-5.2-codex",
        "openrouter_id": "openai/gpt-5.2-codex",
    },
    # --- Reasoning ---
    "DeepSeek R1": {
        "provider": "openrouter",
        "model_id": "deepseek/deepseek-r1",
        "openrouter_id": "deepseek/deepseek-r1",
    },
    "o1": {
        "provider": "openrouter",
        "model_id": "o1",
        "openrouter_id": "openai/o1",
    },
}


# ============================================
# Provider-Endpunkte
# ============================================

PROVIDERS = {
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "key_env": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key_env": "OPENAI_API_KEY",
    },
    "google": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "key_env": "GOOGLE_API_KEY",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
    },
}

KEY_MAP = {
    "ANTHROPIC_API_KEY": ANTHROPIC_KEY,
    "OPENAI_API_KEY": OPENAI_KEY,
    "GOOGLE_API_KEY": GOOGLE_KEY,
    "OPENROUTER_API_KEY": OPENROUTER_KEY,
}

# Per-provider concurrency limits (max simultaneous requests)
PROVIDER_CONCURRENCY = {
    "anthropic": 1,
    "openai": 1,
    "google": 1,
    "openrouter": 1,
}

# Per-provider base delay in seconds (before jitter)
PROVIDER_DELAY = {
    "anthropic": 2.0,
    "openai": 2.0,
    "google": 5.0,     # needs more spacing due to quota limits
    "openrouter": 2.0,
}

# Max retries on HTTP 429 (rate limit)
MAX_RETRIES = 3
RETRY_BASE_DELAY = 10  # seconds, exponential: 10s, 30s, 60s


def resolve_provider(model_cfg: dict) -> tuple[str, str, str]:
    """Determine provider, URL, and API key for a model.
    Falls back to OpenRouter if direct API key is missing."""
    provider = model_cfg["provider"]
    prov_cfg = PROVIDERS[provider]
    key = KEY_MAP.get(prov_cfg["key_env"], "")

    if not key and provider != "openrouter":
        if OPENROUTER_KEY:
            log.debug(f"  Fallback auf OpenRouter (kein {prov_cfg['key_env']})")
            return "openrouter", PROVIDERS["openrouter"]["url"], OPENROUTER_KEY
        else:
            return provider, prov_cfg["url"], ""

    return provider, prov_cfg["url"], key


# ============================================
# Provider-spezifische API-Calls
# ============================================

async def _call_with_retry(coro_factory, retries=MAX_RETRIES):
    """Wrap an API call with retry on HTTP 429/529 (rate limit / overloaded).
    Exponential backoff: 10s, 30s, 60s."""
    result, error = None, None
    for attempt in range(retries + 1):
        result, error = await coro_factory()
        if error and attempt < retries:
            status_str = str(error)
            if "HTTP 429" in status_str or "HTTP 529" in status_str or "HTTP 503" in status_str:
                delay = RETRY_BASE_DELAY * (3 ** attempt)  # 10, 30, 90
                delay = min(delay, 90)  # cap at 90s
                log.warning(f"  Rate-limited/overloaded, retry in {delay}s (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(delay)
                continue
        return result, error
    return result, error


async def call_anthropic(session, model_id, user_content, api_key, use_system):
    """Anthropic Messages API."""
    async def _call():
        payload = {
            "model": model_id,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [{"role": "user", "content": user_content}],
        }
        if use_system:
            payload["system"] = SYSTEM_PROMPT
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        async with session.post(
            PROVIDERS["anthropic"]["url"], json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                return None, f"HTTP {resp.status}: {json.dumps(data, ensure_ascii=False)[:500]}"
            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")
            usage = data.get("usage", {})
            return {
                "response": text,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "raw_json": json.dumps(data, ensure_ascii=False),
            }, None
    return await _call_with_retry(_call)


async def call_openai(session, model_id, user_content, api_key, use_system):
    """OpenAI Chat Completions API."""
    async def _call():
        messages = []
        if use_system:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": user_content})
        payload = {
            "model": model_id,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with session.post(
            PROVIDERS["openai"]["url"], json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                return None, f"HTTP {resp.status}: {json.dumps(data, ensure_ascii=False)[:500]}"
            text = data["choices"][0]["message"]["content"] if data.get("choices") else ""
            usage = data.get("usage", {})
            return {
                "response": text,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "raw_json": json.dumps(data, ensure_ascii=False),
            }, None
    return await _call_with_retry(_call)


async def call_google(session, model_id, user_content, api_key, use_system):
    """Google Gemini API."""
    async def _call():
        url = PROVIDERS["google"]["url"].format(model=model_id) + f"?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "temperature": TEMPERATURE,
                "maxOutputTokens": MAX_TOKENS,
            },
        }
        if use_system:
            payload["systemInstruction"] = {"parts": [{"text": SYSTEM_PROMPT}]}
        headers = {"Content-Type": "application/json"}
        async with session.post(
            url, json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                return None, f"HTTP {resp.status}: {json.dumps(data, ensure_ascii=False)[:500]}"
            text = ""
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    text += part.get("text", "")
            usage = data.get("usageMetadata", {})
            return {
                "response": text,
                "input_tokens": usage.get("promptTokenCount", 0),
                "output_tokens": usage.get("candidatesTokenCount", 0),
                "raw_json": json.dumps(data, ensure_ascii=False),
            }, None
    return await _call_with_retry(_call)


async def call_openrouter(session, model_id, user_content, api_key, use_system):
    """OpenRouter API (OpenAI-compatible)."""
    async def _call():
        messages = []
        if use_system:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": user_content})
        payload = {
            "model": model_id,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hunter-id.com/benchmark",
            "X-Title": "Entscheider-Benchmark v3.0",
        }
        async with session.post(
            PROVIDERS["openrouter"]["url"], json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                return None, f"HTTP {resp.status}: {json.dumps(data, ensure_ascii=False)[:500]}"
            text = data["choices"][0]["message"]["content"] if data.get("choices") else ""
            usage = data.get("usage", {})
            return {
                "response": text,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "raw_json": json.dumps(data, ensure_ascii=False),
            }, None
    return await _call_with_retry(_call)


PROVIDER_CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google,
    "openrouter": call_openrouter,
}
