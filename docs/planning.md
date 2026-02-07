# Planning: Entscheider-Benchmark
**HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46**
Stand: 6. Februar 2026

---

## 1. Ursprung und Motivation

### Auslöser
Am 6. Februar 2026 (Tag des Opus 4.6 Release) entstand die Idee, einen eigenen Benchmark zu entwickeln, der misst, was wissenschaftliche Benchmarks nicht messen: Wie gut unterstützen LLMs reale strategische Entscheidungen?

### Lücke
Existierende Benchmarks (MMLU, HumanEval, GPQA, etc.) testen akademisches Wissen, Coding-Fähigkeit, logisches Denken. Kein Benchmark testet, ob ein LLM einem GF mit 45 Mitarbeitern eine brauchbare Entscheidungsvorlage liefert. GDPval (OpenAI, Oktober 2025) kommt am nächsten – 44 Berufe, echte Arbeitsprodukte – aber deckt strategische Führungsarbeit im KMU-Kontext nicht ab.

### Positionierung
Der Benchmark dient gleichzeitig als Content-Instrument (LinkedIn) und als öffentliches Tool (GitHub-Repository). Die Community-Komponente erlaubt es anderen, den Benchmark zu forken und eigene Ergebnisse beizutragen.

---

## 2. Entscheidungslog

### 2.1 Aufgaben-Design
**Entscheidung:** Sechs Aufgabenkategorien, alle auf strategische Führungsarbeit fokussiert.
**Begründung:** Operative Aufgaben (E-Mails verbessern, Texte schreiben) sind für die Thoughtful-Leader-Positionierung zu kleinteilig.
**Verworfene Alternative:** Breiter Mix aus operativen + strategischen Aufgaben.

| ID | Aufgabe | Was wird getestet |
|----|---------|-------------------|
| A1 | Entscheidungsvorlage | Risikoerkennung, fehlende Info, kritische Distanz |
| A2 | Strategische Zusammenfassung | Signal/Rauschen trennen, KMU-Kontextualisierung |
| A3 | Kritisches Hinterfragen | Strukturelle Schwächen erkennen, konstruktive Kritik |
| A4 | Szenario-Analyse | Distinkte Szenarien, Annahmen explizit machen |
| A5 | Widerspruchserkennung | Quellenvalidierung, Ursachen für Diskrepanzen |
| A6 | Zahlenanalyse | Korrekte Extraktion, nicht-offensichtliche Muster |

### 2.2 Zwei Prompt-Varianten (N/P)
**Entscheidung:** Jede Aufgabe in zwei Varianten – Normal-User und Power-User.
**Begründung:** Der Delta zwischen N und P misst den Wert von Prompt-Kompetenz. Das ist die zentrale These des Benchmarks und der Content-Strategie: „Kompetenz im Umgang mit KI macht den Unterschied, nicht das Tool."
- **N (Normal):** Kein System-Prompt, kein Kontext-Setup, Frage wie ein GF sie stellen würde.
- **P (Power):** Voller System-Prompt, KONTEXT → SITUATION → AUFTRAG, Guardrails, explizite Anforderungen.

### 2.3 Multi-Provider statt nur OpenRouter
**Entscheidung:** Direkt-APIs für Abo-Modelle (Anthropic, OpenAI, Google), OpenRouter nur für Rest.
**Begründung:** Gerald hat Pro/Max/Business-Abos. 13 von 18 Modellen laufen über Abos = keine Zusatzkosten. Nur 5 über OpenRouter. Geschätzte Ersparnis: 50–100 EUR pro Durchlauf.
**Verworfene Alternative:** Alles über OpenRouter (einfacher, aber teurer).

### 2.4 10 Runs bei Temperatur 0
**Entscheidung:** 10 Wiederholungen pro Modell×Aufgabe, Temperatur 0.
**Begründung:** Artificial Analysis nutzt >10 Wiederholungen für 95%-Konfidenzintervall. GDPval fährt 1 Run (statistische Absicherung über Aufgabenmenge). 10 Runs ist der Kompromiss zwischen Aussagekraft und Kosten. Temperatur 0 für maximale Reproduzierbarkeit.
**Alternative:** 3 Runs (schneller, billiger, aber schwächere Statistik).

### 2.5 Modellauswahl
**Entscheidung:** 18 Modelle in 4 Kategorien.
**Begründung:** Frontier zeigt State of the Art, Mid-Tier zeigt Preis-Leistung, Coding-Modelle testen ob Spezialisierung bei Strategie schadet, Reasoning-Modelle testen ob explizites Denken hilft.

| Kategorie | Modelle | Warum |
|-----------|---------|-------|
| Frontier (7) | Opus 4.6, Opus 4.5, GPT-5.2, GPT-5.2 Pro, Gemini 3 Pro, Gemini 2.5 Pro, Grok 4.1 | Bestmögliche Leistung pro Anbieter |
| Mid-Tier (7) | Sonnet 4.5, Haiku 4.5, GPT-5.2 Chat, Gemini Flash, Mistral Large 3, DeepSeek V3.2, Llama 3.3 70B | Preis-Leistung für KMU |
| Coding (1) | GPT-5.2-Codex | Spezialisierung vs. Generalismus |
| Reasoning (2) | DeepSeek R1, o1 | Explizites Denken bei strategischen Aufgaben |

**Hinweis:** GPT-5.3-Codex (Release 5. Feb 2026) fehlt – API noch nicht über OpenRouter verfügbar. Wird manuell über VS Code nachgetestet.

### 2.6 Quelldokumente
**Entscheidung:** 3 Aufgaben szenariobasiert (kein Dokument nötig), 3 dokumentbasiert.

| Aufgabe | Dokument | Status |
|---------|----------|--------|
| A1, A3, A4 | – (Szenario im Prompt) | ✓ Fertig |
| A2 | BCG AI Radar 2026 Executive Summary | ⬜ Zu beschaffen |
| A5_N | Alan Turing Framework (88S.) + EU AI Act (144S.) – volle PDFs | ✓ Fertig |
| A5_P | Kuratierte Extrakte (~2.5k Tokens) aus beiden Dokumenten | ✓ Fertig |
| A6 | EVN Geschäftsbericht 2024/25 | ✓ Fertig |

---

## 3. Roadmap

### Phase 1: Infrastruktur ✓
- [x] Benchmark-Methodik definiert
- [x] Aufgaben und Prompts formuliert (6×N + 6×P = 12)
- [x] Multi-Provider Runner implementiert (benchmark.py)
- [x] Projektstruktur und Dokumentation angelegt
- [x] CLAUDE.md, planning.md, specs.md, methodology.md, scoring_guide.md
- [x] Logik-Check: Keine Fehler, 9 Warnungen dokumentiert
- [x] Benchmark-Specs Skill erstellt (benchmark-specs.skill)
- [x] Refactoring: Monolith (810Z) → 5 Module (benchmark.py 222Z, models.py 158Z, providers.py 329Z, output.py 181Z, prompts.py 313Z)
- [x] Fixes: REQUEST_DELAY aus Semaphore verschoben, 1× Retry bei HTTP 429 eingebaut

### Phase 2: Quelldokumente ✓
- [x] BCG AI Radar 2026 → `documents/pdf_files/ai-radar-2026-web-jan-2026-edit.pdf`
- [x] Alan Turing AI Regulatory Framework → `documents/pdf_files/alan_turing_the_ai_regulatory.pdf`
- [x] EU AI Act (deutsch, 144S.) → `documents/pdf_files/EU_AI_ACT_DE_TXT.pdf`
- [x] EVN Geschäftsbericht 2024/25 → `documents/pdf_files/EVN-GHB-2024-25_online.pdf`
- [x] Kuratierte Extrakte für A5 → `documents/extracts/` (EU_AI_ACT_Art4_extract.txt, turing_framework_extract.txt)
- [x] `generate_extracts.py` erstellt → MUSS EINMAL AUSGEFÜHRT WERDEN: `cd Benchmark_Test && python generate_extracts.py`
- [x] Chunk-Strategie implementiert: Beide A5-Varianten nutzen Extrakte (~4.4k Tokens statt ~108k)
- [x] prompts.py v3.2: Alle doc-Referenzen auf tatsächliche Dateinamen aktualisiert
- [x] Skill entpackt → `skills/benchmark-specs/` (SKILL.md, references/, benchmark.py, prompts.py Snapshot)
- [x] `generate_extracts.py` ausgeführt: EU-Extrakt 1.277 Wörter, Turing-Extrakt 2.533 Wörter, ~4.446 Tokens gesamt
- [x] Skill `benchmark-evaluator` erstellt (SKILL.md + references/scoring_criteria.md + references/methodology_references.md)
- [x] Skill `benchmark-specs` aktualisiert (Phase 2 DONE, Refactoring-Status, Verweis auf Evaluator)
- [-] Statistik Austria / Microsoft Work Trend Index → nicht mehr benötigt (A5 umdesignt auf UK vs. EU Regulierung)
- [x] A5 Dual-Input-Design: N-Variante nutzt volle PDFs (~108k Tokens), P-Variante nutzt kuratierte Extrakte (~4.4k Tokens)
- [x] Retry auf 3 mit exponentiellem Backoff (10s/30s/90s), auch HTTP 503/529
- [x] Dry-Run um Token-Schätzung und Kontextfenster-Warnungen erweitert
- [x] Input-Tokens in AggregatedResult und aggregated_stats.csv aufgenommen
- [x] merge_runs.py erstellt: Führt separate run_*-Verzeichnisse zusammen

### Phase 3: Testdurchlauf 🟡 IN PROGRESS
- [x] `.env` mit API-Keys konfiguriert
- [x] `python benchmark.py --dry-run` – Token-Schätzungen validiert:
  - A5_N: 128.350 Tokens (volle PDFs) – grenzwertig für 128k-Modelle
  - A6_N/P: ~168k Tokens (voller EVN-Bericht) – überschreitet 128k-Modelle
- [x] Smoke Test: Claude Opus 4.6 × A1_N – erfolgreich (1.351 Tokens, 30s)
- [x] System-Prompt-Test: Claude Opus 4.6 × A1_P – Fließtext, Deutsch, keine KI-Referenz ✓
- [ ] o1 System-Prompt-Kompatibilität prüfen (wenn erste P-Ergebnisse vorliegen)
- [x] Google Gemini Flash × A6: HTTP 429 Quota-Problem. Google-Modelle auf separaten Run verschoben.
- [x] Hauptlauf gestartet: 9 Modelle (Anthropic + OpenAI), 12 Tasks × 10 Runs = 1.080 Requests
- [ ] Google-Run nachholen (3 Modelle), dann merge_runs.py
- [ ] Ergebnisse prüfen: Antworten, Statistik, Fehler-Report

### Phase 4: Voller Durchlauf ⬜
- [ ] `python benchmark.py` – 18 Modelle × 12 Aufgaben × 10 Runs
- [ ] Laufzeit und Kosten dokumentieren
- [ ] Konsistenz-Report prüfen (CV < 15% für alle Modelle)
- [ ] Provider-Summary prüfen (Direkt vs. OpenRouter)

### Phase 5: Bewertung ⬜
- [ ] Bewertungs-Template (`bewertung_manual.csv`) ausfüllen
- [ ] Pro Aufgabe×Modell: Exemplarische Antwort (Median-Run) bewerten
- [ ] 5 Kriterien × Gewichtung = gewichteter Score
- [ ] Leaderboard erstellen

### Phase 6: Veröffentlichung ⬜
- [ ] GitHub-Repo anlegen (öffentlich)
- [ ] README finalisieren
- [ ] Ergebnisse als Leaderboard-Tabelle
- [ ] LinkedIn-Post: Benchmark-Ankündigung + Community-Aufruf
- [ ] GPT-5.3-Codex manuell nachtesten und ergänzen

---

## 4. Offene Fragen

1. **Quartalsbericht:** Welches Unternehmen? Immofinanz passt zur Zielgruppe (Immobilien), Verbund wäre breiter.
2. **LLM-as-Judge:** Automatisierte Ersteinschätzung als Vorfilter vor manueller Bewertung? Oder rein manuell?
3. **N-Variante Bewertung:** Gleiche Kriterien und Gewichtung für N und P? Oder separate Bewertung?
4. **GPT-5.3-Codex:** Wann API über OpenRouter verfügbar? Manueller Test reicht erstmal.

---

## 5. Verworfene Alternativen (für Nachvollziehbarkeit)

| Idee | Warum verworfen |
|------|-----------------|
| Operative Aufgaben (E-Mail, Text verbessern) | Zu kleinteilig für Thoughtful-Leader-Positionierung |
| Nur OpenRouter | Teurer, Gerald hat bereits Abos |
| Nur 1 Run pro Modell | Statistisch zu schwach, keine Varianz-Messung |
| Automatische Bewertung (LLM-as-Judge) | Zu unsicher bei nuancierten Strategieantworten, offen als Ergänzung |
| 30+ Modelle | Diminishing Returns, die wichtigsten 18 decken den Markt ab |
| Temperatur > 0 | Nicht reproduzierbar, macht Multi-Run-Vergleich schwieriger |
