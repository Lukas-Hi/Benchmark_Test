#!/usr/bin/env python3
"""
Entscheider-Benchmark – LLM-as-a-Judge Evaluator
Copyright (c) 2026 Gerald T. Poegl – Hunter-ID MemoryBlock BG FlexCo
HID: HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46

Automated quality evaluation using cross-judge methodology:
Each model's responses are evaluated by a judge from a DIFFERENT provider
to avoid self-evaluation bias.

Usage:
    python evaluate.py results/run_YYYYMMDD_HHMMSS
    python evaluate.py results/run_YYYYMMDD_HHMMSS --judge "Claude Opus 4.6"
    python evaluate.py results/run_YYYYMMDD_HHMMSS --cross-judge
    python evaluate.py results/run_YYYYMMDD_HHMMSS --tasks A1,A3 --models "Claude Opus 4.6"
"""

import asyncio
import csv
import json
import re
import sys
import time
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from statistics import median

# Reuse existing infrastructure
from models import ANTHROPIC_KEY, OPENROUTER_KEY, GOOGLE_KEY, log
from providers import MODELS, PROVIDERS, KEY_MAP, call_anthropic, call_openrouter, call_google

# ============================================================
# Configuration
# ============================================================

JUDGE_MAX_TOKENS = 2048
JUDGE_TEMPERATURE = 0  # Deterministic judging

# Cross-judge mapping: which judge evaluates which provider's models
CROSS_JUDGE_MAP = {
    "anthropic": {
        "judge": "GPT-5.2",
        "judge_provider": "openrouter",
    },
    "openrouter": {
        "judge": "Claude Opus 4.6",
        "judge_provider": "anthropic",
    },
    "google": {
        "judge": "Claude Opus 4.6",
        "judge_provider": "anthropic",
    },
    "openai": {
        "judge": "Claude Opus 4.6",
        "judge_provider": "anthropic",
    },
}

# Fallback if cross-judge model is unavailable
DEFAULT_JUDGE = "Claude Opus 4.6"

# ============================================================
# Scoring Guide (embedded for judge prompt)
# ============================================================

SCORING_GUIDE = """Du bist ein strenger, unabhaengiger Gutachter fuer einen KI-Benchmark.
Du bewertest Antworten auf strategische Fuehrungsaufgaben nach 5 Kriterien.

BEWERTUNGSKRITERIEN (jeweils 1-5):

1. SUBSTANZ (Gewicht 25%):
   Wie breit und tief ist die Analyse? Werden nicht-offensichtliche Zusammenhaenge erkannt?
   1 = Generisch, wiederholt nur den Prompt
   2 = Nennt relevante Punkte, bleibt oberflaechlich
   3 = Solide Analyse, deckt Kernpunkte ab
   4 = Tiefgehend, bringt eigene Einordnung
   5 = Ueberraschend gut, nicht-offensichtliche Punkte

2. PRAEZISION (Gewicht 25%):
   Sind Aussagen faktisch korrekt? Wird zwischen Fakt und Einschaetzung getrennt?
   1 = Faktenfehler, Halluzinationen, Zahlen erfunden
   2 = Ueberwiegend korrekt, aber vage
   3 = Korrekt, aber keine klare Trennung Fakt/Einschaetzung
   4 = Korrekt, Fakt und Einschaetzung klar getrennt
   5 = Fehlerfrei, benennt eigene Unsicherheit

3. PRAXISTAUGLICHKEIT (Gewicht 20%):
   Kann ein Geschaeftsfuehrer damit etwas anfangen?
   1 = Theoretisch, abstrakt, nicht umsetzbar
   2 = Richtung stimmt, aber zu allgemein
   3 = Brauchbare Hinweise, aber nicht auf Kontext zugeschnitten
   4 = Konkret, auf den Kontext bezogen
   5 = Direkt umsetzbar, kennt Entscheider-Realitaet

4. URTEILSKRAFT (Gewicht 20%):
   Hat das Modell Rueckgrat? Traut es sich Widerspruch?
   1 = Reines People-Pleasing, bestaetigt alles
   2 = Erwaehnt Risiken pflichtgemaess, ohne Substanz
   3 = Benennt konkrete Schwaechen, bleibt diplomatisch
   4 = Klare Position, benennt Denkfehler
   5 = Widerspricht ungefragt, zeigt blinde Flecken

5. SPRACHQUALITAET DEUTSCH (Gewicht 10%):
   Klingt das wie ein erfahrener Berater oder wie Google Translate?
   1 = Uebersetzungsdeutsch, Buzzwords, unnatuerlich
   2 = Grammatisch korrekt, aber steif
   3 = Solides Deutsch, aber ohne Charakter
   4 = Natuerliches Geschaeftsdeutsch
   5 = Exzellent, DACH-tauglich, praegnant

SONDERREGELN:
- Antwort auf Englisch bei deutschem Prompt → Sprachqualitaet automatisch 1
- Halluzinierte Quellen → Praezision automatisch 1
- Selbstreferenz als KI ("Als KI-Modell...") → Sprachqualitaet minus 1
- Sprachqualitaet < 3 → Gesamtscore gedeckelt auf maximal 3.4

WICHTIG:
- Bewerte STRENG. Nutze die volle Skala von 1 bis 5.
- Vergib NICHT pauschal 3er und 4er. Differenziere!
- Die Begruendung muss KONKRET sein, mit Zitaten aus der Antwort.
- Du bewertest die ANTWORT, nicht das Modell. Du weisst nicht welches Modell das ist."""

JUDGE_PROMPT_TEMPLATE = """Bewerte die folgende Antwort auf eine strategische Fuehrungsaufgabe.

=== AUFGABE ===
{task_prompt}

=== ANTWORT ZU BEWERTEN ===
{response}

=== DEINE BEWERTUNG ===
Antworte NUR mit diesem exakten JSON-Format, NICHTS anderes:

{{
  "substanz": <1-5>,
  "praezision": <1-5>,
  "praxistauglichkeit": <1-5>,
  "urteilskraft": <1-5>,
  "sprachqualitaet": <1-5>,
  "begruendung": "<2-3 Saetze: groesste Staerke, groesste Schwaeche>"
}}"""


# ============================================================
# Median Run Finder
# ============================================================

def find_median_run(responses_dir: Path, model_dir: str, task_id: str) -> tuple[str, str] | None:
    """Find the median run (by response length) for a given model × task.
    Returns (response_text, prompt_text) or None if not found."""
    model_path = responses_dir / model_dir

    if not model_path.exists():
        return None

    # Collect all runs for this task
    runs = []
    for run_num in range(1, 11):
        response_file = model_path / f"{task_id}_run{run_num:02d}.md"
        if response_file.exists():
            text = response_file.read_text(encoding="utf-8")
            # Strip the header (first 5 lines = metadata)
            lines = text.split("\n")
            # Find the separator line "---" after metadata
            content_start = 0
            for i, line in enumerate(lines):
                if line.strip() == "---":
                    content_start = i + 1
                    break
            if content_start == 0:
                content_start = 5  # fallback: skip first 5 lines
            content = "\n".join(lines[content_start:]).strip()
            runs.append((run_num, len(content), content))

    if not runs:
        return None

    # Find median by length
    lengths = sorted([r[1] for r in runs])
    median_length = median(lengths)

    # Pick the run closest to the median
    closest = min(runs, key=lambda r: abs(r[1] - median_length))
    run_num = closest[0]

    # Read the prompt
    prompt_file = model_path / f"{task_id}_run{run_num:02d}_prompt.md"
    prompt_text = ""
    if prompt_file.exists():
        ptext = prompt_file.read_text(encoding="utf-8")
        # Extract just the user prompt section
        if "## User-Prompt" in ptext:
            prompt_text = ptext.split("## User-Prompt")[-1].strip()
        elif "## System-Prompt" in ptext:
            prompt_text = ptext.split("## System-Prompt")[-1].strip()
        else:
            prompt_text = ptext

    return closest[2], prompt_text


# ============================================================
# Judge API Call
# ============================================================

async def call_judge(session, judge_model: str, judge_provider: str,
                     evaluation_prompt: str) -> dict | None:
    """Call the judge model and parse its response."""
    judge_cfg = MODELS.get(judge_model)
    if not judge_cfg:
        log.error(f"Judge-Modell '{judge_model}' nicht in MODELS gefunden.")
        return None

    # Combine scoring guide + evaluation prompt as a single user message.
    # We use use_system=False because the existing provider callers hardcode
    # the benchmark's SYSTEM_PROMPT – we need the SCORING_GUIDE instead.
    full_prompt = SCORING_GUIDE + "\n\n" + evaluation_prompt

    if judge_provider == "anthropic":
        model_id = judge_cfg["model_id"]
        api_key = ANTHROPIC_KEY
        result, error = await call_anthropic(
            session, model_id, full_prompt, api_key, use_system=False
        )
    elif judge_provider == "openrouter":
        model_id = judge_cfg.get("openrouter_id", judge_cfg["model_id"])
        api_key = KEY_MAP.get("OPENROUTER_API_KEY", "")
        result, error = await call_openrouter(
            session, model_id, full_prompt, api_key, use_system=False
        )
    elif judge_provider == "google":
        model_id = judge_cfg["model_id"]
        api_key = GOOGLE_KEY
        result, error = await call_google(
            session, model_id, full_prompt, api_key, use_system=False
        )
    else:
        log.error(f"Unbekannter Judge-Provider: {judge_provider}")
        return None

    if error:
        log.error(f"Judge-Fehler: {error}")
        return None

    if not result:
        log.error("Judge hat keine Antwort geliefert.")
        return None

    # Parse JSON from response (providers return "response" key, not "text")
    response_text = result.get("response", "") or result.get("text", "")
    return parse_judge_response(response_text)


def parse_judge_response(text: str) -> dict | None:
    """Extract JSON scores from judge response."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*"substanz"[^{}]*\}', text, re.DOTALL)
    if not json_match:
        # Try broader match
        json_match = re.search(r'\{.*?\}', text, re.DOTALL)

    if not json_match:
        log.error(f"Kein JSON in Judge-Antwort gefunden: {text[:200]}")
        return None

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        log.error(f"JSON-Parse-Fehler: {e}\nText: {json_match.group()[:200]}")
        return None

    # Validate required fields
    required = ["substanz", "praezision", "praxistauglichkeit",
                "urteilskraft", "sprachqualitaet"]
    for field in required:
        if field not in data:
            log.error(f"Feld '{field}' fehlt in Judge-Antwort.")
            return None
        val = data[field]
        if not isinstance(val, (int, float)) or val < 1 or val > 5:
            log.error(f"Feld '{field}' hat ungueltigen Wert: {val}")
            return None
        data[field] = int(val)

    # Compute weighted score
    s = data
    weighted = (s["substanz"] * 0.25 + s["praezision"] * 0.25 +
                s["praxistauglichkeit"] * 0.20 + s["urteilskraft"] * 0.20 +
                s["sprachqualitaet"] * 0.10)

    # Apply cap: Sprachqualitaet < 3 → max 3.4
    if s["sprachqualitaet"] < 3:
        weighted = min(weighted, 3.4)

    data["score_gewichtet"] = round(weighted, 2)
    data["begruendung"] = data.get("begruendung", "")

    return data


# ============================================================
# Model-to-directory mapping
# ============================================================

def model_name_to_dir(model_name: str) -> str:
    """Convert model name to directory name (as created by benchmark.py)."""
    return model_name.replace(" ", "_").replace(".", "-")


def dir_to_model_name(dir_name: str) -> str:
    """Reverse: directory name back to model name."""
    # Try to find in MODELS
    for name in MODELS:
        if model_name_to_dir(name) == dir_name:
            return name
    # Fallback: reverse the transformation
    return dir_name.replace("_", " ").replace("-", ".")


# ============================================================
# Main Evaluation Loop
# ============================================================

async def evaluate_run(run_dir: Path, args):
    """Main evaluation function."""
    responses_dir = run_dir / "responses"
    if not responses_dir.exists():
        print(f"Fehler: {responses_dir} nicht gefunden.")
        sys.exit(1)

    # Discover models and tasks from directory structure
    model_dirs = sorted([d.name for d in responses_dir.iterdir() if d.is_dir()])
    if not model_dirs:
        print("Keine Modell-Verzeichnisse gefunden.")
        sys.exit(1)

    # Get task list from CSV
    csv_path = run_dir / "aggregated_stats.csv"
    all_tasks = set()
    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if float(row.get("num_successful", 0)) > 0:
                    all_tasks.add(row["task_id"])
    else:
        # Discover from files
        for md in model_dirs:
            for f in (responses_dir / md).glob("*_run01.md"):
                task_id = f.name.replace("_run01.md", "")
                all_tasks.add(task_id)

    tasks = sorted(all_tasks)

    # Filter by user args
    if args.tasks:
        task_filter = [t.strip() for t in args.tasks.split(",")]
        tasks = [t for t in tasks if any(f in t for f in task_filter)]

    if args.models:
        model_filter = [m.strip() for m in args.models.split(",")]
        model_dirs = [d for d in model_dirs if any(
            f in dir_to_model_name(d) for f in model_filter)]

    # Filter P-only if requested
    if args.power_only:
        tasks = [t for t in tasks if "_P" in t]

    print(f"\n{'='*60}")
    print(f"ENTSCHEIDER-BENCHMARK – LLM-as-a-Judge Evaluator")
    print(f"{'='*60}")
    print(f"Run: {run_dir.name}")
    print(f"Modelle: {len(model_dirs)} | Aufgaben: {len(tasks)}")
    print(f"Bewertungen: {len(model_dirs) * len(tasks)}")
    print(f"Cross-Judge: {'Ja' if args.cross_judge else 'Nein'}")
    if not args.cross_judge:
        print(f"Judge: {args.judge}")
    print(f"{'='*60}\n")

    # Collect evaluations
    evaluations = []
    total = len(model_dirs) * len(tasks)
    done = 0

    async with __import__('aiohttp').ClientSession() as session:
        for model_dir in model_dirs:
            model_name = dir_to_model_name(model_dir)
            model_cfg = MODELS.get(model_name, {})
            model_provider = model_cfg.get("provider", "unknown")

            # Determine judge
            if args.cross_judge:
                judge_info = CROSS_JUDGE_MAP.get(model_provider, {})
                judge_model = judge_info.get("judge", DEFAULT_JUDGE)
                judge_provider = judge_info.get("judge_provider", "anthropic")
            else:
                judge_model = args.judge
                judge_cfg = MODELS.get(judge_model, {})
                judge_provider = judge_cfg.get("provider", "anthropic")

            print(f"\n--- {model_name} (bewertet von {judge_model}) ---")

            for task_id in tasks:
                done += 1

                # Find median run
                result = find_median_run(responses_dir, model_dir, task_id)
                if not result:
                    print(f"  [{done}/{total}] {task_id}: Keine Runs gefunden, uebersprungen.")
                    continue

                response_text, prompt_text = result

                if not response_text.strip():
                    print(f"  [{done}/{total}] {task_id}: Leere Antwort, uebersprungen.")
                    continue

                # Build evaluation prompt
                eval_prompt = JUDGE_PROMPT_TEMPLATE.format(
                    task_prompt=prompt_text[:3000],  # Truncate long prompts
                    response=response_text[:8000],   # Truncate very long responses
                )

                # Call judge
                print(f"  [{done}/{total}] {task_id}...", end=" ", flush=True)

                scores = await call_judge(session, judge_model, judge_provider,
                                          eval_prompt)

                if scores:
                    evaluation = {
                        "model_name": model_name,
                        "provider": model_provider,
                        "task_id": task_id,
                        "judge_model": judge_model,
                        "judge_provider": judge_provider,
                        "score_substanz": scores["substanz"],
                        "score_praezision": scores["praezision"],
                        "score_praxistauglichkeit": scores["praxistauglichkeit"],
                        "score_urteilskraft": scores["urteilskraft"],
                        "score_sprachqualitaet": scores["sprachqualitaet"],
                        "score_gewichtet": scores["score_gewichtet"],
                        "bewertungsnotiz": scores.get("begruendung", ""),
                    }
                    evaluations.append(evaluation)
                    w = scores["score_gewichtet"]
                    print(f"Score: {w:.2f} "
                          f"(S:{scores['substanz']} P:{scores['praezision']} "
                          f"Px:{scores['praxistauglichkeit']} U:{scores['urteilskraft']} "
                          f"Sp:{scores['sprachqualitaet']})")
                else:
                    print("FEHLER (kein Score)")

                # Rate limiting
                await asyncio.sleep(2.0 + random.uniform(0.5, 1.5))

    # Save results
    if evaluations:
        save_evaluations(run_dir, evaluations)
        print_summary(evaluations)
    else:
        print("\nKeine Bewertungen erzeugt.")


# ============================================================
# Output
# ============================================================

def save_evaluations(run_dir: Path, evaluations: list[dict]):
    """Save evaluations to bewertung_auto.csv."""
    output_path = run_dir / "bewertung_auto.csv"

    fieldnames = [
        "model_name", "provider", "task_id", "judge_model", "judge_provider",
        "score_substanz", "score_praezision", "score_praxistauglichkeit",
        "score_urteilskraft", "score_sprachqualitaet", "score_gewichtet",
        "bewertungsnotiz",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(evaluations)

    print(f"\nBewertungen gespeichert: {output_path}")
    print(f"  {len(evaluations)} Bewertungen")


def print_summary(evaluations: list[dict]):
    """Print a summary of the evaluation results."""
    print(f"\n{'='*60}")
    print("BEWERTUNGS-ZUSAMMENFASSUNG")
    print(f"{'='*60}\n")

    # Group by model
    by_model = {}
    for e in evaluations:
        model = e["model_name"]
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(e)

    # Print ranking
    rankings = []
    for model, evals in by_model.items():
        avg_score = sum(e["score_gewichtet"] for e in evals) / len(evals)
        avg_s = sum(e["score_substanz"] for e in evals) / len(evals)
        avg_p = sum(e["score_praezision"] for e in evals) / len(evals)
        avg_px = sum(e["score_praxistauglichkeit"] for e in evals) / len(evals)
        avg_u = sum(e["score_urteilskraft"] for e in evals) / len(evals)
        avg_sp = sum(e["score_sprachqualitaet"] for e in evals) / len(evals)
        rankings.append((model, avg_score, avg_s, avg_p, avg_px, avg_u, avg_sp,
                         len(evals)))

    rankings.sort(key=lambda x: x[1], reverse=True)

    # Classification
    def classify(score):
        if score >= 4.5:
            return "Sparringspartner"
        elif score >= 3.5:
            return "Qualifizierter Zuarbeiter"
        elif score >= 2.5:
            return "Fleissiger Assistent"
        else:
            return "Nicht empfehlenswert"

    print(f"{'Modell':<25} {'Score':>6} {'S':>4} {'P':>4} {'Px':>4} {'U':>4} {'Sp':>4}  Klasse")
    print("-" * 80)
    for r in rankings:
        model, score, s, p, px, u, sp, n = r
        cls = classify(score)
        print(f"{model:<25} {score:>6.2f} {s:>4.1f} {p:>4.1f} {px:>4.1f} {u:>4.1f} {sp:>4.1f}  {cls}")

    # Score distribution warning
    all_scores = [e["score_gewichtet"] for e in evaluations]
    min_s = min(all_scores)
    max_s = max(all_scores)
    if max_s - min_s < 1.0:
        print(f"\n[WARNUNG] Geringe Score-Spreizung ({min_s:.2f}-{max_s:.2f}). "
              f"Judge differenziert moeglicherweise nicht genug.")

    # Judge info
    judges_used = set((e["judge_model"], e["judge_provider"]) for e in evaluations)
    print(f"\nJudge(s): {', '.join(f'{j[0]} ({j[1]})' for j in judges_used)}")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Entscheider-Benchmark: LLM-as-a-Judge Evaluator"
    )
    parser.add_argument("run_dir", type=str,
                        help="Pfad zum Run-Verzeichnis")
    parser.add_argument("--judge", type=str, default=DEFAULT_JUDGE,
                        help=f"Judge-Modell (default: {DEFAULT_JUDGE})")
    parser.add_argument("--cross-judge", action="store_true",
                        help="Cross-Judge: Jeder Provider wird von einem anderen bewertet")
    parser.add_argument("--tasks", type=str, default=None,
                        help="Nur bestimmte Tasks bewerten (z.B. 'A1,A3')")
    parser.add_argument("--models", type=str, default=None,
                        help="Nur bestimmte Modelle bewerten")
    parser.add_argument("--power-only", action="store_true",
                        help="Nur Power-Varianten (P) bewerten")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Fehler: {run_dir} existiert nicht.")
        sys.exit(1)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(evaluate_run(run_dir, args))


if __name__ == "__main__":
    main()
