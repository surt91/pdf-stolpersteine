"""Deckblatt mit Inhaltsverzeichnis.

Punktlinien ("Ligaturen ........ 3") erzeugen Rauschen in Chunks und matchen bei
der Suche auf alles. Inhaltsverzeichnisse sind zudem ein Chunk voller
Überschriften ohne Inhalt, der bei Retrieval oft weit oben landet.
Siehe STOLPERSTEINE.md#inhaltsverzeichnis.
"""

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RIGHT, page_label

TITLE = "Deckblatt und Inhaltsverzeichnis"


def draw(c: Canvas, ctx) -> None:
    c.setFont("Helvetica-Bold", 24)
    c.drawString(LEFT, ctx.height - 120, "Stolperstein-Testdokument")
    c.setFont("Helvetica", 12)
    c.drawString(LEFT, ctx.height - 145, "Ein PDF, das Textextraktoren das Leben schwer macht")

    c.setFont("Helvetica-Bold", 14)
    y = ctx.height - 200
    c.drawString(LEFT, y, "Inhaltsverzeichnis")
    y -= 24
    size = 10
    c.setFont("Helvetica", size)
    for entry in ctx.toc:
        text = f"{entry.number}. {entry.title}"
        num = page_label(entry.first_page)
        c.drawString(LEFT, y, text)
        c.drawRightString(RIGHT, y, num)
        start = LEFT + stringWidth(text, "Helvetica", size) + 4
        end = RIGHT - stringWidth(num, "Helvetica", size) - 4
        dots = "." * int((end - start) / stringWidth(".", "Helvetica", size))
        c.drawRightString(end, y, dots)
        y -= 16


def GROUND_TRUTH(ctx) -> str:
    lines = ["Stolperstein-Testdokument", "", "Ein PDF, das Textextraktoren das Leben schwer macht", "", "Inhaltsverzeichnis", ""]
    lines += [f"- {e.number}. {e.title} (Seite {page_label(e.first_page)})" for e in ctx.toc]
    return "\n".join(lines)
