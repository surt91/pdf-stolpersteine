"""ToUnicode-Einträge, die auf U+0000 zeigen.

Kommt bei kaputten Generatoren vor, typischerweise bei Nicht-ASCII-Zeichen.
Ergebnis: Null-Bytes im Text, die z. B. PostgreSQL/pgvector nicht speichern kann
(in REIS werden sie deshalb durch U+FFFD ersetzt).
Siehe STOLPERSTEINE.md#nullbytes.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RawFont

TITLE = "Null-Bytes und Steuerzeichen"

LINES = [
    "Grüße aus Düsseldorf, Königsallee 12.",
    "Die Gebühren für März sind fällig.",
]


def _null_for_non_ascii(gid: int, text: str) -> str:
    return "".join(ch if ord(ch) < 128 else "\x00" for ch in text)


FONT = RawFont("F_null", tounicode=_null_for_non_ascii)


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for line in LINES:
        FONT.show(c, LEFT, y, 12, line)
        y -= 18


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    FONT.install(pdf, pages[0])


GROUND_TRUTH = "\n".join(LINES)
