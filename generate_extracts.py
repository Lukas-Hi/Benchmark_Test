#!/usr/bin/env python3
"""
Generiert die Extrakt-Dateien für Power-User-Varianten.
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Einmal ausführen: python generate_extracts.py
Erstellt:
  A5: documents/extracts/EU_AI_ACT_Art4_extract.txt
      documents/extracts/turing_framework_extract.txt
  A6: documents/extracts/EVN_GHB_2024-25_extract.txt
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

# === EVN GANZHEITSBERICHT EXTRAKT (A6) ===
print("Extrahiere EVN Ganzheitsbericht...")
with pdfplumber.open(DOCS / "EVN-GHB-2024-25_online.pdf") as pdf:
    evn_pages = {}
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            evn_pages[i] = t

def evn_page_range(start, end):
    """Extract text from page range (1-indexed, inclusive)."""
    return "\n\n".join([evn_pages.get(i - 1, "") for i in range(start, end + 1) if evn_pages.get(i - 1)])

evn_extract = f"""EXTRAKT: EVN GANZHEITSBERICHT 2024/25 – Finanzanalytische Kernseiten
====================================================================
Quelle: EVN Ganzheitsbericht 2024/25
Unternehmen: EVN AG, Maria Enzersdorf (Niederösterreich)
Geschäftsjahr: 1. Oktober 2024 bis 30. September 2025
Veröffentlicht: 2025 | 241 Seiten

Hinweis: Dies ist ein Experten-Extrakt für die Finanzanalyse. Er enthält die
Kennzahlen-Übersicht, Konzernlagebericht (Ertragslage, Bilanz, Wertanalyse,
Cashflow), Segmentübersicht, Konzernabschluss (GuV, Bilanz, Cashflow) und
den Ausblick. Der vollständige Bericht mit Nachhaltigkeitsbericht, Corporate
Governance, ESG-Daten und Konzernanhang (241 Seiten) liegt dem Berater vor.

============================================================
KENNZAHLEN-ÜBERSICHT (Seite 6) – 3-Jahresvergleich
============================================================

{evn_page_range(6, 6)}

============================================================
AKTIE, AUSBLICK UND DIVIDENDENPOLITIK (Seite 8)
============================================================

{evn_page_range(8, 8)}

============================================================
KONZERNLAGEBERICHT: ERTRAGSLAGE (Seiten 129–130)
============================================================

{evn_page_range(129, 130)}

============================================================
KONZERNLAGEBERICHT: BILANZ UND WERTANALYSE (Seiten 131–132)
============================================================

{evn_page_range(131, 132)}

============================================================
KONZERNLAGEBERICHT: NETTOVERSCHULDUNG, GEARING UND CASHFLOW (Seiten 133–134)
============================================================

{evn_page_range(133, 134)}

============================================================
KONZERNLAGEBERICHT: AUSBLICK 2025/26 (Seite 142)
============================================================

{evn_page_range(142, 142)}

============================================================
SEGMENTBERICHT: ÜBERSICHT UND SEGMENT ENERGIE (Seiten 144–145)
============================================================

{evn_page_range(144, 145)}

============================================================
KONZERNABSCHLUSS: GEWINN-UND-VERLUST-RECHNUNG (Seite 157)
============================================================

{evn_page_range(157, 157)}

============================================================
KONZERNABSCHLUSS: BILANZ (Seite 158)
============================================================

{evn_page_range(158, 158)}

============================================================
KONZERNABSCHLUSS: EIGENKAPITALENTWICKLUNG (Seite 159)
============================================================

{evn_page_range(159, 159)}

============================================================
KONZERNABSCHLUSS: GELDFLUSSRECHNUNG (Seite 160)
============================================================

{evn_page_range(160, 160)}
"""

(OUT / "EVN_GHB_2024-25_extract.txt").write_text(evn_extract, encoding="utf-8")
print(f"  -> {len(evn_extract.split())} Wörter")

# === ZUSAMMENFASSUNG ===
print(f"\nExtrakte erstellt in {OUT}/")
a5_tokens = int(len(eu_extract.split()) * 1.3 + len(turing_extract.split()) * 1.1)
a6_tokens = int(len(evn_extract.split()) * 1.3)
print(f"A5 (EU + Turing): ca. {a5_tokens:,} Tokens")
print(f"A6 (EVN):         ca. {a6_tokens:,} Tokens")
print(f"Gesamt:           ca. {a5_tokens + a6_tokens:,} Tokens")
