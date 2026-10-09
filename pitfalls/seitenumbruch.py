"""Satz über eine Seitengrenze, mit Fußnote und Fußzeile dazwischen.

Beim seitenweisen Extrahieren und Chunken wird der Satz zerschnitten. Und
selbst ohne Seitenchunks steht zwischen den Satzhälften Fußnote, Fußzeile und
Kopfzeile der nächsten Seite.
Siehe STOLPERSTEINE.md#seitenumbruch.
"""

from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import BODY_FONT, LEFT, TEXT_WIDTH, para

TITLE = "Satz über die Seitengrenze"

FILL = (
    "Diese Seite ist mit Absätzen gefüllt, damit der letzte Satz auf die nächste Seite "
    "umbricht. Die Regelung gilt für alle Standorte gleichermaßen und wurde mit dem "
    "Betriebsrat abgestimmt. "
)
SENTENCE = (
    "Wichtig: Die Kündigung eines Vertrags ist nur wirksam, wenn sie schriftlich und unter "
    "Angabe der Vertragsnummer erfolgt sowie spätestens sechs Wochen vor Ablauf der "
    "Mindestlaufzeit beim Kundenservice eingeht."
)
FOOTNOTE = "* Gilt nur für Verträge, die nach dem 1. Januar 2024 geschlossen wurden."
PARAS = 12


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for _ in range(PARAS):
        y = para(c, LEFT, y, FILL)
    lines = simpleSplit(SENTENCE, BODY_FONT, 11, TEXT_WIDTH)
    c.setFont(BODY_FONT, 11)
    c.drawString(LEFT, y, lines[0] + "*")
    c.setFont(BODY_FONT, 8)
    c.line(LEFT, 75, LEFT + 120, 75)
    c.drawString(LEFT, 64, FOOTNOTE)
    ctx.new_page()
    y = ctx.height - 100
    c.setFont(BODY_FONT, 11)
    for line in lines[1:]:
        c.drawString(LEFT, y, line)
        y -= 15
    y -= 15
    para(c, LEFT, y, "Hier beginnt ein neuer Absatz auf der zweiten Seite.")


def GROUND_TRUTH(ctx) -> str:
    lines = simpleSplit(SENTENCE, BODY_FONT, 11, TEXT_WIDTH)
    first, rest = lines[0], " ".join(lines[1:])
    return "\n\n".join(
        [FILL.strip()] * PARAS
        + [f"{first}* {rest}", "Hier beginnt ein neuer Absatz auf der zweiten Seite.", FOOTNOTE]
    )
