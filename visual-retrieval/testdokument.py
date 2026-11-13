"""Fügt das Testdokument des Artikels zu einem PDF mit 171 Seiten zusammen.

    uv run testdokument.py [ziel.pdf]

Reihenfolge: die 37 Stolperstein-Seiten für die Textextraktion, die 30 Seiten mit visuellen
Stolpersteinen, die 104 Seiten Ablenker. qpdf übernimmt die Seiten unverändert, Textlayer und
Rendering der Stolperstein-Seiten bleiben also wie in stolpersteine.pdf. Braucht qpdf.
"""

import subprocess
import sys

from prepare import DATA, HERE, STOLPER

VIS = DATA / "visuelle_stolpersteine"
TEILE = [
    STOLPER / "stolpersteine.pdf",
    *(VIS / f"{n}.pdf" for n in ("fussnoten", "nup1", "nup2", "nup4", "rechnungen", "kontrast", "gedreht")),
    *sorted((DATA / "ablenker").glob("*.pdf")),
]

if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else str(HERE.parent / "testdokument-visual-retrieval.pdf")
    subprocess.run(["qpdf", "--empty", "--pages", *map(str, TEILE), "--", ziel], check=True)
    print(ziel)
