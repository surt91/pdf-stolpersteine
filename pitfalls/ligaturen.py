"""Ligaturen: eine Glyphe für mehrere Buchstaben (ﬁ, ﬀ, ﬃ, ﬂ).

Gleicher sichtbarer Text, drei verschiedene ToUnicode-Zuordnungen:
A) korrekt aufgelöst ("fi"), B) als Ligatur-Codepoint (U+FB01), C) ohne Eintrag.
Siehe STOLPERSTEINE.md#ligaturen.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RawFont, label

TITLE = "Ligaturen"

LIGS = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi"}
REVERSE = {v: k for k, v in LIGS.items()}

LINES = [
    "Die Eﬃzienz der Auftragsﬁnanzierung wurde oﬃziell geprüft.",
    "Der Stoﬀ ist ﬂexibel, der Einﬂuss auf die Bilanz gering.",
]

FONTS = {
    "A) ToUnicode löst die Ligatur korrekt auf": RawFont("F_lig_a"),
    "B) ToUnicode verweist auf das Ligatur-Zeichen (U+FB01 usw.)": RawFont(
        "F_lig_b", tounicode=lambda gid, text: REVERSE.get(text, text)
    ),
    "C) Ligatur-Glyphen fehlen in der ToUnicode-CMap": RawFont(
        "F_lig_c", tounicode=lambda gid, text: None if text in REVERSE else text
    ),
}


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for caption, font in FONTS.items():
        for lig, meaning in LIGS.items():
            font.glyph(lig, meaning)
        y = label(c, LEFT, y, caption)
        for line in LINES:
            font.show(c, LEFT, y, 12, line)
            y -= 18
        y -= 16


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    for font in FONTS.values():
        font.install(pdf, pages[0])


def _plain(s: str) -> str:
    for k, v in LIGS.items():
        s = s.replace(k, v)
    return s


GROUND_TRUTH = "\n\n".join(
    f"*{caption}*\n\n" + "\n".join(_plain(line) for line in LINES) for caption in FONTS
)
