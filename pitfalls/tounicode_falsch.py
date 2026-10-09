"""Falsche ToUnicode-CMap: Text sieht richtig aus, extrahiert wird etwas anderes.

Jedes Zeichen außer dem Leerzeichen wird in der CMap um einen Codepoint verschoben
(a→b, 3→4, Z→[, ä→å, .→/), wie bei einem bfrange mit falschem Startwert.
Solche kaputten CMaps gibt es wirklich, ebenso absichtliche "Kopierschutz"-Tricks.
Besonders tückisch: Aus "30 Tagen" wird "41 Ubhfo", aus Zahlen werden falsche Zahlen.
Siehe STOLPERSTEINE.md#tounicode_falsch.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RawFont

TITLE = "Falsche ToUnicode-CMap"

LINES = [
    "Die Zahlung erfolgt innerhalb von 30 Tagen netto.",
    "Der Rabatt beträgt 2 Prozent bei Zahlung binnen 10 Tagen.",
]


def _shift(gid: int, text: str) -> str:
    # Leerzeichen bleiben, damit der Text als Satz lesbar bleibt
    return "".join(ch if ch == " " else chr(ord(ch) + 1) for ch in text)


FONT = RawFont("F_wrong", tounicode=_shift)


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for line in LINES:
        FONT.show(c, LEFT, y, 12, line)
        y -= 18


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    FONT.install(pdf, pages[0])


GROUND_TRUTH = "\n".join(LINES)
