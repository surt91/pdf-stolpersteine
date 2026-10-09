"""Formularfelder (AcroForm) und Kommentare.

Ausgefüllte Werte stehen nicht im Content-Stream, sondern in Feldern bzw. deren
Widget-Annotationen. Viele Extraktoren geben nur die Beschriftungen aus
("Name:") und verlieren die eigentlichen Daten. Gleiches gilt für Notizen.
Siehe STOLPERSTEINE.md#formular_annotationen.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT

TITLE = "Formularfelder und Kommentare"

FIELDS = [
    ("Name:", "name", "Erika Mustermann"),
    ("Eintrittsdatum:", "eintritt", "01.04.2019"),
    ("Abteilung:", "abteilung", "Controlling"),
]
NOTE = "Bitte bis Freitag unterschreiben und an die Personalabteilung senden."


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    form = c.acroForm
    for caption, name, value in FIELDS:
        c.setFont("Helvetica", 11)
        c.drawString(LEFT, y, caption)
        form.textfield(name=name, value=value, x=LEFT + 110, y=y - 5, width=220, height=20, fontSize=11, borderWidth=1)
        y -= 32
    c.setFont("Helvetica", 11)
    c.drawString(LEFT, y, "Teilzeit:")
    form.checkbox(name="teilzeit", x=LEFT + 110, y=y - 4, size=14, checked=True, buttonStyle="check")
    y -= 40
    c.drawString(LEFT, y, "Unterschrift: ________________________")
    c.textAnnotation(NOTE, Rect=(LEFT + 260, y - 4, LEFT + 280, y + 16), relative=0)


GROUND_TRUTH = (
    "\n".join(f"{cap} {val}" for cap, _, val in FIELDS)
    + "\nTeilzeit: ja\n\nUnterschrift: ________________________\n\n"
    + f"*Kommentar:* {NOTE}"
)
