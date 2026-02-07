#!/usr/bin/env python3
"""
Entscheider-Benchmark: Merge mehrerer Run-Verzeichnisse
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Liest responses/ aus mehreren run_*-Verzeichnissen, führt zusammen,
generiert neue Auswertung in einem merged_*-Verzeichnis.

Originalverzeichnisse bleiben unverändert.

Usage:
    python merge_runs.py results/run_A results/run_B results/run_C
    python merge_runs.py results/run_*  (Shell-Glob)
"""

import re
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Importiere Projektmodule
from models import (
    SingleResult, OUTPUT_DIR, TEMPERATURE, MAX_TOKENS,
    MAX_CONCURRENT, NUM_RUNS, log, aggregate_results,
)
from output import (
    save_aggregated_csv, save_bewertung_template,
    save_consistency_report, save_leaderboard,
    save_provider_summary, save_run_meta,
)


def parse_response_file(filepath: Path) -> SingleResult | None:
    """Parse a saved response Markdown file back into a SingleResult."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract metadata from header lines
    title_line = lines[0] if lines else ""
    model_line = lines[1] if len(lines) > 1 else ""
    time_line = lines[2] if len(lines) > 2 else ""
    stats_line = lines[3] if len(lines) > 3 else ""
    error_line = lines[4] if len(lines) > 4 else ""

    # Parse run number from title: "# Task Title – Run N"
    run_match = re.search(r"Run (\d+)", title_line)
    run_number = int(run_match.group(1)) if run_match else 0

    # Parse task title
    task_title = title_line.replace("# ", "").split(" – Run")[0].strip()

    # Parse model info: "**Modell:** Name (`id`) via provider"
    model_match = re.search(r"\*\*Modell:\*\* (.+?) \(`(.+?)`\) via (.+)", model_line)
    model_name = model_match.group(1) if model_match else "Unknown"
    model_id = model_match.group(2) if model_match else "unknown"
    provider = model_match.group(3).strip() if model_match else "unknown"

    # Parse timestamp
    time_match = re.search(r"\*\*Zeitpunkt:\*\* (.+)", time_line)
    timestamp = time_match.group(1).strip() if time_match else ""

    # Parse stats: "**Latenz:** 1.23s | **Tokens:** 500 in / 800 out"
    latency = 0.0
    input_tokens = 0
    output_tokens = 0
    lat_match = re.search(r"\*\*Latenz:\*\* ([\d.]+)s", stats_line)
    if lat_match:
        latency = float(lat_match.group(1))
    tok_match = re.search(r"\*\*Tokens:\*\* (\d+) in / (\d+) out", stats_line)
    if tok_match:
        input_tokens = int(tok_match.group(1))
        output_tokens = int(tok_match.group(2))

    # Parse error
    err_match = re.search(r"\*\*Fehler:\*\* (.+)", error_line)
    error = ""
    if err_match and err_match.group(1).strip() != "–":
        error = err_match.group(1).strip()

    # Response is everything after "---\n\n"
    response = ""
    sep_idx = text.find("---\n\n")
    if sep_idx >= 0:
        # Find second occurrence (first is header separator)
        second_sep = text.find("---\n\n", sep_idx + 5)
        if second_sep >= 0:
            response = text[second_sep + 5:].strip()
        else:
            response = text[sep_idx + 5:].strip()

    # Derive task_id from filename: "A1_Entscheidungsvorlage_N_run01.md"
    task_id = filepath.stem.rsplit("_run", 1)[0]

    return SingleResult(
        model_name=model_name, model_id=model_id, provider=provider,
        task_id=task_id, task_title=task_title,
        run_number=run_number, timestamp=timestamp, response=response,
        input_tokens=input_tokens, output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        latency_seconds=latency, error=error,
    )


def merge_runs(run_dirs: list[Path]) -> None:
    """Merge multiple run directories into a single merged output."""

    # Validate input directories
    valid_dirs = []
    for d in run_dirs:
        if not d.exists():
            log.warning(f"Verzeichnis nicht gefunden: {d}")
            continue
        if not (d / "responses").exists():
            log.warning(f"Kein responses/-Ordner in: {d}")
            continue
        valid_dirs.append(d)

    if not valid_dirs:
        log.error("Keine gültigen Run-Verzeichnisse gefunden.")
        return

    log.info(f"Merge {len(valid_dirs)} Run-Verzeichnisse:")
    for d in valid_dirs:
        log.info(f"  {d}")

    # Collect all response files
    all_results: list[SingleResult] = []
    duplicates = 0

    seen = set()  # (model_name, task_id, run_number)

    for run_dir in valid_dirs:
        responses_dir = run_dir / "responses"
        for model_dir in sorted(responses_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            for md_file in sorted(model_dir.glob("*.md")):
                result = parse_response_file(md_file)
                if result is None:
                    log.warning(f"Konnte nicht parsen: {md_file}")
                    continue
                key = (result.model_name, result.task_id, result.run_number)
                if key in seen:
                    duplicates += 1
                    log.debug(f"Duplikat übersprungen: {key}")
                    continue
                seen.add(key)
                all_results.append(result)

    if not all_results:
        log.error("Keine Ergebnisse gefunden.")
        return

    # Statistics
    models = sorted(set(r.model_name for r in all_results))
    tasks = sorted(set(r.task_id for r in all_results))
    ok = [r for r in all_results if not r.error]
    fail = [r for r in all_results if r.error]

    log.info(f"\nErgebnisse: {len(all_results)} ({len(ok)} OK, {len(fail)} Fehler)")
    if duplicates:
        log.info(f"Duplikate übersprungen: {duplicates}")
    log.info(f"Modelle: {len(models)} | Aufgaben: {len(tasks)}")

    # Create merged output directory
    merged_dir = OUTPUT_DIR / f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    merged_dir.mkdir(parents=True, exist_ok=True)

    # Copy all response files (preserving structure)
    for result in all_results:
        slug = result.model_name.replace(" ", "_").replace(".", "-")
        d = merged_dir / "responses" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{result.task_id}_run{result.run_number:02d}.md").write_text(
            f"# {result.task_title} – Run {result.run_number}\n"
            f"**Modell:** {result.model_name} (`{result.model_id}`) via {result.provider}\n"
            f"**Zeitpunkt:** {result.timestamp}\n"
            f"**Latenz:** {result.latency_seconds}s | "
            f"**Tokens:** {result.input_tokens} in / {result.output_tokens} out\n"
            f"**Fehler:** {result.error or '–'}\n\n---\n\n{result.response}\n",
            encoding="utf-8",
        )

    # Generate aggregated outputs
    agg = aggregate_results(all_results)
    elapsed = sum(r.latency_seconds for r in ok)

    save_aggregated_csv(agg, merged_dir)
    save_bewertung_template(agg, merged_dir)
    save_consistency_report(all_results, merged_dir)
    save_leaderboard(agg, merged_dir)
    save_provider_summary(all_results, merged_dir)

    # Save merge metadata
    source_metas = []
    for d in valid_dirs:
        meta_file = d / "run_meta.json"
        if meta_file.exists():
            source_metas.append(json.loads(meta_file.read_text(encoding="utf-8")))

    merge_meta = {
        "benchmark": "Entscheider-Benchmark v2.0",
        "hid": "HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46",
        "type": "merged",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_directories": [str(d) for d in valid_dirs],
        "source_run_count": len(valid_dirs),
        "config": {
            "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
        },
        "models": models,
        "tasks": tasks,
        "stats": {
            "total_results": len(all_results),
            "successful": len(ok),
            "failed": len(fail),
            "duplicates_skipped": duplicates,
            "total_tokens": sum(r.total_tokens for r in ok),
            "total_latency_seconds": round(elapsed, 1),
        },
    }
    (merged_dir / "run_meta.json").write_text(
        json.dumps(merge_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    log.info(f"\nMerge abgeschlossen: {merged_dir}")
    log.info(f"  {len(models)} Modelle × {len(tasks)} Aufgaben")
    log.info(f"  {len(ok)} erfolgreiche Antworten, {sum(r.total_tokens for r in ok):,} Tokens")


def main():
    if len(sys.argv) < 2:
        print("Usage: python merge_runs.py results/run_A results/run_B [...]")
        print("       python merge_runs.py results/run_*")
        sys.exit(1)

    run_dirs = [Path(p) for p in sys.argv[1:]]
    merge_runs(run_dirs)


if __name__ == "__main__":
    main()
