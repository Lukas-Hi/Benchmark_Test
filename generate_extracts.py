#!/usr/bin/env python3
"""
Generiert die Extrakt-Dateien für A5 (Widerspruchserkennung).
Einmal ausführen: python generate_extracts.py
Erstellt: documents/extracts/EU_AI_ACT_Art4_extract.txt
         documents/extracts/turing_framework_extract.txt
"""
import pdfplumber
from pathlib import Path

DOCS = Path("documents/pdf_files")
OUT = Path("documents/extracts")
OUT.mkdir(parents=True, exist_ok=True)

# === EU AI ACT EXTRAKT ===
print("Extrahiere EU AI Act...")
with pdfplumber.open(DOCS / "EU_AI_ACT_DE_TXT.pdf") as pdf:
    full_text = ""
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            full_text += t + "\n"

def extract_between(text, start_marker, end_marker, max_len=5000):
    s = text.find(start_marker)
    if s < 0:
        return f"[NICHT GEFUNDEN: {start_marker[:50]}]"
    e = text.find(end_marker, s + len(start_marker))
    if e < 0 or e - s > max_len:
        return text[s:s+max_len].strip()
    return text[s:e].strip()

art4 = extract_between(full_text, "Artikel 4\nKI-Kompetenz", "KAPITEL II\nVERBOTENE PRAKTIKEN")
eg20 = extract_between(full_text, "(20) Um den größtmöglichen Nutzen aus KI-Systemen", "(21)")
eg91 = extract_between(full_text, "(91) Angesichts des Charakters von KI-Systemen", "(92)")
eg92 = extract_between(full_text, "(92) Diese Verordnung lässt Pflichten der Arbeitgeber", "(93)")
eg93 = extract_between(full_text, "(93) Während Risiken im Zusammenhang mit KI-Systemen", "(94)")
eg165 = extract_between(full_text, "(165) Die Entwicklung anderer KI-Systeme als Hochrisiko", "(166)")

eu_extract = f"""EXTRAKT: EU AI ACT – Relevante Abschnitte zur KI-Kompetenz
=========================================================
Quelle: Verordnung (EU) 2024/1689 des Europäischen Parlaments und des Rates
vom 13. Juni 2024 (EU AI Act)
Veröffentlicht: Amtsblatt der EU, 12.7.2024 | In Kraft seit: 2. Februar 2025
Durchsetzung Artikel 4: ab 2. August 2026

Hinweis: Dies ist ein Experten-Extrakt. Er enthält die für die Aufgabenstellung
relevanten Abschnitte, nicht die vollständige Verordnung (144 Seiten, 180 Erwägungsgründe,
113 Artikel, 13 Anhänge). Die vollständige Verordnung liegt dem Berater vor.

============================================================
KERNNORM: Artikel 4 – KI-Kompetenz
============================================================

{art4}

============================================================
KONTEXT: Erwägungsgrund 20 – KI-Kompetenz als Leitprinzip
============================================================

{eg20}

============================================================
KONTEXT: Erwägungsgründe 91–93 – Betreiberpflichten und Arbeitnehmerschutz
============================================================

{eg91}

{eg92}

{eg93}

============================================================
KONTEXT: Erwägungsgrund 165 – Verhaltenskodizes und KI-Kompetenz
============================================================

{eg165}

============================================================
SANKTIONEN: Artikel 99 – Geldbußen (Hinweis)
============================================================

Artikel 99 EU AI Act regelt Geldbußen. Für Verstöße gegen Artikel 4
(KI-Kompetenz) können Geldbußen von bis zu 15 Mio. EUR oder 3% des
weltweiten Jahresumsatzes verhängt werden (je nachdem, welcher Betrag
höher ist). Für KMU und Start-ups gelten angepasste Obergrenzen
(Art. 99 Abs. 6).
"""

(OUT / "EU_AI_ACT_Art4_extract.txt").write_text(eu_extract, encoding="utf-8")
print(f"  -> {len(eu_extract.split())} Wörter")

# === TURING FRAMEWORK EXTRAKT ===
print("Extrahiere Turing Framework...")
with pdfplumber.open(DOCS / "alan_turing_the_ai_regulatory.pdf") as pdf:
    page_texts = {}
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            page_texts[i] = t

def pages(start, end):
    return "\n".join([page_texts.get(i, "") for i in range(start, end)])

turing_extract = f"""EXTRAKT: ALAN TURING INSTITUTE – AI Regulatory Capability Framework
====================================================================
Quelle: "The AI Regulatory Capability Framework and Self-Assessment Tool"
Autoren: Christopher Thomas (Alan Turing Institute), Richard Beddard
(Department for Science, Innovation and Technology)
Veröffentlicht: 2025 | 88 Seiten

Hinweis: Dies ist ein Experten-Extrakt. Er enthält Executive Summary,
Kernkonzepte, Framework-Struktur und Bewertungskriterien. Die vollständigen
Assessment-Templates, Glossare und Detailbeschreibungen der 28 regulatorischen
Aktivitäten sind im Originaldokument enthalten.

============================================================
EXECUTIVE SUMMARY
============================================================

{pages(4, 7)}

============================================================
WARUM DIESES FRAMEWORK? (Section 1.1)
============================================================

{pages(8, 9)}

============================================================
THEORY OF CHANGE (Section 1.4)
============================================================

{pages(11, 12)}

============================================================
WAS BEDEUTET "CAPABILITY"? (Section 2.1)
============================================================

{pages(12, 13)}

============================================================
FRAMEWORK-KERN: Aktivitäten und Capabilities (Sections 3.1–3.2)
============================================================

{pages(18, 21)}
"""

(OUT / "turing_framework_extract.txt").write_text(turing_extract, encoding="utf-8")
print(f"  -> {len(turing_extract.split())} Wörter")

print(f"\nExtrakte erstellt in {OUT}/")
print("Beide zusammen: ca. {0} Tokens".format(
    int((len(eu_extract.split()) * 1.3 + len(turing_extract.split()) * 1.1))
))
