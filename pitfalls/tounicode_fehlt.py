"""Schrift ohne ToUnicode-CMap (Type0/Identity-H).

Der Content-Stream enthält nur Glyph-IDs. Ohne CMap muss ein Extraktor raten:
A) Die eingebettete TrueType-Schrift hat noch ihre cmap-Tabelle. Manche
   Extraktoren (pdfminer) rekonstruieren daraus den Text, andere geben Glyph-IDs
   als Zeichen aus (".¾QGLJXQJVIULVW").
B) Die eingebettete Schrift hat keine cmap und keine Glyphnamen mehr, wie es
   bei vielen Subset-Fonts der Fall ist. Dann hat niemand eine Chance.
Im Viewer sieht beides perfekt aus.
Siehe STOLPERSTEINE.md#tounicode_fehlt.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RawFont, label

TITLE = "Fehlende ToUnicode-CMap"

LINES_A = [
    "Kündigungsfrist: drei Monate zum Quartalsende.",
    "Ansprechpartnerin ist Frau Weber, Durchwahl 4711.",
]
LINES_B = [
    "Bei Rückfragen wenden Sie sich bitte an den Kundenservice.",
    "Die Servicezeiten sind montags bis freitags von 8 bis 18 Uhr.",
]

FONTS = {
    "A) Ohne ToUnicode, eingebettete Schrift hat noch eine cmap-Tabelle": (RawFont("F_nouni_a", tounicode=None), LINES_A),
    "B) Ohne ToUnicode, ohne cmap-Tabelle und ohne Glyphnamen": (
        RawFont("F_nouni_b", tounicode=None, strip_cmap=True),
        LINES_B,
    ),
}


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for caption, (font, lines) in FONTS.items():
        y = label(c, LEFT, y, caption)
        for line in lines:
            font.show(c, LEFT, y, 12, line)
            y -= 18
        y -= 16


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    for font, _ in FONTS.values():
        font.install(pdf, pages[0])


GROUND_TRUTH = "\n\n".join(f"*{caption}*\n\n" + "\n".join(lines) for caption, (_, lines) in FONTS.items())
