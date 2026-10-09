"""Scan mit eingebettetem, schlechtem OCR-Layer.

Scanner legen oft unsichtbaren Text (Render-Modus 3) über das Bild. Im Viewer
sieht man das saubere Bild, der Extraktor liefert die fehlerhafte OCR,
z. B. "l.Z34,S6" statt "1.234,56". Niemand bemerkt es, weil ja Text da ist.
Siehe STOLPERSTEINE.md#ocr_layer.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, TEXT_WIDTH, draw_pil_image, text_image

TITLE = "Scan mit fehlerhaftem OCR-Layer"

LINES = [
    "Rechnung Nr. 2026-0417",
    "Rechnungsbetrag: 1.234,56 EUR",
    "Zahlbar bis: 15.05.2026",
    "IBAN: DE89 3704 0044 0532 0130 00",
    "Verwendungszweck: Kundennummer 88172",
]
OCR = [
    "Rechnunq Nr. 2O26-O4l7",
    "Rechnunqsbetraq: l.Z34,S6 EUR",
    "Zahlbar bis: l5.O5.2O26",
    "lBAN: DE89 37O4 OO44 O532 Ol3O OO",
    "Verwendunqszweck: Kundennummer 8817Z",
]
H = 150
SIZE, LEAD, MARGIN = 12, 24, 14


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    img = text_image(LINES, TEXT_WIDTH, H, size_pt=SIZE, leading_pt=LEAD, margin_pt=MARGIN, noise=60)
    bottom = y - H
    draw_pil_image(c, img, LEFT, bottom, TEXT_WIDTH, H)
    t = c.beginText()
    t.setTextRenderMode(3)
    t.setFont("Helvetica", SIZE)
    for i, line in enumerate(OCR):
        t.setTextOrigin(LEFT + MARGIN, y - (MARGIN + SIZE + i * LEAD))
        t.textOut(line)
    t.setTextRenderMode(0)  # Tr gehört zum Grafikzustand und gilt sonst über ET hinaus
    c.drawText(t)


GROUND_TRUTH = "\n".join(LINES)
