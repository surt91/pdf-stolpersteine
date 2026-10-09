"""Information steckt in Grafiken und Bildern.

A) Balkendiagramm: Die Werte sind nur als Balkenhöhe vorhanden, als Text gibt es
   nur Achsenbeschriftung und Titel.
B) Screenshot einer Tabelle, eingefügt als Bild.
Siehe STOLPERSTEINE.md#diagramm_bild.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import DEJAVU, LEFT, draw_pil_image, label, text_image

TITLE = "Diagramme und Bilder"

VALUES = {"Q1": 12, "Q2": 18, "Q3": 9, "Q4": 22}
SCREENSHOT = [
    "Tarif         Preis/Monat",
    "Basis         9,99 €",
    "Pro           19,99 €",
    "Enterprise    auf Anfrage",
]


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Balkendiagramm")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT, y, "Abbildung 1: Neukunden je Quartal 2025")
    x0, y0, h, unit = LEFT + 30, y - 190, 150, 6
    c.setFont("Helvetica", 8)
    for tick in range(0, 26, 5):
        c.setStrokeGray(0.85)
        c.line(x0, y0 + tick * unit, x0 + 280, y0 + tick * unit)
        c.drawRightString(x0 - 5, y0 + tick * unit - 3, str(tick))
    c.setStrokeGray(0)
    c.line(x0, y0, x0, y0 + h)
    c.line(x0, y0, x0 + 280, y0)
    for i, (q, v) in enumerate(VALUES.items()):
        c.setFillColorRGB(0.2, 0.4, 0.7)
        c.rect(x0 + 20 + i * 65, y0, 40, v * unit, stroke=0, fill=1)
        c.setFillGray(0)
        c.drawCentredString(x0 + 40 + i * 65, y0 - 12, q)

    y = y0 - 50
    y = label(c, LEFT, y, "B) Screenshot einer Tabelle")
    img = text_image(SCREENSHOT, 260, 100, font_path=DEJAVU, leading_pt=20, size_pt=11)
    draw_pil_image(c, img, LEFT, y - 100, 260, 100, quality=80)


GROUND_TRUTH = """\
*A) Balkendiagramm*

Abbildung 1: Neukunden je Quartal 2025

| Quartal | Neukunden |
|---|---|
| Q1 | 12 |
| Q2 | 18 |
| Q3 | 9 |
| Q4 | 22 |

*B) Screenshot einer Tabelle*

| Tarif | Preis/Monat |
|---|---|
| Basis | 9,99 € |
| Pro | 19,99 € |
| Enterprise | auf Anfrage |
"""
