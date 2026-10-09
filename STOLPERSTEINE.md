# Katalog der Stolpersteine

Jeder Abschnitt gehört zu einem Modul `pitfalls/<id>.py`. Die Reihenfolge entspricht
der Registry in `pitfalls/__init__.py` und damit dem PDF.

**Beobachtet** gibt wieder, was `uv run extract.py` mit diesen Versionen geliefert hat:
pypdf 6.19.0, pdfminer.six 20260107, PyMuPDF 1.28.2, pdftotext (Poppler) 26.08.0,
MarkItDown 0.1.8, Docling 2.132.0 (Standardeinstellungen, CPU, OCR mit RapidOCR),
Unstructured 0.27.10 (`strategy="hi_res"`, Tabellenerkennung, OCR mit Tesseract),
Tesseract 5.5.3 (`deu`, 300 dpi, nur das gerenderte Bild) und
Claude Sonnet 5.5 auf den Seitenbildern (110 dpi, Prompt in `vlm_prompt.md`). Claude Haiku 5.5
lief später mit demselben Prompt (`out/stolpersteine.haiku.txt`), die Beobachtungen unten
beziehen sich auf Sonnet.
Nach Updates lohnt es sich, neu zu messen.

Die drei Werkzeugklassen verhalten sich grundverschieden:

- **Klassische Extraktoren** (pypdf, pdfminer, PyMuPDF, pdftotext) lesen nur den
  Textlayer. **MarkItDown** gehört dazu: Es ruft intern pdfminer auf und nur für
  Seiten, die nach Tabelle oder Formular aussehen, pdfplumber. Die Ergebnisse sind
  deshalb fast überall identisch mit pdfminer.
- **Docling** liest ebenfalls den Textlayer, legt aber ein Layoutmodell darüber
  (Überschriften, Listen, Tabellen, Kopf-/Fußzeilen) und macht OCR auf Bildbereichen.
  Kaputte Zeichenzuordnungen repariert es nicht.
- **Unstructured** ist eine Layout-Pipeline wie Docling. Es
  fällt bei offensichtlichem Zeichensalat (fehlende CMap, Type 3) auf OCR zurück und
  liefert dort korrekten Text, plausibel falschen Text (falsche CMap) erkennt es nicht.
  Details im Abschnitt [Unstructured, Tesseract](#unstructured-tesseract).
- **Tesseract** sieht wie ein VLM nur das Bild, kopiert aber statt zu interpretieren.
  Immun gegen alle Textlayer-Probleme, dafür klassische OCR-Fehler bei Hochstellungen,
  Formeln, gedrehtem Text und Symbolen.
- **Ein multimodales LLM** sieht nur das gerenderte Bild. Es ist immun gegen alles,
  was den Textlayer betrifft (CMaps, Stream-Reihenfolge, versteckter Text,
  Schwärzung), interpretiert aber, statt zu kopieren (z. B. "ca."-Werte aus Diagrammen,
  Beschreibungen in eckigen Klammern), und sieht nichts, was nicht gerendert wird
  (Kommentartexte). Die Fehlerart ist eine andere: Wenn es falsch liegt, liegt es
  plausibel falsch. Außerdem ist das Ergebnis nicht deterministisch: Bei
  wiederholten Läufen setzte Sonnet z. B. einmal Darstellungshinweise in eckigen
  Klammern ("[gesperrt]"), einmal nicht.

Übersicht:

| # | ID | Kurz |
|---|---|---|
| – | [kopf_fusszeile](#kopf_fusszeile) | Kopf-/Fußzeilen auf jeder Seite |
| – | [metadaten_seitenzahlen](#metadaten_seitenzahlen) | Müll-Metadaten, Page Labels ≠ physische Seite |
| 1 | [inhaltsverzeichnis](#inhaltsverzeichnis) | Punktlinien und Überschriften ohne Inhalt |
| 2 | [ligaturen](#ligaturen) | ﬁ, ﬀ, ﬃ, ﬂ: korrekt, als Codepoint oder verschluckt |
| 3 | [tounicode_fehlt](#tounicode_fehlt) | Glyph-IDs ohne Zuordnung zu Zeichen |
| 4 | [tounicode_falsch](#tounicode_falsch) | sichtbarer und extrahierter Text weichen ab |
| 5 | [nullbytes](#nullbytes) | `\x00` im Text |
| 6 | [type3_font](#type3_font) | Type-3-Schrift ohne Zeichenzuordnung |
| 7 | [unicode_doppelgaenger](#unicode_doppelgaenger) | gleich aussehende, verschiedene Zeichen |
| 8 | [leerzeichen](#leerzeichen) | Wortgrenzen müssen geraten werden |
| 9 | [schrift_nicht_eingebettet](#schrift_nicht_eingebettet) | Schrift nicht eingebettet, Glyphbreiten fehlen |
| 10 | [silbentrennung](#silbentrennung) | Trennstriche und harte Zeilenumbrüche |
| 11 | [mehrspaltig](#mehrspaltig) | Spalten werden verschränkt gelesen |
| 12 | [stream_reihenfolge](#stream_reihenfolge) | Zeichenreihenfolge ≠ Lesereihenfolge |
| 13 | [hoch_tiefgestellt](#hoch_tiefgestellt) | aus "2023¹" wird "20231" |
| 14 | [ueberschriften_listen](#ueberschriften_listen) | Struktur nur optisch, Bullets aus Symbolschriften |
| 15 | [tabellen](#tabellen) | Zeilen-/Spaltenbezug geht verloren |
| 16 | [tabelle_seitenumbruch](#tabelle_seitenumbruch) | Tabelle mit Übertrag und gesplitteter Zeile |
| 17 | [gedreht_rtl](#gedreht_rtl) | gedrehter Text, Hebräisch |
| 18 | [doppelter_text](#doppelter_text) | Pseudo-Fett und Schatten |
| 19 | [wasserzeichen](#wasserzeichen) | "ENTWURF" mitten im Text |
| 20 | [seitenumbruch](#seitenumbruch) | Satz über Seitengrenze |
| 21 | [text_als_kurven](#text_als_kurven) | Text als Vektorpfade |
| 22 | [scan](#scan) | Bild ohne Text |
| 23 | [ocr_layer](#ocr_layer) | unsichtbarer, fehlerhafter OCR-Text |
| 24 | [diagramm_bild](#diagramm_bild) | Information nur in Grafiken |
| 25 | [formular_annotationen](#formular_annotationen) | Werte in Formularfeldern und Kommentaren |
| 26 | [versteckter_text](#versteckter_text) | unsichtbarer Text, Prompt Injection |
| 27 | [schwaerzung](#schwaerzung) | Schwärzung, die keine ist |
| 28 | [inkrementelles_update](#inkrementelles_update) | alte Fassung steckt noch in der Datei |
| 29 | [text_in_xobject](#text_in_xobject) | Text in Form-XObjects (Stempel, Montage) |
| 30 | [formel](#formel) | Ising-Modell aus pdflatex, lualatex, dvips |
| 31 | [office_export](#office_export) | LibreOffice: Änderungsverfolgung, Initiale, Textrahmen, Datumsfeld |
| 32 | [browser_chrome](#browser_chrome) | Chrome „Drucken als PDF“ |
| 33 | [browser_postscript](#browser_postscript) | über PostScript „gedruckt“: ganze Seite als Bild |
| V | [kaputte_xref](#kaputte_xref) | beschädigte Datei (eigene PDF-Datei) |
| V | [verschluesselt](#verschluesselt) | Verschlüsselung und Rechte (eigene PDF-Datei) |

---

## kopf_fusszeile

**Was:** Jede Seite hat eine Kopfzeile ("Musterfirma GmbH · Stolperstein-Testdokument",
"VERTRAULICH – nur für den internen Gebrauch") und eine Fußzeile (Dokument-ID, Seitenzahl).

**Warum relevant:** Kopf- und Fußzeilen landen in jedem Chunk und machen die Chunks
einander ähnlicher, als sie sind. Sie verwässern Embeddings und zerreißen Sätze an
Seitengrenzen (siehe [seitenumbruch](#seitenumbruch)). Die Frage "Was ist vertraulich?"
findet jede Seite.

**Erzeugung:** Hook `on_every_page`, ganz normaler Text.

**Beobachtet:** Alle Extraktoren geben Kopf- und Fußzeilen als normalen Text aus.

**Docling, MarkItDown, Sonnet:** Docling entfernt Kopf- und Fußzeilen (klassifiziert als Page-Header/-Footer).
MarkItDown gibt sie aus wie pdfminer, bei Tabellenseiten landet die Fußzeile sogar als
letzte Tabellenzeile. Sonnet übernimmt sie, wie im Prompt verlangt.

**Gegenmaßnahmen:** Zeilen erkennen, die auf vielen Seiten an derselben Position
wiederkehren, und entfernen. Layout-Modelle wie Docling klassifizieren Page-Header
und -Footer. Bei Tagged PDF sind sie als Artefakt markiert.

## metadaten_seitenzahlen

**Was:** Das Info-Dictionary enthält Titel "Microsoft Word - Dokument1.docx", Autor
"admin" und kein `CreationDate`. Über `/PageLabels` ist das Deckblatt "i", danach
beginnt die Zählung bei "1". Physische Seite 3 trägt die gedruckte Seitenzahl "2".

**Warum relevant:**
- Metadaten als Titel zu übernehmen ergibt Unsinn in Quellenangaben.
- Fehlende Metadaten können Parser zum Absturz bringen. LangChains `PDFMinerParser`
  scheiterte an fehlendem `creationdate`; in REIS musste deshalb ein toleranter
  Parser her (`TolerantPDFMinerParser`).
- Seitenzahlen in Quellenangaben ("siehe Seite 2") stimmen nur, wenn klar ist, ob
  der physische Index (0- oder 1-basiert!) oder das gedruckte Label gemeint ist.
  Auch der PDF-Viewer muss damit umgehen, wenn er zur Fundstelle springen soll.

**Erzeugung:** `postprocess` mit pikepdf (`pdf.docinfo`, `pdf.Root.PageLabels`).

**Docling, MarkItDown, Sonnet:** Sonnet bemerkte von selbst, dass Bildnummer und gedruckte
Seitenzahl um eins versetzt sind, und hielt das Inhaltsverzeichnis zunächst für falsch,
weil es Bildnummern mit Seitenzahlen verglich. Genau diese Verwechslung passiert auch in
Pipelines.

**Gegenmaßnahmen:** Titel aus dem Inhalt ableiten (erste Überschrift) oder den
Dateinamen nehmen. Seitenindex konsistent 1-basiert speichern und Labels zusätzlich
ablegen (`pypdf`: `reader.page_labels`).

**Quellen:** ISO 32000-1:2008, Abschnitt 12.4.2 (Page Labels).

## inhaltsverzeichnis

**Was:** Deckblatt mit Inhaltsverzeichnis und Punktlinien ("2. Ligaturen ....... 1").

**Warum relevant:** Punktlinien erzeugen lange Zeichenketten aus Punkten. Ein
Inhaltsverzeichnis ist ein Chunk, der zu jedem Thema passt, aber keine Antwort
enthält. Beim Retrieval landet er gerne weit oben.

**Beobachtet:** pypdf und PyMuPDF trennen Titel, Seitenzahl und Punktlinie in
eigene Zeilen. Die Zuordnung von Kapitel zu Seitenzahl geht verloren.

**Docling, MarkItDown, Sonnet:** Docling macht aus Titel und Untertitel Überschriften und trennt
Einträge, Punktlinien und Seitenzahlen; die Seitenzahlen fehlen ganz. Sonnet übernimmt
das Verzeichnis korrekt mit Seitenzahlen, die Punktlinien kürzt es zu "...".

**Gegenmaßnahmen:** Wiederholte Füllzeichen entfernen; Inhaltsverzeichnisse erkennen
und ausschließen oder getrennt als Strukturinformation nutzen. Viele PDFs haben
zusätzlich Lesezeichen (Outlines), die strukturiert auslesbar sind.

## ligaturen

**Was:** Derselbe sichtbare Text in drei Varianten. Die Ligaturglyphen (ﬁ, ﬂ, ﬀ, ﬃ)
werden in der ToUnicode-CMap
- A) korrekt auf "fi", "ffi" usw. abgebildet,
- B) auf die Ligatur-Codepoints U+FB01 usw. abgebildet,
- C) gar nicht abgebildet.

**Warum relevant:** "Eﬃzienz" (B) ist für BM25 und Exact Match ein anderes Wort als
"Effizienz". Bei Embeddings fällt es weniger auf, kostet aber trotzdem Qualität.
"EᎴzienz" bzw. "E zienz" (C) ist schlicht kaputt.

**Erzeugung:** `RawFont` mit drei verschiedenen ToUnicode-Policies.

**Beobachtet:**
- A: alle korrekt.
- B: alle geben U+FB01 usw. aus, keiner normalisiert.
- C: pypdf/PyMuPDF geben die Glyph-ID als Zeichen aus ("EᎴzienz"), pdfminer
  `(cid:5044)`, pdftotext ein Leerzeichen ("E zienz").

**Docling, MarkItDown, Sonnet:** Docling normalisiert B (NFKC) und liefert dort korrekten Text, C bleibt
kaputt ("EᎴzienz"). MarkItDown wie pdfminer. Sonnet liest alle drei Varianten korrekt.

**Gegenmaßnahmen:** Unicode-Normalisierung NFKC behebt B (und schadet in der Regel
nicht). C lässt sich nur per OCR oder mit Wörterbuch-Heuristiken reparieren.

**Quellen:**
[Twig: PDF Extraction Issues](https://help.twig.so/rag-scenarios-and-solutions/chunking/pdf-extraction),
[ComPDF: What is so hard about PDF text extraction](https://www.compdf.com/blog/what-is-so-hard-about-pdf-text-extraction).

## tounicode_fehlt

**Was:** Type0-Schrift mit `Identity-H`-Encoding, also Glyph-IDs im Content-Stream,
ohne ToUnicode-CMap.
- A) Die eingebettete TrueType-Schrift hat noch ihre `cmap`-Tabelle.
- B) `cmap`-Tabelle und Glyphnamen sind entfernt, wie bei vielen Subset-Fonts.

**Warum relevant:** Der häufigste Grund für "PDF sieht gut aus, Text ist Müll". Die
Seite wird perfekt gerendert, weil der Renderer nur Glyphen braucht. Die Zuordnung
zu Zeichen ist optional, die PDF-Spezifikation verlangt sie selbst für PDF/A-b nicht.

**Erzeugung:** `RawFont(..., tounicode=None)` bzw. zusätzlich `strip_cmap=True`.

**Beobachtet:**
- A: pdfminer rekonstruiert den Text vollständig aus der `cmap` der eingebetteten
  Schrift. pypdf, PyMuPDF und pdftotext liefern ".¾QGLJXQJVIULVW" mit Steuerzeichen:
  die Glyph-IDs als Zeichencodes, bei DejaVu gegenüber ASCII um 29 verschoben.
  Solche "Caesar-Chiffren" sind ein typisches Erkennungsmerkmal.
- B: Auch pdfminer gibt auf (`(cid:37)(cid:72)…`).

**Docling, MarkItDown, Sonnet:** Docling gibt in A und B den Zeichensalat aus und greift nicht auf OCR
zurück. MarkItDown wie pdfminer (A korrekt, B `(cid:…)`). Sonnet liest beides korrekt.

**Gegenmaßnahmen:** Erkennen (Anteil von Nicht-Wörterbuch-Wörtern,
Steuerzeichen, `(cid:`), dann OCR auf diese Seiten.

**Quellen:** ISO 32000-1:2008, Abschnitt 9.10 (Extraction of Text Content);
[PDF Association](https://pdfa.org/?p=217926).

## tounicode_falsch

**Was:** Die ToUnicode-CMap verschiebt jedes Zeichen außer dem Leerzeichen um einen
Codepoint (a→b, 3→4, Z→[, ä→å, .→/), wie bei einem `bfrange` mit falschem Startwert.
Sichtbar ist "Die Zahlung erfolgt innerhalb von 30 Tagen netto.", extrahiert wird
"Ejf [bimvoh fsgpmhu joofsibmc wpo 41 Ubhfo ofuup/".

**Warum relevant:** Es gibt keinen Fehler und keine Warnung, auch keine
Steuerzeichen, nur plausibel aussehenden Unsinn. Bei Zahlen ist das Ergebnis ein
anderer gültiger Wert. Solche CMaps entstehen durch fehlerhafte Generatoren oder
absichtlich als "Kopierschutz".

**Erzeugung:** `RawFont` mit Policy `_shift`.

**Beobachtet:** Alle Extraktoren geben den verschobenen Text aus.

**Docling, MarkItDown, Sonnet:** Docling und MarkItDown liefern den verschobenen Text. Sonnet liest
korrekt "30 Tagen".

**Gegenmaßnahmen:** Plausibilitätsprüfung (Sprache erkennen, Wörterbuchquote), bei
Verdacht OCR des gerenderten Seitenbilds und Vergleich mit dem Textlayer.

## nullbytes

**Was:** Die ToUnicode-CMap bildet alle Nicht-ASCII-Glyphen (ü, ß, ö, ä) auf U+0000 ab.

**Warum relevant:** Null-Bytes im Text sprengen nachgelagerte Systeme. PostgreSQL
(und damit pgvector) kann `\x00` in Text-Spalten nicht speichern. In REIS werden sie
deshalb vor dem Speichern durch U+FFFD ersetzt. Außerdem gehen die Umlaute verloren.

**Erzeugung:** `RawFont` mit Policy `_null_for_non_ascii`.

**Beobachtet:** pypdf und pdfminer liefern `Gr\x00\x00e`, pdftotext ersetzt durch
Leerzeichen ("Gr e"), PyMuPDF fällt auf die Glyph-IDs zurück ("Gr¾¡e").

**Docling, MarkItDown, Sonnet:** Docling und MarkItDown ersetzen die Null-Bytes durch Leerzeichen
("Gr e aus D sseldorf"). Sonnet liest korrekt.

**Gegenmaßnahmen:** Steuerzeichen vor dem Speichern immer entfernen oder ersetzen.
Häufung als Qualitätssignal für die Seite nutzen.

## type3_font

**Was:** Type-3-Schrift, deren Glyphen PDF-Zeichenprogramme sind (hier: DejaVu-Umrisse),
Glyphnamen `/g1`, `/g2` … und keine ToUnicode-CMap.

**Warum relevant:** Type-3-Fonts kommen aus alten LaTeX/dvips-Workflows
(Bitmap-Fonts), aus Grafikprogrammen und manchen Berichtsgeneratoren. Ohne Zuordnung
gibt es keinen Text.

**Erzeugung:** `Type3Font`.

**Beobachtet:** pypdf gibt die Glyphnamen aus (`/g1/g2/g3…`), pdfminer `(cid:1)(cid:2)…`,
PyMuPDF und pdftotext Steuerzeichen. Alle Extraktoren liefern Müll, aber jeder
anderen.

**Docling, MarkItDown, Sonnet:** Docling gibt U+FFFD-Ersatzzeichen aus, MarkItDown `(cid:…)`. Sonnet liest korrekt.

**Gegenmaßnahmen:** Wie [tounicode_fehlt](#tounicode_fehlt): erkennen, dann OCR.

## unicode_doppelgaenger

**Was:** Zeichen, die gleich aussehen, aber verschieden kodiert sind:
"Müller" (u + kombinierendes Trema), "Pass​wort" (Null-Breite-Leerzeichen),
"Kаffee" (kyrillisches а), schmales und geschütztes Leerzeichen, Gedankenstrich
und Minuszeichen, typografische Anführungszeichen.

**Warum relevant:** Die Extraktion ist hier korrekt! Trotzdem findet die
Volltextsuche "Müller" und "Passwort" nicht, Tokenizer zerlegen die Wörter anders,
und Zahlenparser verschlucken sich an "10 000" und "−5".

**Erzeugung:** reportlab mit DejaVu und den entsprechenden Codepoints.

**Beobachtet:** Alle Extraktoren geben die Codepoints unverändert aus.

**Docling, MarkItDown, Sonnet:** Docling normalisiert teilweise: Anführungszeichen, Striche und
Leerzeichen werden vereinheitlicht, das zerlegte "Mü ller" bekommt aber ein Leerzeichen
vor dem Trema, das kyrillische "а" bleibt. Sonnet schreibt alles vorkomponiert und
lateinisch, behält aber Gedankenstrich, Minuszeichen und „…“.

**Gegenmaßnahmen:** NFKC-Normalisierung (behebt zerlegte Umlaute, viele Leerzeichen-
Varianten, Ligaturen), unsichtbare Zeichen (U+200B, U+00AD, U+FEFF) entfernen.
Homoglyphen (kyrillisch/lateinisch) lassen sich nur mit Skript-Prüfung erkennen,
das ist auch ein Sicherheitsthema.

## leerzeichen

**Was:** PDF kennt keine Wörter. Fünf Arten, Text ohne (echte) Leerzeichen zu setzen:
- A) jeder Buchstabe mit eigenem Positionierungsbefehl, Lücken nur durch Position,
- B) gesperrt mit zusätzlichem Zeichenabstand (`Tc`),
- C) TJ-Array mit Verschiebungen statt Leerzeichen,
- D) Wortabstände von nur 1 pt,
- E) Blocksatz mit riesigen Lücken.

**Warum relevant:** Ob ein Abstand ein Leerzeichen ist, entscheidet jeder Extraktor
mit eigenen Schwellwerten. Ergebnis: "D i e s" oder "Diesisteintext", beides
schlecht für Tokenizer und Suche.

**Erzeugung:** reportlab (`drawString` pro Buchstabe/Wort, `charSpace`), `RawFont.show_tj`.

**Beobachtet:**
- A: pypdf gibt jeden Buchstaben in einer eigenen Zeile aus, die anderen setzen das Wort korrekt zusammen.
- B: pdfminer und PyMuPDF liefern "W i c h t i g e r", pypdf und pdftotext korrekt.
- C: alle korrekt.
- D: pdfminer, PyMuPDF, pdftotext: "RechnungsadresseundLieferadressesindidentisch."; pypdf: ein Wort pro Zeile.
- E: Wörter in eigenen Zeilen bzw. mit vielen Leerzeichen dazwischen.

**Docling, MarkItDown, Sonnet:** Docling wie pdfminer (B gesperrt, D zusammengeklebt), E korrekt.
MarkItDown wie pdfminer. Sonnet liest alle Varianten korrekt.

**Gegenmaßnahmen:** Extraktor nach Dokumenttyp wählen und Schwellwerte prüfen
(pdfminer: `LAParams(char_margin, word_margin)`); Qualitätssignal "mittlere Wortlänge"
(sehr kurz → gesperrt, sehr lang → Leerzeichen fehlen).

**Quellen:** [setasign: Word Strategy](https://manuals.setasign.com/setapdf-extractor-manual/strategies/word).

## schrift_nicht_eingebettet

**Was:** Text in "Calibri", die nur beim Namen genannt wird: keine eingebettete
Fontdatei, kein `/Widths`-Array, kein `MissingWidth`. A) mit Leerzeichen im
Content-Stream, B) jedes Wort einzeln positioniert, wie es viele Reporting-Tools tun.
Im Viewer sieht die Seite normal aus, er setzt eine Ersatzschrift ein.

**Warum relevant:** Wortgrenzen werden aus den Lücken zwischen den Glyphen geraten
(siehe [leerzeichen](#leerzeichen)), und für die Lücke braucht der Extraktor die
Breite jeder Glyphe. Die steht in `/Widths` oder in der eingebetteten Schrift. Fehlt
beides, muss er raten, und jeder rät anders: pypdf nimmt 500/1000 em pro Glyphe an,
zu breit für i, l, f, t. Die errechneten Lücken schrumpfen, Leerzeichen fallen weg.
pdfminer nimmt `MissingWidth` an, Standardwert 0. Jede Glyphe hat dann keine Breite,
und die Zeilenbildung zerfällt. PyMuPDF und pdftotext liegen richtig, vermutlich weil sie
die Metriken ihrer Ersatzschrift verwenden. Ob es schiefgeht, hängt also an der Bibliothek,
und ob die Schrift auf dem System verfügbar ist, spielt nur für Werkzeuge mit
Ersatzschriften eine Rolle. Laut Spezifikation ist `/Widths` außer für die 14
Standardschriften Pflicht. In freier Wildbahn fehlt es trotzdem. Für bekannte Namen
wie Arial haben pypdf und pdfminer eingebaute Metriken, dort passiert nichts.

**Erzeugung:** Rohe Operatoren (`Tm`/`Tj` pro Zeile bzw. pro Wort), TrueType-Fontdictionary
ohne `FontFile2`, `Widths` und `MissingWidth` im `postprocess`. Wortpositionen mit
Helvetica-Metriken.

**Beobachtet:**
- A: pypdf, PyMuPDF, pdftotext, Docling, MarkItDown korrekt. pdfminer: ein Zeichen pro Zeile.
- B: pypdf "Die LieferungerfolgtfreiHaus und istbiszur Übergabe versichert.", pypdf-Layout und
  Docling ebenso zusammengeklebt. pdfminer: ein Zeichen pro Zeile. MarkItDown erkennt in B eine
  Tabelle, nimmt deshalb für die ganze Seite pdfplumber statt pdfminer und zerlegt die Sätze in Zellen. PyMuPDF und pdftotext korrekt.
- Unstructured: A korrekt, B zusammengeklebt wie pypdf ("LieferungerfolgtfreiHaus", "zusätzlichenKostenan").
- Tesseract liest beide Varianten korrekt (bis auf "Ubergabe"), Sonnet ebenso.
- Der Ähnlichkeitswert in `vergleich.md` bemerkt fehlende Leerzeichen kaum (pypdf 0,99),
  nur das Zerfallen bei pdfminer (0,51).

**Gegenmaßnahmen:** Fonts ohne `FontFile*` und ohne `/Widths` beim Ingest erkennen
(PyMuPDF `page.get_fonts()` meldet nicht eingebettete Schriften mit `n/a`, das gilt aber auch
für die 14 Standardschriften, die keine `/Widths` brauchen. Ob `/Widths` fehlt, zeigt das
Fontdictionary, z. B. mit pikepdf) und für diese Seiten einen
Extraktor mit Ersatzmetriken (PyMuPDF, pdftotext) oder OCR verwenden. Qualitätssignal wie bei
[leerzeichen](#leerzeichen): mittlere Wortlänge, Anteil der Zeilen mit nur einem Zeichen.

**Quellen:** ISO 32000-1, Abschnitt 9.6.2.1 (`Widths` außer für Standardschriften erforderlich)
und 9.8.1 (`MissingWidth`, Standardwert 0); pypdf `_font.py` (Standardbreite 500).

## silbentrennung

**Was:**
- A) schmale Spalte mit Trennstrichen ("Donaudampfschiff-/fahrtsgesellschaft") und
  einem echten Bindestrich am Zeilenende ("E-/Mail"),
- B) weiches Trennzeichen U+00AD am Zeilenende.

**Warum relevant:** Getrennte Wörter zerfallen in zwei Tokens. Naives Zusammenfügen
(`-\n` entfernen) macht aus "E-Mail" ein "EMail". Harte Zeilenumbrüche mitten im Satz
verwirren Splitter, die `\n` als Trennmarke nutzen.

**Beobachtet:** Alle Extraktoren behalten Trennstriche, Zeilenumbrüche und U+00AD.

**Docling, MarkItDown, Sonnet:** Docling fügt getrennte Wörter zusammen und tappt dabei genau in die
Falle: aus "E-Mail" wird "EMail". U+00AD bleibt stehen. Sonnet übernimmt die Zeilen
originalgetreu mit Trennstrichen und schreibt das weiche Trennzeichen als normalen
Bindestrich.

**Gegenmaßnahmen:** U+00AD + Zeilenumbruch immer entfernen. Bei "-\n" nur
zusammenfügen, wenn das Ergebnis ein bekanntes Wort ist oder das nächste Wort klein
beginnt (Deutsch: "E-\nMail" bleibt). Zeilen innerhalb eines Absatzes zusammenführen.

## mehrspaltig

**Was:** Zwei Spalten mit unterschiedlichen Themen (Urlaub, Reisekosten), die Zeilen
werden im Stream abwechselnd links und rechts gezeichnet.

**Warum relevant:** Wer der Stream-Reihenfolge folgt oder Zeilen über die ganze
Breite liest, mischt beide Themen. Der Chunk enthält dann Sätze wie "Jeder
Mitarbeitende hat Reisekosten: Dienstreisen werden mit der…". Klassiker bei Papers,
Broschüren, Zeitschriften.

**Beobachtet:** pdfminer trennt die Spalten korrekt (Layoutanalyse). pypdf und PyMuPDF
(Standard-`get_text()`) verschränken die Zeilen. pdftotext `-layout` setzt die
Spalten nebeneinander, was zeilenweise gelesen dasselbe Problem ergibt.

**Docling, MarkItDown, Sonnet:** Überraschend: Docling verschränkt die Spalten wie pypdf. Das
Layoutmodell erkennt hier nur einen Block. MarkItDown korrekt (pdfminer). Sonnet korrekt.

**Gegenmaßnahmen:** Extraktor mit Layoutanalyse (pdfminer, PyMuPDF mit
`sort=True`/Blöcken, Docling …), bei Tagged PDF die Strukturreihenfolge nutzen.

## stream_reihenfolge

**Was:**
- A) Die Zeilen eines Absatzes werden von unten nach oben gezeichnet.
- B) Die Schritte einer Anleitung werden in der Reihenfolge 3, 1, 4, 2 gezeichnet,
  stehen optisch aber korrekt untereinander.

**Warum relevant:** Die Reihenfolge der Zeichenbefehle ist beliebig. Generatoren
zeichnen z. B. erst alle fetten Elemente, dann den Rest. Für Anleitungen ist eine
falsche Reihenfolge fatal.

**Beobachtet:** pypdf (Standardmodus) und PyMuPDF folgen dem Stream (Absatz rückwärts,
Schritte 3, 1, 4, 2). pdfminer, pdftotext und `pypdf` mit `extraction_mode="layout"`
sortieren nach Position.

**Docling, MarkItDown, Sonnet:** Docling folgt in A der Stream-Reihenfolge (Absatz rückwärts) und
in B teilweise (3, 1, 2, 4). MarkItDown korrekt (pdfminer). Sonnet korrekt.

**Gegenmaßnahmen:** Nach Position sortieren (PyMuPDF: `get_text(sort=True)`), Layoutanalyse.

**Quellen:** [PDFlib: Tagged PDF Basics](https://pdflib.com/pdf-knowledge-base/pdfua/tagged-pdf-basics).

## hoch_tiefgestellt

**Was:** "2023¹", "250 m²", "10⁻³", "CO₂" und Fußnoten, jeweils als kleinerer,
angehobener bzw. abgesenkter Text.

**Warum relevant:** Aus Fußnotenzeichen werden falsche Zahlen: "Der Umsatz stieg
20231 um 12 Prozent". Ein LLM kann das nicht mehr auflösen.

**Beobachtet:** pdfminer, PyMuPDF und pdftotext schreiben die Hochstellung in die
Zeile ("20231", "m2", "10-3"). pypdf setzt sie in eigene Zeilen, was den Satz zerreißt,
aber die Zahl nicht verfälscht.

**Docling, MarkItDown, Sonnet:** Docling setzt Leerzeichen ("2023 1", "m 2"), das ist besser als
"20231", aber nicht eindeutig. MarkItDown wie pdfminer ("20231"). Sonnet gibt Unicode-
Hochzeichen aus ("2023¹", "m²").

**Gegenmaßnahmen:** Schriftgröße und Grundlinie auswerten (pdfminer/PyMuPDF liefern
beides pro Zeichen) und als `^1` oder Unicode-Hochzeichen ausgeben. Layoutmodelle
erkennen Fußnoten.

## ueberschriften_listen

**Was:** Überschriftenhierarchie nur über Schriftgröße/Fettdruck, ein fettes "Wichtig:"
am Absatzanfang, Aufzählungszeichen aus ZapfDingbats (● und ■), nummerierte Liste mit
hängendem Einzug.

**Warum relevant:** Ohne erkannte Überschriften kein strukturbewusstes Chunking
(z. B. Markdown-Header-Splitter) und keine Überschrift als Kontext im Chunk.
Aufzählungszeichen aus Symbolschriften werden zu beliebigen Buchstaben.

**Beobachtet:** Überschriften kommen bei allen als normale Zeilen ohne Hierarchie
heraus. Statt ● und ■ liefern pypdf und pdftotext "■" für beide, pdfminer "n", PyMuPDF "I".
pypdf und PyMuPDF trennen Listennummer und Text in eigene Zeilen.

**Docling, MarkItDown, Sonnet:** Docling erkennt Überschriften (alle auf einer Ebene `##`) und
Listen, das Aufzählungszeichen bleibt als "n" stehen. Sonnet trifft Hierarchie, Listen
und Fettdruck exakt.

**Gegenmaßnahmen:** Extraktoren mit Strukturerkennung, die Markdown ausgeben
(Docling, pymupdf4llm). Alternativ Heuristiken über Schriftgrößen.

## tabellen

**Was:**
- A) Tabelle mit Rahmen, verbundener Kopfzelle ("Umsatz (Mio. €)" über 2023 und 2024),
  leerer Zelle und zweizeiliger Zelle.
- B) Rahmenlose Tabelle, nur durch Ausrichtung erkennbar.

**Warum relevant:** Im PDF gibt es keine Tabelle, nur Text an Positionen und Linien.
Extrahiert entsteht eine Zahlenkolonne ohne Bezug. Die Frage "Wie hoch war der Umsatz
im Süden 2024?" ist damit nicht mehr sicher zu beantworten. Leere Zellen verschieben
die Zuordnung.

**Beobachtet:** pypdf und PyMuPDF geben jede Zelle in einer eigenen Zeile aus.
pdfminer gruppiert spaltenweise, und zwar über beide Tabellen hinweg: erst alle
Regionen und Positionen, dann alle Zahlen. Das ist am schlimmsten. pdftotext `-layout`
erhält die Zeilen optisch am besten.

**Docling, MarkItDown, Sonnet:** Docling erkennt beide Tabellen perfekt, inkl. aufgelöster verbundener
Kopfzelle ("Umsatz (Mio. €) - 2023"). MarkItDown erkennt sie mit pdfplumber, verschiebt
aber die Spalten (leere Zwischenspalten, "2023/2024" als Datenzeile, Fußzeile als
Tabellenzeile). Sonnet liefert saubere Tabellen und vermerkt die verbundenen Zellen.

**Gegenmaßnahmen:** Tabellen gezielt erkennen (pdfplumber, Camelot, PyMuPDF
`find_tables()`, Docling/TableFormer) und als Markdown/HTML ausgeben oder per LLM in
Sätze umschreiben. Tabellen nicht mitten durchchunken.

**Quellen:** [Elastic: Parsing PDF tables for RAG](https://www.elastic.co/search-labs/blog/alternative-approach-for-parsing-pdfs-in-rag).

## tabelle_seitenumbruch

**Was:** Eine Inventarliste mit 48 Zeilen über zwei Seiten, so wie Office-Programme sie
umbrechen: Kopfzeile auf Seite 2 wiederholt, Beschriftung "(Fortsetzung)",
"Übertrag"-Zeile am Ende von Seite 1 und am Anfang von Seite 2, Summe am Schluss.
Zeile 37 hat eine zweizeilige Zelle ("Konferenzsystem mit Kamera, / Mikrofonen und
Display"), deren zweite Zeile erst auf Seite 2 steht.

**Warum relevant:** Für Retrieval und Chunking sind das zwei Tabellen. Die zweite hat
zwar eine Kopfzeile, aber keinen Hinweis, wozu sie gehört, wenn die Beschriftung
fehlt. Die gesplittete Zeile zerfällt in einen Datensatz mit halbem Namen und einen
Datensatz ohne Werte. Übertragszeilen sind Pseudo-Daten: Wer naiv summiert, zählt
49.357 Euro doppelt. Dazwischen stehen Fuß- und Kopfzeile.

**Beobachtet:** Kein Werkzeug fügt die Tabellen zusammen.
- pypdf und PyMuPDF geben jede Zelle in einer eigenen Zeile aus; Zeile 37 endet auf
  Seite 1 mit "Konferenzsystem mit Kamera,", auf Seite 2 folgt "Mikrofonen und Display"
  ohne Bezug.
- pdfminer liest spaltenweise: erst alle Nummern, dann alle Geräte, dann alle Werte.
  Bei 36 Zeilen ist die Zuordnung praktisch nicht mehr herstellbar.
- pdftotext `-layout` erhält die Zeilen, MarkItDown erkennt die Tabellen, zieht aber
  die Fußzeile als letzte Tabellenzeile hinein.
- Docling und Sonnet liefern zwei saubere Markdown-Tabellen, beide mit den
  Übertragszeilen und mit "Mikrofonen und Display" als eigener Zeile mit leeren Zellen.

**Gegenmaßnahmen:** Tabellen über Seitengrenzen erkennen (gleiche Spalten, wiederholte
Kopfzeile, "Fortsetzung") und zusammenführen, Übertragszeilen entfernen, Zeilen ohne
Schlüsselwert an die vorherige Zeile anhängen. Tabellen als eigene Chunks behandeln
und die Kopfzeile in jeden Chunk wiederholen.

## gedreht_rtl

**Was:**
- A) um 90° gedrehte Randnotiz,
- B) kopfstehender Text,
- C) Hebräisch ("שלום עולם"), in visueller Reihenfolge gespeichert, also rückwärts.

**Warum relevant:** Gedrehte Elemente (Randnotizen, Tabellenköpfe, Achsenbeschriftungen)
werden buchstabenweise oder an falscher Stelle ausgegeben. Rechts-nach-links-Text ist
je nach Generator logisch oder visuell gespeichert. Der Extraktor muss raten, ob er
umdrehen muss.

**Beobachtet:** pdfminer gibt die gedrehte Randnotiz einen Buchstaben pro Zeile und
rückwärts aus und lässt das Hebräische rückwärts stehen ("םלוע םולש"). pypdf, PyMuPDF
und pdftotext geben die Randnotiz am Stück aus und drehen das Hebräische korrekt um
(pdftotext mit Bidi-Steuerzeichen).

**Docling, MarkItDown, Sonnet:** Docling gibt "Bitte nicht knicken" und das Hebräische korrekt (als
Überschriften) aus, die gedrehte Randnotiz fehlt. MarkItDown wie pdfminer. Sonnet liest
alles korrekt und vermerkt Drehung und Position in Klammern.

**Gegenmaßnahmen:** Rotierte Textblöcke erkennen und gesondert behandeln. Für
RTL-Sprachen gezielt testen.

## doppelter_text

**Was:**
- A) "Pseudo-Fettdruck": derselbe Text dreimal um 0,4 pt versetzt,
- B) Schatten: grauer Text versetzt hinter schwarzem Text.

**Warum relevant:** Der Text steht zwei- bis dreimal im Chunk. Das verfälscht die
Gewichtung (BM25) und sieht im Kontext des LLMs seltsam aus.

**Beobachtet:** pypdf, pdfminer und PyMuPDF geben beide Zeilen mehrfach aus.
pdftotext entfernt den Pseudo-Fettdruck (A), zerlegt den Schatten (B) aber in
"Jahresabschluss / Jahresabschluss 2025 / 2025".

**Docling, MarkItDown, Sonnet:** Docling halbiert nur: "Warnung…" erscheint zweimal statt dreimal.
Sonnet liest den Text einmal, fett.

**Gegenmaßnahmen:** Deduplizieren von Zeichen bzw. Zeilen mit (fast) identischer
Position. pdfplumber hat dafür `dedupe_chars()`.

## wasserzeichen

**Was:** Diagonales "ENTWURF" zwischen zwei Absätzen und ein gedrehter Stempel "GEPRÜFT".

**Warum relevant:** Das Wasserzeichen landet mitten im Text. "GEPRÜFT" kann ein LLM
als inhaltliche Aussage missverstehen.

**Beobachtet:** pypdf und PyMuPDF geben "ENTWURF" zwischen den Absätzen aus (Stream-
Reihenfolge), pdfminer dahinter. pdftotext `-layout` verstreut die gedrehten
Buchstaben über mehrere Zeilen ("F", "U R", "T W", "E N") und macht aus dem Stempel
"GEPRÜF" + "T". Alle geben beide Stempel aus.

**Docling, MarkItDown, Sonnet:** Docling gibt "ENTWURF" am Anfang des zweiten Absatzes aus ("ENTWURF
Überstunden werden…"), "GEPRÜFT" fehlt. Sonnet trennt beide als Beschreibung in eckigen
Klammern ab.

**Gegenmaßnahmen:** Text mit großer Schrift, heller Farbe oder Drehung als Artefakt
filtern. Bei Tagged PDF sind Wasserzeichen oft als Artefakt markiert.

## seitenumbruch

**Was:** Eine Seite voller Absätze, der letzte Satz bricht mit Fußnotenzeichen auf die
nächste Seite um. Dazwischen liegen Fußnote, Fußzeile und Kopfzeile.

**Warum relevant:** Bei seitenweisem Chunking (in REIS `mode="page"`, damit die
Seitenzahl als Metadatum erhalten bleibt) ist der Satz in zwei Chunks zerschnitten.
Auch bei durchgehendem Text stehen Fußnote, Fußzeile und Kopfzeile mitten im Satz.

**Beobachtet:** Bei allen Extraktoren stehen zwischen "…schriftlich und unter*" und
"Angabe der Vertragsnummer…" die Fußnote, die Fußzeile und die Kopfzeile.

**Docling, MarkItDown, Sonnet:** Docling entfernt Kopf-/Fußzeile, die Fußnote steht aber weiter mitten
im Satz. Sonnet wie die übrigen.

**Gegenmaßnahmen:** Kopf-/Fußzeilen und Fußnoten entfernen, dann Seiten
zusammenfügen und erst danach chunken. Seitenzahlen über Zeichenoffsets zuordnen.

## text_als_kurven

**Was:** Zwei Zeilen ("Kündigungsfrist: 3 Monate zum Quartalsende", Hotline-Nummer)
als gefüllte Vektorpfade.

**Warum relevant:** In Druckvorstufe und Grafikprogrammen wird Text oft "in Kurven
umgewandelt". Optisch identisch, aber für Extraktoren existiert er nicht.

**Erzeugung:** `draw_text_as_paths` (Glyphumrisse mit fontTools).

**Beobachtet:** Kein Extraktor findet den Text.

**Docling, MarkItDown, Sonnet:** Docling OCRt nur die zweite Zeile ("Hotline…"), die fett gesetzte
Kündigungsfrist fehlt. Sonnet liest beide.

**Gegenmaßnahmen:** OCR. Seiten mit vielen Pfaden und wenig Text als Kandidaten markieren.

## scan

**Was:** Eine leicht schiefe, verrauschte Bescheinigung als JPEG, ohne Textlayer.

**Warum relevant:** Klassische Extraktoren liefern einen leeren String, und zwar ohne
Fehler. Ohne Prüfung landet das Dokument still als leerer oder fast leerer Chunk im
Index und ist nie auffindbar.

**Beobachtet:** Alle Extraktoren geben nur Titel, Kopf- und Fußzeile aus.

**Docling, MarkItDown, Sonnet:** Docling OCRt den Scan gut, mit einem OCR-Fehler ("Februar2 2026") und
vertauschter Kopfzeile ("Personalabteilung Musterfirma GmbH"). Sonnet liest fehlerfrei
und schreibt "[Gescanntes Bild, Text:]" davor.

**Gegenmaßnahmen:** Zeichen pro Seite messen und Seiten mit großem Bildanteil und
wenig Text an OCR (Tesseract, docTR, PaddleOCR) oder ein VLM weiterreichen.

**Quellen:** [OCR Hinders RAG (OHRBench)](https://arxiv.org/abs/2412.02592).

## ocr_layer

**Was:** Ein Rechnungsscan mit unsichtbarem Textlayer (Render-Modus 3), wie ihn
Scanner erzeugen, mit typischen OCR-Fehlern: "l.Z34,S6" statt "1.234,56",
"O" statt "0", "q" statt "g".

**Warum relevant:** Weil Text vorhanden ist, schlägt keine "leere Seite"-Prüfung an.
Der Viewer zeigt das saubere Bild, im Index stehen falsche Beträge, Daten und IBANs.

**Beobachtet:** Alle Extraktoren geben den fehlerhaften OCR-Text aus.

**Docling, MarkItDown, Sonnet:** Docling ignoriert den vorhandenen OCR-Layer und OCRt selbst: Die Werte
stimmen, Leerzeichen fehlen ("Rechnungsbetrag:1.234,56EUR"). Sonnet liest korrekt.

**Gegenmaßnahmen:** Vorhandene OCR-Layer nicht blind vertrauen. Qualität prüfen
(Wörterbuchquote, Zahlenformate), ggf. neu OCRen (`ocrmypdf --force-ocr`).

**Quellen:** [OCR Hinders RAG (OHRBench)](https://arxiv.org/abs/2412.02592).

## diagramm_bild

**Was:**
- A) Balkendiagramm aus Vektorgrafik, die Werte stecken nur in den Balkenhöhen,
- B) Screenshot einer Preistabelle als Bild.

**Warum relevant:** Die eigentliche Information (Neukunden je Quartal, Preise) ist für
Textextraktion unsichtbar. Übrig bleiben Achsenbeschriftungen ("0 5 10 15 20 25 Q1 Q2
Q3 Q4"), die zu Fragen passen, aber nichts beantworten.

**Beobachtet:** Alle Extraktoren geben nur Titel und Achsenbeschriftungen aus,
die Tabelle im Bild fehlt komplett.

**Docling, MarkItDown, Sonnet:** Docling gibt nur den Diagrammtitel aus, die Achsenwerte fehlen ganz.
Den Tabellen-Screenshot OCRt es mit Fehlern: Aus "9,99 €" wird "366′6", die
Spaltenzuordnung ist kaputt. Sonnet liest die Balken korrekt ab (in einem früheren Lauf
als "ca."-Werte gekennzeichnet, im aktuellen als "Ablesbare Werte") und überträgt den
Screenshot als Tabelle.

**Gegenmaßnahmen:** Bilder und Grafiken erkennen und mit einem VLM beschreiben lassen
(Bildbeschreibung als zusätzlicher Chunk) oder visuelles Retrieval (ColPali).

## formular_annotationen

**Was:** AcroForm-Textfelder mit ausgefüllten Werten (Name, Eintrittsdatum, Abteilung),
eine angehakte Checkbox und eine Notiz-Annotation ("Bitte bis Freitag unterschreiben…").

**Warum relevant:** Formularwerte stehen nicht im Content-Stream, sondern in den
Feldern bzw. deren Widget-Annotationen. Ohne sie bleibt ein Formular voller
Beschriftungen ohne Daten.

**Beobachtet:** pypdf und pdfminer liefern nur die Beschriftungen. PyMuPDF hängt die
Feldwerte am Ende an (ohne Zuordnung zur Beschriftung), pdftotext setzt sie neben die
Beschriftungen. Checkbox und Kommentar fehlen bei allen.

**Docling, MarkItDown, Sonnet:** Docling hängt die Feldwerte wie PyMuPDF ohne Zuordnung ans Ende.
MarkItDown liefert nur Beschriftungen. Sonnet ordnet die Werte richtig zu und erkennt die
angehakte Checkbox. Den Kommentartext sieht es nicht, nur das Symbol, weil er nicht
gerendert wird.

**Gegenmaßnahmen:** Formularfelder separat auslesen (`pypdf`: `reader.get_fields()`,
PyMuPDF: `page.widgets()`) und Annotationen (`page.annots()`) einbeziehen, oder das
Formular vorher "flatten".

**Quellen:** ISO 32000-1:2008, Abschnitt 12.7 (Interactive Forms).

## versteckter_text

**Was:** Eine Bewerbung mit sechs versteckten Botschaften:
weiß auf weiß, Render-Modus 3 (unsichtbar), 0,5-pt-Schrift, außerhalb der Seite,
hinter einem weißen Rechteck, Textfarbe gleich Hintergrundfarbe.

**Warum relevant:** Parser extrahieren alles, was im Content-Stream steht, auch das,
was kein Mensch sieht. Das ist ein Einfallstor für Prompt Injection ("Ignoriere alle
bisherigen Anweisungen…"), real dokumentiert bei automatisiertem Bewerbungs-Screening.
Dokumente sind ein Eingabekanal, der oft an Guardrails für Nutzereingaben vorbeiläuft.

**Beobachtet:** Alle Extraktoren geben fünf bis sechs der versteckten Texte aus.
Nur den Text außerhalb der Seite lassen PyMuPDF und pdftotext weg. Bei pdftotext
(`-layout`) verschränkt sich der weiße Text zusätzlich mit dem sichtbaren Absatz.

**Docling, MarkItDown, Sonnet:** Docling gibt alle versteckten Texte bis auf den außerhalb der Seite
aus. MarkItDown wie pdfminer, also alle. Sonnet ist immun: Es sieht nur den sichtbaren
Text und markiert die 0,5-pt-Schrift (im Bild ein grauer Strich) als "[unleserlich]".
Nebenbei hat Sonnet einen Fehler im Testdokument gefunden: In einer früheren Version
galt der unsichtbare Render-Modus über das Textobjekt hinaus (`Tr` gehört zum
Grafikzustand), sodass auch der eigentlich sichtbare Schlusssatz unsichtbar war. Alle
Textextraktoren hatten ihn trotzdem ausgegeben.

**Gegenmaßnahmen:** Hochgeladene Dokumente als nicht vertrauenswürdige Eingabe behandeln.
Unsichtbaren Text erkennen: Render-Modus, Farbe gegen Hintergrund, Schriftgröße,
Position außerhalb der MediaBox, Verdeckung. Pragmatisch: OCR des gerenderten Bilds
mit dem Textlayer vergleichen.

**Quellen:**
[Measuring Real-World Prompt Injection Attacks in LLM-based Resume Screening](https://arxiv.org/pdf/2605.28999),
[Document Injection in RAG-Pipelines](https://tianpan.co/blog/2026-04-15-document-injection-rag-pipeline).

## schwaerzung

**Was:** Gehaltsabrechnung, Name, IBAN, Gehalt und Steuerklasse mit schwarzen Balken
"geschwärzt". Der Text darunter ist unverändert vorhanden.

**Warum relevant:** Der Klassiker unter den Datenlecks: Im Viewer ist alles geschwärzt,
im extrahierten Text alles lesbar. Für RAG bedeutet das vertrauliche Daten im Index
und in Antworten.

**Beobachtet:** Alle Extraktoren geben die geschwärzten Daten vollständig aus.

**Docling, MarkItDown, Sonnet:** Docling und MarkItDown geben die geschwärzten Daten aus. Sonnet schreibt
"[geschwärzt]".

**Gegenmaßnahmen:** Text unter gefüllten dunklen Rechtecken erkennen (Bounding-Box-
Überlappung). Echtes Schwärzen entfernt den Text (z. B. PyMuPDF `add_redact_annot` +
`apply_redactions`).

## inkrementelles_update

**Was:** Das PDF wird nachträglich per inkrementellem Update geändert: Ans Dateiende
werden ein neuer Content-Stream und eine neue Seitendefinition angehängt, in denen der
Vertragswert 75.000 statt 50.000 EUR beträgt. Die alte Fassung bleibt in den Bytes.

**Warum relevant:** Normale Parser lesen die neueste Revision, das ist korrekt. Aber
die alte Fassung ist noch da: `grep -a 50.000 out/stolpersteine.pdf` findet sie, und
Werkzeuge zur Reparatur oder zum Revisionsvergleich können sie wieder hervorholen.
"Gelöschte" Inhalte sind also nicht gelöscht. Signierte PDFs bestehen typischerweise
aus mehreren Revisionen.

**Erzeugung:** Hook `finalize`, schreibt das Update von Hand (neue Objekte, xref-Abschnitt,
Trailer mit `/Prev`).

**Beobachtet:** Alle Extraktoren liefern korrekt 75.000 EUR.

**Docling, MarkItDown, Sonnet:** Alle liefern 75.000 EUR.

**Gegenmaßnahmen:** Für Indexierung unkritisch. Bei Weitergabe von Dokumenten ein
vollständiges Neuschreiben erzwingen (`qpdf in.pdf out.pdf`).

**Quellen:** ISO 32000-1:2008, Abschnitt 7.5.6 (Incremental Updates).

## text_in_xobject

**Was:** Ein Absatz direkt auf der Seite, ein zweiter in einem Form-XObject, das
auf 85 % verkleinert eingebunden wird.

**Warum relevant:** Form-XObjects sind wiederverwendbare Seitenbausteine. Werkzeuge,
die Seiten zusammenfügen, Briefpapier hinterlegen, stempeln oder mehrere Seiten auf
eine montieren (n-up), packen Inhalte dort hinein. Manche Extraktoren behandeln Text
darin wie eine Grafik.

**Erzeugung:** reportlab `beginForm`/`doForm`.

**Beobachtet:** pdfminer in der Variante `extract_pages` + `LTTextContainer` (wie in
`extract.py`) und `pypdf` im Layoutmodus verlieren den Absatz **komplett**. pdfminers
`extract_text` und damit MarkItDown liefern ihn, kleben aber die Zeilen ohne Leerzeichen
aneinander ("so wie esWerkzeuge") und stellen ihn hinter die Fußzeile. pypdf (Standard),
PyMuPDF, pdftotext, Docling und Sonnet lesen ihn korrekt.

Aufgefallen ist das, als die Formel- und Browserseiten zunächst als XObject eingesetzt
wurden: pdfminer lieferte dort "DasIsing-ModellbeschreibtSpins…". Deshalb werden diese
Seiten jetzt unverändert übernommen (`ExternalPage(mode="replace")`).

**Gegenmaßnahmen:** pdfminer mit `LAParams(all_texts=True)` aufrufen und `LTFigure`
rekursiv auswerten. Bei Pipelines, die PDFs vorher zusammenführen oder stempeln, die
Extraktion vorher und nachher vergleichen.

## formel

**Was:** Ein Absatz zum Ising-Modell mit Hamiltonoperator, Zustandssumme und
Magnetisierung, aus derselben Quelle (`quellen/formel.tex`) dreimal gesetzt. Die
Originalseiten werden unverändert eingesetzt (kleines Seitenformat, ohne Kopf-/Fußzeile):
- A) `pdflatex`: Computer Modern als Type 1, OT1-Encoding, ohne `cmap`/`mmap`-Paket
  (die Voreinstellung eines minimalen Dokuments),
- B) `lualatex` mit `unicode-math`: OpenType (Latin Modern Math) mit ToUnicode,
- C) `latex` → `dvips -Ppk` → `ps2pdf`: Bitmap-Schriften als Type 3, so wie viele
  ältere arXiv-PDFs und DVI-Workflows sie erzeugen.

**Warum relevant:** Formeln sind zweidimensional (Brüche, Indizes, Summengrenzen), Text
ist eindimensional. Dazu kommen Font-Eigenheiten der TeX-Welt: zusammengesetzte Umlaute
in OT1 ("F¨ur" statt "Für"), große Operatoren aus der Schrift CMEX, deren Glyphe
`summationdisplay` als "X" oder `(cid:88)` herauskommt, und mathematische
Unicode-Buchstaben (𝜎 U+1D70E statt σ U+03C3), die keine Suche nach "σ" findet.

**Erzeugung:** `quellen/build.sh`, eingebunden über `ExternalPage`.

**Beobachtet:**
- A: Alle Textextraktoren zerlegen die Formeln in Einzelzeilen ("H(σ) = −J / X / ⟨i,j⟩ /
  σiσj −h / N / X / i=1"). Das Summenzeichen ist "X" (pypdf, PyMuPDF) bzw.
  `(cid:88)` (pdfminer). Umlaut als "F¨ur" (pypdf, pdfminer, PyMuPDF).
- B: Text korrekt, aber mit mathematischen Unicode-Zeichen ("𝜎𝑖", "ℋ", "𝑁"); Struktur
  zerfällt genauso. pdftotext `-layout` erhält Summengrenzen optisch über und unter dem ∑.
- C: Überraschend lesbar, weil dvips Glyphnamen mitliefert. Aber: pdftotext macht aus
  ⟨i,j⟩ "hi,ji" (die Winkelklammern heißen in der Schrift `h`/`i`), pdfminer verwürfelt
  die Reihenfolge ("Xh / N / i=1 / X"). MarkItDown hält Teile für eine Tabelle und
  zerlegt den Fließtext buchstabenweise ("Dfi ag su Ia s in gn").
- **Docling** lässt alle Formeln in der Standardeinstellung weg
  (`<!-- formula-not-decoded -->`) und ordnet Text der falschen Seite zu. Bei C bleibt
  von der ganzen Seite nur ein Komma: Der Text der Type-3-Bitmapschrift wird nicht
  gelesen, und OCR springt nicht an, weil kein Bild auf der Seite ist.
  Mit `PdfPipelineOptions(do_formula_enrichment=True)` (zusätzliches Modell, etwa
  2 Minuten auf CPU für die drei Seiten) erkennt Docling A und B sehr gut als LaTeX,
  macht in B aber aus ⟨i,j⟩ ein (i,j) und stellt "Für die Zustandssumme gilt" hinter
  alle Formeln. C bleibt ein Komma.
- **Sonnet** liefert für alle drei Varianten identisches, korrektes LaTeX.

**Gegenmaßnahmen:** Formelseiten erkennen (viele Einzelzeichen, mathematische Fonts)
und mit einem Formelmodell oder VLM nach LaTeX übersetzen. Für eigene Dokumente:
`\usepackage{cmap}` bzw. `mmap` oder lualatex verwenden, nicht `-Ppk`.
Mathematische Unicode-Buchstaben per NFKC auf normale Buchstaben abbilden
(𝜎 → σ, ℋ → H; dabei geht die Unterscheidung kursiv/kalligrafisch verloren).

**Quellen:** [Unicode Mathematical Alphanumeric Symbols](https://www.unicode.org/charts/PDF/U1D400.pdf).

## office_export

**Was:** Eine Betriebsvereinbarung als Flat-ODT (`quellen/office.fodt`), mit
`soffice --convert-to pdf` exportiert, wie es bei Word- und LibreOffice-Dokumenten
ständig passiert. Die Originalseite wird unverändert eingesetzt. Enthält:
Kopf-/Fußzeile mit Seitenfeldern ("Seite 1 von 1"), automatische Kapitelnummern,
eine Initiale (großes "D" über drei Zeilen), zwei Fußnoten, Änderungsverfolgung
("zwei" gelöscht, "drei" eingefügt), einen Kommentar, verborgenen Text, einen
schwebenden Textrahmen, eine automatisch nummerierte Liste und ein Datumsfeld.

**Warum relevant:** Office-Dokumente sind der Hauptbestand in Unternehmensablagen und
werden oft nur als PDF abgelegt. Office-Funktionen werden dabei zu Zeichenbefehlen,
mit teils überraschenden Folgen für den Inhalt:
- **Änderungsverfolgung:** Ist die Anzeige der Änderungen beim Export an (Standard in
  diesem Dokument), stehen gelöschter und eingefügter Text im PDF. Durchgestrichenes
  "zwei" und unterstrichenes "drei" werden zu "zweidrei".
- **Datumsfeld:** Ein nicht fixiertes Feld wird beim Export neu berechnet. Im PDF
  steht das Exportdatum (`Köln, den 02.10.26`), nicht das Datum der Vereinbarung
  (10.02.2026). Das ist kein Extraktionsfehler, aber die Information im Index ist falsch.
  Die Ground Truth liest deshalb das Exportdatum aus den Metadaten.
- Kommentar und verborgener Text werden von LibreOffice standardmäßig nicht exportiert,
  sie lecken hier also nicht. Das hängt aber von den Exporteinstellungen ab
  (Kommentare als Annotationen oder am Rand).
- Das Original-PDF ist ein Tagged PDF mit Strukturbaum. Beim Einsetzen in unser
  Testdokument geht der Strukturbaum verloren; genutzt hat ihn aber ohnehin keiner
  der Extraktoren.

**Beobachtet:**
- **Initiale:** Das "D" steht nirgends am richtigen Platz. pypdf hängt es ans Absatzende
  ("Produktion.D"), PyMuPDF dahinter in eine eigene Zeile, pdfminer, pdftotext,
  MarkItDown und Docling davor in eine eigene Zeile ("D / iese Vereinbarung"). Damit
  findet keine Suche "Diese Vereinbarung".
- **Änderungsverfolgung:** Alle Textextraktoren und Docling liefern "bis zu zweidrei
  Tage". Sonnet erkennt die Durchstreichung und schreibt "~~zwei~~ drei".
- **Textrahmen:** pypdf und PyMuPDF stellen ihn ans Seitenende hinter die Fußzeile,
  pdftotext `-layout` verschränkt ihn zeilenweise mit dem Absatz, Docling fügt ihn mitten
  in den Satz ein ("das gesamte Wichtig: Die Vereinbarung tritt am 1. März 2026 in Kraft.
  Team vor Ort"). pdfminer, MarkItDown und Sonnet setzen ihn hinter den Absatz.
- **Fußnotenzeichen:** "Ausbildungsjahr1" bzw. "Ausbildungsjahr 1", "Datenschutz2"
  (wie bei [hoch_tiefgestellt](#hoch_tiefgestellt)); Sonnet schreibt "¹".
- **Datumsfeld:** Alle liefern das Exportdatum.

**Gegenmaßnahmen:** Wenn möglich das Office-Original indexieren (DOCX/ODT), dort sind
Änderungen, Kommentare und Felder als solche erkennbar. Vor dem PDF-Export Änderungen
annehmen und Felder fixieren. Für PDFs: Tagged-PDF-Strukturbaum nutzen, wo vorhanden.

## browser_chrome

**Was:** Eine typische Intranet-Seite (`quellen/browser.html`) mit Chrome headless als PDF
gedruckt. Enthält Navigationsleiste, festen Cookie-Banner, unsichtbaren Skip-Link,
CSS-Großbuchstaben mit Sperrung, Kapitälchen, zweispaltigen Blocksatz, Ligaturen,
per CSS erzeugtes "Hinweis:", Listennummern aus dem Browser, Tabelle, SVG-Text, Emoji
und Textschatten auf Überschriften.

**Warum relevant:** "Drucken als PDF" ist eine der häufigsten Arten, wie Webseiten,
Wiki-Seiten und Tickets in Dokumentablagen landen. Der Browser übersetzt CSS in
Zeichenbefehle, Semantik geht dabei verloren.

**Erzeugung:** `google-chrome-stable --headless --print-to-pdf` (siehe `quellen/build.sh`).
Chrome schreibt CID-TrueType-Subsets mit ToUnicode, Emoji als Type-3-Bitmap.

**Beobachtet:**
- **Textschatten verdoppelt Überschriften:** Chrome zeichnet den Schatten als zweiten
  Text. "Ablauf der AbrechnungAblauf der Abrechnung" bei pypdf, pdfminer, PyMuPDF,
  Docling, "KKoonnttaakktt" bei MarkItDown.
- **Blocksatz:** Chrome positioniert in Blocksatzzeilen jedes Wort einzeln. PyMuPDF
  gibt diese Wörter je in einer Zeile aus, pdfminer verwürfelt sogar ihre Reihenfolge
  ("grundsätzlich / unter / Vorrang / offizielle … 500 Kilometern / Flügen. Die / vor").
- **Sperrung** (`letter-spacing`): "R E I S E R I C H T L I N I E" bei pypdf, pdfminer,
  PyMuPDF; Docling "REISERICHTL INIE".
- **Kapitälchen:** pypdf "G ÜLTIG AB 1. J ANUAR", pdfminer "GÜLTIG AB 1. JANUAR",
  PyMuPDF und pdftotext "Gültig ab 1. Januar". Drei Extraktoren, drei Ergebnisse.
- **Ligaturen:** Chrome bildet die ff-Ligatur auf U+FB00 ab: pypdf und pdfminer liefern
  "Eﬀizienz", PyMuPDF und pdftotext normalisieren.
- **Boilerplate:** Navigation und Cookie-Banner landen bei allen Textextraktoren und
  bei Sonnet im Text. Docling entfernt beides. Der Skip-Link wird von Chrome nicht
  gezeichnet und taucht nirgends auf.
- **MarkItDown** hält die ganze Seite für eine Tabelle (pdfplumber) und produziert
  zerhackte Pseudo-Tabellen, auch aus der Überschrift ("| R E | I S E | R I |…").
- **Sonnet** liefert sauberes Markdown. In einem früheren Lauf ergänzte es Dinge, die
  nicht sichtbar sind: Die Navigation wurde zu Links mit erfundenem Ziel (`[Startseite](#)`),
  die E-Mail zu einem `mailto:`-Link, das Info-Icon zu "ⓘ". Im aktuellen Lauf (nach
  Neuaufbau des PDFs) steht die Navigation als Text da und die E-Mail ohne Link.

**Gegenmaßnahmen:** Wenn die HTML-Quelle verfügbar ist, die HTML-Quelle indexieren,
nicht das PDF (siehe Outline: "Nehmt die Quelle"). Sonst: Layout-Extraktor mit
Boilerplate-Erkennung, Deduplizierung überlagerter Zeichen.

## browser_postscript

**Was:** Die Chrome-PDF über einen PostScript-"Druckertreiber" gedruckt
(`pdftops -level3` → `ps2pdf`), so wie es bei "Drucken" auf einen PDF-Drucker über
PostScript passiert.

**Warum relevant:** PostScript kennt keine Transparenz. Seiten mit Transparenz
(hier: Textschatten, Emoji) werden beim "Flattening" gerastert. pdftops rastert dabei
die ganze Seite: Das Ergebnis ist ein einziges Bild, in dem kein Text mehr steckt.
Optisch sieht die Seite aus wie das Original.

**Beobachtet:** Alle Textextraktoren liefern eine leere Seite. Docling OCRt die Seite,
mit Fehlern ("2O26", "Ubernachtungskosten", fehlende Leerzeichen) und doppelten
Absätzen. Sonnet liest die Seite fehlerfrei, identisch zur Chrome-Variante.

**Gegenmaßnahmen:** Wie [scan](#scan): leere Seiten erkennen, OCR oder VLM.

## kaputte_xref

**Was:** Variante `out/stolpersteine--kaputte_xref.pdf`: Nach der Kopfzeile wird eine
Zeile eingefügt, damit stimmen alle Byte-Offsets der xref-Tabelle nicht mehr.

**Warum relevant:** Defekte PDFs sind häufig (abgebrochene Uploads, schlampige
Generatoren, nachträgliches Editieren). Viewer reparieren still, Parser unterschiedlich
gut. In REIS gibt es deshalb einen Fallback von PDFMiner auf PyPDF.

**Beobachtet:** Alle Extraktoren reparieren die Datei und liefern alle Seiten,
pypdf mit Warnung ("incorrect startxref pointer"). Andere Defekte (abgeschnittene
Dateien, kaputte Streams) sind deutlich härter und ein guter Kandidat für weitere
Varianten.

**Docling, MarkItDown, Sonnet:** Docling und MarkItDown lesen die Datei ebenfalls vollständig.

**Gegenmaßnahmen:** Fallback-Kette mehrerer Parser, vorher mit `qpdf` reparieren,
Parser-Name und -Version als Metadatum am Chunk speichern, Timeouts und
Prozessisolation gegen hängende Parser.

## verschluesselt

**Was:** Variante `out/stolpersteine--verschluesselt.pdf`: AES-256, leeres
Benutzerpasswort (öffnet ohne Abfrage), Owner-Passwort gesetzt, Rechte zum
Textextrahieren entzogen.

**Warum relevant:** Je nach Bibliothek wird das Recht ignoriert, führt zum Abbruch oder
braucht Zusatzpakete für AES (pypdf: `cryptography`). Ob man die Rechte respektieren
muss, ist eine organisatorische Frage, die man bewusst entscheiden sollte.

**Beobachtet:** Alle Extraktoren extrahieren den Text. pdfminer weist darauf hin, dass
es das Verbot ignoriert. Dateien mit echtem Benutzerpasswort scheitern dagegen
überall.

**Docling, MarkItDown, Sonnet:** Docling und MarkItDown extrahieren ebenfalls.

**Gegenmaßnahmen:** Verschlüsselung erkennen und sauber melden statt leere Chunks zu
indexieren.

---

## Unstructured, Tesseract

Diese beiden kamen später dazu. Statt jeden Abschnitt oben zu ergänzen, hier die
Beobachtungen gesammelt (aus `out/vergleich.md`).

**Unstructured** (0.27.10, `hi_res`). Ausgabe hier: Elemente mit `# ` für `Title`,
`- ` für `ListItem`, Tabellen als HTML (`text_as_html`).
- [tounicode_fehlt](#tounicode_fehlt) und [type3_font](#type3_font): **korrekt**, weil
  unlesbarer Text per OCR ersetzt wird. [tounicode_falsch](#tounicode_falsch): verschoben wie alle.
  [nullbytes](#nullbytes): Umlaute verschwinden.
- [mehrspaltig](#mehrspaltig) und [stream_reihenfolge](#stream_reihenfolge): korrekt.
- [leerzeichen](#leerzeichen): wie pdfminer ("W i c h t i g e r", "Rechnungsadresseund…").
- [ueberschriften_listen](#ueberschriften_listen): alle Überschriften `Title` ohne Ebene,
  Aufzählungszeichen "n". Kopf- und Fußzeilen bleiben.
- [tabellen](#tabellen): **schlecht**. Von Tabelle A bleibt eine HTML-Zeile, die Umsatzzahlen
  fehlen ganz. In Tabelle B schneidet die Zellerkennung erste Buchstaben ab ("Zeratung",
  "zeisekosten", "_izenz"). [tabelle_seitenumbruch](#tabelle_seitenumbruch): Tabellen erkannt,
  "Mikrofonen und Display" als eigene Zeile.
- [gedreht_rtl](#gedreht_rtl): Hebräisch rückwärts, gedrehtes "Entwurf…" einen Buchstaben
  pro Zeile und rückwärts.
- [text_als_kurven](#text_als_kurven), [scan](#scan), [diagramm_bild](#diagramm_bild) (Screenshot):
  per OCR gelesen. [ocr_layer](#ocr_layer): übernimmt den fehlerhaften Layer.
- [formular_annotationen](#formular_annotationen): Feldwerte vorhanden, teils neben der Beschriftung.
- [versteckter_text](#versteckter_text), [schwaerzung](#schwaerzung): alles im Klartext.

**Tesseract** (5.5.3, `deu`, 300 dpi, etwa 2,5 s pro Seite auf 8 Kernen).
- Alles, was den Textlayer betrifft, ist korrekt: Ligaturen, fehlende/falsche CMap,
  Null-Bytes, Type 3, Doppelgänger (vorkomponiert, lateinisch), Stream-Reihenfolge,
  mehrspaltig, doppelter Text, Text als Kurven, Scan, OCR-Layer (eigene OCR fehlerfrei).
- [versteckter_text](#versteckter_text): nur der sichtbare Text. [schwaerzung](#schwaerzung):
  keine Daten, nur Rauschen aus den Balken ("B", "]]").
- [leerzeichen](#leerzeichen): D liest auch Tesseract teils zusammen ("Rechnungsadresseund
  Lieferadresse sindidentisch.").
- [hoch_tiefgestellt](#hoch_tiefgestellt): **falsche Werte**: "2023'", "m*", "10°" statt 10⁻³, "CO,".
- [ueberschriften_listen](#ueberschriften_listen): keine Struktur, Aufzählungszeichen "m".
- [tabellen](#tabellen): Zeilen erhalten, verbundene Kopfzelle zerfällt.
- [gedreht_rtl](#gedreht_rtl): gedrehter und hebräischer Text Unsinn ("U9M9IUM }YdIU SMIg").
- [formular_annotationen](#formular_annotationen): Feldwerte fehlen (beim Rendern mit `pdftoppm`
  nicht sichtbar).
- [formel](#formel): unbrauchbar ("H(o)= —JZ 0;0j").
- [browser_postscript](#browser_postscript): Spalten verschränkt, einzelne Fehler.

---

## Ideen für weitere Stolpersteine

- Office-Export mit Kommentaren am Rand, Word-Export mit Tagged PDF
- Fußnoten im Fließtext statt am Seitenende, Randnotizen (Marginalien)
- Tagged PDF mit Strukturbaum, dessen Reihenfolge korrekt ist, obwohl der Stream es nicht ist
- `/ActualText` (korrekt und absichtlich falsch)
- Text in Mustern (Pattern), Text in Anhängen (Embedded Files), Portfolio-PDF
- optionale Inhalte (Ebenen/OCG), die standardmäßig ausgeblendet sind
- CJK-Text mit vertikalem Satz
- abgeschnittene Datei (fehlender Trailer), kaputter Flate-Stream
- riesige Seite oder "Zip-Bombe" (sehr stark komprimierter Stream) gegen Laufzeit/Speicher
- falsch eingebettetes Bild (JPEG2000, CMYK) für Viewer und OCR
- Seite mit `/Rotate 90`, CropBox kleiner als MediaBox (Text außerhalb des sichtbaren Bereichs)

## Vorlage für einen neuen Abschnitt

```markdown
## <id>

**Was:** Was steht auf der Seite, wie sieht es aus?

**Warum relevant:** Was geht bei RAG schief? Realer Hintergrund?

**Erzeugung:** Welche Technik/welcher Helfer (falls nicht offensichtlich)?

**Beobachtet:** Was liefern die Extraktoren (aus out/vergleich.md)?

**Gegenmaßnahmen:** Wie erkennt oder behebt man es?

**Quellen:** Links, Spezifikationsabschnitte.
```
