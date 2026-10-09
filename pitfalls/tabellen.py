"""Tabellen sind nur Text an Positionen (und ein paar Linien).

A) Tabelle mit Rahmen, verbundener Kopfzelle, leerer Zelle und mehrzeiliger Zelle.
B) Rahmenlose Tabelle, nur durch Ausrichtung erkennbar, mit rechtsbündigen Zahlen.
Extrahiert entsteht eine Zahlenkolonne ohne Zeilen-/Spaltenbezug.
Siehe STOLPERSTEINE.md#tabellen.
"""

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, label

TITLE = "Tabellen"

F, FB, S = "Helvetica", "Helvetica-Bold", 10


def _cell(c, x, y, w, text, font=F, align="l"):
    c.setFont(font, S)
    if align == "r":
        c.drawRightString(x + w - 5, y, text)
    elif align == "c":
        c.drawCentredString(x + w / 2, y, text)
    else:
        c.drawString(x + 5, y, text)


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Tabelle mit Rahmen und verbundenen Zellen")
    cols = [LEFT, LEFT + 150, LEFT + 230, LEFT + 310, LEFT + 390]
    widths = [b - a for a, b in zip(cols, cols[1:])]
    rh = 18
    top = y
    # Kopf: "Region" über zwei Zeilen, "Umsatz (Mio. €)" über zwei Spalten, "Anmerkung" über zwei Zeilen
    _cell(c, cols[0], top - 22, widths[0], "Region", FB)
    _cell(c, cols[1], top - 13, widths[1] + widths[2], "Umsatz (Mio. €)", FB, "c")
    _cell(c, cols[1], top - 31, widths[1], "2023", FB, "c")
    _cell(c, cols[2], top - 31, widths[2], "2024", FB, "c")
    _cell(c, cols[3], top - 22, widths[3], "Anmerkung", FB)
    rows = [
        ("Nord", "12,4", "13,1", ""),
        ("Süd", "8,7", "9,9", "inkl. Österreich"),
        ("West", "15,0", "", "Zahlen folgen"),
    ]
    yy = top - 2 * rh - 13
    for region, a, b, note in rows:
        _cell(c, cols[0], yy, widths[0], region)
        _cell(c, cols[1], yy, widths[1], a, align="r")
        _cell(c, cols[2], yy, widths[2], b, align="r")
        _cell(c, cols[3], yy, widths[3], note)
        yy -= rh
    # mehrzeilige Zelle
    _cell(c, cols[0], yy, widths[0], "Ost (Neugründung")
    _cell(c, cols[0], yy - 12, widths[0], "seit Q3/2024)")
    _cell(c, cols[1], yy, widths[1], "–", align="r")
    _cell(c, cols[2], yy, widths[2], "2,3", align="r")
    _cell(c, cols[3], yy, widths[3], "")
    bottom = yy - 12 - 6
    c.setLineWidth(0.6)
    c.rect(cols[0], bottom, cols[-1] - cols[0], top - bottom)
    for x in cols[1:-1]:
        c.line(x, bottom, x, top if x != cols[2] else top - rh)
    c.line(cols[1], top - rh, cols[3], top - rh)
    for i in range(len(rows) + 1):
        c.line(cols[0], top - 2 * rh - i * rh, cols[-1], top - 2 * rh - i * rh)

    y = bottom - 40
    y = label(c, LEFT, y, "B) Rahmenlose Tabelle")
    data = [
        ("Position", "Menge", "Einzelpreis", "Summe"),
        ("Beratung", "12", "150,00 €", "1.800,00 €"),
        ("Reisekosten", "1", "320,50 €", "320,50 €"),
        ("Lizenz (jährlich)", "3", "1.200,00 €", "3.600,00 €"),
    ]
    xs = [LEFT, LEFT + 200, LEFT + 290, LEFT + 390]
    for i, row in enumerate(data):
        font = FB if i == 0 else F
        c.setFont(font, S)
        c.drawString(xs[0], y, row[0])
        for x, w, val in zip(xs[1:], [60, 80, 60], row[1:]):
            c.drawRightString(x + w, y, val)
        y -= 16


GROUND_TRUTH = """\
*A) Tabelle mit Rahmen und verbundenen Zellen*

| Region | Umsatz (Mio. €) 2023 | Umsatz (Mio. €) 2024 | Anmerkung |
|---|---|---|---|
| Nord | 12,4 | 13,1 | |
| Süd | 8,7 | 9,9 | inkl. Österreich |
| West | 15,0 | | Zahlen folgen |
| Ost (Neugründung seit Q3/2024) | – | 2,3 | |

*B) Rahmenlose Tabelle*

| Position | Menge | Einzelpreis | Summe |
|---|---|---|---|
| Beratung | 12 | 150,00 € | 1.800,00 € |
| Reisekosten | 1 | 320,50 € | 320,50 € |
| Lizenz (jährlich) | 3 | 1.200,00 € | 3.600,00 € |
"""
