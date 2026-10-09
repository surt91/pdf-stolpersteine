"""Mathematische Formel (Ising-Modell), dreimal mit LaTeX gesetzt.

A) pdflatex: Type-1-Fonts (Computer Modern), OT1-Encoding, ohne cmap/mmap-Paket.
   Umlaute sind aus Buchstabe und Akzent zusammengesetzt ("F¨ ur"), große
   Operatoren kommen aus CMEX und heißen dort z. B. "summationdisplay" ("X").
B) lualatex + unicode-math: OpenType mit ToUnicode. Extrahiert werden die
   mathematischen Unicode-Zeichen (𝜎 U+1D70E statt σ), die keine Suche findet.
C) latex → dvips -Ppk → ps2pdf: Bitmap-Fonts als Type 3, wie in alten arXiv-PDFs.
Die drei Originalseiten werden unverändert eingesetzt (kleines Seitenformat, ohne
Kopf-/Fußzeile), damit nur der Erzeuger den Unterschied macht.
Bei allen: Hoch-/Tiefstellungen, Brüche und Summengrenzen zerfallen in Zeilen.
Quellen: quellen/formel.tex, gebaut mit quellen/build.sh.
Siehe STOLPERSTEINE.md#formel.
"""

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, ExternalPage, label

TITLE = "Mathematische Formeln (LaTeX)"

VARIANTS = {
    "A) pdflatex (Type 1, OT1)": ExternalPage("formel-pdflatex.pdf"),
    "B) lualatex mit unicode-math (OpenType)": ExternalPage("formel-lualatex.pdf"),
    "C) latex, dvips -Ppk, ps2pdf (Bitmap-Fonts, Type 3)": ExternalPage("formel-dvips.pdf"),
}
AVAILABLE = all(v.exists for v in VARIANTS.values())
MISSING = "quellen/out/formel-*.pdf fehlen, erst quellen/build.sh ausführen"


def draw(c: Canvas, ctx) -> None:
    # Platzhalter, werden im postprocess durch die Originalseiten ersetzt
    for i, caption in enumerate(VARIANTS):
        if i:
            ctx.new_page()
        y = ctx.title()
        label(c, LEFT, y, caption)


def postprocess(pdf: pikepdf.Pdf, pages: list[pikepdf.Page]) -> None:
    for ext, page in zip(VARIANTS.values(), pages):
        ext.install(pdf, page)


FORMULA = r"""Das Ising-Modell beschreibt Spins $\sigma_i \in \{-1, +1\}$ auf einem Gitter. Die Energie einer Konfiguration ist durch den Hamiltonoperator gegeben:

$$\mathcal{H}(\sigma) = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j - h \sum_{i=1}^{N} \sigma_i$$

Für die Zustandssumme gilt

$$Z = \sum_{\{\sigma\}} e^{-\beta \mathcal{H}(\sigma)}, \qquad \beta = \frac{1}{k_B T},$$

und die Magnetisierung pro Spin ergibt sich zu

$$m = \frac{1}{N} \sum_{i=1}^{N} \langle \sigma_i \rangle = \frac{1}{N\beta} \frac{\partial \ln Z}{\partial h}.$$"""

GROUND_TRUTH = "\n\n".join([FORMULA] * len(VARIANTS))
