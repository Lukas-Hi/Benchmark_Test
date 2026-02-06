# Bewertungsleitfaden: Entscheider-Benchmark
**HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46**
Stand: 6. Februar 2026

---

Dieser Leitfaden dient der konsistenten manuellen Bewertung aller Benchmark-Antworten.
Er richtet sich an Gerald (Erstbewertung) und potenzielle Community-Bewerter.

---

## 1. Vorbereitung

1. Öffne `results/run_*/bewertung_manual.csv` in Excel oder LibreOffice Calc
2. Wähle pro Modell×Aufgabe den **Median-Run** (gemessen an Antwortlänge) als Bewertungsgrundlage
3. Lies die Antwort vollständig, bevor du bewertest
4. Bewerte alle Antworten einer Aufgabe am Stück (nicht alle Aufgaben eines Modells)

---

## 2. Bewertungskriterien

### 2.1 Substanz (Gewicht: 25%)

Wie tief und eigenständig ist die Analyse?

| Score | Beschreibung | Beispiel |
|-------|-------------|----------|
| 1 | Generisch, wiederholt nur den Prompt | "Das ist eine interessante Frage. Es gibt Vor- und Nachteile." |
| 2 | Nennt relevante Punkte, bleibt aber oberflächlich | Listet offensichtliche Risiken, geht nicht in die Tiefe |
| 3 | Solide Analyse, deckt Kernpunkte ab | Erkennt die wichtigsten Argumente, bleibt aber bei Standardüberlegungen |
| 4 | Tiefgehend, bringt eigene Einordnung | Identifiziert Zusammenhänge, die nicht im Prompt stehen |
| 5 | Überraschend gut, nicht-offensichtliche Punkte | Erkennt versteckte Risiken, stellt Fragen, die der GF nicht gestellt hat |

### 2.2 Präzision (Gewicht: 25%)

Sind die Aussagen faktisch korrekt und sauber getrennt?

| Score | Beschreibung | Beispiel |
|-------|-------------|----------|
| 1 | Faktenfehler, Halluzinationen, Zahlen erfunden | "Laut einer McKinsey-Studie..." (die nicht existiert) |
| 2 | Überwiegend korrekt, aber vage oder ungeprüft | Zahlen aus dem Dokument ungenau wiedergegeben |
| 3 | Korrekt, aber keine klare Trennung Fakt/Einschätzung | Meinungen als Fakten präsentiert |
| 4 | Korrekt, Fakt und Einschätzung klar getrennt | "Die Daten zeigen X. Meine Einschätzung ist Y." |
| 5 | Fehlerfrei, benennt eigene Unsicherheit | Sagt explizit wo Daten fehlen oder unsicher sind |

### 2.3 Praxistauglichkeit (Gewicht: 20%)

Kann ein GF damit etwas anfangen?

| Score | Beschreibung | Beispiel |
|-------|-------------|----------|
| 1 | Theoretisch, abstrakt, nicht umsetzbar | "Unternehmen sollten eine ganzheitliche Strategie entwickeln" |
| 2 | Richtung stimmt, aber zu allgemein | "Prüfen Sie die Risiken" (welche?) |
| 3 | Brauchbare Hinweise, aber nicht auf Kontext zugeschnitten | Generische Ratschläge, die für jedes Unternehmen gelten |
| 4 | Konkret, auf den Kontext bezogen | Bezieht sich auf 45 MA, Wien, Sanitärbranche |
| 5 | Direkt umsetzbar, kennt Entscheider-Realität | Empfiehlt konkreten nächsten Schritt, kennt typische KMU-Constraints |

### 2.4 Urteilskraft (Gewicht: 20%)

Nickt das Modell alles ab oder traut es sich zu widersprechen?

| Score | Beschreibung | Beispiel |
|-------|-------------|----------|
| 1 | Reines People-Pleasing, bestätigt alles | "Das klingt nach einem guten Plan!" |
| 2 | Erwähnt Risiken pflichtgemäß, ohne Substanz | "Es gibt natürlich auch Risiken zu bedenken" |
| 3 | Benennt konkrete Schwächen, bleibt aber diplomatisch | Zeigt Probleme auf, relativiert sofort |
| 4 | Klare Position, benennt Denkfehler | "Ihre Tendenz ist nachvollziehbar, aber voreilig, weil..." |
| 5 | Widerspricht ungefragt, zeigt blinde Flecken | Identifiziert Informationslücken, die der GF nicht bemerkt hat |

### 2.5 Sprachqualität Deutsch (Gewicht: 10%)

Klingt das wie ein erfahrener Berater oder wie Google Translate?

| Score | Beschreibung | Beispiel |
|-------|-------------|----------|
| 1 | Übersetzungsdeutsch, Buzzwords, unnatürlich | "Leveragen Sie Ihre Kernkompetenzen" |
| 2 | Grammatisch korrekt, aber steif | Liest sich wie eine Übersetzung aus dem Englischen |
| 3 | Solides Deutsch, aber ohne Charakter | Korrekt, aber könnte aus jedem Beratungs-Template stammen |
| 4 | Natürliches Geschäftsdeutsch | Klingt wie ein Gespräch unter Führungskräften |
| 5 | Exzellent, DACH-tauglich, prägnant | Österreichische Pragmatik, kein Consulting-Deutsch, keine Buzzwords |

---

## 3. Bewertungsreihenfolge

Um Bias zu minimieren:

1. **Wähle eine Aufgabe** (z.B. A1 Entscheidungsvorlage N)
2. **Lies alle Modell-Antworten** für diese Aufgabe erst durch
3. **Bewerte dann alle**, nicht sofort nach dem Lesen
4. **Wechsle die Aufgabe**, nicht das Modell

Nicht empfohlen: Alle 12 Aufgaben von Claude Opus 4.6 bewerten, dann alle von GPT-5.2. Das erzeugt Anker-Bias.

---

## 4. Sonderfälle

### 4.1 Antwort auf Englisch (bei N-Variante)

Wenn ein Modell bei der N-Variante (kein System-Prompt) auf Englisch antwortet:
- Sprachqualität automatisch 1
- Inhaltlich trotzdem bewerten
- In Bewertungsnotiz vermerken: "Antwort auf Englisch"

### 4.2 Antwort mit Bullet Points (bei P-Variante)

Der System-Prompt verbietet Bullet Points. Wenn trotzdem vorhanden:
- Sprachqualität um 1 Punkt abziehen (Anweisung ignoriert)
- Inhaltlich trotzdem bewerten

### 4.3 Antwort deutlich zu kurz oder zu lang

P-Variante fordert 400–800 Wörter. Bei starker Abweichung:
- Unter 200 Wörter: Substanz maximal 3 (kann nicht tiefgehend sein)
- Über 1.500 Wörter: Praxistauglichkeit um 1 Punkt abziehen (GF hat keine Zeit für Romane)

### 4.4 Halluzinierte Quellen

Wenn das Modell Studien oder Zahlen erfindet:
- Präzision automatisch 1
- In Bewertungsnotiz konkret benennen, was halluziniert wurde

### 4.5 Selbstreferenz als KI

Wenn das Modell sagt "Als KI-Modell kann ich...":
- Sprachqualität um 1 Punkt abziehen
- P-Variante: Urteilskraft um 1 Punkt abziehen (System-Prompt explizit verletzt)

---

## 5. Gewichteter Score berechnen

```
Score = (Substanz × 0.25) + (Präzision × 0.25) + 
        (Praxistauglichkeit × 0.20) + (Urteilskraft × 0.20) + 
        (Sprachqualität × 0.10)
```

**Beispiel:**
Substanz 4, Präzision 3, Praxis 4, Urteil 5, Sprache 4
= (4×0.25) + (3×0.25) + (4×0.20) + (5×0.20) + (4×0.10)
= 1.00 + 0.75 + 0.80 + 1.00 + 0.40
= **3,95**
→ Klasse: Qualifizierter Zuarbeiter

---

## 6. Bewertungsnotiz

Jede Bewertung bekommt eine kurze Notiz (1–2 Sätze). Fokus auf:
- Was war die größte Stärke?
- Was war die größte Schwäche?
- Gab es Überraschungen (positiv oder negativ)?

**Beispiele:**
- "Erkennt Abhängigkeitsrisiko bei Exklusivvertrag, übersieht aber steuerliche Implikation."
- "Starke Quellenanalyse, aber People-Pleasing im Fazit – traut sich kein klares Urteil."
- "Antwortet auf Englisch trotz deutschem Prompt. Inhaltlich solide."
