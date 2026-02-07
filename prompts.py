"""
Entscheider-Benchmark: Prompt-Definitionen v3.2
HID-LINKEDIN-BENCHMARK-PROMPTS-2026-02-06-ACTIVE-D9F2C3-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Zwei Prompt-Varianten pro Aufgabe:
  N = Normal-User (wie ein GF die Frage stellen würde, ohne Prompt-Engineering)
  P = Power-User (optimiert, mit System-Prompt, Guardrails, expliziten Anforderungen)

Die Power-User-Variante nutzt den SYSTEM_PROMPT.
Die Normal-User-Variante nutzt KEINEN System-Prompt – nur die nackte Frage.

Importiert von benchmark.py.

Änderungshistorie:
  v3.0 → v3.1: A5 (Widerspruchserkennung) komplett überarbeitet.
    Alte Quellen: Statistik Austria ICT 2025 + Microsoft Work Trend Index 2025
    Neue Quellen: Alan Turing AI Regulatory Framework + EU AI Act (Art. 4)
    Begründung: Regulierungsphilosophie UK vs. EU ergibt substanziellere
    Widersprüche und höheren Benchmark-Anspruch.
  v3.1 → v3.2: Chunk-Strategie für A5 implementiert.
    Beide Varianten auf Extrakte gesetzt (Zwischenstand).
  v3.2 → v3.3: A5 Dual-Input-Design finalisiert.
    N-Variante: Volle PDFs (88+144 Seiten, ~108k Tokens) – simuliert Normal-User
    der alles reinwirft ohne Vorbereitung.
    P-Variante: Kuratierte Extrakte (~4.4k Tokens) – simuliert Power-User
    der Chunking/Fokussierung als Vorbereitung macht.
    Kategorie aktualisiert: "Quellenvergleich und regulatorische Einordnung".
    Measures A5_P: Substanz > Urteilskraft > Präzision (Substanz primär).
"""

# ============================================
# System-Prompt (NUR für Power-User-Variante)
# ============================================

SYSTEM_PROMPT = """Du bist ein erfahrener Strategieberater, der mittelständische Unternehmen im DACH-Raum berät. Dein Auftraggeber ist ein Geschäftsführer oder Inhaber, der fundierte Einschätzungen braucht – keine Bestätigung seiner Meinung.

GRUNDREGELN:

1. SPRACHE: Antworte ausschließlich auf Deutsch. Verwende natürliches Geschäftsdeutsch, wie es in einem Gespräch unter Führungskräften in Wien oder München üblich wäre. Keine Anglizismen außer etablierten Fachbegriffen (KI, ROI, Due Diligence).

2. FORMAT: Antworte in Fließtext mit Absätzen. Keine Bullet Points, keine nummerierten Listen, keine Markdown-Formatierung (keine **, keine ##, keine ```). Zwischenüberschriften sind erlaubt, aber als einfacher Text ohne Sonderzeichen.

3. LÄNGE: Zwischen 400 und 800 Wörtern. Nicht kürzer, nicht länger.

4. HALTUNG: Du bist kein Ja-Sager. Wenn der Auftraggeber einen Denkfehler macht, sagst du das. Wenn Informationen fehlen, benennst du die Lücke. Wenn ein Plan Schwächen hat, zeigst du sie auf – auch ungefragt. Diplomatische Floskeln ohne Substanz sind nicht erwünscht.

5. FAKTEN VS. EINSCHÄTZUNG: Kennzeichne klar, was gesicherte Information ist und was deine Einschätzung. Formulierungen wie „Die Daten zeigen…" vs. „Meine Einschätzung ist…" oder „Das lässt sich nicht sicher beurteilen, aber…"

6. KEINE SELBSTREFERENZ: Erwähne nicht, dass du ein KI-Modell bist. Erwähne nicht deine Limitationen als Sprachmodell. Antworte als der Berater, der du in dieser Rolle bist."""


# ============================================
# Aufgaben
# ============================================

TASKS = {

    # ══════════════════════════════════════════
    # AUFGABE 1: Entscheidungsvorlage
    # ══════════════════════════════════════════

    "A1_Entscheidungsvorlage_N": {
        "title": "Entscheidungsvorlage (Normal)",
        "variant": "N",
        "category": "Entscheidungsunterstützung bei Unsicherheit",
        "docs": [],
        "measures": ["Substanz", "Urteilskraft", "Praxistauglichkeit"],
        "use_system_prompt": False,
        "prompt": """Ich leite einen Großhandel in Wien, 45 Mitarbeiter, 12 Mio Umsatz, Sanitär und Heizung. Ein Lieferant bietet mir an, exklusiv eine neue Produktlinie in Österreich zu vertreiben. 42% Marge, 18 Monate Exklusivität, Mindestabnahme 200.000 Euro im ersten Jahr. Dafür muss ich eine bestehende Linie rausnehmen die 28% Marge bringt und ca 15% vom Umsatz macht.

Ich tendiere dazu es anzunehmen. Übersehe ich was?""",
    },

    "A1_Entscheidungsvorlage_P": {
        "title": "Entscheidungsvorlage (Power)",
        "variant": "P",
        "category": "Entscheidungsunterstützung bei Unsicherheit",
        "docs": [],
        "measures": ["Substanz", "Urteilskraft", "Praxistauglichkeit"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Du berätst den Geschäftsführer eines Großhandelsunternehmens in Wien. Das Unternehmen hat 45 Mitarbeiter, einen Jahresumsatz von 12 Millionen Euro und vertreibt Sanitär- und Heizungskomponenten an Installationsbetriebe in Ostösterreich.

SITUATION:
Ein langjähriger Lieferant bietet dem Geschäftsführer exklusiv an, als erster Handelspartner in Österreich eine neue Produktlinie zu vertreiben. Die Konditionen im Detail:

– Marge: 42 Prozent (Bruttohandelsspanne)
– Exklusivität: 18 Monate für den österreichischen Markt
– Mindestabnahme: 200.000 Euro im ersten Jahr
– Bedingung: Eine bestehende Produktlinie muss aus dem Sortiment genommen werden. Diese Linie bringt aktuell 28 Prozent Marge und macht rund 15 Prozent des Gesamtumsatzes aus (ca. 1,8 Mio. Euro).

Der Geschäftsführer tendiert dazu, das Angebot anzunehmen. Er sagt: „42 Prozent Marge, Exklusivität, und der Lieferant ist verlässlich. Übersehe ich etwas?"

DEIN AUFTRAG:
Erstelle eine Entscheidungsvorlage für den Geschäftsführer. Konkret:

Erstens: Benenne, was für die Annahme spricht – aber geh über die offensichtliche Margenrechnung hinaus.

Zweitens: Benenne, was dagegen spricht oder problematisch sein könnte. Sei dabei konkret und praxisbezogen. Allgemeine Risiko-Hinweise wie „es gibt Unwägbarkeiten" sind wertlos.

Drittens: Identifiziere die Informationen, die für eine verantwortungsvolle Entscheidung noch fehlen. Was müsste der Geschäftsführer klären, bevor er unterschreibt?

Viertens: Gib eine Einschätzung, ob die Grundtendenz des Geschäftsführers nachvollziehbar ist oder ob du sie für voreilig hältst. Begründe das.""",
    },

    # ══════════════════════════════════════════
    # AUFGABE 2: Strategische Zusammenfassung
    # ══════════════════════════════════════════

    "A2_Strategische_Zusammenfassung_N": {
        "title": "Strategische Zusammenfassung (Normal)",
        "variant": "N",
        "category": "Informationsverdichtung für Führungsentscheidungen",
        "docs": ["pdf_files/ai-radar-2026-web-jan-2026-edit.pdf"],
        "measures": ["Substanz", "Präzision", "Praxistauglichkeit"],
        "use_system_prompt": False,
        "prompt": """Ich bin Geschäftsführer eines Handelsunternehmens in Österreich, 60 Mitarbeiter. Wir haben noch keine KI-Strategie. Kannst du mir den beigefügten Bericht zusammenfassen? Was davon ist für mich relevant und was kann ich ignorieren?""",
    },

    "A2_Strategische_Zusammenfassung_P": {
        "title": "Strategische Zusammenfassung (Power)",
        "variant": "P",
        "category": "Informationsverdichtung für Führungsentscheidungen",
        "docs": ["pdf_files/ai-radar-2026-web-jan-2026-edit.pdf"],
        "measures": ["Substanz", "Präzision", "Praxistauglichkeit"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Du berätst den Geschäftsführer eines mittelständischen Handelsunternehmens in Österreich mit 60 Mitarbeitern. Das Unternehmen hat bisher keine strukturierte KI-Strategie. Einzelne Mitarbeiter nutzen ChatGPT und Copilot, aber es gibt keinen Plan, keine Governance und kein dediziertes Budget.

DOKUMENT:
Dir liegt der oben beigefügte Bericht vor.

DEIN AUFTRAG:
Der Geschäftsführer hat keine Zeit, den Bericht selbst zu lesen. Er sagt: „Sagen Sie mir, was davon mich betrifft. Ich brauche keine Nacherzählung – ich brauche Ihre Einschätzung."

Erstelle eine strategische Zusammenfassung. Konkret:

Erstens: Was sind die drei bis fünf relevantesten Erkenntnisse aus dem Bericht für ein Unternehmen dieser Größe und Branche? Nicht die spektakulärsten Zahlen, sondern die handlungsrelevantesten.

Zweitens: Was aus dem Bericht ist für dieses Unternehmen ausdrücklich nicht relevant – und warum? Der Geschäftsführer muss wissen, was er ignorieren kann.

Drittens: Welche konkreten Fragen sollte sich der Geschäftsführer nach der Lektüre deiner Zusammenfassung stellen?

Trenne dabei konsequent, was der Bericht sagt und was deine Einordnung ist. Erfinde keine Zahlen, die nicht im Bericht stehen.""",
    },

    # ══════════════════════════════════════════
    # AUFGABE 3: Kritisches Hinterfragen
    # ══════════════════════════════════════════

    "A3_Kritisches_Hinterfragen_N": {
        "title": "Kritisches Hinterfragen (Normal)",
        "variant": "N",
        "category": "Qualitätssicherung strategischer Pläne",
        "docs": [],
        "measures": ["Urteilskraft", "Substanz", "Praxistauglichkeit"],
        "use_system_prompt": False,
        "prompt": """Ein Freund von mir hat ein Ingenieurbüro, 25 Leute, Gebäudetechnik in Graz. Er hat folgenden Plan für KI:

1. 25 ChatGPT Team Lizenzen kaufen (7.500 Euro/Jahr)
2. Jeder soll es selbst ausprobieren und eigene Anwendungsfälle finden
3. Nach 6 Monaten schauen welche Abteilungen am meisten davon haben
4. Keine externen Berater, soll organisch wachsen

Was hältst du davon?""",
    },

    "A3_Kritisches_Hinterfragen_P": {
        "title": "Kritisches Hinterfragen (Power)",
        "variant": "P",
        "category": "Qualitätssicherung strategischer Pläne",
        "docs": [],
        "measures": ["Urteilskraft", "Substanz", "Praxistauglichkeit"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Ein befreundeter Unternehmer bittet dich um deine ehrliche Einschätzung. Er leitet ein Ingenieurbüro für Gebäudetechnik in Graz mit 25 Mitarbeitern. Das Unternehmen erstellt Planungsunterlagen, Energieausweise, technische Gutachten und wickelt die Bauaufsicht ab.

SEIN PLAN:
„Wir haben uns für folgende KI-Strategie entschieden:

Erstens: Wir kaufen 25 ChatGPT-Team-Lizenzen für alle Mitarbeiter. Kosten: rund 7.500 Euro pro Jahr.

Zweitens: Jeder soll ChatGPT in seinem Arbeitsbereich selbstständig nutzen und eigene Anwendungsfälle finden. Die Ingenieure für technische Texte und Berechnungsprüfungen, die Projektassistenz für Protokolle und Korrespondenz, die Geschäftsführung für Angebotslegung und Strategiearbeit.

Drittens: Nach sechs Monaten evaluieren wir, welche Abteilungen den größten Nutzen haben, und investieren dort weiter.

Viertens: Wir haben bewusst auf externe Berater verzichtet. Wir wollen das organisch wachsen lassen, ohne dass uns jemand eine Lösung überstülpt."

Er fragt dich: „Was hältst du davon? Bin ich auf dem richtigen Weg?"

DEIN AUFTRAG:
Gib eine ehrliche Einschätzung. Nicht pauschal positiv, nicht pauschal negativ. Konkret:

Erstens: Was an diesem Plan ist grundsätzlich vernünftig? Benenne das ehrlich, bevor du kritisierst.

Zweitens: Wo hat der Plan strukturelle Schwächen? Denke an: Datenschutz und Compliance (Ingenieurbüro, technische Pläne, Kundendaten), fehlende Steuerung (was passiert, wenn 25 Leute 25 verschiedene Dinge machen?), Qualitätssicherung (wer prüft, ob die KI-Outputs in technischen Gutachten korrekt sind?), das Evaluierungsproblem (woran messen die nach sechs Monaten „Nutzen"?).

Drittens: Was würdest du konkret anders machen – mit dem gleichen Budget und der gleichen Teamgröße?

Vermeide diplomatische Absicherungsfloskeln. Der Unternehmer fragt einen Freund, keinen Gutachter.""",
    },

    # ══════════════════════════════════════════
    # AUFGABE 4: Szenario-Analyse
    # ══════════════════════════════════════════

    "A4_Szenario_Analyse_N": {
        "title": "Szenario-Analyse (Normal)",
        "variant": "N",
        "category": "Strategische Planung unter Unsicherheit",
        "docs": [],
        "measures": ["Substanz", "Urteilskraft", "Praxistauglichkeit"],
        "use_system_prompt": False,
        "prompt": """Ich habe ein Maklerbüro in Wien, 8 Leute, Schwerpunkt Zinshäuser. Der Markt ist seit 2024 ziemlich am Boden, Transaktionen runter, Preise auch.

Ich überlege ob ich jetzt in KI investieren soll – automatische Exposés, Marktanalysen, Due Diligence Vorprüfung. Oder lieber warten bis sich der Markt erholt.

Welche Szenarien sind realistisch für die nächsten 18 Monate und was bedeutet das für meine Entscheidung?""",
    },

    "A4_Szenario_Analyse_P": {
        "title": "Szenario-Analyse (Power)",
        "variant": "P",
        "category": "Strategische Planung unter Unsicherheit",
        "docs": [],
        "measures": ["Substanz", "Urteilskraft", "Praxistauglichkeit"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Du berätst die Geschäftsführerin eines Immobilienmakler-Unternehmens in Wien. Das Unternehmen hat 8 Mitarbeiter und ist auf Zinshaus-Vermittlung spezialisiert (Ankauf und Verkauf von Mietwohnhäusern als Investmentobjekte). Der Wiener Zinshausmarkt hat sich 2024 und 2025 deutlich abgekühlt: Das Transaktionsvolumen ist um rund 40 Prozent gegenüber dem Höchststand gefallen, die Preise sind gesunken, und die Verweildauer von Objekten am Markt hat sich verdoppelt.

SITUATION:
Die Geschäftsführerin überlegt, ob sie jetzt in KI-gestützte Prozesse investieren soll. Konkret geht es um drei Bereiche: automatisierte Exposé-Erstellung (Texte, Aufbereitung von Kennzahlen, Visualisierung), KI-basierte Marktanalyse (Preisvergleiche, Renditeschätzungen, Standortbewertungen) und automatisierte Due-Diligence-Vorprüfung (Grundbuchanalyse, Mietvertragsprüfung, Risikoeinschätzung).

Sie sagt: „Ich will keine Glaskugel. Ich will verstehen, welche Szenarien realistisch sind und was sie jeweils für meine Entscheidung bedeuten."

DEIN AUFTRAG:
Entwickle drei realistische Szenarien für die nächsten 18 Monate. Die Szenarien müssen sich in ihren Annahmen klar unterscheiden – nicht nur in der Tonalität. Konkret:

Für jedes Szenario: Benenne die zugrunde liegenden Annahmen (Marktentwicklung, Zinsentwicklung, regulatorisches Umfeld). Beschreibe, was das Szenario für ein 8-Personen-Maklerunternehmen konkret bedeutet (Auftragslage, Umsatz, Wettbewerbssituation). Leite eine Handlungsempfehlung ab: Was sollte die Geschäftsführerin in diesem Szenario bezüglich KI-Investment tun – und warum?

Abschließend: Gibt es eine Empfehlung, die in allen drei Szenarien Bestand hat? Wenn ja, benenne sie. Wenn nein, erkläre warum.

Mache deine Annahmen explizit. Verkaufe keine Einschätzung als Prognose.""",
    },

    # ══════════════════════════════════════════
    # AUFGABE 5: Widerspruchserkennung
    # Quellen: UK Turing Framework vs. EU AI Act
    # N = Volle PDFs (Normal-User wirft alles rein)
    # P = Kuratierte Extrakte (Power-User chunked)
    # ══════════════════════════════════════════

    "A5_Widerspruchserkennung_N": {
        "title": "Widerspruchserkennung (Normal)",
        "variant": "N",
        "category": "Quellenvergleich und regulatorische Einordnung",
        "docs": ["pdf_files/alan_turing_the_ai_regulatory.pdf", "pdf_files/EU_AI_ACT_DE_TXT.pdf"],
        "measures": ["Präzision", "Urteilskraft", "Substanz"],
        "use_system_prompt": False,
        "prompt": """Ich hab hier zwei Dokumente zum Thema KI-Regulierung. Das eine ist ein Framework vom Alan Turing Institute aus Großbritannien, das andere ist der EU AI Act.

Mich interessiert: Widersprechen sich die beiden Ansätze? Und was davon betrifft mich als Geschäftsführer eines Unternehmens mit 30 Leuten in Österreich konkret?""",
    },

    "A5_Widerspruchserkennung_P": {
        "title": "Widerspruchserkennung (Power)",
        "variant": "P",
        "category": "Quellenvergleich und regulatorische Einordnung",
        "docs": ["extracts/turing_framework_extract.txt", "extracts/EU_AI_ACT_Art4_extract.txt"],
        "measures": ["Substanz", "Urteilskraft", "Präzision"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Du berätst den Geschäftsführer eines österreichischen KMU mit 30 Mitarbeitern. Das Unternehmen setzt KI-Tools im Tagesgeschäft ein (ChatGPT, Copilot, KI-gestützte Angebotserstellung). Der Geschäftsführer will verstehen, welche regulatorischen Anforderungen auf ihn zukommen – und wie unterschiedlich das Thema international betrachtet wird.

DOKUMENTE:
Dir liegen zwei Dokumente vor, die oben beigefügt sind.

Dokument 1: "The AI Regulatory Capability Framework and Self-Assessment Tool" vom Alan Turing Institute, erstellt mit dem britischen Department for Science, Innovation and Technology. Ein Framework für KI-Regulierungskompetenz mit 28 regulatorischen Aktivitäten, 6 Capability Factors und 17 Capability Statements.

Dokument 2: Die EU-Verordnung 2024/1689 (EU AI Act), insbesondere Artikel 4 zur KI-Kompetenz. In Kraft seit 2. Februar 2025, Durchsetzung ab 2. August 2026.

DEIN AUFTRAG:
Analysiere beide Dokumente im Vergleich. Konkret:

Erstens: Welchen Regulierungsansatz verfolgt das UK-Framework und welchen der EU AI Act? Beschreibe die grundlegenden Unterschiede in Philosophie, Adressat und Verbindlichkeit.

Zweitens: Wo widersprechen sich die Ansätze? Identifiziere konkrete Divergenzen, nicht nur unterschiedliche Schwerpunkte. Beispiele: Was der EU AI Act als Pflicht formuliert, behandelt das UK-Framework als freiwillige Capability. Was das Turing-Framework als komplexen Prozess mit 28 Aktivitäten und 17 Capability Statements beschreibt, reduziert der EU AI Act auf einen einzigen Artikel. Wo das UK dezentral und sektorspezifisch reguliert, schafft die EU einen horizontalen Rahmen.

Drittens: Was bedeuten diese Unterschiede für den Geschäftsführer konkret? Er operiert unter EU-Recht, nicht unter UK-Recht. Aber: Kann er aus dem UK-Framework trotzdem etwas lernen? Wenn ja, was? Wenn nein, warum nicht?

Viertens: Was muss der Geschäftsführer bis August 2026 nachweisbar umgesetzt haben, um Artikel 4 EU AI Act zu erfüllen? Sei dabei so konkret wie der Gesetzestext es erlaubt – und benenne ehrlich, wo der Text vage bleibt und Interpretation erfordert.

Fünftens: Welcher der beiden Ansätze ist für ein KMU mit 30 Mitarbeitern praxistauglicher? Begründe das.

Erfinde keine Inhalte, die nicht in den Dokumenten stehen. Wenn ein Dokument eine Information nicht enthält, schreib das. Wenn der EU AI Act bewusst unspezifisch bleibt, benenne das als regulatorische Lücke.""",
    },

    # ══════════════════════════════════════════
    # AUFGABE 6: Zahlenanalyse
    # ══════════════════════════════════════════

    "A6_Zahlenanalyse_N": {
        "title": "Zahlenanalyse (Normal)",
        "variant": "N",
        "category": "Finanzanalyse und datengestützte Strategiebewertung",
        "docs": ["pdf_files/EVN-GHB-2024-25_online.pdf"],
        "measures": ["Präzision", "Substanz", "Urteilskraft"],
        "use_system_prompt": False,
        "prompt": """Ich überlege mir eine Beteiligung an diesem Unternehmen. Kannst du dir den Quartalsbericht anschauen und mir sagen ob die Zahlen gut aussehen oder ob es Warnsignale gibt?""",
    },

    "A6_Zahlenanalyse_P": {
        "title": "Zahlenanalyse (Power)",
        "variant": "P",
        "category": "Finanzanalyse und datengestützte Strategiebewertung",
        "docs": ["pdf_files/EVN-GHB-2024-25_online.pdf"],
        "measures": ["Präzision", "Substanz", "Urteilskraft"],
        "use_system_prompt": True,
        "prompt": """KONTEXT:
Du berätst einen Investor, der eine mögliche Beteiligung an dem Unternehmen prüft, dessen Quartalsbericht oben beigefügt ist. Der Investor ist kein Finanzanalyst, aber geschäftserfahren. Er will eine fundierte Einschätzung, keine Bilanz-Nacherzählung.

DEIN AUFTRAG:
Analysiere den Quartalsbericht. Konkret:

Erstens: Wie hat sich das Unternehmen im Vergleich zum Vorjahresquartal entwickelt? Nenne die zentralen Veränderungen bei Umsatz, Ergebnis, Margen und relevanten Bilanzkennzahlen. Berechne Veränderungsraten, wo die Daten das erlauben. Gib die konkreten Zahlen an – keine vagen Formulierungen wie „leicht gestiegen".

Zweitens: Welche Kennzahlen sind positiv und sprechen für eine Beteiligung? Welche geben Anlass zur Vorsicht oder sind Warnsignale? Trenne das klar.

Drittens: Gibt es Auffälligkeiten, die bei oberflächlicher Betrachtung leicht übersehen werden? Dazu gehören: ungewöhnliche Verschiebungen zwischen Quartalen, Einmaleffekte die das Ergebnis verzerren, steigende Verbindlichkeiten bei stagnierendem Umsatz, Diskrepanzen zwischen operativem Ergebnis und Cashflow, Veränderungen in der Bilanzstruktur.

Viertens: Was ist dein Gesamturteil? Würdest du dem Investor empfehlen, die Prüfung zu vertiefen, oder siehst du Gründe für Zurückhaltung? Begründe das.

Rechne nach. Wenn im Bericht Zahlen stehen, die du prüfen kannst, prüfe sie. Wenn Zahlen fehlen, die du für eine Einschätzung bräuchtest, benenne die Lücke.""",
    },
}
