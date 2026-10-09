"""Gescannte Seite: nur ein Bild, kein Text.

Klassische Extraktoren liefern einen leeren String, und zwar ohne Fehlermeldung.
Ohne Prüfung ("wie viele Zeichen pro Seite?") landet das Dokument still als
leerer Chunk im Index. Leicht schief und verrauscht, wie ein echter Scan.
Siehe STOLPERSTEINE.md#scan.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, TEXT_WIDTH, draw_pil_image, text_image

TITLE = "Gescannte Seite ohne Text"

LINES = [
    "Musterfirma GmbH · Personalabteilung",
    "",
    "Bescheinigung",
    "",
    "Hiermit bestätigen wir, dass Frau Erika Mustermann",
    "seit dem 1. April 2019 in unserem Unternehmen als",
    "Projektleiterin in Vollzeit beschäftigt ist.",
    "",
    "Köln, den 14. Februar 2026",
]
H = 260


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    img = text_image(LINES, TEXT_WIDTH, H, rotate=0.8, noise=90)
    draw_pil_image(c, img, LEFT, y - H, TEXT_WIDTH, H)


GROUND_TRUTH = "\n".join(LINES).replace("\n\n\n", "\n\n")
