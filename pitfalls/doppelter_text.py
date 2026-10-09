"""Mehrfach gezeichneter Text: Pseudo-Fettdruck und Schatten.

Manche Generatoren erzeugen "fett", indem sie denselben Text mehrfach leicht
versetzt zeichnen. Schatteneffekte funktionieren genauso. Extraktoren liefern
dann "WWaarrnnuunngg" oder den Satz zwei- bis dreimal.
Siehe STOLPERSTEINE.md#doppelter_text.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, label, para

TITLE = "Doppelter Text (Pseudo-Fett, Schatten)"

FAUX = "Warnung: Gerät nicht öffnen!"
SHADOW = "Jahresabschluss 2025"
BODY = "Bei Zuwiderhandlung erlischt die Garantie."


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Pseudo-Fettdruck: dreimal versetzt gezeichnet")
    c.setFont("Helvetica", 14)
    for dx in (0, 0.4, 0.8):
        c.drawString(LEFT + dx, y, FAUX)
    y -= 20
    y = para(c, LEFT, y, BODY)
    y -= 20
    y = label(c, LEFT, y, "B) Schatten: grauer Text versetzt hinter schwarzem Text") - 10
    c.setFont("Helvetica-Bold", 20)
    c.setFillGray(0.7)
    c.drawString(LEFT + 2, y - 2, SHADOW)
    c.setFillGray(0)
    c.drawString(LEFT, y, SHADOW)


GROUND_TRUTH = (
    "*A) Pseudo-Fettdruck: dreimal versetzt gezeichnet*\n\n" + FAUX + "\n\n" + BODY +
    "\n\n*B) Schatten: grauer Text versetzt hinter schwarzem Text*\n\n" + SHADOW
)
