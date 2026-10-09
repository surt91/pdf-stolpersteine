"""Wasserzeichen und Stempel mitten im Text.

Ein großes, diagonales "ENTWURF" wird zwischen zwei Absätzen in den Stream
geschrieben. Es landet mitten im extrahierten Text, gedrehte Buchstaben werden
oft einzeln oder in seltsamer Reihenfolge ausgegeben.
Siehe STOLPERSTEINE.md#wasserzeichen.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, para

TITLE = "Wasserzeichen"

P1 = (
    "Die Arbeitszeit beträgt 40 Stunden pro Woche. Gleitzeit ist zwischen 7 und 20 Uhr "
    "möglich, die Kernarbeitszeit liegt zwischen 10 und 15 Uhr."
)
P2 = (
    "Überstunden werden auf einem Arbeitszeitkonto erfasst und können in Absprache mit "
    "der Führungskraft abgebaut werden. Mehr als 50 Plusstunden sind nicht zulässig."
)


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = para(c, LEFT, y, P1)
    c.saveState()
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.translate(ctx.width / 2, ctx.height / 2 + 100)
    c.rotate(35)
    c.setFont("Helvetica-Bold", 90)
    c.drawCentredString(0, 0, "ENTWURF")
    c.restoreState()
    y = para(c, LEFT, y, P2)
    c.saveState()
    c.setStrokeColorRGB(0.8, 0, 0)
    c.setFillColorRGB(0.8, 0, 0)
    c.translate(LEFT + 300, y - 60)
    c.rotate(-8)
    c.roundRect(0, 0, 130, 34, 4, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(65, 10, "GEPRÜFT")
    c.restoreState()


GROUND_TRUTH = P1 + "\n\n" + P2
