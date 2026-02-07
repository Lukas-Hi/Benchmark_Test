# Entscheider-Benchmark

**Wie gut unterstützen KI-Modelle strategische Geschäftsentscheidungen?**

Ein praxisnaher Benchmark für Führungskräfte im DACH-Raum. Keine Quizfragen, keine Coding-Aufgaben – stattdessen sechs Szenarien, die jeder Geschäftsführer kennt.

## Warum dieser Benchmark?

Bestehende KI-Benchmarks messen Mathematik, Code und Allgemeinwissen. Kein einziger misst, was Entscheider tatsächlich brauchen: eine fundierte Einschätzung zu einer Geschäftsentscheidung. Auf Deutsch. Mit kritischer Distanz statt People-Pleasing.

Dieser Benchmark schließt diese Lücke. Er testet 18 Modelle gegen sechs Aufgaben, die aus dem Alltag mittelständischer Unternehmen kommen – von der Entscheidungsvorlage über Szenario-Analysen bis zur Finanzanalyse.

## Die sechs Aufgaben

| # | Aufgabe | Testet |
|---|---------|--------|
| A1 | Entscheidungsvorlage | Risikoerkennung, fehlende Informationen, kritische Distanz |
| A2 | Strategische Zusammenfassung | Signal/Rauschen trennen, KMU-Kontextualisierung |
| A3 | Kritisches Hinterfragen | Strukturelle Schwächen erkennen, konstruktive Kritik |
| A4 | Szenario-Analyse | Distinkte Szenarien, Annahmen explizit, Handlungsempfehlung |
| A5 | Widerspruchserkennung | Quellenvergleich, Methodenkritik, Verlässlichkeitsbewertung |
| A6 | Zahlenanalyse | Korrekte Extraktion, Veränderungsraten, nicht-offensichtliche Muster |

## Bewertungskriterien

| Kriterium | Gewicht | Was es misst |
|-----------|---------|-------------|
| Substanz | 25% | Tiefe der Analyse, eigenständige Schlüsse |
| Präzision | 25% | Faktenfreiheit, Fakt vs. Einschätzung getrennt |
| Praxistauglichkeit | 20% | Direkt umsetzbar für KMU-Entscheider |
| Urteilskraft | 20% | Benennt Risiken ungefragt, traut sich Widerspruch |
| Sprachqualität (DE) | 10% | Natürliches Geschäftsdeutsch, DACH-tauglich |

Scoring: 1–5 pro Kriterium, gewichteter Durchschnitt = Gesamtscore.

| Score | Klasse |
|-------|--------|
| 4,5–5,0 | Sparringspartner |
| 3,5–4,4 | Qualifizierter Zuarbeiter |
| 2,5–3,4 | Fleißiger Assistent |
| 1,0–2,4 | Nicht empfehlenswert |

## Getestete Modelle (18)

**Frontier:** Claude Opus 4.6, Claude Opus 4.5, GPT-5.2, GPT-5.2 Pro, Gemini 3 Pro, Gemini 2.5 Pro, Grok 4.1

**Mid-Tier:** Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.2 Chat, Gemini 2.5 Flash, Mistral Large 3, DeepSeek V3.2, Llama 3.3 70B

**Coding:** GPT-5.2-Codex

**Reasoning:** DeepSeek R1, o1

## Quick Start

```bash
git clone https://github.com/[user]/entscheider-benchmark.git
cd entscheider-benchmark
pip install -r requirements.txt
cp .env.example .env
# OpenRouter API-Key in .env eintragen
```

### Trockenlauf (ohne API-Kosten)
```bash
python benchmark.py --dry-run
```

### Testlauf (1 Run, 2 Modelle)
```bash
python benchmark.py --runs 1 --models "Claude Opus 4.6,GPT-5.2"
```

### Voller Durchlauf (10 Runs, alle Modelle)
```bash
python benchmark.py
```

### Nur bestimmte Aufgaben
```bash
python benchmark.py --tasks A1,A3,A4
```

## Quelldokumente

Die szenariobasierten Aufgaben (A1, A3, A4) brauchen keine Dokumente und laufen sofort.

Für A2, A5, A6 werden PDFs benötigt. Diese in `./documents/` ablegen:

| Dateiname | Quelle | Aufgabe |
|-----------|--------|---------|
| `bcg_ai_radar_2026.pdf` | BCG AI Radar 2026 | A2 |
| `statistik_austria_ict_2025.pdf` | Statistik Austria ICT-Erhebung | A5 |
| `microsoft_work_trend_index_2025.pdf` | Microsoft Work Trend Index | A5 |
| `quartalsbericht.pdf` | Quartalsbericht eines börsennotierten Unternehmens | A6 |

## Output-Struktur

```
results/run_YYYYMMDD_HHMMSS/
├── run_meta.json              # Konfiguration, Token-Verbrauch, Laufzeit
├── aggregated_stats.csv       # Statistiken pro Modell×Aufgabe (Latenz, Tokens, Varianz)
├── bewertung_manual.csv       # Template für manuelle Score-Eingabe
├── consistency_report.md      # Wie stabil antwortet jedes Modell über 10 Runs?
├── leaderboard.md             # Leaderboard-Template (nach Bewertung ausfüllen)
└── responses/
    ├── Claude_Opus_4-6/
    │   ├── A1_Entscheidungsvorlage_run01.md
    │   ├── A1_Entscheidungsvorlage_run02.md
    │   ├── ...
    │   └── A6_Zahlenanalyse_run10.md
    ├── GPT-5-2/
    │   └── ...
    └── ...
```

## Methodik

**10 Durchläufe pro Modell×Aufgabe** bei Temperatur 0. Das entspricht dem Minimum, das Artificial Analysis für ihr 95%-Konfidenzintervall verwendet (>10 Repeats, ±1% CI).

Bei Temperatur 0 sollten die Antworten nahezu identisch sein. Wenn sie es nicht sind, ist das bereits eine Erkenntnis (Modell-Instabilität). Der Konsistenz-Report misst das über den Coefficient of Variation (CV) der Antwortlänge.

**System-Prompt und Aufgaben-Prompts sind standardisiert** – jedes Modell bekommt exakt den gleichen Input. Details in `prompts.py`.

**Bewertung ist manuell.** Automatisierte LLM-Bewertung (LLM-as-a-Judge) erreicht nur ~66% Übereinstimmung mit menschlichen Experten bei komplexen Aufgaben (GDPval-Studie, OpenAI 2025). Für strategische Qualität ist menschliche Bewertung nach wie vor der Goldstandard.

## Mitmachen

Jeder kann diesen Benchmark mit eigenen Modellen oder eigener Bewertung durchführen.

**Ergebnisse einreichen:**
1. Fork dieses Repo
2. Benchmark durchlaufen lassen
3. Bewertung in `bewertung_manual.csv` eintragen
4. Pull Request mit dem `results/`-Ordner erstellen

Je mehr unabhängige Bewertungen, desto belastbarer die Ergebnisse.

## Limitationen (transparent)

- **Kleine Aufgabenzahl:** 6 Aufgaben sind kein umfassender Benchmark. Sie decken strategische Kernkompetenz ab, nicht den gesamten Einsatzbereich.
- **Manuelle Bewertung:** Subjektiv, nicht skalierbar. Aber für strategische Qualität gibt es aktuell keine zuverlässige Alternative.
- **DACH-Fokus:** Prompts und Bewertung sind auf deutschsprachige Geschäftskommunikation ausgerichtet. Ergebnisse sind nicht direkt auf andere Märkte übertragbar.
- **Statischer Zeitpunkt:** Modelle werden ständig aktualisiert. Ergebnisse gelten für die getestete Version.
- **Keine Kosten-Normalisierung:** Ein Modell mit 10× höherem Preis und 5% besserem Score ist nicht automatisch die bessere Wahl.

## Lizenz

MIT – verwenden, forken, erweitern.

## Referenzen

- Artificial Analysis Intelligence Index v4.0: >10 Repeats für 95% CI (±1%)
- GDPval (OpenAI, Oktober 2025): 44 Berufe, echte Arbeitsprodukte, Expert:innen-Bewertung
- Bewertungsmethodik orientiert am GDPval-Prinzip: Praxisnähe vor akademischer Reinheit

---

Gerald T. Pögl
KI-Sparringspartner für Entscheider im DACH-Raum
[hunter-id.com](https://hunter-id.com)

#VisiON #KI_Sparring #unternehmerische_Weichenstellung
