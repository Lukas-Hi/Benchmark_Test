#!/usr/bin/env python3
"""
Entscheider-Benchmark: Strategische KI-Kompetenz im Praxistest
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Multi-Provider Benchmark-Runner:
  - Anthropic API (Claude-Modelle mit Pro/Max-Abo)
  - OpenAI API (GPT-Modelle mit Business-Abo)
  - Google Gemini API (Gemini-Modelle mit Abo)
  - OpenRouter (alle anderen Modelle)

Usage:
    python benchmark.py                  # Voller Durchlauf
    python benchmark.py --runs 3         # Nur 3 Durchläufe
    python benchmark.py --models "Claude Opus 4.6,GPT-5.2"
    python benchmark.py --tasks A1,A3
    python benchmark.py --dry-run        # Zeigt Konfiguration ohne API-Calls
"""

import os
import json
import time
import csv
import asyncio
import argparse
import aiohttp
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
from statistics import mean, stdev
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, TASKS

# ============================================
# Konfiguration
# ============================================

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

DOCS_DIR = Path(os.getenv("DOCS_DIR", "./documents"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./results"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2"))
NUM_RUNS = int(os.getenv("NUM_RUNS", "10"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("benchmark")


# ============================================
# Provider-Konfiguration
# ============================================

# provider: "anthropic" | "openai" | "google" | "openrouter"
# model_id: Provider-spezifische Modell-ID
# openrouter_id: Fallback-ID falls Direkt-API nicht verfügbar

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
        "provider": "openai",
        "model_id": "gpt-5.2",
        "openrouter_id": "openai/gpt-5.2",
    },
    "GPT-5.2 Pro": {
        "provider": "openai",
        "model_id": "gpt-5.2-pro",
        "openrouter_id": "openai/gpt-5.2-pro",
    },
    "Gemini 3 Pro": {
        "provider": "google",
        "model_id": "gemini-3-pro",
        "openrouter_id": "google/gemini-3-pro",
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
        "provider": "openai",
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
        "provider": "openai",
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
        "provider": "openai",
        "model_id": "o1",
        "openrouter_id": "openai/o1",
    },
}


# ============================================
# Provider-Endpunkte und Formate
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
        # Gemini API via generativelanguage endpoint
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


def resolve_provider(model_cfg: dict) -> tuple[str, str, str]:
    """Bestimmt Provider, URL und Key für ein Modell.
    Falls Direkt-API-Key fehlt, Fallback auf OpenRouter."""
    provider = model_cfg["provider"]
    prov_cfg = PROVIDERS[provider]
    key = KEY_MAP.get(prov_cfg["key_env"], "")

    if not key and provider != "openrouter":
        # Fallback auf OpenRouter
        if OPENROUTER_KEY:
            log.debug(f"  Fallback auf OpenRouter (kein {prov_cfg['key_env']})")
            return "openrouter", PROVIDERS["openrouter"]["url"], OPENROUTER_KEY
        else:
            return provider, prov_cfg["url"], ""  # wird als Fehler behandelt

    return provider, prov_cfg["url"], key


# ============================================
# Datenklassen
# ============================================

@dataclass
class SingleResult:
    model_name: str
    model_id: str
    provider: str
    task_id: str
    task_title: str
    run_number: int
    timestamp: str
    response: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    error: str = ""


@dataclass
class AggregatedResult:
    model_name: str
    model_id: str
    provider: str
    task_id: str
    task_title: str
    num_runs: int = 0
    num_successful: int = 0
    num_failed: int = 0
    latency_mean: float = 0.0
    latency_stdev: float = 0.0
    latency_min: float = 0.0
    latency_max: float = 0.0
    output_tokens_mean: float = 0.0
    output_tokens_stdev: float = 0.0
    response_length_mean: float = 0.0
    response_length_stdev: float = 0.0
    response_length_cv: float = 0.0


# ============================================
# Hilfsfunktionen
# ============================================

def load_document(filename: str) -> str:
    filepath = DOCS_DIR / filename
    if not filepath.exists():
        log.warning(f"Dokument nicht gefunden: {filepath}")
        return f"[DOKUMENT NICHT GEFUNDEN: {filename}]"
    if filepath.suffix == ".pdf":
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        parts.append(text)
            return "\n\n".join(parts)
        except ImportError:
            return f"[pdfplumber nicht installiert]"
    return filepath.read_text(encoding="utf-8")


def build_user_content(task: dict) -> str:
    parts = []
    for doc_file in task["docs"]:
        doc_text = load_document(doc_file)
        parts.append(f"--- DOKUMENT: {doc_file} ---\n\n{doc_text}\n\n--- ENDE DOKUMENT ---")
    parts.append(task["prompt"])
    return "\n\n".join(parts)


def calc_stats(values: list[float]) -> dict:
    if not values:
        return {"mean": 0, "stdev": 0, "min": 0, "max": 0, "cv": 0}
    m = mean(values)
    s = stdev(values) if len(values) > 1 else 0
    cv = (s / m * 100) if m > 0 else 0
    return {"mean": round(m, 2), "stdev": round(s, 2),
            "min": round(min(values), 2), "max": round(max(values), 2),
            "cv": round(cv, 1)}


# ============================================
# Provider-spezifische API-Calls
# ============================================

async def call_anthropic(session, model_id, user_content, api_key, use_system):
    """Anthropic Messages API."""
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
        }, None


async def call_openai(session, model_id, user_content, api_key, use_system):
    """OpenAI Chat Completions API."""
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
        }, None


async def call_google(session, model_id, user_content, api_key, use_system):
    """Google Gemini API."""
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
        }, None


async def call_openrouter(session, model_id, user_content, api_key, use_system):
    """OpenRouter API (OpenAI-kompatibel)."""
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
        "X-Title": "Entscheider-Benchmark v2.0",
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
        }, None


PROVIDER_CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google,
    "openrouter": call_openrouter,
}


# ============================================
# Unified API-Call
# ============================================

async def call_model(
    session, model_name, model_cfg, task_id, task, run_number, semaphore,
) -> SingleResult:
    """Sendet einen Benchmark-Request an den richtigen Provider."""

    provider, url, api_key = resolve_provider(model_cfg)
    model_id = model_cfg["openrouter_id"] if provider == "openrouter" else model_cfg["model_id"]
    timestamp = datetime.now(timezone.utc).isoformat()
    user_content = build_user_content(task)
    use_system = task.get("use_system_prompt", True)

    result = SingleResult(
        model_name=model_name, model_id=model_id, provider=provider,
        task_id=task_id, task_title=task["title"],
        run_number=run_number, timestamp=timestamp, response="",
    )

    if not api_key:
        result.error = f"Kein API-Key für Provider '{provider}'"
        log.error(f"✗ {model_name}: {result.error}")
        return result

    async with semaphore:
        try:
            log.info(f"▶ {model_name} [{provider}] × {task['title']} [Run {run_number}]")
            start = time.monotonic()

            caller = PROVIDER_CALLERS[provider]
            data, error = await caller(session, model_id, user_content, api_key, use_system)
            result.latency_seconds = round(time.monotonic() - start, 2)

            if error:
                result.error = error
                log.error(f"✗ {model_name} [Run {run_number}]: {error[:200]}")
            else:
                result.response = data["response"]
                result.input_tokens = data["input_tokens"]
                result.output_tokens = data["output_tokens"]
                result.total_tokens = data["input_tokens"] + data["output_tokens"]
                log.info(
                    f"✓ {model_name} [Run {run_number}] "
                    f"({result.latency_seconds}s, {result.total_tokens} tok)"
                )

        except asyncio.TimeoutError:
            result.error = "Timeout (300s)"
            log.error(f"✗ Timeout: {model_name} [Run {run_number}]")
        except Exception as e:
            result.error = str(e)
            log.error(f"✗ {model_name} [Run {run_number}]: {e}")

        await asyncio.sleep(REQUEST_DELAY)

    return result


# ============================================
# Aggregation
# ============================================

def aggregate_results(results: list[SingleResult]) -> list[AggregatedResult]:
    groups: dict[tuple, list[SingleResult]] = {}
    for r in results:
        groups.setdefault((r.model_name, r.task_id), []).append(r)

    aggregated = []
    for (model_name, task_id), group in sorted(groups.items()):
        ok = [r for r in group if not r.error]
        lat = calc_stats([r.latency_seconds for r in ok])
        tok = calc_stats([float(r.output_tokens) for r in ok])
        rlen = calc_stats([float(len(r.response)) for r in ok])
        aggregated.append(AggregatedResult(
            model_name=model_name, model_id=group[0].model_id,
            provider=group[0].provider,
            task_id=task_id, task_title=group[0].task_title,
            num_runs=len(group), num_successful=len(ok),
            num_failed=len(group) - len(ok),
            latency_mean=lat["mean"], latency_stdev=lat["stdev"],
            latency_min=lat["min"], latency_max=lat["max"],
            output_tokens_mean=tok["mean"], output_tokens_stdev=tok["stdev"],
            response_length_mean=rlen["mean"], response_length_stdev=rlen["stdev"],
            response_length_cv=rlen["cv"],
        ))
    return aggregated


# ============================================
# Output
# ============================================

def save_single_responses(results: list[SingleResult], run_dir: Path):
    for r in results:
        slug = r.model_name.replace(" ", "_").replace(".", "-")
        d = run_dir / "responses" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{r.task_id}_run{r.run_number:02d}.md").write_text(
            f"# {r.task_title} – Run {r.run_number}\n"
            f"**Modell:** {r.model_name} (`{r.model_id}`) via {r.provider}\n"
            f"**Zeitpunkt:** {r.timestamp}\n"
            f"**Latenz:** {r.latency_seconds}s | "
            f"**Tokens:** {r.input_tokens} in / {r.output_tokens} out\n"
            f"**Fehler:** {r.error or '–'}\n\n---\n\n{r.response}\n",
            encoding="utf-8",
        )


def save_aggregated_csv(agg: list[AggregatedResult], run_dir: Path):
    fp = run_dir / "aggregated_stats.csv"
    fields = [
        "model_name", "model_id", "provider", "task_id", "task_title",
        "num_runs", "num_successful", "num_failed",
        "latency_mean", "latency_stdev", "latency_min", "latency_max",
        "output_tokens_mean", "output_tokens_stdev",
        "response_length_mean", "response_length_stdev", "response_length_cv",
    ]
    with open(fp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for a in agg:
            w.writerow({k: getattr(a, k, "") for k in fields})


def save_bewertung_template(agg: list[AggregatedResult], run_dir: Path):
    fp = run_dir / "bewertung_manual.csv"
    fields = [
        "model_name", "provider", "task_id", "task_title",
        "score_substanz", "score_praezision", "score_praxistauglichkeit",
        "score_urteilskraft", "score_sprachqualitaet", "score_gewichtet",
        "bewertungsnotiz",
    ]
    with open(fp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for a in agg:
            w.writerow({
                "model_name": a.model_name, "provider": a.provider,
                "task_id": a.task_id, "task_title": a.task_title,
                **{k: "" for k in fields[4:]},
            })


def save_consistency_report(results: list[SingleResult], run_dir: Path):
    groups: dict[tuple, list[SingleResult]] = {}
    for r in results:
        if not r.error:
            groups.setdefault((r.model_name, r.task_id), []).append(r)

    lines = [
        "# Konsistenz-Report",
        f"**{NUM_RUNS} Runs | Temp {TEMPERATURE} | "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}**",
        "", "CV: 🟢 <5% | 🟡 5–15% | 🔴 >15%", "",
        "| Modell | Provider | Aufgabe | Runs | Länge Ø | CV | Tokens Ø | Latenz Ø |",
        "|--------|----------|---------|------|---------|-----|----------|----------|",
    ]
    for (model, task_id), group in sorted(groups.items()):
        l = calc_stats([float(len(r.response)) for r in group])
        t = calc_stats([float(r.output_tokens) for r in group])
        lat = calc_stats([r.latency_seconds for r in group])
        m = "🟢" if l["cv"] < 5 else ("🟡" if l["cv"] < 15 else "🔴")
        lines.append(
            f"| {model} | {group[0].provider} | {task_id} | {len(group)} | "
            f"{l['mean']:.0f} | {m} {l['cv']}% | {t['mean']:.0f} | {lat['mean']:.1f}s |"
        )
    (run_dir / "consistency_report.md").write_text("\n".join(lines), encoding="utf-8")


def save_leaderboard(agg: list[AggregatedResult], run_dir: Path):
    models = sorted(set(a.model_name for a in agg))
    task_ids = sorted(set(a.task_id for a in agg))
    cols = " | ".join(t.split("_")[0] for t in task_ids)
    dashes = " | ".join("---" for _ in task_ids)

    lines = [
        "# Entscheider-Benchmark – Leaderboard", "",
        f"**{NUM_RUNS} Runs × {len(task_ids)} Aufgaben × {len(models)} Modelle** | "
        f"Temp {TEMPERATURE} | {datetime.now().strftime('%d.%m.%Y')}",
        "", f"| Rang | Modell | Provider | Ø Score | Klasse | {cols} |",
        f"|------|--------|----------|---------|--------|{dashes}|",
    ]

    # Provider-Zuordnung
    model_prov = {a.model_name: a.provider for a in agg}
    for m in models:
        scores = " | ".join("–" for _ in task_ids)
        lines.append(f"| – | {m} | {model_prov.get(m, '?')} | –/5,0 | – | {scores} |")

    lines.extend([
        "", "## Ergebnisklassen", "",
        "| Score | Klasse |", "|-------|--------|",
        "| 4,5–5,0 | Sparringspartner |",
        "| 3,5–4,4 | Qualifizierter Zuarbeiter |",
        "| 2,5–3,4 | Fleißiger Assistent |",
        "| 1,0–2,4 | Nicht empfehlenswert |",
    ])
    (run_dir / "leaderboard.md").write_text("\n".join(lines), encoding="utf-8")


def save_provider_summary(results: list[SingleResult], run_dir: Path):
    """Zeigt Kostenersparnis: Direkt-API vs. OpenRouter."""
    providers: dict[str, list[SingleResult]] = {}
    for r in results:
        if not r.error:
            providers.setdefault(r.provider, []).append(r)

    lines = [
        "# Provider-Übersicht", "",
        "| Provider | Modelle | Requests OK | Tokens gesamt | Ø Latenz |",
        "|----------|---------|-------------|---------------|----------|",
    ]
    for prov, group in sorted(providers.items()):
        models = len(set(r.model_name for r in group))
        tokens = sum(r.total_tokens for r in group)
        lat = mean([r.latency_seconds for r in group]) if group else 0
        lines.append(f"| {prov} | {models} | {len(group)} | {tokens:,} | {lat:.1f}s |")

    direct = sum(1 for r in results if not r.error and r.provider != "openrouter")
    routed = sum(1 for r in results if not r.error and r.provider == "openrouter")
    lines.extend(["", f"**Direkt-API:** {direct} Requests | **OpenRouter:** {routed} Requests"])

    (run_dir / "provider_summary.md").write_text("\n".join(lines), encoding="utf-8")


def save_run_meta(results: list[SingleResult], run_dir: Path, elapsed: float):
    ok = [r for r in results if not r.error]
    meta = {
        "benchmark": "Entscheider-Benchmark v2.0",
        "hid": "HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "num_runs": NUM_RUNS, "max_concurrent": MAX_CONCURRENT,
        },
        "providers_used": list(set(r.provider for r in ok)),
        "models": list(set(r.model_name for r in results)),
        "tasks": list(set(r.task_id for r in results)),
        "stats": {
            "total_requests": len(results), "successful": len(ok),
            "failed": len(results) - len(ok),
            "total_tokens": sum(r.total_tokens for r in ok),
            "wall_clock_seconds": round(elapsed, 1),
        },
    }
    (run_dir / "run_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ============================================
# Hauptprogramm
# ============================================

async def run_benchmark(models, tasks, num_runs, dry_run=False):
    total = len(models) * len(tasks) * num_runs

    # Provider-Zuordnung anzeigen
    direct_models = {n: c for n, c in models.items() if c["provider"] != "openrouter"}
    routed_models = {n: c for n, c in models.items() if c["provider"] == "openrouter"}

    log.info("=" * 60)
    log.info("ENTSCHEIDER-BENCHMARK v2.0 (Multi-Provider)")
    log.info(f"Modelle: {len(models)} | Aufgaben: {len(tasks)} | "
             f"Runs: {num_runs} | Total: {total} Requests")
    log.info(f"Direkt-API: {len(direct_models)} Modelle | "
             f"OpenRouter: {len(routed_models)} Modelle")
    log.info("=" * 60)

    if dry_run:
        log.info("\nDRY RUN\n")
        log.info("Direkt-API (Abo-Modelle):")
        for name, cfg in direct_models.items():
            key_ok = "✓" if KEY_MAP.get(PROVIDERS[cfg["provider"]]["key_env"]) else "✗ Key fehlt"
            log.info(f"  {name} → {cfg['provider']} ({cfg['model_id']}) [{key_ok}]")
        log.info("\nOpenRouter:")
        for name, cfg in routed_models.items():
            key_ok = "✓" if OPENROUTER_KEY else "✗ Key fehlt"
            log.info(f"  {name} → {cfg['model_id']} [{key_ok}]")
        log.info(f"\nAufgaben:")
        for tid, t in tasks.items():
            docs_ok = all((DOCS_DIR / d).exists() for d in t["docs"]) if t["docs"] else True
            log.info(f"  {tid}: {t['title']} [{'✓' if docs_ok else '⚠ Docs fehlen'}]")

        direct_requests = len(direct_models) * len(tasks) * num_runs
        routed_requests = len(routed_models) * len(tasks) * num_runs
        log.info(f"\nDirekt-API: {direct_requests} Requests (Abo, keine Zusatzkosten)")
        log.info(f"OpenRouter: {routed_requests} Requests (geschätzt {routed_requests * 0.08:.0f}–{routed_requests * 0.15:.0f} EUR)")
        return

    available_keys = [k for k, v in KEY_MAP.items() if v]
    if not available_keys:
        log.error("Keine API-Keys gesetzt. Bitte .env konfigurieren.")
        return

    run_dir = OUTPUT_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    for tid, t in tasks.items():
        for doc in t["docs"]:
            if not (DOCS_DIR / doc).exists():
                log.warning(f"⚠ Dokument fehlt: {DOCS_DIR / doc} ({tid})")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    all_results: list[SingleResult] = []
    wall_start = time.monotonic()

    async with aiohttp.ClientSession() as session:
        for run_num in range(1, num_runs + 1):
            log.info(f"\n{'═' * 50} RUN {run_num}/{num_runs} {'═' * 50}")

            for task_id, task in tasks.items():
                log.info(f"\n── {task['title']} ({task_id}) ──")
                coros = [
                    call_model(session, name, cfg, task_id, task, run_num, semaphore)
                    for name, cfg in models.items()
                ]
                all_results.extend(await asyncio.gather(*coros))

    elapsed = time.monotonic() - wall_start
    agg = aggregate_results(all_results)

    save_single_responses(all_results, run_dir)
    save_aggregated_csv(agg, run_dir)
    save_bewertung_template(agg, run_dir)
    save_consistency_report(all_results, run_dir)
    save_leaderboard(agg, run_dir)
    save_provider_summary(all_results, run_dir)
    save_run_meta(all_results, run_dir, elapsed)

    ok = [r for r in all_results if not r.error]
    fail = [r for r in all_results if r.error]
    log.info(f"\n{'═' * 60}")
    log.info(f"ABGESCHLOSSEN | {len(ok)}/{len(all_results)} OK | "
             f"{sum(r.total_tokens for r in ok):,} Tokens | {elapsed/60:.1f} min")
    log.info(f"Ergebnisse: {run_dir}")
    if fail:
        log.warning(f"\n{len(fail)} Fehler:")
        for r in fail:
            log.warning(f"  {r.model_name} [{r.provider}] × {r.task_title} [Run {r.run_number}]: {r.error}")


def main():
    p = argparse.ArgumentParser(description="Entscheider-Benchmark v2.0 (Multi-Provider)")
    p.add_argument("--runs", type=int, default=NUM_RUNS)
    p.add_argument("--models", type=str, default=None)
    p.add_argument("--tasks", type=str, default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    models = MODELS
    if args.models:
        sel = [m.strip() for m in args.models.split(",")]
        models = {k: v for k, v in MODELS.items() if k in sel}
        if not models:
            log.error(f"Verfügbar: {', '.join(MODELS.keys())}")
            return

    tasks = TASKS
    if args.tasks:
        sel = [t.strip() for t in args.tasks.split(",")]
        tasks = {k: v for k, v in TASKS.items() if any(k.startswith(s) for s in sel)}
        if not tasks:
            log.error(f"Verfügbar: {', '.join(TASKS.keys())}")
            return

    asyncio.run(run_benchmark(models, tasks, args.runs, args.dry_run))


if __name__ == "__main__":
    main()
