"""Unicode-Doppelgänger: gleich aussehende, aber verschiedene Zeichen.

Zerlegte Umlaute (u + U+0308), Null-Breite-Leerzeichen, kyrillisches "а",
geschützte und schmale Leerzeichen, Gedanken- und Minusstriche. Korrekt
extrahiert, aber Volltextsuche, Tokenizer und Exact-Match finden nichts.
Siehe STOLPERSTEINE.md#unicode_doppelgaenger.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, dejavu

TITLE = "Unicode-Doppelgänger"

LINES = [
    # (wie im PDF, normalisiert)
    ("Herr Müller und Herr Müller sind dieselbe Person.", "Herr Müller und Herr Müller sind dieselbe Person."),
    ("Bitte ändern Sie Ihr Pass​wort regelmäßig.", "Bitte ändern Sie Ihr Passwort regelmäßig."),
    ("Kaffee und Kаffee sehen gleich aus.", "Kaffee und Kaffee sehen gleich aus."),
    ("Der Betrag von 10 000 Euro ist fällig.", "Der Betrag von 10 000 Euro ist fällig."),
    ("Siehe Seiten 3–5, Temperatur −5 °C.", "Siehe Seiten 3-5, Temperatur -5 °C."),
    ("Er sagte „Ja“ und meinte ‚Nein‘.", "Er sagte \"Ja\" und meinte 'Nein'."),
]


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    c.setFont(dejavu(), 12)
    for shown, _ in LINES:
        c.drawString(LEFT, y, shown)
        y -= 20


GROUND_TRUTH = "\n".join(norm for _, norm in LINES)
