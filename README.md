# PDF-Stolpersteine: ein Testdokument für Textextraktion

Dieses Repository erzeugt `out/stolpersteine.pdf`: ein PDF, das im Viewer harmlos
aussieht, in dem aber auf jeder Seite ein typisches Problem für die Textextraktion
steckt (Ligaturen, fehlende ToUnicode-CMaps, mehrspaltiges Layout, Scans, versteckter
Text, falsche Schwärzung …). Dazu gibt es eine Ground Truth und ein Skript, das
mehrere Extraktoren vergleicht.

Was die einzelnen Stolpersteine sind, warum sie für RAG relevant sind und was die
Extraktoren daraus machen, steht in **[STOLPERSTEINE.md](STOLPERSTEINE.md)**.

Wer nur das Testdokument braucht, muss nichts bauen: [`out/stolpersteine.pdf`](out/stolpersteine.pdf),
die Ground Truth [`out/stolpersteine.ground_truth.md`](out/stolpersteine.ground_truth.md) und
die Ausgaben aller Extraktoren liegen fertig im Repository, der Vergleich in
[`out/vergleich.md`](out/vergleich.md).

## Schnellstart

```bash
./quellen/build.sh  # optional: erzeugt die externen Quell-PDFs neu (LaTeX, Chrome, LibreOffice)
uv run build.py     # erzeugt out/stolpersteine*.pdf, Ground Truth, Seitenzuordnung
uv run extract.py   # lässt pypdf, pdfminer, PyMuPDF, pdftotext los -> out/vergleich.md
```

Die externen Quell-PDFs liegen fertig in `quellen/out/`, `build.py` läuft also auch ohne
LaTeX, Chrome und LibreOffice. `pdftotext` (Poppler) ist optional; fehlt es, steht im Vergleich ein Fehler.
Docling, MarkItDown, Unstructured und pytesseract liegen in einer eigenen
Abhängigkeitsgruppe, weil sie groß sind (PyTorch, Modelle werden beim ersten Lauf
heruntergeladen; der Lauf dauert auf CPU einige Minuten):

```bash
uv sync --group parsers
```

Ohne die Gruppe stehen diese Extraktoren im Vergleich als Fehler. Tesseract (mit
deutschen Sprachdaten, z. B. `pacman -S tesseract tesseract-data-deu`) muss als
Systempaket installiert sein, Unstructured `hi_res` braucht es ebenfalls.

Ergebnisse in `out/`:

| Datei | Inhalt |
|---|---|
| `stolpersteine.pdf` | das Testdokument |
| `stolpersteine--kaputte_xref.pdf`, `stolpersteine--verschluesselt.pdf` | Varianten, die ein ganzes Dokument betreffen |
| `stolpersteine.ground_truth.md` | was ein perfekter Extraktor liefern sollte |
| `stolpersteine.seiten.json` | welcher Stolperstein auf welcher Seite steht |
| `stolpersteine.<extraktor>.txt` | Rohtext je Extraktor |
| `vergleich.md` | Tabelle mit groben Ähnlichkeitswerten und Ausgaben je Stolperstein |

**Ground Truth** ist hier definiert als das, was ein Mensch beim Lesen als Inhalt
wahrnimmt und was in einen RAG-Index gehört: ohne Kopf-/Fußzeilen, Wasserzeichen,
unsichtbaren oder geschwärzten Text, mit normalisierten Zeichen (`fi` statt `ﬁ`),
Tabellen als Markdown.

Die Ähnlichkeitswerte in `vergleich.md` sind grob (difflib auf der ganzen Seite,
ohne Kopf- und Fußzeile). Sie zeigen, wo man hinschauen sollte. Für ein Urteil
taugen sie nicht, dafür muss man die Ausgaben selbst lesen.

## Aufbau

```
build.py              Rahmen: rendert alle Stolpersteine, ruft Hooks auf, schreibt out/
extract.py            Extraktoren und Vergleichsbericht
pitfalls/__init__.py  Registry: Liste und Reihenfolge der Stolpersteine
pitfalls/_lib.py      Helfer (Absätze, eigene Font-Einbettung, Type-3-Fonts, Bilder, …)
pitfalls/<id>.py      ein Modul pro Stolperstein
fonts/                DejaVu-Schriften (freie Lizenz, siehe fonts/DejaVu-LICENSE)
STOLPERSTEINE.md      Katalog mit Erklärung, Beobachtungen und Quellen
```

Das PDF wird mit [reportlab](https://www.reportlab.com/) gezeichnet und anschließend
mit [pikepdf](https://pikepdf.readthedocs.io/) (qpdf) nachbearbeitet. Wo reportlab
etwas nicht kann, etwa eine bewusst kaputte ToUnicode-CMap, schreiben die Module
rohe PDF-Operatoren in den Content-Stream (`c._code.append(...)`) und installieren
die passenden Ressourcen im `postprocess`.

## Einen neuen Stolperstein hinzufügen

1. **Modul anlegen**: `pitfalls/<id>.py`. Der Dateiname ist die ID; sie taucht in
   `seiten.json`, im Vergleich und als Anker in `STOLPERSTEINE.md` auf.
2. **In die Registry eintragen**: `<id>` in `PITFALLS` in `pitfalls/__init__.py`
   an der gewünschten Stelle einfügen. Die Reihenfolge dort ist die Reihenfolge im PDF.
3. **Dokumentieren**: einen Abschnitt `## <id>` in `STOLPERSTEINE.md` ergänzen
   (Vorlage am Ende der Datei).
4. `uv run build.py && uv run extract.py` ausführen und `out/vergleich.md` ansehen:
   Schnappt die Falle zu? Die Beobachtungen in `STOLPERSTEINE.md` eintragen.

### Minimales Modul

```python
"""Kurze Beschreibung. Siehe STOLPERSTEINE.md#mein_stolperstein."""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, para

TITLE = "Mein Stolperstein"          # Seitenüberschrift und Eintrag im Inhaltsverzeichnis

TEXT = "Der sichtbare Inhalt der Seite."


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()                  # zeichnet "N. TITLE", gibt y darunter zurück
    para(c, LEFT, y, TEXT)


GROUND_TRUTH = TEXT                   # String oder Funktion ctx -> str
```

### Hooks

Ein Modul definiert nur die Hooks, die es braucht. Aufgerufen werden sie in dieser
Reihenfolge:

| Hook | Wann / wofür | Beispiel |
|---|---|---|
| `draw(c, ctx)` | zeichnet die eigene(n) Seite(n). Ohne `draw` bekommt das Modul keine Seite. Mehr Seiten mit `ctx.new_page()` | fast alle |
| `on_every_page(c, ctx)` | wird zu Beginn jeder Seite aufgerufen | `kopf_fusszeile` |
| `postprocess(pdf, pages)` | pikepdf-Nachbearbeitung; `pages` sind die eigenen Seiten | `tounicode_falsch`, `metadaten_seitenzahlen` |
| `finalize(data, page_numbers) -> bytes` | Eingriff auf Byte-Ebene nach dem Speichern | `inkrementelles_update` |
| `variant(data) -> bytes` | erzeugt eine eigene Datei `stolpersteine--<id>.pdf` | `kaputte_xref`, `verschluesselt` |

Pflichtattribut ist `TITLE`. Hat das Modul ein `draw`, braucht es auch `GROUND_TRUTH`.

Nützliches aus `ctx`: `ctx.width`/`ctx.height` (A4 in pt), `ctx.page` (physische Seite),
`ctx.label` (gedruckte Seitenzahl), `ctx.toc` (Inhaltsverzeichnis aus dem ersten Durchlauf).

### Helfer in `pitfalls/_lib.py`

| Helfer | Zweck |
|---|---|
| `para(c, x, y, text, ...)` | umbrochener Absatz in Helvetica, sauber extrahierbar |
| `label(c, x, y, text)` | kleine graue Zwischenzeile ("A) …") |
| `dejavu(bold=, serif=)` | DejaVu bei reportlab registrieren (für Nicht-Latin-1-Zeichen) |
| `RawFont(name, tounicode=..., strip_cmap=...)` | Type0-Schrift mit frei wählbarer ToUnicode-CMap; `show()`/`show_tj()` in `draw`, `install()` in `postprocess` |
| `Type3Font(name)` | Type-3-Schrift aus Glyphumrissen ohne Zeichenzuordnung |
| `draw_text_as_paths(c, x, y, size, text)` | Text als Vektorpfade |
| `text_image(lines, w, h, ...)` + `draw_pil_image(...)` | Text als Rasterbild (Scan, Screenshot) |

### Konventionen

- **Eindeutige Ressourcennamen**: `RawFont`/`Type3Font` brauchen einen pro Modul
  eindeutigen Namen (`F_<kürzel>`), sonst überschreiben sich die Fonts.
- **Font-Objekte auf Modulebene** anlegen: `draw` und `postprocess` müssen dasselbe
  Objekt sehen. Es wird zweimal gerendert (erst für das Inhaltsverzeichnis), das ist
  dafür unschädlich.
- **Nur die Falle, kein Erklärtext auf der Seite**: Die Seite enthält Titel, ggf.
  kurze Variantenbeschriftung ("A) …") und den Testinhalt. Die Erklärung gehört in
  `STOLPERSTEINE.md` und den Docstring.
- **Ground Truth ehrlich halten**: Wenn ein Mensch es nicht sieht, gehört es nicht hinein.
- **Reproduzierbar**: Kein Zufall ohne festen Seed, reportlab läuft mit `invariant=1`.

### Seiten aus fremden Erzeugern (LaTeX, Browser, Office, …)

Manche Stolpersteine entstehen erst durch den Erzeuger: Wie ein Browser beim
"Drucken als PDF" Schriften einbettet oder wie ein DVI-Workflow Bitmap-Fonts
erzeugt, lässt sich mit reportlab nicht nachbauen. Dafür gibt es `quellen/`:

```
quellen/formel.tex    Ising-Modell, wird mit pdflatex, lualatex und latex+dvips gesetzt
quellen/office.fodt   Betriebsvereinbarung (Flat-ODT) für den LibreOffice-Export
quellen/browser.html  Intranet-Seite für "Drucken als PDF"
quellen/build.sh      erzeugt quellen/out/*.pdf
```

Ein Modul bindet eine solche Seite mit `ExternalPage("datei.pdf")` aus `_lib.py` ein:
`draw()` zeichnet einen Platzhalter (damit Seitenzählung und Inhaltsverzeichnis
stimmen), `postprocess()` ersetzt ihn durch die Originalseite (`mode="replace"`,
Standard). Die Seite bleibt so exakt, wie der Erzeuger sie geschrieben hat, nur ohne
unsere Kopf- und Fußzeile. `mode="overlay"` setzt die Seite stattdessen als
Form-XObject in die eigene Seite. Das verändert aber das Extraktionsverhalten (siehe
[text_in_xobject](STOLPERSTEINE.md#text_in_xobject)) und taugt daher nicht für
faire Vergleiche.

Fehlt die Quelldatei, setzt das Modul `AVAILABLE = False` und wird beim Bauen mit
Hinweis übersprungen (z. B. wenn `quellen/build.sh` nicht gelaufen ist):

```python
PAGE = ExternalPage("browser-chrome.pdf")
AVAILABLE = PAGE.exists
MISSING = "quellen/out/browser-chrome.pdf fehlt"
```

Ideen für weitere Erzeuger: Scanner-Software, Reporting-Tools (JasperReports, SAP),
`wkhtmltopdf`, macOS-Vorschau, PDF-Ausgabe aus PowerPoint mit Notizen.

### Einen Extraktor hinzufügen

In `extract.py` eine Funktion `pfad -> list[str]` (ein String pro Seite) schreiben
und in `EXTRACTORS` eintragen. Fehler werden abgefangen und im Bericht angezeigt.
Weitere Kandidaten: MinerU, pymupdf4llm, docTR, PaddleOCR.

### Multimodales LLM

Ausgaben, die nicht aus einem Python-Aufruf kommen, werden über `from_file("<name>")`
eingebunden: `extract.py` liest dann `out/stolpersteine.<name>.txt` im Format
`===== Seite N =====`. Für Haiku und Sonnet:

1. Seitenbilder rendern: `mkdir -p out/seiten && pdftoppm -r 110 -png out/stolpersteine.pdf out/seiten/seite`
2. Das Modell mit dem Prompt aus [`vlm_prompt.md`](vlm_prompt.md) auf die Bilder loslassen
   (hier: Haiku- bzw. Sonnet-Subagent in Claude Code; geht genauso über die API mit einem Bild pro Seite).
3. `uv run extract.py`

Nach Änderungen am PDF müssen die Seitenbilder und die Transkription neu erzeugt werden,
sonst vergleicht der Bericht mit einer veralteten Fassung.

## Lizenz

Code, Testdokument, Ground Truth und Katalog stehen unter der [MIT-Lizenz](LICENSE).
Die DejaVu-Schriften in `fonts/` haben eine eigene, freie Lizenz (`fonts/DejaVu-LICENSE`).
