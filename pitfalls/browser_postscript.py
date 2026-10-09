"""Browser über PostScript-Druckertreiber.

Die Chrome-PDF über PostScript „gedruckt“ (pdftops -level3 | ps2pdf). Weil die
Seite Transparenz enthält (Textschatten, Emoji), rastert pdftops die ganze Seite:
das Ergebnis ist ein einziges Bild ohne Text.
Die Originalseite wird unverändert eingesetzt (ohne unsere Kopf-/Fußzeile).
Quelle: quellen/browser.html, gebaut mit quellen/build.sh.
Siehe STOLPERSTEINE.md#browser_postscript.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._browser import GROUND_TRUTH, draw_external  # noqa: F401
from pitfalls._lib import ExternalPage

TITLE = "Browser über PostScript-Druckertreiber"

PAGE = ExternalPage("browser-postscript.pdf")
AVAILABLE = PAGE.exists
MISSING = "quellen/out/browser-postscript.pdf fehlt (siehe README, Abschnitt externe Quellen)"


def draw(c: Canvas, ctx) -> None:
    draw_external(c, ctx, PAGE)


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    PAGE.install(pdf, pages[0])
