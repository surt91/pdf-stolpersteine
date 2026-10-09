"""Hoch- und tiefgestellte Zeichen, Fußnotenzeichen.

Hochgestelltes ist im PDF nur kleinerer, angehobener Text. Extrahiert wird es
meist als normales Zeichen in der Zeile: "2023¹" wird zu "20231", "250 m²" zu
"250 m2", "10⁻³" zu "10-3". Aus Fußnotenzeichen werden falsche Zahlen.
Siehe STOLPERSTEINE.md#hoch_tiefgestellt.
"""

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, label

TITLE = "Hoch- und Tiefstellungen"

# (Text, Modus) mit Modus: "" normal, "^" hoch, "_" tief
LINES = [
    [("Der Umsatz stieg 2023", ""), ("1", "^"), (" um 12 Prozent.", "")],
    [("Die Bürofläche beträgt 250 m", ""), ("2", "^"), (".", "")],
    [("Die zulässige Abweichung liegt bei 10", ""), ("-3", "^"), (".", "")],
    [("Der CO", ""), ("2", "_"), ("-Ausstoß sank laut Bericht", ""), ("2", "^"), (" deutlich.", "")],
]
FOOTNOTES = ["1 Vorläufige Zahlen, ungeprüft.", "2 Nachhaltigkeitsbericht 2024, S. 17."]
FOOTNOTES_GT = ["¹ Vorläufige Zahlen, ungeprüft.", "² Nachhaltigkeitsbericht 2024, S. 17."]

SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
SUB = str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋")
F, S = "Helvetica", 12


def _draw_mixed(c: Canvas, x: float, y: float, pieces, size: float) -> None:
    for text, mode in pieces:
        s = size * 0.6 if mode else size
        rise = {"": 0, "^": size * 0.4, "_": -size * 0.2}[mode]
        c.setFont(F, s)
        c.drawString(x, y + rise, text)
        x += stringWidth(text, F, s)


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    for pieces in LINES:
        _draw_mixed(c, LEFT, y, pieces, S)
        y -= 24
    y -= 20
    c.line(LEFT, y + 10, LEFT + 120, y + 10)
    y = label(c, LEFT, y - 4, "Fußnoten")
    for note in FOOTNOTES:
        _draw_mixed(c, LEFT, y, [(note[0], "^"), (note[1:], "")], 9)
        y -= 13


def _gt(pieces) -> str:
    return "".join(t.translate(SUP) if m == "^" else t.translate(SUB) if m == "_" else t for t, m in pieces)


GROUND_TRUTH = "\n".join(_gt(p) for p in LINES) + "\n\n*Fußnoten*\n\n" + "\n".join(FOOTNOTES_GT)
