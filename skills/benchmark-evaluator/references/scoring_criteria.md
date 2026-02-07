# Scoring-Kriterien: Entscheider-Benchmark
Referenz für den Benchmark-Evaluator. Quelle: docs/scoring_guide.md

## Gewichtung

| Kriterium | Gewicht |
|-----------|---------|
| Substanz | 25% |
| Präzision | 25% |
| Praxistauglichkeit | 20% |
| Urteilskraft | 20% |
| Sprachqualität DE | 10% |

Formel: `(Sub×0.25) + (Präz×0.25) + (Prax×0.20) + (Urt×0.20) + (Spr×0.10)`

## Substanz (25%)

Analytische Abdeckung: Wie viele relevante Aspekte identifiziert, wie tief durchdacht, welche nicht-offensichtlichen Zusammenhänge hergestellt?

Abgrenzung zu Urteilskraft: Versteckten Risikofaktor identifizieren → Substanz. Dem GF sagen, seine Tendenz sei voreilig → Urteilskraft. Substanz = Was wurde analysiert? Urteilskraft = Wie wurde Position bezogen?

| 1 | Generisch, wiederholt nur den Prompt |
| 2 | Nennt relevante Punkte, bleibt oberflächlich |
| 3 | Solide Analyse, deckt Kernpunkte ab, Standardüberlegungen |
| 4 | Tiefgehend, eigene Einordnung, Zusammenhänge die nicht im Prompt stehen |
| 5 | Nicht-offensichtliche Punkte, versteckte Risiken, Fragen die der GF nicht gestellt hat |

## Präzision (25%)

Faktische Korrektheit und Trennschärfe Fakt/Einschätzung.

| 1 | Faktenfehler, Halluzinationen, erfundene Zahlen/Studien |
| 2 | Überwiegend korrekt, aber vage oder ungeprüft |
| 3 | Korrekt, aber keine klare Trennung Fakt vs. Einschätzung |
| 4 | Korrekt, Fakt und Einschätzung klar getrennt |
| 5 | Fehlerfrei, benennt eigene Unsicherheit und Datenlücken |

## Praxistauglichkeit (20%)

Kann ein GF damit sofort etwas anfangen?

| 1 | Theoretisch, abstrakt, nicht umsetzbar |
| 2 | Richtung stimmt, zu allgemein |
| 3 | Brauchbare Hinweise, nicht auf Kontext zugeschnitten |
| 4 | Konkret, auf den spezifischen Kontext bezogen (Branche, Größe, Standort) |
| 5 | Direkt umsetzbar, kennt Entscheider-Realität und KMU-Constraints |

## Urteilskraft (20%)

Positionierung und Haltung: Traut sich das Modell eine klare Empfehlung, widerspricht es dem Auftraggeber, benennt es Denkfehler ungefragt?

Abgrenzung zu Substanz: Substanz = analytische Breite/Tiefe (was erkannt). Urteilskraft = Haltung gegenüber dem Auftraggeber (wie damit umgegangen). Modell kann alle Risiken identifizieren (Substanz 5) aber diplomatisch ausweichen (Urteilskraft 3).

| 1 | Bestätigt alles, kein Widerspruch |
| 2 | Erwähnt Risiken pflichtgemäß ohne Substanz |
| 3 | Benennt konkrete Schwächen, relativiert sofort |
| 4 | Klare Position, benennt Denkfehler des Auftraggebers |
| 5 | Widerspricht ungefragt, zeigt blinde Flecken, identifiziert Informationslücken |

## Sprachqualität Deutsch (10%)

Natürliches Geschäftsdeutsch vs. Übersetzungsdeutsch.

| 1 | Übersetzungsdeutsch, Buzzwords, unnatürlich |
| 2 | Grammatisch korrekt, steif, klingt nach Übersetzung |
| 3 | Solides Deutsch, ohne Charakter, Beratungs-Template |
| 4 | Natürliches Geschäftsdeutsch, wie Gespräch unter Führungskräften |
| 5 | Exzellent, DACH-tauglich, österreichische Pragmatik, prägnant |

## Ergebnisklassen

| 4.5–5.0 | Sparringspartner – Denkpartner für strategische Entscheidungen |
| 3.5–4.4 | Qualifizierter Zuarbeiter – brauchbare Vorarbeit, braucht Führung |
| 2.5–3.4 | Fleißiger Assistent – Routinearbeit ja, Strategie überfordert |
| 1.0–2.4 | Nicht empfehlenswert – für Entscheider-Aufgaben ungeeignet |

## Sonderfälle

| Sonderfall | Auswirkung |
|-----------|-----------|
| Antwort auf Englisch (N-Variante) | Sprachqualität = 1, Rest normal bewerten |
| Bullet Points trotz Verbot (P-Variante) | Sprachqualität −1 |
| Unter 200 Wörter | Substanz max. 3 |
| Über 1.500 Wörter | Praxistauglichkeit −1 |
| Halluzinierte Quellen/Zahlen | Präzision = 1, in Notiz benennen |
| Selbstreferenz als KI ("Als KI-Modell...") | Sprachqualität −1, bei P auch Urteilskraft −1 |

## Sprachqualität als Schwellenkriterium

Sprachqualität < 3 → Gesamtscore gedeckelt auf maximal 3,4 ("Fleißiger Assistent").
Anwendung: Zuerst Score normal berechnen. Dann: min(Score, 3.4) falls Sprache < 3.

## Bewertungsreihenfolge (Bias-Kontrolle)

1. Eine Aufgabe wählen (z.B. A1_N)
2. Alle Modell-Antworten für diese Aufgabe erst durchlesen
3. Dann alle bewerten (nicht sofort nach dem Lesen)
4. Aufgabe wechseln, nicht Modell
