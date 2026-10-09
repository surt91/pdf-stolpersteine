"""Browser: Chrome „Drucken als PDF“.

Chrome/Chromium headless (--print-to-pdf). Skia schreibt CID-TrueType-Subsets
mit ToUnicode, Emoji als Type-3-Bitmap. Blocksatz: jedes Wort einzeln positioniert.
Die Originalseite wird unverändert eingesetzt (ohne unsere Kopf-/Fußzeile).
Quelle: quellen/browser.html, gebaut mit quellen/build.sh.
Siehe STOLPERSTEINE.md#browser_chrome.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._browser import GROUND_TRUTH, draw_external  # noqa: F401
from pitfalls._lib import ExternalPage

TITLE = "Browser: Chrome „Drucken als PDF“"

PAGE = ExternalPage("browser-chrome.pdf")
AVAILABLE = PAGE.exists
MISSING = "quellen/out/browser-chrome.pdf fehlt (siehe README, Abschnitt externe Quellen)"


def draw(c: Canvas, ctx) -> None:
    draw_external(c, ctx, PAGE)


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    PAGE.install(pdf, pages[0])
