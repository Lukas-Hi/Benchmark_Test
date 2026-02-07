# HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46

**Entscheider-Benchmark – Projektstatus**
Stand: 6. Februar 2026, 13:45 Uhr
Referenz-Chat: "benchmark-refactoring-v3-modular" (dieser Chat)

---

## Phase 1: Infrastruktur – ABGESCHLOSSEN ✓

5 Module: benchmark.py (222Z), models.py (158Z), providers.py (329Z), output.py (181Z), prompts.py (320Z).
Fixes: REQUEST_DELAY aus Semaphore, 1× Retry bei HTTP 429. Syntax OK.

## Phase 2: Quelldokumente – ABGESCHLOSSEN ✓

### Verfügbare Dokumente
| Aufgabe | Dokument | Pfad | Status |
|---------|----------|------|--------|
| A2 | BCG AI Radar 2026 | `documents/pdf_files/ai-radar-2026-web-jan-2026-edit.pdf` | ✓ |
| A5 | Turing AI Regulatory Framework (88S.) | `documents/pdf_files/alan_turing_the_ai_regulatory.pdf` | ✓ |
| A5 | EU AI Act (144S.) | `documents/pdf_files/EU_AI_ACT_DE_TXT.pdf` | ✓ |
| A6 | EVN Geschäftsbericht 2024/25 | `documents/pdf_files/EVN-GHB-2024-25_online.pdf` | ✓ |

### Chunk-Strategie (Option C: Experten-Extrakte)
Problem: A5 Dokumente zusammen ~108.000 Tokens – sprengt Context Windows.
Lösung: Kuratierte Extrakte mit Quellenhinweis ("Dies ist ein Experten-Extrakt").
- `documents/extracts/EU_AI_ACT_Art4_extract.txt` (~1.660 Tokens): Art. 4 + Erwägungsgründe 20, 91-93, 165 + Sanktionshinweis
- `documents/extracts/turing_framework_extract.txt` (~2.786 Tokens): Executive Summary + Capability Framework + Theory of Change
- Zusammen ~4.400 Tokens – funktioniert mit allen 17 Modellen
- `generate_extracts.py` erstellt → MUSS EINMAL AUSGEFÜHRT WERDEN (Extrakt-Dateien sind aktuell noch Placeholder)

### Skill
benchmark-specs.skill entpackt nach `skills/benchmark-specs/`. SKILL.md, references/scoring_criteria.md, Snapshots vorhanden.
Skill muss um Chunk-Strategie-Dokumentation erweitert werden (im nächsten Chat).

## Phase 3: Testdurchlauf – OFFEN ⬜

---

## Aufgaben für nächsten Chat

### Gerald (vor Chat):
1. `cd C:\Users\Geri\Benchmark_Test && python generate_extracts.py` ausführen → generiert die Extrakt-Dateien
2. `.env` mit API-Keys befüllen (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY)

### Claude (im Chat):
3. Prüfen ob Extrakte korrekt generiert wurden
4. SKILL.md um Chunk-Strategie-Abschnitt erweitern
5. prompts.py prüfen: A2-Docs auf BCG-Dateinamen, A6-Docs auf EVN-Dateinamen aktualisieren
6. `python benchmark.py --dry-run` → Provider-Zuordnung und Dokument-Laden testen
7. Erster Testlauf: `python benchmark.py --runs 1 --models "Claude Opus 4.6" --tasks A1_Entscheidungsvorlage_N A5_Widerspruchserkennung_P`

### Prompt für nächsten Chat:
"Benchmark weiter. Lies docs/planning.md als Einstieg. Hunter-ID: HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46. Aufgaben: Extrakte prüfen, Skill erweitern, Dry-Run durchführen."
