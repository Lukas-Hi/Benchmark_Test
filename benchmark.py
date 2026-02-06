#!/usr/bin/env python3
"""
Entscheider-Benchmark: Strategische KI-Kompetenz im Praxistest
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Multi-Provider Benchmark-Runner (modular, v3.0)

Usage:
    python benchmark.py                  # Voller Durchlauf
    python benchmark.py --runs 3         # Nur 3 Durchläufe
    python benchmark.py --models "Claude Opus 4.6,GPT-5.2"
    python benchmark.py --tasks A1,A3
    python benchmark.py --dry-run        # Zeigt Konfiguration ohne API-Calls
"""

import time
import asyncio
import argparse
import aiohttp
from datetime import datetime, timezone

from models import (
    SingleResult, DOCS_DIR, OUTPUT_DIR, TEMPERATURE, MAX_TOKENS,
    MAX_CONCURRENT, REQUEST_DELAY, NUM_RUNS, OPENROUTER_KEY,
    log, build_user_content, aggregate_results,
)
from providers import (
    MODELS, PROVIDERS, KEY_MAP,
    resolve_provider, PROVIDER_CALLERS,
)
from prompts import TASKS
from output import (
    save_single_responses, save_aggregated_csv, save_bewertung_template,
    save_consistency_report, save_leaderboard, save_provider_summary,
    save_run_meta,
)


# ============================================
# Unified API-Call
# ============================================

async def call_model(
    session, model_name, model_cfg, task_id, task, run_number, semaphore,
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

    # FIX: REQUEST_DELAY outside semaphore to not block other slots
    await asyncio.sleep(REQUEST_DELAY)

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
        log.info("\nAufgaben:")
        for tid, t in tasks.items():
            docs_ok = all((DOCS_DIR / d).exists() for d in t["docs"]) if t["docs"] else True
            log.info(f"  {tid}: {t['title']} [{'✓' if docs_ok else '⚠ Docs fehlen'}]")

        direct_requests = len(direct_models) * len(tasks) * num_runs
        routed_requests = len(routed_models) * len(tasks) * num_runs
        log.info(f"\nDirekt-API: {direct_requests} Requests (Abo, keine Zusatzkosten)")
        log.info(f"OpenRouter: {routed_requests} Requests "
                 f"(geschätzt {routed_requests * 0.08:.0f}–{routed_requests * 0.15:.0f} EUR)")
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
            log.warning(f"  {r.model_name} [{r.provider}] × {r.task_title} "
                        f"[Run {r.run_number}]: {r.error}")


def main():
    p = argparse.ArgumentParser(description="Entscheider-Benchmark v3.0 (Multi-Provider, modular)")
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
