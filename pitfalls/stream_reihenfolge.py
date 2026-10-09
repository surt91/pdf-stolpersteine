"""Reihenfolge im Content-Stream ≠ Lesereihenfolge.

A) Die Zeilen eines Absatzes werden von unten nach oben gezeichnet.
B) Die Schritte einer Anleitung werden in der Reihenfolge 3, 1, 4, 2 gezeichnet,
   stehen optisch aber korrekt untereinander.
Extraktoren ohne Layoutanalyse geben die Stream-Reihenfolge wieder.
Siehe STOLPERSTEINE.md#stream_reihenfolge.
"""

from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import BODY_FONT, LEFT, TEXT_WIDTH, label

TITLE = "Stream-Reihenfolge und Lesereihenfolge"

A = (
    "Der Server wird jeden Sonntag um 3 Uhr neu gestartet. Während des Neustarts sind "
    "keine Anmeldungen möglich. Laufende Sitzungen werden vorher automatisch gespeichert. "
    "Bei Problemen hilft die Hotline unter der Nummer 1234."
)
STEPS = [
    "1. Gerät ausschalten und vom Strom trennen.",
    "2. Gehäuse öffnen und alte Batterie entnehmen.",
    "3. Neue Batterie einsetzen und Gehäuse schließen.",
    "4. Gerät wieder einschalten und Uhrzeit einstellen.",
]


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Zeilen von unten nach oben gezeichnet")
    c.setFont(BODY_FONT, 11)
    lines = simpleSplit(A, BODY_FONT, 11, TEXT_WIDTH)
    for i in reversed(range(len(lines))):
        c.drawString(LEFT, y - i * 15, lines[i])
    y -= len(lines) * 15 + 25

    y = label(c, LEFT, y, "B) Anleitung in der Reihenfolge 3, 1, 4, 2 gezeichnet")
    c.setFont(BODY_FONT, 11)
    for i in (2, 0, 3, 1):
        c.drawString(LEFT, y - i * 18, STEPS[i])


GROUND_TRUTH = (
    "*A) Zeilen von unten nach oben gezeichnet*\n\n" + A +
    "\n\n*B) Anleitung in der Reihenfolge 3, 1, 4, 2 gezeichnet*\n\n" + "\n".join(STEPS)
)
