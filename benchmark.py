#!/usr/bin/env python3
"""
Entscheider-Benchmark: Strategische KI-Kompetenz im Praxistest
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Multi-Provider Benchmark-Runner (modular, v3.0)

Usage:
    python benchmark.py                          # Voller Durchlauf
    python benchmark.py --runs 3                 # Nur 3 Durchläufe
    python benchmark.py --models "Claude Opus 4.6,GPT-5.2"
    python benchmark.py --tasks A1,A3
    python benchmark.py --providers anthropic,openai  # Nur Abo-Modelle
    python benchmark.py --providers google        # Google separat nachholen
    python benchmark.py --dry-run                 # Zeigt Konfiguration ohne API-Calls
"""

import time
import random
import logging
import asyncio
import argparse
import aiohttp
from datetime import datetime, timezone

from models import (
    SingleResult, DOCS_DIR, OUTPUT_DIR, TEMPERATURE, MAX_TOKENS,
    MAX_CONCURRENT, REQUEST_DELAY, NUM_RUNS, OPENROUTER_KEY,
    log, build_user_content, aggregate_results,
    hash_documents, hash_string,
)
from providers import (
    MODELS, PROVIDERS, KEY_MAP,
    resolve_provider, PROVIDER_CALLERS,
    PROVIDER_CONCURRENCY, PROVIDER_DELAY,
)
from prompts import TASKS, SYSTEM_PROMPT
from output import (
    save_single_responses, save_prompt_archive, save_raw_responses,
    save_aggregated_csv, save_bewertung_template,
    save_consistency_report, save_leaderboard, save_provider_summary,
    save_run_meta,
)


# ============================================
# Unified API-Call
# ============================================

async def call_model(
    session, model_name, model_cfg, task_id, task, run_number,
    global_semaphore, provider_semaphores,
) -> SingleResult:
    """Send a benchmark request to the appropriate provider."""

    provider, url, api_key = resolve_provider(model_cfg)
    model_id = model_cfg["openrouter_id"] if provider == "openrouter" else model_cfg["model_id"]
    timestamp = datetime.now(timezone.utc).isoformat()
    user_content = build_user_content(task)
    use_system = task.get("use_system_prompt", True)

    result = SingleResult(
        model_name=model_name, model_id=model_id, provider=provider,
        task_id=task_id, task_title=task["title"],
        run_number=run_number, timestamp=timestamp, response="",
        user_content=user_content, use_system_prompt=use_system,
    )

    if not api_key:
        result.error = f"Kein API-Key für Provider '{provider}'"
        log.error(f"✗ {model_name}: {result.error}")
        return result

    prov_sem = provider_semaphores.get(provider, global_semaphore)

    async with global_semaphore:
        async with prov_sem:
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
                    result.raw_response = data.get("raw_json", "")
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

    # Provider-specific delay with jitter (outside semaphores)
    base_delay = PROVIDER_DELAY.get(provider, REQUEST_DELAY)
    jitter = base_delay + random.uniform(0, base_delay * 0.5)
    await asyncio.sleep(jitter)

    return result


# ============================================
# Hauptprogramm
# ============================================

async def run_benchmark(models, tasks, num_runs, dry_run=False):
    total = len(models) * len(tasks) * num_runs

    direct_models = {n: c for n, c in models.items() if c["provider"] != "openrouter"}
    routed_models = {n: c for n, c in models.items() if c["provider"] == "openrouter"}

    log.info("=" * 60)
    log.info("ENTSCHEIDER-BENCHMARK v3.0 (Multi-Provider, modular)")
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

        # Token-Schätzung pro Aufgabe
        log.info("\nAufgaben + Token-Schätzung:")
        total_input_tokens_est = 0
        for tid, t in tasks.items():
            docs_ok = all((DOCS_DIR / d).exists() for d in t["docs"]) if t["docs"] else True
            content = build_user_content(t)
            token_est = int(len(content.split()) * 1.3)  # grobe Schätzung
            total_input_tokens_est += token_est
            # Kontextfenster-Warnung
            warn = ""
            if token_est > 100_000:
                warn = " ⚠ >100k Tokens – Llama 3.3/Flash evtl. zu groß"
            elif token_est > 50_000:
                warn = " ⚠ >50k Tokens – große Kontextlast"
            log.info(f"  {tid}: {t['title']} [{'✓' if docs_ok else '⚠ Docs fehlen'}] "
                     f"~{token_est:,} Input-Tokens{warn}")

        direct_requests = len(direct_models) * len(tasks) * num_runs
        routed_requests = len(routed_models) * len(tasks) * num_runs
        total_requests = direct_requests + routed_requests

        # Geschätzte Gesamtkosten (Input + Output)
        est_output_tokens = 800  # ~600 Wörter Durchschnitt
        total_tokens_per_run = sum(
            int(len(build_user_content(t).split()) * 1.3) + est_output_tokens
            for t in tasks.values()
        )
        total_tokens_all = total_tokens_per_run * len(models) * num_runs

        log.info(f"\nToken-Budget (geschätzt):")
        log.info(f"  Input pro Durchlauf (alle Aufgaben): ~{total_input_tokens_est:,} Tokens")
        log.info(f"  Total (alle Modelle × Runs): ~{total_tokens_all:,} Tokens")
        log.info(f"\nDirekt-API: {direct_requests} Requests (Abo, keine Zusatzkosten)")
        log.info(f"OpenRouter: {routed_requests} Requests")
        log.info(f"  Geschätzte OpenRouter-Kosten: "
                 f"{routed_requests * total_tokens_per_run * 0.000003:.0f}–"
                 f"{routed_requests * total_tokens_per_run * 0.000010:.0f} EUR")
        return

    available_keys = [k for k, v in KEY_MAP.items() if v]
    if not available_keys:
        log.error("Keine API-Keys gesetzt. Bitte .env konfigurieren.")
        return

    run_dir = OUTPUT_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Execution log to file (audit trail)
    file_handler = logging.FileHandler(run_dir / "execution.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    ))
    log.addHandler(file_handler)

    # Document checksums (audit trail)
    all_doc_hashes: dict[str, str] = {}
    for tid, t in tasks.items():
        all_doc_hashes.update(hash_documents(t))
    if all_doc_hashes:
        log.info(f"\nDocument-Checksummen (SHA-256):")
        for doc, h in all_doc_hashes.items():
            log.info(f"  {doc}: {h[:16]}...")

    # Prompt hashes (audit trail)
    prompt_hashes = {"system_prompt": hash_string(SYSTEM_PROMPT)}
    for tid, t in tasks.items():
        content = build_user_content(t)
        prompt_hashes[tid] = hash_string(content)

    for tid, t in tasks.items():
        for doc in t["docs"]:
            if not (DOCS_DIR / doc).exists():
                log.warning(f"⚠ Dokument fehlt: {DOCS_DIR / doc} ({tid})")

    global_semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    provider_semaphores = {
        prov: asyncio.Semaphore(limit)
        for prov, limit in PROVIDER_CONCURRENCY.items()
    }
    all_results: list[SingleResult] = []
    wall_start = time.monotonic()

    log.info(f"\nRate-Limiting: Sequentiell (1 Request nach dem anderen)")
    for prov in PROVIDER_CONCURRENCY:
        delay = PROVIDER_DELAY.get(prov, REQUEST_DELAY)
        log.info(f"  {prov}: {delay}s+ delay (mit Jitter)")

    async with aiohttp.ClientSession() as session:
        for run_num in range(1, num_runs + 1):
            log.info(f"\n{'═' * 50} RUN {run_num}/{num_runs} {'═' * 50}")

            for task_id, task in tasks.items():
                log.info(f"\n── {task['title']} ({task_id}) ──")
                # Sequential execution: one request at a time
                for name, cfg in models.items():
                    result = await call_model(
                        session, name, cfg, task_id, task, run_num,
                        global_semaphore, provider_semaphores,
                    )
                    all_results.append(result)

    elapsed = time.monotonic() - wall_start
    agg = aggregate_results(all_results)

    save_single_responses(all_results, run_dir)
    save_prompt_archive(all_results, run_dir, SYSTEM_PROMPT)
    save_raw_responses(all_results, run_dir)
    save_aggregated_csv(agg, run_dir)
    save_bewertung_template(agg, run_dir)
    save_consistency_report(all_results, run_dir)
    save_leaderboard(agg, run_dir)
    save_provider_summary(all_results, run_dir)
    save_run_meta(all_results, run_dir, elapsed, all_doc_hashes, prompt_hashes)

    ok = [r for r in all_results if not r.error]
    fail = [r for r in all_results if r.error]
    log.info(f"\n{'═' * 60}")
    log.info(f"ABGESCHLOSSEN | {len(ok)}/{len(all_results)} OK | "
             f"{sum(r.total_tokens for r in ok):,} Tokens | {elapsed/60:.1f} min")
    log.info(f"Ergebnisse: {run_dir}")
    if fail:
        log.warning(f"\n{len(fail)} Fehler:")
        for r in fail:
            log.warning(f"  {r.model_name} [{r.provider}] × {r.task_title} "
                        f"[Run {r.run_number}]: {r.error}")

    # Cleanup file handler
    log.removeHandler(file_handler)
    file_handler.close()


def main():
    p = argparse.ArgumentParser(description="Entscheider-Benchmark v3.0 (Multi-Provider, modular)")
    p.add_argument("--runs", type=int, default=NUM_RUNS)
    p.add_argument("--models", type=str, default=None)
    p.add_argument("--tasks", type=str, default=None)
    p.add_argument("--providers", type=str, default=None,
                   help="Provider-Filter: anthropic,openai,google,openrouter")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    models = MODELS
    if args.providers:
        sel = [p.strip().lower() for p in args.providers.split(",")]
        models = {k: v for k, v in models.items() if v["provider"] in sel}
        if not models:
            log.error(f"Keine Modelle für Provider: {args.providers}")
            log.error(f"Verfügbare Provider: anthropic, openai, google, openrouter")
            return
        log.info(f"Provider-Filter: {', '.join(sel)} → {len(models)} Modelle")

    if args.models:
        sel = [m.strip() for m in args.models.split(",")]
        models = {k: v for k, v in models.items() if k in sel}
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
