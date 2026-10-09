"""Nicht eingebettete Schrift ohne Breitenangaben (/Widths).

Die Schrift "Calibri" wird nur beim Namen genannt: keine eingebettete Fontdatei,
kein /Widths-Array, kein MissingWidth. Der Viewer ersetzt sie durch eine
Systemschrift und sieht gut aus. Extraktoren, die Lücken aus den Glyphbreiten der
PDF-Schrift berechnen, müssen die Breiten raten: pypdf nimmt 500/1000 em an
(zu breit für i, l, f, t, die Lücken schrumpfen, Leerzeichen fehlen),
pdfminer 0 (jede Glyphe ein Punkt, die Zeilen zerfallen).
A) Leerzeichen im Stream, B) jedes Wort einzeln positioniert (wie bei vielen
Reporting-Tools).
Siehe STOLPERSTEINE.md#schrift_nicht_eingebettet.
"""

import pikepdf
from pikepdf import Array, Dictionary, Name
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, add_font_resource, label

TITLE = "Nicht eingebettete Schrift"

A = [
    "Die Kündigungsfrist beträgt drei Monate zum Quartalsende.",
    "Sie ist schriftlich gegenüber der Personalabteilung zu erklären.",
]
B = [
    "Die Lieferung erfolgt frei Haus und ist bis zur Übergabe versichert.",
    "Für Teillieferungen fallen keine zusätzlichen Kosten an.",
]

NAME, S, LEAD = "F_ne", 12, 17
# Positionen wie mit den Metriken des Erzeugers berechnet (Helvetica als Näherung)
METRICS = "Helvetica"


def _tj(x: float, y: float, text: str) -> str:
    s = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"BT /{NAME} {S} Tf 1 0 0 1 {x:.3f} {y:.3f} Tm ({s}) Tj ET"


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()

    y = label(c, LEFT, y, "A) Leerzeichen im Content-Stream")
    for line in A:
        c._code.append(_tj(LEFT, y, line))
        y -= LEAD
    y -= 17

    y = label(c, LEFT, y, "B) Jedes Wort einzeln positioniert")
    for line in B:
        x = LEFT
        for word in line.split(" "):
            c._code.append(_tj(x, y, word))
            x += stringWidth(word + " ", METRICS, S)
        y -= LEAD


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    descriptor = Dictionary(
        Type=Name.FontDescriptor, FontName=Name("/Calibri"), Flags=32,
        FontBBox=Array([-503, -313, 1240, 1026]), ItalicAngle=0,
        Ascent=750, Descent=-250, CapHeight=632, StemV=80,
    )  # bewusst ohne FontFile2 und ohne MissingWidth
    font = Dictionary(
        Type=Name.Font, Subtype=Name.TrueType, BaseFont=Name("/Calibri"),
        Encoding=Name.WinAnsiEncoding, FontDescriptor=pdf.make_indirect(descriptor),
    )  # bewusst ohne FirstChar/LastChar/Widths
    add_font_resource(pages[0], NAME, pdf.make_indirect(font))


GROUND_TRUTH = "\n\n".join(
    [
        "*A) Leerzeichen im Content-Stream*\n\n" + "\n".join(A),
        "*B) Jedes Wort einzeln positioniert*\n\n" + "\n".join(B),
    ]
)
