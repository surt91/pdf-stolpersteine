"""Kopf- und Fußzeilen auf jeder Seite.

Landen beim seitenweisen Extrahieren in jedem Chunk und verwässern Embeddings.
Siehe STOLPERSTEINE.md#kopf_fusszeile.
"""

from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, RIGHT

TITLE = "Kopf- und Fußzeilen"


def on_every_page(c: Canvas, ctx) -> None:
    c.setFont("Helvetica", 8)
    c.setFillGray(0.4)
    c.drawString(LEFT, ctx.height - 40, "Musterfirma GmbH · Stolperstein-Testdokument")
    c.drawRightString(RIGHT, ctx.height - 40, "VERTRAULICH – nur für den internen Gebrauch")
    c.line(LEFT, ctx.height - 46, RIGHT, ctx.height - 46)
    c.line(LEFT, 52, RIGHT, 52)
    c.drawString(LEFT, 40, "Dokument-ID: MF-2026-0815 · Version 3.2")
    c.drawRightString(RIGHT, 40, f"Seite {ctx.label}")
    c.setFillGray(0)
