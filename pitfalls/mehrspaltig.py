"""Zweispaltiges Layout, im Content-Stream zeilenweise verschränkt.

Die Zeilen werden abwechselnd links und rechts gezeichnet. Extraktoren, die der
Stream-Reihenfolge folgen oder Zeilen über die ganze Breite zusammenfassen,
mischen zwei Themen zu einem Satzbrei.
Siehe STOLPERSTEINE.md#mehrspaltig.
"""

from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import BODY_FONT, LEFT, TEXT_WIDTH

TITLE = "Mehrspaltiges Layout"

LEFT_COL = (
    "Urlaubsregelung: Jeder Mitarbeitende hat Anspruch auf 30 Urlaubstage pro Jahr. "
    "Resturlaub muss bis zum 31. März des Folgejahres genommen werden, sonst verfällt er. "
    "Urlaubsanträge sind mindestens zwei Wochen im Voraus zu stellen."
)
RIGHT_COL = (
    "Reisekosten: Dienstreisen werden mit der Bahn in der zweiten Klasse durchgeführt. "
    "Hotelkosten werden bis 120 Euro pro Nacht erstattet. Belege sind innerhalb von "
    "vier Wochen nach Reiseende einzureichen."
)

GAP = 24
COL_W = (TEXT_WIDTH - GAP) / 2


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    size, leading = 11, 15
    c.setFont(BODY_FONT, size)
    left = simpleSplit(LEFT_COL, BODY_FONT, size, COL_W)
    right = simpleSplit(RIGHT_COL, BODY_FONT, size, COL_W)
    for i in range(max(len(left), len(right))):
        if i < len(left):
            c.drawString(LEFT, y, left[i])
        if i < len(right):
            c.drawString(LEFT + COL_W + GAP, y, right[i])
        y -= leading


GROUND_TRUTH = LEFT_COL + "\n\n" + RIGHT_COL
