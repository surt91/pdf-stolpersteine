"""Irreführende Metadaten und Seitenzahlen.

- Dokumenttitel aus dem Info-Dictionary ist Müll ("Microsoft Word - Dokument1.docx").
- Kein CreationDate (hat LangChains PDFMinerParser früher zum Absturz gebracht).
- Page Labels: Deckblatt ist "i", danach beginnt die Zählung bei "1". Physische
  Seite 3 trägt also die gedruckte Seitenzahl 2.
Siehe STOLPERSTEINE.md#metadaten_seitenzahlen.
"""

import pikepdf

from pitfalls._lib import FRONT_MATTER_PAGES

TITLE = "Metadaten und Seitenzahlen"


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    info = pdf.docinfo
    for key in list(info.keys()):
        del info[key]
    info.Title = "Microsoft Word - Dokument1.docx"
    info.Author = "admin"
    info.Subject = "Vorlage_final_v2_NEU"
    info.Producer = "Acrobat Distiller 6.0 (Windows)"

    pdf.Root.PageLabels = pikepdf.Dictionary(
        Nums=[
            0,
            pikepdf.Dictionary(S=pikepdf.Name.r),
            FRONT_MATTER_PAGES,
            pikepdf.Dictionary(S=pikepdf.Name.D, St=1),
        ]
    )
