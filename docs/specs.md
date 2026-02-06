# Technische Spezifikation: Entscheider-Benchmark
**HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46**
Stand: 6. Februar 2026

---

## 1. Systemübersicht

### 1.1 Architektur

```
┌─────────────────────────────────────────────────┐
│                  benchmark.py                    │
│              (Async Orchestrator)                │
├──────────┬──────────┬──────────┬────────────────┤
│ Anthropic│  OpenAI  │  Google  │   OpenRouter    │
│  API     │  API     │  Gemini  │   API           │
│          │          │  API     │                  │
│ Claude   │ GPT-5.2  │ Gemini   │ Grok, DeepSeek  │
│ Opus/    │ Pro/Chat │ 3 Pro/   │ Mistral, Llama  │
│ Sonnet/  │ Codex/o1 │ 2.5 Pro/ │                  │
│ Haiku    │          │ Flash    │                  │
└──────────┴──────────┴──────────┴────────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────┐
              │  prompts.py     │
              │  12 Aufgaben    │
              │  (6×N + 6×P)   │
              │  + System-Prompt│
              └─────────────────┘
                         │
                         ▼
              ┌─────────────────┐
              │  results/       │
              │  run_YYYYMMDD/  │
              └─────────────────┘
```

### 1.2 Datenfluss

1. `benchmark.py` liest Aufgaben aus `prompts.py`
2. Pro Aufgabe: prüft `use_system_prompt` Flag
3. Falls Dokumente referenziert: lädt aus `documents/` (PDF → Text via pdfplumber)
4. Routet an Provider basierend auf Modell-Konfiguration (Direkt-API oder OpenRouter-Fallback)
5. Speichert jede Einzelantwort als Markdown in `results/run_*/responses/`
6. Aggregiert Statistiken nach Abschluss aller Runs

---

## 2. Provider-Routing

### 2.1 Entscheidungslogik

```
Für jedes Modell:
  1. Prüfe Provider-Feld (anthropic/openai/google/openrouter)
  2. Prüfe ob API-Key für diesen Provider in .env gesetzt ist
  3. Wenn Key vorhanden → Direkt-API
  4. Wenn Key fehlt UND OpenRouter-Key vorhanden → Fallback auf OpenRouter
  5. Wenn kein Key → Fehler loggen, nächstes Modell
```

### 2.2 API-Endpunkte

| Provider | Endpunkt | Auth-Methode |
|----------|----------|--------------|
| Anthropic | `https://api.anthropic.com/v1/messages` | `x-api-key` Header |
| OpenAI | `https://api.openai.com/v1/chat/completions` | `Authorization: Bearer` |
| Google | `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | `?key=` Query-Param |
| OpenRouter | `https://openrouter.ai/api/v1/chat/completions` | `Authorization: Bearer` |

### 2.3 System-Prompt-Handling

| Variante | System-Prompt | Format |
|----------|---------------|--------|
| **N (Normal)** | KEINER | Nur User-Message |
| **P (Power)** | Vollständig | Provider-spezifisch |

Provider-spezifische Implementierung:
- **Anthropic:** `system`-Feld im Request-Body (nur wenn P)
- **OpenAI/OpenRouter:** `messages[0].role = "system"` (nur wenn P)
- **Google:** `systemInstruction`-Objekt (nur wenn P)

---

## 3. Modellkatalog

### 3.1 Vollständige Modell-IDs

| Display-Name | Provider | Direkt-ID | OpenRouter-ID |
|-------------|----------|-----------|---------------|
| Claude Opus 4.6 | anthropic | `claude-opus-4-6` | `anthropic/claude-opus-4-6` |
| Claude Opus 4.5 | anthropic | `claude-opus-4-5` | `anthropic/claude-opus-4-5` |
| Claude Sonnet 4.5 | anthropic | `claude-sonnet-4-5-20250929` | `anthropic/claude-sonnet-4-5` |
| Claude Haiku 4.5 | anthropic | `claude-haiku-4-5-20251001` | `anthropic/claude-haiku-4-5` |
| GPT-5.2 | openai | `gpt-5.2` | `openai/gpt-5.2` |
| GPT-5.2 Pro | openai | `gpt-5.2-pro` | `openai/gpt-5.2-pro` |
| GPT-5.2 Chat | openai | `gpt-5.2-chat` | `openai/gpt-5.2-chat` |
| GPT-5.2-Codex | openai | `gpt-5.2-codex` | `openai/gpt-5.2-codex` |
| o1 | openai | `o1` | `openai/o1` |
| Gemini 3 Pro | google | `gemini-3-pro` | `google/gemini-3-pro` |
| Gemini 2.5 Pro | google | `gemini-2.5-pro` | `google/gemini-2.5-pro` |
| Gemini 2.5 Flash | google | `gemini-2.5-flash` | `google/gemini-2.5-flash` |
| Grok 4.1 | openrouter | `x-ai/grok-4.1` | `x-ai/grok-4.1` |
| Mistral Large 3 | openrouter | `mistralai/mistral-large-3` | `mistralai/mistral-large-3` |
| DeepSeek V3.2 | openrouter | `deepseek/deepseek-v3.2` | `deepseek/deepseek-v3.2` |
| DeepSeek R1 | openrouter | `deepseek/deepseek-r1` | `deepseek/deepseek-r1` |
| Llama 3.3 70B | openrouter | `meta-llama/llama-3.3-70b-instruct` | `meta-llama/llama-3.3-70b-instruct` |

**Nicht enthalten (Begründung):**
- GPT-5.3-Codex: API noch nicht über OpenRouter, wird manuell über VS Code nachgetestet
- Claude 3.5: Veraltet, nicht mehr primäres Modell
- Gemini Ultra: Nicht öffentlich über API verfügbar

---

## 4. Aufgaben-Spezifikation

### 4.1 Task-Dictionary-Struktur

```python
{
    "A1_Entscheidungsvorlage_N": {
        "title": str,           # Anzeigename
        "variant": "N" | "P",   # Normal oder Power
        "category": str,        # Beschreibung der Testkategorie
        "docs": list[str],      # Dateinamen in documents/ (leer bei Szenarien)
        "measures": list[str],  # Primär getestete Bewertungskriterien
        "use_system_prompt": bool,  # False für N, True für P
        "prompt": str,          # Der eigentliche Prompt-Text
    }
}
```

### 4.2 Aufgabenmatrix

| Task-ID | Kategorie | Docs | N-Prompt | P-Prompt |
|---------|-----------|------|----------|----------|
| A1 | Entscheidungsvorlage | – | 4 Sätze, direkte Frage | KONTEXT/SITUATION/AUFTRAG, 4 explizite Teilaufgaben |
| A2 | Strategische Zusammenfassung | bcg_ai_radar_2026.pdf | 2 Sätze + "was ist relevant" | 3 explizite Teilaufgaben + Trennungsanweisung |
| A3 | Kritisches Hinterfragen | – | Plan schildern + "was hältst du davon" | 3 Teilaufgaben + spezifische Prüfpunkte |
| A4 | Szenario-Analyse | – | Situation + "welche Szenarien" | 3 Szenarien + explizite Annahmen + szenarienübergreifende Empfehlung |
| A5 | Widerspruchserkennung | 2 PDFs | "widersprechen die sich" | 5 Teilaufgaben: Aussagen/Widersprüche/Erklärung/Gewichtung/Implikation |
| A6 | Zahlenanalyse | quartalsbericht.pdf | "sehen die Zahlen gut aus" | 4 Teilaufgaben: YoY/Positiv vs. Warnsignal/Auffälligkeiten/Gesamturteil |

---

## 5. Output-Spezifikation

### 5.1 Verzeichnisstruktur pro Run

```
results/run_20260206_143022/
├── responses/
│   ├── Claude_Opus_4-6/
│   │   ├── A1_Entscheidungsvorlage_N_run01.md
│   │   ├── A1_Entscheidungsvorlage_N_run02.md
│   │   ├── ...
│   │   ├── A1_Entscheidungsvorlage_P_run01.md
│   │   └── ...
│   ├── GPT-5-2/
│   │   └── ...
│   └── .../
├── aggregated_stats.csv        # Statistiken pro Modell×Aufgabe
├── bewertung_manual.csv        # Template für manuelle Scores
├── consistency_report.md       # CV-Analyse über Runs
├── leaderboard.md              # Score-Tabelle (nach manueller Bewertung)
├── provider_summary.md         # Direkt-API vs. OpenRouter Aufschlüsselung
└── run_meta.json               # Konfiguration, Laufzeit, Token-Verbrauch
```

### 5.2 CSV-Formate

**aggregated_stats.csv** (Semikolon-getrennt):
```
model_name;model_id;provider;task_id;task_title;num_runs;num_successful;num_failed;
latency_mean;latency_stdev;latency_min;latency_max;
output_tokens_mean;output_tokens_stdev;
response_length_mean;response_length_stdev;response_length_cv
```

**bewertung_manual.csv** (Semikolon-getrennt):
```
model_name;provider;task_id;task_title;
score_substanz;score_praezision;score_praxistauglichkeit;
score_urteilskraft;score_sprachqualitaet;score_gewichtet;
bewertungsnotiz
```

### 5.3 run_meta.json

```json
{
    "benchmark": "Entscheider-Benchmark v2.0",
    "hid": "HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46",
    "timestamp": "2026-02-06T14:30:22Z",
    "config": {
        "temperature": 0,
        "max_tokens": 4096,
        "num_runs": 10,
        "max_concurrent": 3
    },
    "providers_used": ["anthropic", "openai", "google", "openrouter"],
    "models": ["Claude Opus 4.6", ...],
    "tasks": ["A1_Entscheidungsvorlage_N", ...],
    "stats": {
        "total_requests": 2160,
        "successful": 2140,
        "failed": 20,
        "total_tokens": 8600000,
        "wall_clock_seconds": 7200
    }
}
```

---

## 6. Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| API-Key fehlt | Log Fehler, Skip Modell, weiter mit nächstem |
| HTTP-Fehler (4xx/5xx) | Log mit Status + Body (max 500 Zeichen), Retry NICHT implementiert |
| Timeout (300s) | Log, SingleResult mit `error="Timeout (300s)"` |
| Dokument fehlt | Log Warnung, Platzhalter `[DOKUMENT NICHT GEFUNDEN: ...]` im Prompt |
| pdfplumber nicht installiert | Log, Platzhalter im Prompt |
| Rate Limit | Kein explizites Retry, `REQUEST_DELAY` (2s) und `MAX_CONCURRENT` (3) als Schutz |

---

## 7. CLI-Interface

```
usage: benchmark.py [-h] [--runs N] [--models M1,M2,...] [--tasks T1,T2,...] [--dry-run]

Entscheider-Benchmark v2.0 (Multi-Provider)

optional arguments:
  --runs N          Anzahl Durchläufe (default: aus .env, Standard 10)
  --models M1,M2   Komma-getrennte Modellnamen (default: alle)
  --tasks T1,T2    Komma-getrennte Task-Prefixe, z.B. A1,A3 (default: alle)
  --dry-run         Zeigt Konfiguration ohne API-Calls
```

**Beispiele:**
```bash
# Nur Normal-User Varianten testen
python benchmark.py --tasks A1_Entscheidungsvorlage_N,A3_Kritisches_Hinterfragen_N

# Nur Power-User Varianten
python benchmark.py --tasks A1_Entscheidungsvorlage_P,A3_Kritisches_Hinterfragen_P

# Nur Frontier-Modelle
python benchmark.py --models "Claude Opus 4.6,GPT-5.2,Gemini 3 Pro"

# Quick Smoke Test
python benchmark.py --runs 1 --models "Claude Opus 4.6" --tasks A1
```

---

## 8. Abhängigkeiten

```
aiohttp>=3.9.0      # Async HTTP für API-Calls
python-dotenv>=1.0   # .env-Konfiguration
pdfplumber>=0.11     # PDF → Text-Extraktion
```

Python 3.11+ erforderlich (asyncio, type hints mit `tuple[...]`).
Kein Framework, keine DB, kein Webserver. Reines CLI-Tool.
