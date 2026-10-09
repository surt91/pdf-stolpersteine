"""Silbentrennung und harte Zeilenumbrüche.

Jede Zeile endet mit einem harten Umbruch, getrennte Wörter zerfallen in zwei
Tokens. Naives Zusammenfügen ("-\n" entfernen) macht aus "E-Mail" ein "EMail".
Variante B nutzt das weiche Trennzeichen U+00AD, das im Text stehen bleibt.
Siehe STOLPERSTEINE.md#silbentrennung.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, dejavu, label

TITLE = "Silbentrennung und Zeilenumbrüche"

A_LINES = [
    "Die Donaudampfschiff-",
    "fahrtsgesellschaft hat ihre",
    "Rechtsschutzversiche-",
    "rung zum Jahresende ge-",
    "kündigt. Rückfragen bitte per E-",
    "Mail an den Vertrieb.",
]
A_TEXT = (
    "Die Donaudampfschifffahrtsgesellschaft hat ihre Rechtsschutzversicherung zum "
    "Jahresende gekündigt. Rückfragen bitte per E-Mail an den Vertrieb."
)

B_LINES = [
    "Bitte reichen Sie die Arbeitsunfähigkeits­",
    "bescheinigung spätestens am dritten",
    "Kalendertag ein.",
]
B_TEXT = "Bitte reichen Sie die Arbeitsunfähigkeitsbescheinigung spätestens am dritten Kalendertag ein."


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = label(c, LEFT, y, "A) Schmale Spalte mit Trennstrichen (Bindestrich-Minus)")
    c.setFont(dejavu(), 12)
    for line in A_LINES:
        c.drawString(LEFT, y, line)
        y -= 16
    y -= 20
    y = label(c, LEFT, y, "B) Weiches Trennzeichen U+00AD am Zeilenende")
    c.setFont(dejavu(), 12)
    for line in B_LINES:
        c.drawString(LEFT, y, line)
        y -= 16


GROUND_TRUTH = (
    "*A) Schmale Spalte mit Trennstrichen (Bindestrich-Minus)*\n\n" + A_TEXT +
    "\n\n*B) Weiches Trennzeichen U+00AD am Zeilenende*\n\n" + B_TEXT
)
