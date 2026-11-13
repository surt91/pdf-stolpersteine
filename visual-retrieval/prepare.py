"""Baut den Korpus: Seitenbilder (150 dpi) und Text pro Seite für jede Text-Pipeline.

    uv run prepare.py                     # Bilder + pypdf + Tesseract
    (Docling läuft im venv des übergeordneten Projekts, siehe docling_pages.py)

Korpus = stolpersteine.pdf (37 Seiten) + Ablenker in data/ablenker/*.pdf.
Für stolpersteine.pdf werden pypdf-, Docling- und Tesseract-Text aus
../out/ übernommen, damit sie exakt den Ergebnissen im PDF-Artikel
entsprechen.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

import pymupdf
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
STOLPER = HERE.parent / "out"
DPI = 150


def page_ids(pdf: Path) -> list[str]:
    with pymupdf.open(pdf) as doc:
        return [f"{pdf.stem}-{i + 1:03d}" for i in range(len(doc))]


def render(pdf: Path) -> None:
    out = DATA / "seiten"
    out.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf) as doc:
        for i, page in enumerate(doc):
            target = out / f"{pdf.stem}-{i + 1:03d}.png"
            if not target.exists():
                page.get_pixmap(dpi=DPI).save(target)


def from_stolpersteine(name: str) -> list[str]:
    text = (STOLPER / f"stolpersteine.{name}.txt").read_text()
    return re.split(r"\n?===== Seite \d+ =====\n", text)[1:]


def tesseract(pdf: Path) -> list[str]:
    import pytesseract
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "300", "-png", str(pdf), f"{tmp}/s"], check=True)
        return [pytesseract.image_to_string(Image.open(p), lang="deu") for p in sorted(Path(tmp).glob("s-*.png"))]


def main() -> None:
    pdfs = [STOLPER / "stolpersteine.pdf", *sorted((DATA / "ablenker").glob("*.pdf"))]
    for pdf in pdfs:
        render(pdf)

    for name in ["pypdf", "tesseract"]:
        target = DATA / "text" / f"{name}.json"
        target.parent.mkdir(exist_ok=True)
        corpus = json.loads(target.read_text()) if target.exists() else {}
        for pdf in pdfs:
            ids = page_ids(pdf)
            if all(i in corpus for i in ids):
                continue
            if pdf.stem == "stolpersteine":
                pages = from_stolpersteine(name)
            elif name == "pypdf":
                pages = [p.extract_text() or "" for p in PdfReader(pdf).pages]
            else:
                pages = tesseract(pdf)
            corpus.update(dict(zip(ids, pages, strict=True)))
            print(name, pdf.name, len(pages))
        target.write_text(json.dumps(corpus, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
