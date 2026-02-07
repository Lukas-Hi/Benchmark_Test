# Methodik-Referenzen: Benchmark-Design und Evaluation
Referenz für den Benchmark-Evaluator (Modus DESIGN).

## Referenz-Benchmarks

### GDPval (OpenAI, Oktober 2025)
- 44 Berufe, echte Arbeitsprodukte, Experten-Bewertung
- 1 Run pro Aufgabe, statistische Absicherung über Aufgabenmenge
- Relevanz: Vorbild für praxisnahe Szenarien statt synthetischer Tests
- Limitation: Keine Multi-Run-Konsistenz, kein Dual-Prompt-Design

### Artificial Analysis Intelligence Index v4.0
- >10 Wiederholungen pro Modell für 95%-Konfidenzintervall (±1%)
- Automatisierte Bewertung
- Relevanz: Multi-Run-Methodik als statistische Basis
- Limitation: Automatische Bewertung versagt bei nuancierten Strategieantworten

### BetterBench (Stanford, 2025)
- Kritik an Score-Inflation und fehlender Reproduzierbarkeit
- Head-to-Head-Vergleiche statt absolute Scores
- Relevanz: Testbedingungen explizit dokumentieren, Temperatur fixieren
- Limitation: Head-to-Head unpraktikabel bei 18×12 Kombinationen

### HELM (Stanford, laufend)
- Holistic Evaluation of Language Models
- Multi-dimensionale Bewertung (Accuracy, Calibration, Robustness, Fairness, Efficiency)
- Relevanz: Mehrdimensionale Bewertung statt Single-Score
- Limitation: Akademische Aufgaben, nicht strategische Führungsarbeit

## Methodische Prüfpunkte für das Testdesign

### Konstruktvalidität
- Misst jede Aufgabe tatsächlich die behauptete Kompetenz?
- Sind die Kriterien (Substanz, Präzision, etc.) operational definiert?
- Gibt es Ceiling-Effekte (alle Modelle Score 4–5) oder Floor-Effekte (alle 1–2)?

### Dual-Prompt-Validität
- Ist der N-Prompt authentisch? Würde ein GF wirklich so fragen?
- Ist der P-Prompt zu führend? Gibt er die Antwortstruktur so stark vor, dass das Modell nur ausfüllen muss?
- Ist das Delta (P–N) dem Prompt zuzuschreiben oder dem System-Prompt allein?
- Konfound: System-Prompt enthält Format- UND Inhaltsanweisungen – was treibt das Delta?

### Statistische Power
- 10 Runs × Temperatur 0: Misst Restvarianz (GPU-Parallelismus, Batching)
- CV < 5% erwartet bei Temp 0 – wenn höher, ist die Varianzquelle unklar
- Bei manueller Bewertung: Nur Median-Run bewertet → 90% der Daten ungenutzt
- Alternative: Bewertung von 3 Runs (25./50./75. Perzentil) für robustere Schätzung

### Dokumenten-Fairness
- PDF-Extraktion (pdfplumber) kann Tabellen, Grafiken, Fußnoten verlieren
- Modelle mit nativem PDF-Verständnis haben Vorteil wenn sie das Original bekämen
- Extrakt-Qualität beeinflusst A5 direkt – kuratierter Extrakt ist eine Designentscheidung

### Bias-Quellen
- Reihenfolge-Bias: Erste bewertete Antwort setzt Anker
- Erwartungs-Bias: Modellname sichtbar (Blind-Bewertung unpraktikabel bei 216 Antworten)
- Prompt-Leakage: N- und P-Prompts für gleiche Aufgabe könnten sich gegenseitig "kalibrieren"
- Aufgaben-Heterogenität: Szenario-Tasks (A1/A3/A4) vs. Dokumenten-Tasks (A2/A5/A6) testen Verschiedenes

## Entscheider-Benchmark: Spezifika

### 6 Aufgabenkategorien
| ID | Aufgabe | Typ | Dokument |
|----|---------|-----|----------|
| A1 | Entscheidungsvorlage | Szenario | – |
| A2 | Strategische Zusammenfassung | Dokument | BCG AI Radar 2026 |
| A3 | Kritisches Hinterfragen | Szenario | – |
| A4 | Szenario-Analyse | Szenario | – |
| A5 | Widerspruchserkennung | Dokument | Turing Framework + EU AI Act |
| A6 | Zahlenanalyse | Dokument | EVN Geschäftsbericht |

### Dual-Prompt-Design
- N = Normal-User: Kein System-Prompt, natürliche Sprache, unvollständiger Kontext
- P = Power-User: System-Prompt + KONTEXT → SITUATION → AUFTRAG + Guardrails
- Delta (P–N) = Messgröße für Prompt-Kompetenz-Hebel

### 18 Modelle in 4 Kategorien
- Frontier (7): Opus 4.6/4.5, GPT-5.2/Pro, Gemini 3 Pro/2.5 Pro, Grok 4.1
- Mid-Tier (7): Sonnet 4.5, Haiku 4.5, GPT-5.2 Chat, Gemini Flash, Mistral Large 3, DeepSeek V3.2, Llama 3.3 70B
- Coding (1): GPT-5.2-Codex
- Reasoning (2): DeepSeek R1, o1
