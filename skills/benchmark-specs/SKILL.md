---
name: benchmark-specs
description: >
  Project scaffolding and specification system for the Entscheider-Benchmark.
  Triggers: Any request to set up, document, plan, or specify benchmark infrastructure.
  Keywords: "benchmark", "specs", "planning", "CLAUDE.md", "Projektstruktur",
  "Spezifikation", "Testlauf", "Logik-Check", "Refactoring".
  Also triggers when Claude Code needs to understand the benchmark project structure,
  current phase, or next steps. Read this before modifying any benchmark file.
---

# Benchmark-Specs: Projektsteuerung für den Entscheider-Benchmark

## Zweck

Steuert die Arbeit am Entscheider-Benchmark-Projekt. Definiert Projektstruktur, aktuelle Phase, Konventionen und Qualitätsgates.

## Projektstruktur

```
Benchmark_Test/
├── CLAUDE.md              <- Einstiegspunkt
├── benchmark.py           <- Monolith (810Z) -> wird refactored
├── prompts.py             <- System-Prompt + 12 Aufgaben (6xN, 6xP)
├── .env / .env.example
├── requirements.txt
├── docs/
│   ├── planning.md        <- LEITDOKUMENT: Phasen, Status, Entscheidungen
│   ├── specs.md           <- Technische Spezifikation
│   ├── methodology.md     <- Wissenschaftliche Methodik
│   └── scoring_guide.md   <- Bewertungsanleitung
├── documents/             <- PDFs fuer Aufgaben
└── results/               <- Generiert (gitignored)
```

## Arbeitsablauf

Vor jeder Aenderung:
1. `docs/planning.md` lesen -> aktuelle Phase und offene Tasks
2. Betroffene Datei(en) identifizieren
3. Nur betroffene Dateien lesen, nicht alles

Nach jeder Aenderung:
1. `python -m py_compile <datei>`
2. `docs/planning.md` aktualisieren
3. Bei Entscheidungen: Entscheidungslog ergaenzen

## Phasen

| Phase | Status | Schlüsseldateien |
|-------|--------|------------------|
| 1. Infrastruktur | DONE | Alle |
| 2. Quelldokumente | DONE | documents/, generate_extracts.py |
| 3. Testdurchlauf | TODO | benchmark.py, .env |
| 4. Voller Durchlauf | TODO | benchmark.py |
| 5. Bewertung | TODO | results/bewertung_manual.csv |
| 6. Veroeffentlichung | TODO | README.md |

## Modulstruktur (Refactoring abgeschlossen)

| Modul | Verantwortung | Zeilen |
|-------|--------------|--------|
| benchmark.py | CLI, Orchestrator, call_model | 222 |
| models.py | Dataclasses, Config, Hilfsfunktionen | 158 |
| providers.py | 4 API-Caller, MODELS-Dict, Routing + Retry | 329 |
| prompts.py | System-Prompt + 12 Aufgaben (6×N, 6×P) | 313 |
| output.py | Alle save_*-Funktionen | 181 |
| generate_extracts.py | PDF-Extraktion fuer A5-Dokumente | ~80 |

Fixes erledigt: REQUEST_DELAY aus Semaphore verschoben, 1× Retry bei HTTP 429.

## Konventionen

Code: Englisch. Doku: Deutsch. Python 3.11+, asyncio, type hints.
CSV: Semikolon. Temperatur: 0. Hunter-ID Header in jeder .py-Datei.

## Verwandte Skills

- **benchmark-evaluator**: Neutraler Methodiker & Evaluator. Zwei Modi:
  - DESIGN: Testdesign-Beratung, Methodik-Kritik, Scoring-Validierung
  - EVAL: LLM-Output-Bewertung gegen Scoring-Rubric
  - Liest: `references/scoring_criteria.md`, `references/methodology_references.md`

## Referenz

Bewertungskriterien -> `references/scoring_criteria.md`
