# HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46

**Entscheider-Benchmark – Projektstatus**
Stand: 7. Februar 2026, 12:30 Uhr
Referenz-Chat: "benchmark-fork-review" (Claude Code, Fork auf neuem Rechner)

---

## Memoryblock: Session 7. Februar 2026

### Kontext
Projekt von GitHub geklont auf neuen Rechner (`C:\Users\gpoeg\Benchmark_Test`).
Erster Review als Developer: Codebase lesen, Inkonsistenzen finden, A6-Problem lösen.

### Durchgeführte Arbeiten

**1. A6 Dual-Input-Design implementiert (wie A5)**
- Problem: EVN-Geschäftsbericht hat ~168k Tokens → sprengt 128k-Modelle bei A6_N und A6_P
- Lösung: A6_P auf kuratierten Extrakt umgestellt, A6_N bleibt beim vollen PDF
- `generate_extracts.py` um EVN-Extrakt erweitert (15 finanzanalytisch relevante Seiten aus 241)
- Extrahierte Abschnitte: Kennzahlen-Übersicht, Aktie/Ausblick, Ertragslage, Bilanz, Wertanalyse, Nettoverschuldung, Cashflow, Segmentbericht, Konzernabschluss (GuV, Bilanz, EK, Geldfluss)
- Ergebnis: 6.812 Wörter / ~8.855 Tokens statt ~168k
- `prompts.py` angepasst: A6_P nutzt `extracts/EVN_GHB_2024-25_extract.txt`, Prompt von "Quartalsbericht" auf "Geschäftsbericht" korrigiert

**2. Versionsnummern vereinheitlicht**
- `output.py`, `merge_runs.py`, `providers.py`: "v2.0" → "v3.0" (konsistent mit benchmark.py)

**3. Modellanzahl korrigiert**
- README.md, CLAUDE.md: "18 Modelle" → "17 Modelle" (MODELS-Dict in providers.py hat 17 Einträge)

**4. CLAUDE.md Projektstruktur aktualisiert**
- `generate_extracts.py`, `merge_runs.py`, `HUNTER_ID_STATUS.md` hinzugefügt (fehlten)
- `skills/benchmark-evaluator/` hinzugefügt (fehlte)
- Zeilenzahlen auf aktuelle Werte aktualisiert
- `extracts/` Beschreibung um A6_P ergänzt

**5. README.md ins Projektstamm kopiert**
- War nur unter `skills/benchmark-specs/README.md` vorhanden, nicht im Root

### Offene Punkte (für nächste Session)
- Hauptlauf-Status klären: 1.080 Requests gestartet, aber keine Ergebnisse im Original vorhanden
- Google-Modelle nachholen (HTTP 429 Quota)
- o1 System-Prompt-Kompatibilität testen
- `generate_extracts.py` im Originalprojekt neu ausführen (jetzt mit EVN-Extrakt)
- SKILL.md um Chunk-Strategie für A6 erweitern
- Modellanzahl in planning.md korrigieren (18 → 17 durchgängig)

### Geänderte Dateien
| Datei | Änderung |
|-------|----------|
| `generate_extracts.py` | EVN-Extrakt hinzugefügt (A6_P), Header ergänzt |
| `prompts.py` | A6_P docs auf Extrakt, Prompt "Quartalsbericht" → "Geschäftsbericht" |
| `output.py` | Version v2.0 → v3.0 |
| `merge_runs.py` | Version v2.0 → v3.0 |
| `providers.py` | OpenRouter X-Title v2.0 → v3.0 |
| `README.md` | Ins Root kopiert, Modellanzahl 18 → 17 |
| `CLAUDE.md` | Projektstruktur aktualisiert, Zeilenzahlen, fehlende Dateien, 18 → 17 |
| `HUNTER_ID_STATUS.md` | Dieses Update |

---

## Phase 1: Infrastruktur – ABGESCHLOSSEN ✓

7 Module: benchmark.py (250Z), models.py (162Z), providers.py (335Z), output.py (182Z), prompts.py (336Z), generate_extracts.py (258Z), merge_runs.py (245Z).
Fixes: REQUEST_DELAY aus Semaphore, 3× Retry bei HTTP 429/503/529. Syntax OK.
Versionen durchgängig v3.0.

## Phase 2: Quelldokumente – ABGESCHLOSSEN ✓

### Verfügbare Dokumente
| Aufgabe | Dokument | Pfad | Status |
|---------|----------|------|--------|
| A2 | BCG AI Radar 2026 | `documents/pdf_files/ai-radar-2026-web-jan-2026-edit.pdf` | ✓ |
| A5_N | Turing Framework (88S.) + EU AI Act (144S.) – volle PDFs | `documents/pdf_files/` | ✓ |
| A5_P | Kuratierte Extrakte (~4.4k Tokens) | `documents/extracts/` | ✓ |
| A6_N | EVN Geschäftsbericht 2024/25 (241S., ~168k Tokens) | `documents/pdf_files/EVN-GHB-2024-25_online.pdf` | ✓ |
| A6_P | EVN Finanz-Extrakt (~8.9k Tokens) | `documents/extracts/EVN_GHB_2024-25_extract.txt` | ✓ NEU |

### Dual-Input-Design (A5 + A6)
| Aufgabe | N-Variante (Normal-User) | P-Variante (Power-User) |
|---------|--------------------------|-------------------------|
| A5 | Volle PDFs (~108k Tokens) | Kuratierte Extrakte (~4.4k Tokens) |
| A6 | Voller EVN-Bericht (~168k Tokens) | Finanz-Extrakt (~8.9k Tokens) |

Normal-User wirft alles rein. Power-User bereitet vor. Das Delta ist die Messung.

## Phase 3: Testdurchlauf – IN PROGRESS 🟡

Smoke Tests erfolgreich (Claude Opus 4.6 × A1). Hauptlauf gestartet aber Status unklar.

## Aufgaben für nächsten Chat

### Gerald (vor Chat):
1. Im Originalprojekt: `python generate_extracts.py` erneut ausführen (generiert jetzt auch EVN-Extrakt)
2. Hauptlauf-Status klären: Gibt es Ergebnisse unter `results/`?
3. Änderungen aus diesem Fork übernehmen (generate_extracts.py, prompts.py, output.py, merge_runs.py, providers.py, CLAUDE.md, README.md)

### Claude (im Chat):
4. Dry-Run mit neuem A6_P-Extrakt validieren
5. Hauptlauf starten oder fortsetzen
6. Google-Modelle separat nachholen

### Prompt für nächsten Chat:
"Benchmark weiter. Lies HUNTER_ID_STATUS.md als Einstieg. HID: HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46. Wichtig: generate_extracts.py wurde erweitert (EVN-Extrakt für A6_P). Nächster Schritt: Dry-Run + Hauptlauf."
