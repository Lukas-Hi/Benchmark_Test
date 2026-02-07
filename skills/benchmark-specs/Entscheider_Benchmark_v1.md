# Entscheider-Benchmark: Strategische KI-Kompetenz im Praxistest

**HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46**

Version 1.0 | 6. Februar 2026
Gerald T. Pögl | KI-Sparringspartner für Entscheider im DACH-Raum

---

## 1. Motivation

Wissenschaftliche Benchmarks messen, was Forscher interessiert: mathematisches Reasoning, Code-Generierung, Wissensabfragen auf PhD-Niveau. Der GDPval-Benchmark (OpenAI, Oktober 2025) war ein erster Schritt in Richtung wirtschaftlich relevanter Aufgaben – 44 Berufe, echte Arbeitsprodukte, Expert:innen-Bewertung.

Aber auch GDPval bildet nicht ab, was ein Geschäftsführer mit 15 oder 50 Mitarbeitern tatsächlich von einem KI-Modell braucht: strategische Denkunterstützung. Keine Examensantworten, keine Code-Reviews – sondern die Fähigkeit, unvollständige Informationen zu strukturieren, Risiken zu erkennen, Zahlen zu interpretieren und Widersprüche aufzudecken.

Dieser Benchmark schließt diese Lücke. Sechs Aufgaben, die jede Geschäftsführung kennt – branchenunabhängig, praxisnah, reproduzierbar.

---

## 2. Design-Prinzipien

| Prinzip | Umsetzung |
|---------|-----------|
| **Praxisnähe** | Jede Aufgabe bildet eine reale strategische Situation ab, die branchenübergreifend vorkommt. |
| **Reproduzierbarkeit** | Identischer Prompt, identische Quelldokumente, standardisierte Bewertungskriterien. Jedes Modell wird unter gleichen Bedingungen getestet. |
| **Echte Daten** | Quelldokumente sind öffentlich verfügbare Berichte und Finanzpublikationen – als PDF beigelegt, nicht als Copy-Paste im Prompt. |
| **Strategischer Fokus** | Keine operativen Aufgaben (E-Mails, Textverbesserung). Ausschließlich Aufgaben, die Urteilskraft, Risikoerkennung und analytisches Denken erfordern. |
| **DACH-Relevanz** | Alle Prompts auf Deutsch. Bewertung berücksichtigt Sprachqualität und kulturelle Passung für den deutschsprachigen Geschäftskontext. |
| **Transparenz** | Prompts, Quelldokumente, Bewertungsmatrix und Ergebnisse werden vollständig offengelegt. |

---

## 3. Testbedingungen

| Parameter | Vorgabe |
|-----------|---------|
| **Sprache** | Alle Prompts auf Deutsch. Antwort wird auf Deutsch erwartet. |
| **Chat-Kontext** | Neuer Chat. Kein System-Prompt, keine Custom Instructions, keine Projektdateien. Jedes Modell startet bei Null. |
| **Dokument-Input** | Quelldokumente werden als Datei-Upload beigelegt (PDF). Kein Copy-Paste in den Prompt. |
| **Temperatur** | Standard-Einstellung des jeweiligen Anbieters. Keine manuelle Anpassung. |
| **Reasoning-Modus** | Standard (kein „Extended Thinking", kein „Deep Research", kein „Reasoning Effort High"). |
| **Durchläufe** | Ein Durchlauf pro Aufgabe. Bei Ausreißern (>5 Punkte Abweichung vom Erwartungswert) optionaler zweiter Durchlauf, beide Ergebnisse werden dokumentiert. |
| **Zeitstempel** | Jeder Test wird mit Datum und Modellversion dokumentiert. |

---

## 4. Bewertungsmatrix

Jede Aufgabe wird auf fünf Kriterien bewertet. Skala 1–5 pro Kriterium.

### 4.1 Bewertungskriterien

| Kriterium | Gewichtung | 1 (mangelhaft) | 3 (solide) | 5 (exzellent) |
|-----------|------------|----------------|------------|----------------|
| **Substanz** | 25% | Oberflächlich, generisch, keine eigene Analyse | Brauchbare Analyse, erkennbare Logik | Tiefgehend, differenziert, eigenständige Schlüsse |
| **Präzision** | 25% | Faktenfehler, Halluzinationen, falsche Zahlen | Weitgehend korrekt, kleinere Unschärfen | Fehlerfrei, saubere Trennung Fakt vs. Einschätzung |
| **Praxistauglichkeit** | 20% | Theoretisch, nicht umsetzbar, generische Ratschläge | Brauchbare Ansätze, teilweise konkret | Direkt umsetzbar, auf Entscheider-Realität zugeschnitten |
| **Urteilskraft** | 20% | Nickt alles ab, keine kritische Distanz, People-Pleasing | Erkennt offensichtliche Probleme | Benennt Risiken ungefragt, differenziert eigenständig, traut sich Widerspruch |
| **Sprachqualität (DE)** | 10% | Übersetzungsdeutsch, steif, Buzzword-lastig | Verständlich, aber generisch oder stilistisch flach | Natürliches Geschäftsdeutsch, DACH-tauglich, prägnant |

### 4.2 Scoring

| Ebene | Berechnung |
|-------|------------|
| **Pro Kriterium** | 1–5 Punkte |
| **Pro Aufgabe (gewichtet)** | (Substanz × 0,25) + (Präzision × 0,25) + (Praxis × 0,20) + (Urteilskraft × 0,20) + (Sprache × 0,10) = max. 5,0 |
| **Gesamt-Score** | Durchschnitt über alle 6 Aufgaben = max. 5,0 |

### 4.3 Ergebnisklassen

| Score | Klasse | Bedeutung |
|-------|--------|-----------|
| 4,5–5,0 | **Sparringspartner** | Eigenständiges strategisches Denken. Brauchbar als erste Analyse für Entscheider. |
| 3,5–4,4 | **Qualifizierter Zuarbeiter** | Solide Vorarbeit, aber braucht menschliche Nachschärfung bei Urteilskraft und Kontext. |
| 2,5–3,4 | **Fleißiger Assistent** | Strukturiert und formuliert, aber wenig eigene Substanz. Spart Zeit, nicht Denkarbeit. |
| 1,0–2,4 | **Nicht empfehlenswert** | Unzuverlässig für strategische Aufgaben. Halluzinationen, generische Antworten, kein Mehrwert. |

---

## 5. Die sechs Aufgaben

---

### Aufgabe 1: Entscheidungsvorlage

**Kategorie:** Entscheidungsunterstützung bei Unsicherheit
**Quelldokument:** Keines – szenariobasiert
**Erwartete Bearbeitungszeit (Mensch):** 45–90 Minuten

**Prompt:**

> Sie sind strategischer Berater der Geschäftsführung. Ein mittelständisches Großhandelsunternehmen (45 Mitarbeiter, Jahresumsatz 12 Mio. EUR, Standort Wien) steht vor folgender Entscheidung:
>
> Ein langjähriger Lieferant bietet exklusiv an, als erster Handelspartner in Österreich eine neue Produktlinie zu vertreiben. Die Konditionen: 42% Marge, Exklusivität auf 18 Monate befristet, Mindestabnahme 200.000 EUR im ersten Jahr. Bedingung: Das Unternehmen müsste dafür eine bestehende Produktlinie aus dem Sortiment nehmen (28% Marge, aber stabil, 15% des Umsatzes).
>
> Der Geschäftsführer tendiert dazu, das Angebot anzunehmen. Er fragt Sie: „Übersehe ich etwas?"
>
> Erstellen Sie eine strukturierte Entscheidungsvorlage. Benennen Sie, was für die Entscheidung spricht, was dagegen, und welche Informationen noch fehlen, bevor man verantwortungsvoll entscheiden kann.

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Erkennt versteckte Risiken (Post-Exklusivität, Kundenverlust, Kapitalbindung). Identifiziert fehlende Informationen aktiv. Hinterfragt die Tendenz des GF. Gewichtet Pro/Contra statt bloßer Auflistung. |
| 3 | Strukturierte Pro-Contra-Analyse, erkennt die offensichtlichen Risiken, aber keine tiefere Durchdringung. Fehlende Informationen werden teilweise benannt. |
| 1 | Generische Liste. Bestätigt die Tendenz des GF. Vergisst die Frage nach dem Ende der Exklusivität. Halluziniert Marktdaten. |

---

### Aufgabe 2: Strategische Zusammenfassung

**Kategorie:** Informationsverdichtung für Führungsentscheidungen
**Quelldokument:** BCG AI Radar 2026 – Executive Summary (PDF, öffentlich verfügbar)
**Erwartete Bearbeitungszeit (Mensch):** 60–120 Minuten

**Prompt:**

> Sie beraten den Geschäftsführer eines mittelständischen Handelsunternehmens in Österreich (60 Mitarbeiter). Er hat keine Zeit, den beigefügten Bericht selbst zu lesen, und bittet Sie:
>
> „Fassen Sie mir zusammen, was in diesem Bericht für mein Unternehmen relevant ist. Ich brauche keine Nacherzählung – ich brauche Ihre Einschätzung, was davon mich betrifft und was ich ignorieren kann."
>
> Erstellen Sie eine strategische Zusammenfassung (max. 500 Wörter).

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Trennt Rauschen von Signal. Übersetzt globale Trends in den KMU-Kontext. Benennt die 2–3 wirklich relevanten Erkenntnisse und begründet die Auswahl. Warnt, wo der Bericht für die Unternehmensgröße nicht übertragbar ist. |
| 3 | Brauchbare Zusammenfassung mit einigen Kontextbezügen. Priorisiert, aber nicht konsequent genug. Mischung aus Nacherzählung und eigener Einschätzung. |
| 1 | Absatz-für-Absatz-Zusammenfassung ohne Priorisierung. Keine Kontextualisierung für KMU. Halluziniert Inhalte, die nicht im Dokument stehen. |

---

### Aufgabe 3: Kritisches Hinterfragen

**Kategorie:** Qualitätssicherung strategischer Pläne
**Quelldokument:** Keines – szenariobasiert
**Erwartete Bearbeitungszeit (Mensch):** 30–60 Minuten

**Prompt:**

> Ein befreundeter Unternehmer zeigt Ihnen seinen Plan für die KI-Einführung in seinem Unternehmen (Ingenieurbüro, 25 Mitarbeiter, Schwerpunkt Gebäudetechnik):
>
> „Wir haben uns für folgende Strategie entschieden:
> 1. Wir kaufen 25 ChatGPT-Team-Lizenzen für alle Mitarbeiter (ca. 7.500 EUR/Jahr).
> 2. Jeder soll ChatGPT in seinem Arbeitsbereich selbstständig nutzen und eigene Anwendungsfälle finden.
> 3. Nach sechs Monaten evaluieren wir, welche Abteilungen den größten Nutzen haben, und investieren dort weiter.
> 4. Wir haben bewusst auf externe Berater verzichtet – wir wollen das organisch wachsen lassen."
>
> Er fragt Sie: „Was halten Sie davon?"
>
> Geben Sie eine ehrliche, konstruktive Einschätzung. Benennen Sie, was funktionieren kann, was problematisch ist, und was Sie anders machen würden.

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Erkennt strukturelle Schwächen (kein Use Case, kein Skill-Aufbau, Schatten-KI-Risiko, Evaluierung ohne Baseline). Würdigt, was richtig ist (Budget, Experimentierbereitschaft). Bietet konkrete Alternativen. Adressiert Datenschutz/Compliance. |
| 3 | Erkennt einige Schwächen, bleibt aber bei den offensichtlichen. Ton ist konstruktiv, aber Alternativen sind generisch. |
| 1 | „Solider Ansatz!" ohne Substanz. Oder: Totalkritik ohne Anerkennung. Generische KI-Tipps statt szenariobezogener Analyse. |

---

### Aufgabe 4: Szenario-Analyse

**Kategorie:** Strategische Planung unter Unsicherheit
**Quelldokument:** Keines – szenariobasiert
**Erwartete Bearbeitungszeit (Mensch):** 60–120 Minuten

**Prompt:**

> Sie beraten die Geschäftsführerin eines Immobilienmakler-Unternehmens in Wien (8 Mitarbeiter, Schwerpunkt Zinshaus-Vermittlung). Der Wiener Zinshausmarkt hat sich 2024/2025 deutlich abgekühlt – Transaktionsvolumen und Preise sind gesunken.
>
> Sie steht vor der Frage: Soll sie jetzt in KI-gestützte Prozesse investieren (automatisierte Exposé-Erstellung, KI-basierte Marktanalyse, automatisierte Due-Diligence-Vorprüfung), oder abwarten, bis sich der Markt erholt?
>
> Sie sagt: „Ich will keine Glaskugel. Ich will verstehen, welche Szenarien möglich sind und was sie jeweils für meine Entscheidung bedeuten."
>
> Entwickeln Sie drei realistische Szenarien für die nächsten 18 Monate und leiten Sie für jedes Szenario eine Handlungsempfehlung ab.

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Drei distinkte, plausible Szenarien mit unterschiedlichen Handlungsempfehlungen. Verknüpft KI-Investition mit Marktszenario. Benennt Annahmen explizit. Berücksichtigt die Unternehmensgröße (8 MA). |
| 3 | Drei Szenarien vorhanden, aber wenig distinkt. Empfehlungen sind ähnlich. Annahmen teilweise implizit. |
| 1 | Lineare Empfehlung ohne Szenario-Differenzierung. Drei Szenarien, die zur gleichen Empfehlung führen. Halluziniert Marktdaten. |

---

### Aufgabe 5: Widerspruchserkennung

**Kategorie:** Quellenvalidierung und kritische Analyse
**Quelldokumente:** Zwei Berichte mit widersprüchlichen Aussagen zum selben Thema (z.B. KI-Nutzung in Unternehmen), als PDF beigelegt.
**Erwartete Bearbeitungszeit (Mensch):** 45–90 Minuten

*Empfohlene Dokumentenkombination: Statistik Austria ICT-Erhebung 2024/2025 (20% KI-Nutzung in Österreich) + Microsoft Work Trend Index 2025 (75%+ nutzen KI am Arbeitsplatz). Die Diskrepanz entsteht durch unterschiedliche Definitionen, Stichproben und Erhebungsmethoden.*

**Prompt:**

> Ich habe Ihnen zwei Berichte beigelegt, die beide das Thema KI-Nutzung in Unternehmen behandeln.
>
> Widersprechen sich die beiden Berichte? Wenn ja, wo genau – und wie erklären Sie sich die Unterschiede? Wenn nein, wie passen die Aussagen zusammen?
>
> Ich brauche eine klare Analyse, nicht eine diplomatische Zusammenführung.

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Identifiziert die konkreten Widersprüche. Erklärt Ursachen (Definition, Stichprobe, Region, Zeitraum). Bewertet Verlässlichkeit kontextabhängig. Benennt verbleibende Ambiguität. |
| 3 | Erkennt den Hauptwiderspruch, erklärt ihn aber nur oberflächlich. Bevorzugt eine Quelle ohne klare Begründung. |
| 1 | Glättet Widersprüche. Oder: Gibt einer Quelle ohne Begründung den Vorzug. Vermutungen statt Analyse. |

---

### Aufgabe 6: Zahlenanalyse

**Kategorie:** Finanzanalyse und datengestützte Strategiebewertung
**Quelldokument:** Quartalsbericht eines börsennotierten Unternehmens (PDF). Empfehlung: Immofinanz, CA Immobilien oder Verbund (österreichischer Bezug), alternativ ein S&P-500-Unternehmen.
**Erwartete Bearbeitungszeit (Mensch):** 90–180 Minuten

**Prompt:**

> Ich habe Ihnen den aktuellen Quartalsbericht von [Unternehmen] beigelegt. Sie beraten einen Investor, der eine mögliche Beteiligung prüft.
>
> Analysieren Sie die wesentlichen Finanzkennzahlen:
> 1. Wie hat sich das Unternehmen im Vergleich zum Vorjahresquartal entwickelt?
> 2. Welche Kennzahlen sind positiv, welche geben Anlass zur Vorsicht?
> 3. Gibt es Auffälligkeiten, die bei oberflächlicher Betrachtung leicht übersehen werden?
>
> Ich brauche eine Analyse, keine Nacherzählung der Bilanz.

**Bewertungsanker:**

| Score | Beschreibung |
|-------|-------------|
| 5 | Korrekte Extraktion der Kernkennzahlen. Veränderungsraten stimmen. Erkennt nicht-offensichtliche Muster (Margendrift, Sondereffekte, Working-Capital-Veränderungen). Trennt Fakt von Interpretation. |
| 3 | Wichtigste Zahlen korrekt extrahiert. Analyse bleibt bei den Headline-Kennzahlen. Keine groben Fehler, aber auch keine Tiefe. |
| 1 | Rechenfehler. Nur Headline-Zahlen übernommen. Halluziniert Vergleichszahlen. Generische Bewertung ohne Bezug zum konkreten Unternehmen. |

---

## 6. Getestete Modelle (Erstdurchlauf)

| Modell | Anbieter | Version | Zugangspunkt | Testdatum |
|--------|----------|---------|-------------|-----------|
| Claude Opus 4.6 | Anthropic | claude-opus-4-6 | claude.ai (Pro) | Feb 2026 |
| Claude Opus 4.5 | Anthropic | claude-opus-4-5 | claude.ai (Pro) | Feb 2026 |
| Claude Sonnet 4.5 | Anthropic | claude-sonnet-4-5 | claude.ai (Pro) | Feb 2026 |
| GPT-5.2 | OpenAI | gpt-5.2 | ChatGPT Plus | Feb 2026 |
| Gemini 2.5 Pro | Google | gemini-2.5-pro | Gemini Advanced | Feb 2026 |

*Weitere Modelle können ergänzt werden. Voraussetzung: identische Testbedingungen.*

---

## 7. Ergebnistabelle (Template)

### 7.1 Gesamtübersicht

| Modell | A1 | A2 | A3 | A4 | A5 | A6 | **Ø Gesamt** |
|--------|-----|-----|-----|-----|-----|-----|-------------|
| Opus 4.6 | — | — | — | — | — | — | **—** |
| Opus 4.5 | — | — | — | — | — | — | **—** |
| Sonnet 4.5 | — | — | — | — | — | — | **—** |
| GPT-5.2 | — | — | — | — | — | — | **—** |
| Gemini 2.5 | — | — | — | — | — | — | **—** |

### 7.2 Detailbewertung (pro Aufgabe, pro Modell)

| Kriterium | Gewicht | Score | Gewichtet |
|-----------|---------|-------|-----------|
| Substanz | 25% | /5 | |
| Präzision | 25% | /5 | |
| Praxistauglichkeit | 20% | /5 | |
| Urteilskraft | 20% | /5 | |
| Sprachqualität (DE) | 10% | /5 | |
| **Gesamt** | | | **/5,0** |

*Anmerkungen zur Bewertung werden als Freitext dokumentiert.*

---

## 8. Quelldokumente

| Aufgabe | Dokument | Quelle | Format |
|---------|----------|--------|--------|
| A2 | BCG AI Radar 2026 – Executive Summary | bcg.com | PDF |
| A5 | Statistik Austria ICT-Erhebung 2024/2025 | statistik.at | PDF |
| A5 | Microsoft Work Trend Index 2025 | microsoft.com | PDF |
| A6 | Quartalsbericht (Unternehmen TBD) | IR-Website | PDF |

*Aufgaben 1, 3, 4 sind szenariobasiert und benötigen keine externen Dokumente.*

---

## 9. Limitationen

1. **Einzelbewerter.** Die Bewertung erfolgt durch eine Person, nicht durch ein Expert:innen-Panel. Sie reflektiert die Perspektive eines KI-Strategieberaters mit Geschäftsführungs-Erfahrung.

2. **Subjektive Kriterien.** „Urteilskraft" und „Praxistauglichkeit" enthalten bewusst subjektive Elemente. Strategische Beratungsqualität lässt sich nicht vollständig automatisiert bewerten – das ist kein Mangel, sondern der Punkt.

3. **Stichprobe n=1.** Ein Durchlauf pro Modell zeigt eine Momentaufnahme, kein statistisch belastbares Mittel. Varianz der Modellantworten wird nicht erfasst.

4. **Keine API-Standardisierung.** Verschiedene Zugangspunkte (claude.ai, ChatGPT, Gemini) haben unterschiedliche Defaults. Diese Unterschiede können Ergebnisse beeinflussen.

5. **Möglicher Trainingsdaten-Bias.** Modelle, die verwendete Quelldokumente in ihren Trainingsdaten hatten, könnten bei Aufgaben 2, 5 und 6 bevorteilt sein. Der Effekt wird durch spezifische Fragestellungen (Analyse statt Wiedergabe) minimiert, aber nicht eliminiert.

---

## 10. Geplante Erweiterungen

- **v1.1:** Quelldokumente finalisiert und als Download-Paket bereitgestellt
- **v1.2:** Erstdurchlauf mit allen fünf Modellen, Ergebnisse dokumentiert
- **v2.0:** Optional zweiter Bewerter für Inter-Rater-Reliabilität, erweiterte Modellliste

---

## 11. Methodik-Referenzen

- GDPval: Patwardhan et al. (2025). „Evaluating AI Model Performance on Real-World Economically Valuable Tasks." OpenAI. 44 Berufe, 1.320 Aufgaben, Expert:innen-Bewertung.
- Artificial Analysis Intelligence Index v4.0 (2026). 10 Evaluierungen, Fokus auf wirtschaftlich nützliche Handlungen statt akademischer Tests.
- BetterBench (Stanford, 2025). Meta-Framework zur Bewertung von Benchmark-Qualität.

---

Gerald T. Pögl
KI-Sparringspartner für Entscheider im DACH-Raum

#VisiON #KI_Sparring #unternehmerische_Weichenstellung
