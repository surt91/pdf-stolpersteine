"""Gedrehter Text und Rechts-nach-links-Schrift.

A) Randnotiz um 90° gedreht, B) kopfstehender Text,
C) Hebräisch in visueller Reihenfolge gespeichert (wie es viele Generatoren tun):
   extrahiert kommt der Text rückwärts heraus.
Siehe STOLPERSTEINE.md#gedreht_rtl.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RIGHT, dejavu, label, para

TITLE = "Gedrehter Text und Schreibrichtung"

MAIN = (
    "Dieser Absatz ist ganz normaler Fließtext. Am rechten Rand steht eine gedrehte "
    "Randnotiz, darunter ein kopfstehender Hinweis."
)
SIDE = "Entwurf – Freigabe durch die Rechtsabteilung ausstehend"
UPSIDE = "Bitte nicht knicken"
HEBREW = "שלום עולם"  # logische Reihenfolge ("Hallo Welt")


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) und B) Gedrehte Elemente")
    y = para(c, LEFT, y, MAIN, width=380)

    c.saveState()
    c.translate(RIGHT + 10, 300)
    c.rotate(90)
    c.setFont("Helvetica", 9)
    c.drawString(0, 0, SIDE)
    c.restoreState()

    c.saveState()
    c.translate(LEFT + 150, y - 10)
    c.rotate(180)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0, 0, UPSIDE)
    c.restoreState()

    y -= 60
    y = label(c, LEFT, y, "C) Hebräisch, in visueller Reihenfolge gespeichert")
    c.setFont(dejavu(), 14)
    c.drawString(LEFT, y, HEBREW[::-1])


GROUND_TRUTH = (
    "*A) und B) Gedrehte Elemente*\n\n" + MAIN + "\n\n" + UPSIDE + "\n\n" + SIDE +
    "\n\n*C) Hebräisch, in visueller Reihenfolge gespeichert*\n\n" + HEBREW
)
