# Experiment: Visuelles Retrieval auf den Stolpersteinen

Code zum Artikel über visuelles Retrieval. Das fertige Testdokument mit 171 Seiten liegt als
[`testdokument-visual-retrieval.pdf`](../testdokument-visual-retrieval.pdf) im Wurzelverzeichnis.

Voraussetzung: `../out/` ist gebaut und `../extract.py` ist gelaufen
(pypdf-, Docling- und Tesseract-Text für `stolpersteine.pdf`). Läuft komplett auf der CPU.

Das Testdokument hat 171 Seiten: die 37 Stolperstein-Seiten für die Textextraktion, 104 Seiten
Ablenker und 30 Seiten mit visuellen Stolpersteinen (kleine Schrift, mehrere Seiten pro Blatt,
verwechselbare Rechnungsnummern, blasser und gedrehter Text, Textlayer in Ordnung). Gesucht wird
immer in allen 171 Seiten.

1. Ablenker laden (neun Gesetze von gesetze-im-internet.de nach `data/ablenker/`):
   AGG, ArbZG, BDSG, BRKG, BUrlG, EntgFG, KSchG, NachwG, TzBfG. Dazu die Quelle der Seiten mit
   mehreren Seiten pro Blatt:
   `curl -o data/visuelle_stolpersteine/quelle/MuSchG.pdf https://www.gesetze-im-internet.de/muschg_2018/MuSchG.pdf`
2. `uv run prepare.py`: Seitenbilder (150 dpi) und pypdf-/Tesseract-Text pro Seite.
   `uv run visuelle_stolpersteine.py`: baut die PDFs mit den visuellen Stolpersteinen, ihre
   Seitenbilder und ihren pypdf- und Tesseract-Text.
3. Docling-Text, im venv des übergeordneten Projekts:
   `uv run --project .. --group parsers python docling_pages.py`
   und ebenso `docling_visuelle_stolpersteine.py`.
4. `uv run embed_visual.py <clip|colmodernvbert|colqwen2|qwen3vl>` bettet alle Seiten und alle
   Fragen ein und ist fortsetzbar (ColQwen2 ca. 30 bis 40 s/Seite auf der CPU).
   CLIP nutzt für die deutschen Fragen den mehrsprachigen Text-Encoder
   `clip-ViT-B-32-multilingual-v1`. Beide Qwen-Modelle laufen mit der Voreinstellung
   ihres Prozessors: ColQwen2 mit höchstens 768 Bild-Tokens pro Seite, Qwen3-VL-Embedding mit
   rund 1280 (ca. 37 s/Seite auf der CPU).
5. `uv run evaluate.py`: Fragen aus `fragen.json` (Stolpersteine für die Textextraktion),
   Recall@1/@3, schreibt `data/ergebnisse.json`.
6. `uv run evaluate_visuelle_stolpersteine.py`: Fragen aus `fragen_visuelle_stolpersteine.json`,
   schreibt `data/visuelle_stolpersteine/ergebnisse.json`. Von den Fußnoten- und den
   Mehrfachseiten gibt es drei Varianten desselben Inhalts. Jede wird einzeln gewertet, und die
   beiden inhaltsgleichen Schwesterseiten sind dabei aus der Rangfolge genommen.
7. `uv run extra.py`: "Was ist vertraulich?" und Zeitmessung
8. `uv run aufloesung.py <qwen3vl|colqwen2> 4`: bettet die Seiten mit kleiner Schrift mit der
   vierfachen Zahl von Bild-Tokens neu ein und wertet ihre Fragen noch einmal aus.
9. `uv run abbildungen.py`, `uv run similarity_maps.py`: Abbildungen nach `img/`
10. `uv run testdokument.py`: fügt alle 171 Seiten zu `../testdokument-visual-retrieval.pdf`
    zusammen (braucht qpdf).

`maxsim.py` ist der MaxSim-Nachbau aus dem Artikel. Fragen und Zielseiten stehen in `fragen.json`.

Verschiebung der Similarity Maps auf synthetischen Seiten (je Modell einige Minuten auf der CPU):

    uv run similarity_offset.py colqwen2
    uv run similarity_offset.py colmodernvbert
    uv run similarity_offset.py colpali   # braucht ca. 12 GB RAM
    uv run similarity_maps.py      # speichert auch die Maps der echten Testseiten
    uv run similarity_dicht.py     # echte Gesetzesseiten, nutzt data/emb/colqwen2.pt
    uv run abbildungen.py          # similarity_offset.png, similarity_vorschau*.png
