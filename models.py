#!/usr/bin/env python3
"""
Entscheider-Benchmark: Datenmodelle, Konfiguration, Hilfsfunktionen
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from statistics import mean, stdev
from dotenv import load_dotenv

load_dotenv()

# ============================================
# Konfiguration (aus .env)
# ============================================

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
    input_tokens_mean: float = 0.0
    input_tokens_stdev: float = 0.0
    output_tokens_mean: float = 0.0
    output_tokens_stdev: float = 0.0
    response_length_mean: float = 0.0
    response_length_stdev: float = 0.0
    response_length_cv: float = 0.0


# ============================================
# Hilfsfunktionen
# ============================================

def load_document(filename: str) -> str:
    """Load a document from DOCS_DIR. Supports .pdf and text files."""
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
            return "[pdfplumber nicht installiert]"
    return filepath.read_text(encoding="utf-8")


def build_user_content(task: dict) -> str:
    """Build the user message: embedded documents + prompt."""
    parts = []
    for doc_file in task["docs"]:
        doc_text = load_document(doc_file)
        parts.append(f"--- DOKUMENT: {doc_file} ---\n\n{doc_text}\n\n--- ENDE DOKUMENT ---")
    parts.append(task["prompt"])
    return "\n\n".join(parts)


def calc_stats(values: list[float]) -> dict:
    """Calculate mean, stdev, min, max, CV for a list of values."""
    if not values:
        return {"mean": 0, "stdev": 0, "min": 0, "max": 0, "cv": 0}
    m = mean(values)
    s = stdev(values) if len(values) > 1 else 0
    cv = (s / m * 100) if m > 0 else 0
    return {
        "mean": round(m, 2), "stdev": round(s, 2),
        "min": round(min(values), 2), "max": round(max(values), 2),
        "cv": round(cv, 1),
    }


def aggregate_results(results: list[SingleResult]) -> list[AggregatedResult]:
    """Aggregate multiple runs into per-model-per-task statistics."""
    groups: dict[tuple, list[SingleResult]] = {}
    for r in results:
        groups.setdefault((r.model_name, r.task_id), []).append(r)

    aggregated = []
    for (model_name, task_id), group in sorted(groups.items()):
        ok = [r for r in group if not r.error]
        lat = calc_stats([r.latency_seconds for r in ok])
        itok = calc_stats([float(r.input_tokens) for r in ok])
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
            input_tokens_mean=itok["mean"], input_tokens_stdev=itok["stdev"],
            output_tokens_mean=tok["mean"], output_tokens_stdev=tok["stdev"],
            response_length_mean=rlen["mean"], response_length_stdev=rlen["stdev"],
            response_length_cv=rlen["cv"],
        ))
    return aggregated
