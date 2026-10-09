"""Wortgrenzen müssen aus Abständen geraten werden.

PDF kennt keine Wörter. Fünf Varianten, wie Text ohne (echte) Leerzeichen
positioniert sein kann:
A) jeder Buchstabe einzeln platziert, B) gesperrt (Zeichenabstand),
C) TJ-Array mit Verschiebungen statt Leerzeichen, D) zu enge Wortabstände,
E) Blocksatz mit riesigen Lücken.
Siehe STOLPERSTEINE.md#leerzeichen.
"""

import pikepdf
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, TEXT_WIDTH, RawFont, label

TITLE = "Leerzeichen und Wortgrenzen"

A = "Die Lieferung erfolgt frei Haus."
B = "Wichtiger Hinweis zur Lieferung"
C = "Das Angebot ist gültig bis Ende des Monats."
D = "Rechnungsadresse und Lieferadresse sind identisch."
E = "Kurz und gut."

TJ_FONT = RawFont("F_tj")
F, S = "Helvetica", 12


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()

    y = label(c, LEFT, y, "A) Jeder Buchstabe einzeln positioniert, keine Leerzeichen im Stream")
    c.setFont(F, S)
    x = LEFT
    for ch in A:
        if ch != " ":
            c.drawString(x, y, ch)
        x += stringWidth(ch, F, S)
    y -= 34

    y = label(c, LEFT, y, "B) Gesperrt: zusätzlicher Zeichenabstand (Tc)")
    c.setFont(F, S)
    c.drawString(LEFT, y, B, charSpace=4)
    y -= 34

    y = label(c, LEFT, y, "C) TJ-Array: Wörter mit Verschiebungen statt Leerzeichen")
    parts: list = []
    for word in C.split(" "):
        parts += [word, -320]
    TJ_FONT.show_tj(c, LEFT, y, S, parts[:-1])
    y -= 34

    y = label(c, LEFT, y, "D) Zu enge Wortabstände (1 pt)")
    c.setFont(F, S)
    x = LEFT
    for word in D.split(" "):
        c.drawString(x, y, word)
        x += stringWidth(word, F, S) + 1
    y -= 34

    y = label(c, LEFT, y, "E) Blocksatz: wenige Wörter über die ganze Zeilenbreite")
    c.setFont(F, S)
    words = E.split(" ")
    gap = (TEXT_WIDTH - sum(stringWidth(w, F, S) for w in words)) / (len(words) - 1)
    x = LEFT
    for word in words:
        c.drawString(x, y, word)
        x += stringWidth(word, F, S) + gap


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    TJ_FONT.install(pdf, pages[0])


GROUND_TRUTH = "\n\n".join(
    [
        "*A) Jeder Buchstabe einzeln positioniert, keine Leerzeichen im Stream*\n\n" + A,
        "*B) Gesperrt: zusätzlicher Zeichenabstand (Tc)*\n\n" + B,
        "*C) TJ-Array: Wörter mit Verschiebungen statt Leerzeichen*\n\n" + C,
        "*D) Zu enge Wortabstände (1 pt)*\n\n" + D,
        "*E) Blocksatz: wenige Wörter über die ganze Zeilenbreite*\n\n" + E,
    ]
)
