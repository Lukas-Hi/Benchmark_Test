# Entscheider-Benchmark

Strategischer KI-Benchmark für Geschäftsführer und Entscheider im DACH-Raum.
Misst, wie gut LLMs bei realen Führungsaufgaben performen – nicht bei Mathe oder Code.

**Owner:** Gerald T. Pögl – Hunter-ID MemoryBlock BG FlexCo
**HID:** HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46

## Was dieses Projekt ist

Ein Benchmark-Runner der 18 LLMs gegen 6 strategische Aufgaben testet, jeweils in zwei Varianten:
- **N (Normal-User):** Prompt wie ein GF ihn tippen würde – kein System-Prompt, keine Struktur
- **P (Power-User):** Optimierter Prompt mit System-Prompt, Guardrails, expliziten Anforderungen

Das Delta zwischen N und P pro Modell ist die eigentliche Messgröße: Wie viel holt Prompt-Kompetenz heraus?

## Projektstruktur

```
Benchmark_Test/
├── CLAUDE.md              ← Du bist hier. Lies das zuerst.
├── benchmark.py           ← Orchestrator: CLI, Main-Loop, call_model (222 Zeilen)
├── models.py              ← Datenklassen, Config, Hilfsfunktionen (158 Zeilen)
├── providers.py           ← 4 API-Caller, MODELS-Dict, Routing + Retry (329 Zeilen)
├── output.py              ← Alle save_*-Funktionen (181 Zeilen)
├── prompts.py             ← System-Prompt + 12 Aufgaben (313 Zeilen)
├── .env                   ← API-Keys (NICHT committen)
├── .env.example           ← Template für .env
├── requirements.txt       ← Python-Abhängigkeiten
├── .gitignore
├── README.md              ← Öffentliche Dokumentation für GitHub
├── docs/                  ← Interne Projektdokumentation
│   ├── planning.md        ← Entscheidungslog und Roadmap
│   ├── specs.md           ← Technische Spezifikation
│   ├── methodology.md     ← Wissenschaftliche Methodik
│   └── scoring_guide.md   ← Anleitung für manuelle Bewertung
├── documents/             ← Quelldokumente für Aufgaben A2, A5, A6
│   ├── bcg_ai_radar_2026.pdf
│   ├── statistik_austria_ict_2025.pdf
│   ├── microsoft_work_trend_index_2025.pdf
│   └── quartalsbericht.pdf
└── results/               ← Wird vom Runner erstellt (gitignored)
    └── run_YYYYMMDD_HHMMSS/
```

## Befehle

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Konfiguration prüfen (kein API-Verbrauch)
python benchmark.py --dry-run

# Testlauf: 1 Run, 2 Modelle, 1 Aufgabe
python benchmark.py --runs 1 --models "Claude Opus 4.6,GPT-5.2" --tasks A1

# Voller Durchlauf: 10 Runs, alle Modelle
python benchmark.py
```

## Multi-Provider-Architektur

Modelle mit Abo (Anthropic/OpenAI/Google) laufen über Direkt-APIs. Alle anderen über OpenRouter.
Automatischer Fallback: Kein Direkt-Key → OpenRouter. Konfiguration in `.env`.

| Provider | Modelle | Kosten |
|----------|---------|--------|
| Anthropic direkt | Claude Opus 4.6, 4.5, Sonnet 4.5, Haiku 4.5 | Abo |
| OpenAI direkt | GPT-5.2, 5.2 Pro, 5.2 Chat, 5.2-Codex, o1 | Abo |
| Google direkt | Gemini 3 Pro, 2.5 Pro, 2.5 Flash | Abo |
| OpenRouter | Grok 4.1, Mistral Large 3, DeepSeek V3.2/R1, Llama 3.3 | Pay-per-use |

## Konventionen

- **Sprache Code:** Englisch (Variablen, Kommentare, Docstrings)
- **Sprache Doku:** Deutsch (README, docs/, Prompts)
- **Python:** 3.11+, asyncio, type hints, kein Framework
- **Hunter-ID Header:** Jede Python-Datei bekommt Copyright-Header
- **Formatierung:** Keine auto-formatter konfiguriert, manuell konsistent halten
- **Commits:** Deutsch, imperativ, mit HID-Referenz wenn relevant

## WICHTIG

- `.env` enthält API-Keys → NIE committen
- `documents/` enthält urheberrechtlich geschützte PDFs → NIE committen
- `results/` wird lokal generiert → gitignored
- Bewertung ist manuell → `results/*/bewertung_manual.csv`
- Temperatur ist IMMER 0 für Reproduzierbarkeit

## Detaildokumentation

Für tiefere Informationen, lies die Dateien in `docs/`:
- Entscheidungen und Roadmap → `docs/planning.md`
- Technische Spezifikation → `docs/specs.md`
- Wissenschaftliche Methodik → `docs/methodology.md`
- Bewertungsanleitung → `docs/scoring_guide.md`
