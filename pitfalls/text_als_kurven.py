"""Text als Vektorpfade ("in Kurven umgewandelt").

Grafikprogramme und Druckvorstufe wandeln Text oft in Pfade um. Optisch
identisch, aber es gibt keinen Text mehr: Extraktoren liefern nichts, nur OCR hilft.
Siehe STOLPERSTEINE.md#text_als_kurven.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import DEJAVU, DEJAVU_BOLD, LEFT, draw_text_as_paths, label, para

TITLE = "Text als Kurven"

NORMAL = "Der folgende Hinweis ist kein Text, sondern eine Grafik aus Pfaden:"
CURVES = [
    ("Kündigungsfrist: 3 Monate zum Quartalsende", DEJAVU_BOLD, 14),
    ("Hotline: 0800 123 456 (kostenfrei)", DEJAVU, 12),
]


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    y = para(c, LEFT, y, NORMAL)
    y = label(c, LEFT, y, "Pfade:")
    for text, font, size in CURVES:
        draw_text_as_paths(c, LEFT, y, size, text, font)
        y -= size + 10


GROUND_TRUTH = NORMAL + "\n\n*Pfade:*\n\n" + "\n".join(t for t, _, _ in CURVES)
