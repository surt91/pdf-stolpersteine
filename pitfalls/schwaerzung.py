"""Schwärzung, die keine ist: schwarzes Rechteck über weiterhin vorhandenem Text.

Der klassische Datenleck-Fehler. Im Viewer geschwärzt, im extrahierten Text
vollständig lesbar. Für RAG heißt das: vertrauliche Daten im Index.
Siehe STOLPERSTEINE.md#schwaerzung.
"""

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, para

TITLE = "Schwärzung"

INTRO = "Auszug aus der Gehaltsabrechnung (personenbezogene Daten geschwärzt):"
ROWS = [
    ("Mitarbeiter: ", "Max Mustermann"),
    ("IBAN: ", "DE89 3704 0044 0532 0130 00"),
    ("Bruttogehalt: ", "6.450,00 EUR"),
    ("Steuerklasse: ", "III"),
]


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = para(c, LEFT, y, INTRO)
    for caption, secret in ROWS:
        c.setFont("Helvetica", 11)
        c.drawString(LEFT, y, caption + secret)
        x = LEFT + stringWidth(caption, "Helvetica", 11)
        c.rect(x - 1, y - 3, stringWidth(secret, "Helvetica", 11) + 2, 14, stroke=0, fill=1)
        y -= 20


GROUND_TRUTH = INTRO + "\n\n" + "\n".join(f"{cap}[geschwärzt]" for cap, _ in ROWS)
