"""Text in einem Form-XObject (wiederverwendbarer, skalierter Seitenbaustein).

Werkzeuge, die Seiten zusammensetzen, stempeln, auf Briefpapier legen oder
mehrere Seiten auf eine montieren (n-up), packen fremde Inhalte in Form-XObjects.
pdfminer analysiert Text darin standardmäßig nicht als Layout (`all_texts=False`):
Zeilen und Leerzeichen gehen verloren, alles klebt zusammen.
Siehe STOLPERSTEINE.md#text_in_xobject.
"""

from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import BODY_FONT, LEFT, TEXT_WIDTH, label, para

TITLE = "Text in Form-XObjects"

DIRECT = "Dieser Absatz steht direkt im Content-Stream der Seite."
IN_FORM = (
    "Dieser Absatz steckt in einem Form-XObject, das auf 85 Prozent verkleinert "
    "eingebunden wird, so wie es Werkzeuge zum Zusammenfügen, Stempeln oder Verkleinern "
    "von Seiten tun. Die Kündigungsfrist beträgt drei Monate zum Quartalsende."
)
SCALE = 0.85


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Direkt auf der Seite")
    y = para(c, LEFT, y, DIRECT)
    y = label(c, LEFT, y - 10, "B) In einem Form-XObject, skaliert")

    lines = simpleSplit(IN_FORM, BODY_FONT, 11, TEXT_WIDTH / SCALE)
    c.beginForm("absatz", lowerx=0, lowery=-len(lines) * 15, upperx=TEXT_WIDTH / SCALE, uppery=15)
    c.setFont(BODY_FONT, 11)
    for i, line in enumerate(lines):
        c.drawString(0, -i * 15, line)
    c.endForm()

    c.saveState()
    c.translate(LEFT, y)
    c.scale(SCALE, SCALE)
    c.doForm("absatz")
    c.restoreState()


GROUND_TRUTH = f"*A) Direkt auf der Seite*\n\n{DIRECT}\n\n*B) In einem Form-XObject, skaliert*\n\n{IN_FORM}"
