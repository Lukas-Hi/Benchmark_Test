#!/usr/bin/env python3
"""
Entscheider-Benchmark: Output-Funktionen
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo
"""

import csv
import sys
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean

from models import (
    SingleResult, AggregatedResult,
    NUM_RUNS, TEMPERATURE, MAX_TOKENS, MAX_CONCURRENT,
    calc_stats, hash_string,
)


def save_single_responses(results: list[SingleResult], run_dir: Path):
    """Save each individual response as a Markdown file."""
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


def save_prompt_archive(results: list[SingleResult], run_dir: Path, system_prompt: str):
    """Save the exact prompt sent for each request (audit trail)."""
    for r in results:
        slug = r.model_name.replace(" ", "_").replace(".", "-")
        d = run_dir / "responses" / slug
        d.mkdir(parents=True, exist_ok=True)

        sys_section = ""
        if r.use_system_prompt:
            sys_section = f"\n---\n## System-Prompt\n\n{system_prompt}\n"

        (d / f"{r.task_id}_run{r.run_number:02d}_prompt.md").write_text(
            f"# Prompt: {r.task_title} – Run {r.run_number}\n"
            f"**Modell:** {r.model_name} (`{r.model_id}`) via {r.provider}\n"
            f"**System-Prompt:** {'Ja' if r.use_system_prompt else 'Nein'}\n"
            f"**Zeitpunkt:** {r.timestamp}\n"
            f"**Prompt-Hash (SHA-256):** {hash_string(r.user_content)}\n"
            f"{sys_section}"
            f"\n---\n## User-Prompt\n\n{r.user_content}\n",
            encoding="utf-8",
        )


def save_raw_responses(results: list[SingleResult], run_dir: Path):
    """Save raw API JSON responses (audit trail)."""
    for r in results:
        if not r.raw_response:
            continue
        slug = r.model_name.replace(" ", "_").replace(".", "-")
        d = run_dir / "responses" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{r.task_id}_run{r.run_number:02d}_raw.json").write_text(
            r.raw_response, encoding="utf-8",
        )


def get_git_info() -> dict:
    """Capture git commit hash and dirty state."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL
        ).strip())
        return {"commit": commit, "dirty": dirty}
    except Exception:
        return {"commit": "unknown", "dirty": False}


def get_environment() -> dict:
    """Capture runtime environment for reproducibility."""
    try:
        packages = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().split("\n")
    except Exception:
        packages = []
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": packages,
    }


def save_aggregated_csv(agg: list[AggregatedResult], run_dir: Path):
    """Save aggregated statistics as semicolon-separated CSV."""
    fp = run_dir / "aggregated_stats.csv"
    fields = [
        "model_name", "model_id", "provider", "task_id", "task_title",
        "num_runs", "num_successful", "num_failed",
        "latency_mean", "latency_stdev", "latency_min", "latency_max",
        "input_tokens_mean", "input_tokens_stdev",
        "output_tokens_mean", "output_tokens_stdev",
        "response_length_mean", "response_length_stdev", "response_length_cv",
    ]
    with open(fp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for a in agg:
            w.writerow({k: getattr(a, k, "") for k in fields})


def save_bewertung_template(agg: list[AggregatedResult], run_dir: Path):
    """Create empty manual scoring template."""
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
    """Generate Markdown consistency report with CV indicators."""
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
    """Generate Markdown leaderboard template (scores filled manually)."""
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
    """Show cost efficiency: direct API vs. OpenRouter."""
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
        n_models = len(set(r.model_name for r in group))
        tokens = sum(r.total_tokens for r in group)
        lat = mean([r.latency_seconds for r in group]) if group else 0
        lines.append(f"| {prov} | {n_models} | {len(group)} | {tokens:,} | {lat:.1f}s |")

    direct = sum(1 for r in results if not r.error and r.provider != "openrouter")
    routed = sum(1 for r in results if not r.error and r.provider == "openrouter")
    lines.extend(["", f"**Direkt-API:** {direct} Requests | **OpenRouter:** {routed} Requests"])

    (run_dir / "provider_summary.md").write_text("\n".join(lines), encoding="utf-8")


def save_run_meta(
    results: list[SingleResult], run_dir: Path, elapsed: float,
    document_checksums: dict | None = None,
    prompt_hashes: dict | None = None,
):
    """Save run metadata as JSON with full audit trail."""
    ok = [r for r in results if not r.error]
    meta = {
        "benchmark": "Entscheider-Benchmark v3.0",
        "hid": "HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
            "num_runs": NUM_RUNS, "max_concurrent": MAX_CONCURRENT,
        },
        "providers_used": list(set(r.provider for r in ok)),
        "models": sorted(set(r.model_name for r in results)),
        "tasks": sorted(set(r.task_id for r in results)),
        "stats": {
            "total_requests": len(results), "successful": len(ok),
            "failed": len(results) - len(ok),
            "total_tokens": sum(r.total_tokens for r in ok),
            "wall_clock_seconds": round(elapsed, 1),
        },
        # Audit trail
        "git": get_git_info(),
        "environment": get_environment(),
    }
    if document_checksums:
        meta["document_checksums"] = document_checksums
    if prompt_hashes:
        meta["prompt_hashes"] = prompt_hashes
    (run_dir / "run_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
