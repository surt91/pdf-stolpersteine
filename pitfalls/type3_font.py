"""Type-3-Schrift: Glyphen sind kleine PDF-Zeichenprogramme.

Glyphnamen ohne Bedeutung (/g1, /g2, …) und keine ToUnicode-CMap. So sehen
z. B. Bitmap-Fonts aus alten LaTeX/dvips-Workflows oder manche Exporte aus
Grafikprogrammen aus. Extraktoren haben keine Chance, die Zeichen zu erkennen.
Siehe STOLPERSTEINE.md#type3_font.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, Type3Font

TITLE = "Type-3-Schrift ohne Zeichenzuordnung"

LINES = [
    "Diese Zeilen verwenden eine Type-3-Schrift.",
    "Die Garantie verlängert sich auf 24 Monate.",
]

FONT = Type3Font("F_t3")


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for line in LINES:
        FONT.show(c, LEFT, y, 12, line)
        y -= 18


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    FONT.install(pdf, pages[0])


GROUND_TRUTH = "\n".join(LINES)
