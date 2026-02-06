# Methodik: Entscheider-Benchmark
**HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46**
Stand: 6. Februar 2026

---

## 1. Design-Prinzipien

Dieser Benchmark orientiert sich an etablierten Methodik-Vorbildern, adaptiert sie aber für einen spezifischen Anwendungsfall: strategische Führungsarbeit im KMU-Kontext.

### 1.1 Referenz-Benchmarks

**GDPval (OpenAI, Oktober 2025)**
- 44 Berufe, echte Arbeitsprodukte, Experten-Bewertung
- Grundsatz: Teste mit realen Aufgaben, nicht mit synthetischen
- Übernommen: Praxisnahe Szenarien, standardisierte Bewertung, Limitationen transparent benennen
- Nicht übernommen: Skalierung auf 1.320 Tasks (für unser Setting unrealistisch)

**Artificial Analysis Intelligence Index v4.0**
- >10 Wiederholungen pro Modell für 95%-Konfidenzintervall (±1%)
- Übernommen: Multi-Run-Methodik mit Konsistenz-Messung
- Nicht übernommen: Automatisierte Bewertung (bei nuancierten Strategieantworten unzureichend)

**BetterBench (Stanford, 2025)**
- Kritik an existierenden Benchmarks: fehlende Reproduzierbarkeit, Score-Inflation
- Übernommen: Testbedingungen explizit dokumentieren, Temperatur fixieren
- Nicht übernommen: Head-to-Head-Vergleich (wir nutzen absolute Scores)

**MLPerf Inference**
- Industriestandard für Hardware-Benchmarks, strenge Reproduzierbarkeit
- Übernommen: Dokumentation aller Parameter, identische Bedingungen für alle Teilnehmer

### 1.2 Kernprinzipien

1. **Praxisnähe:** Jede Aufgabe bildet eine reale Entscheidungssituation ab, wie sie ein GF im DACH-Raum kennt.
2. **Reproduzierbarkeit:** Temperatur 0, identische Prompts, dokumentierte Modellversionen. Jeder kann den Test wiederholen.
3. **Echte Daten:** Dokumentbasierte Aufgaben nutzen publizierte Berichte (BCG, Statistik Austria, Microsoft), keine synthetischen Texte.
4. **DACH-Relevanz:** Szenarien in Wien/Graz, österreichische Unternehmen, deutsche Sprache, EU-Regulatorik.
5. **Transparenz:** Alle Prompts, Bewertungskriterien, Limitationen und verworfene Alternativen werden veröffentlicht.

---

## 2. Testbedingungen

| Parameter | Wert | Begründung |
|-----------|------|------------|
| Sprache | Deutsch | Zielgruppe DACH, testet Sprachqualität |
| Temperatur | 0 | Maximale Reproduzierbarkeit |
| Max Tokens | 4.096 | Ausreichend für 400–800 Wörter + Overhead |
| Runs pro Modell×Aufgabe | 10 | Statistisch belastbar (vgl. Artificial Analysis) |
| Parallele Requests | Max 3 | Rate-Limit-Schutz |
| Delay zwischen Requests | 2 Sekunden | Rate-Limit-Schutz |
| Timeout | 300 Sekunden | Großzügig für Reasoning-Modelle |
| Kontext | Neuer Chat pro Request | Keine Vorgeschichte, kein Memory |

### 2.1 Warum Temperatur 0?

Bei Temperatur 0 sollte ein Modell bei identischem Input identische Outputs liefern. In der Praxis variieren Antworten trotzdem leicht (GPU-Parallelismus, Batching, Provider-spezifisches Sampling). Die 10 Runs messen diese Restvarianz. Ein Coefficient of Variation (CV) unter 5% gilt als sehr konsistent, 5–15% als normal, über 15% als instabil.

### 2.2 Warum kein Chat-Kontext?

Jeder Request ist ein isolierter, neuer Chat. Kein System-Prompt aus vorherigen Interaktionen, kein Memory, keine Tools. Das simuliert die Realität: Ein GF öffnet ChatGPT/Claude und stellt eine Frage. Die N-Variante (Normal-User) bildet genau das ab.

---

## 3. Das Dual-Prompt-Design

### 3.1 Rationale

Die zentrale Hypothese: **Prompt-Kompetenz ist der stärkste Hebel für Output-Qualität – stärker als die Modellwahl.**

Um das zu testen, bekommt jedes Modell jede Aufgabe in zwei Varianten:

**N (Normal-User):** Wie ein typischer Geschäftsführer die Frage stellen würde.
- Kein System-Prompt
- Keine Struktur im Prompt
- Natürliche Sprache, oft unvollständiger Kontext
- Implizite Erwartungen ("sag mir was ich wissen muss")

**P (Power-User):** Optimierter Prompt nach Prompt-Engineering-Prinzipien.
- Vollständiger System-Prompt (Rolle, Sprache, Format, Haltung, Länge)
- Strukturierter Aufgaben-Prompt: KONTEXT → SITUATION → AUFTRAG
- Explizite Teilaufgaben ("Erstens... Zweitens... Drittens...")
- Anti-People-Pleasing-Guardrails
- Trennungsanweisungen (Fakt vs. Einschätzung)

### 3.2 Messbare Deltas

Für jedes Modell ergeben sich drei Messwerte pro Aufgabe:
- **Score N:** Leistung bei normalem Prompt
- **Score P:** Leistung bei optimiertem Prompt
- **Delta (P–N):** Wie viel holt Prompt-Kompetenz heraus

Ein hohes Delta bedeutet: Das Modell hat Potenzial, das ohne gute Prompts brachliegt.
Ein niedriges Delta bedeutet: Das Modell liefert auch bei schlechten Prompts gute Ergebnisse (oder ist generell schwach).

### 3.3 Content-Implikation

Das Delta ist die Story für LinkedIn:
- "Modell X verbessert sich um 40% wenn der Prompt stimmt"
- "Das teuerste Modell mit schlechtem Prompt schlägt das billigste mit gutem Prompt nicht"
- "Kompetenz schlägt Budget – und hier sind die Zahlen"

---

## 4. Bewertungsmatrix

### 4.1 Fünf Kriterien

| Kriterium | Gewicht | Was wird gemessen |
|-----------|---------|-------------------|
| **Substanz** | 25% | Tiefe der Analyse, eigenständige Schlüsse, über das Offensichtliche hinaus |
| **Präzision** | 25% | Faktentreue, keine Halluzinationen, Fakt vs. Einschätzung getrennt |
| **Praxistauglichkeit** | 20% | Direkt umsetzbar, kennt Entscheider-Realität, konkret statt abstrakt |
| **Urteilskraft** | 20% | Benennt Risiken ungefragt, kein People-Pleasing, traut sich Widerspruch |
| **Sprachqualität (DE)** | 10% | Natürliches Geschäftsdeutsch, keine Anglizismen, DACH-tauglich |

### 4.2 Bewertungsskala (1–5)

| Score | Label | Beschreibung |
|-------|-------|-------------|
| 1 | Mangelhaft | Oberflächlich, generisch, Faktenfehler, nicht umsetzbar |
| 2 | Schwach | Einige relevante Punkte, aber lückenhaft oder unpräzise |
| 3 | Solide | Brauchbar, deckt Kernpunkte ab, keine groben Fehler |
| 4 | Gut | Tiefgehend, praxisnah, eigenständige Einordnung |
| 5 | Exzellent | Überraschend gut, identifiziert nicht-offensichtliche Punkte, GF würde das sofort nutzen |

### 4.3 Gewichteter Score

```
Score_gewichtet = (Substanz × 0.25) + (Präzision × 0.25) + 
                  (Praxistauglichkeit × 0.20) + (Urteilskraft × 0.20) + 
                  (Sprachqualität × 0.10)
```

Maximal: 5,00 | Minimal: 1,00

### 4.4 Ergebnisklassen

| Score | Klasse | Bedeutung für einen Entscheider |
|-------|--------|--------------------------------|
| 4,5–5,0 | **Sparringspartner** | Kann als Denkpartner für strategische Entscheidungen dienen |
| 3,5–4,4 | **Qualifizierter Zuarbeiter** | Liefert brauchbare Vorarbeit, braucht aber Führung |
| 2,5–3,4 | **Fleißiger Assistent** | Erledigt Routinearbeit, bei Strategie überfordert |
| 1,0–2,4 | **Nicht empfehlenswert** | Für Entscheider-Aufgaben ungeeignet |

---

## 5. Bewertungsprozess

### 5.1 Vorgehen

1. Pro Modell×Aufgabe: Den Median-Run (gemessen an Antwortlänge) als Bewertungsgrundlage nehmen
2. Antwort lesen und gegen die 5 Kriterien bewerten (1–5 pro Kriterium)
3. Gewichteten Score berechnen
4. Kurze Bewertungsnotiz (1–2 Sätze: Was war gut, was war schwach)
5. Ergebnis in `bewertung_manual.csv` eintragen

### 5.2 Bias-Kontrolle

- **Reihenfolge-Bias:** Antworten nicht in der Reihenfolge der Modellliste bewerten, sondern randomisiert
- **Erwartungs-Bias:** Modellname ist sichtbar (Blind-Bewertung bei 12×18 Antworten unpraktikabel), aber bewusst dagegen steuern
- **Anker-Bias:** Nicht die erste Antwort als Maßstab nehmen. Alle Antworten einer Aufgabe erst lesen, dann bewerten.

### 5.3 Inter-Rater-Reliabilität

Aktuell: Einzelbewerter (Gerald). Bei Community-Beiträgen: Mehrere Bewerter möglich, aber kein standardisiertes Inter-Rater-Protokoll. Das ist eine explizite Limitation.

---

## 6. Statistische Auswertung

### 6.1 Konsistenz-Metriken (automatisch)

| Metrik | Formel | Interpretation |
|--------|--------|----------------|
| Antwortlänge Ø | mean(len(response)) über 10 Runs | Produktivität |
| Antwortlänge CV | stdev/mean × 100% | Konsistenz: 🟢 <5%, 🟡 5–15%, 🔴 >15% |
| Output-Tokens Ø | mean(output_tokens) | Token-Effizienz |
| Latenz Ø | mean(latency_seconds) | Geschwindigkeit |

### 6.2 Bewertungs-Metriken (manuell)

| Metrik | Berechnung |
|--------|------------|
| Score pro Aufgabe | Gewichteter Durchschnitt der 5 Kriterien |
| Gesamt-Score N | Durchschnitt über alle N-Aufgaben |
| Gesamt-Score P | Durchschnitt über alle P-Aufgaben |
| Delta (P–N) | Gesamt-Score P minus Gesamt-Score N |
| Leaderboard-Rang | Sortiert nach Gesamt-Score P (primär), dann Delta |

---

## 7. Limitationen

Diese Limitationen werden im README und in jeder Veröffentlichung transparent benannt:

1. **Kleine Aufgabenzahl:** 6 Aufgabenkategorien (12 mit N/P) decken nicht alle Führungsaufgaben ab. Repräsentativität ist begrenzt.
2. **Einzelbewerter:** Manuelle Bewertung durch eine Person. Subjektivität ist unvermeidbar. Inter-Rater-Reliabilität nicht gemessen.
3. **DACH-Fokus:** Szenarien, Sprache und Regulatorik sind auf den deutschsprachigen Raum zugeschnitten. Ergebnisse sind nicht global übertragbar.
4. **Statischer Zeitpunkt:** Benchmark zeigt Leistung zum Testzeitpunkt. Modelle werden laufend aktualisiert.
5. **Keine Kosten-Normalisierung:** Ein Modell das 10× teurer ist und 5% besser performt, erscheint im Leaderboard gleichwertig.
6. **Keine Tool-Use:** Getestet wird reines Text-in/Text-out. Web-Search, Code-Ausführung, Datei-Analyse sind deaktiviert.
7. **Temperatur-0-Artefakte:** Bei Temperatur 0 können einige Modelle in Wiederholungsschleifen geraten oder degenerierte Outputs produzieren.
8. **PDF-Extraktion:** Dokumentbasierte Aufgaben hängen von der Qualität der Text-Extraktion ab (pdfplumber). Tabellen und Grafiken gehen möglicherweise verloren.
