"""Lässt mehrere Extraktoren auf die erzeugten PDFs los und schreibt einen Vergleich.

    uv run extract.py            # alle PDFs in out/
    uv run extract.py datei.pdf  # nur eine Datei

Ergebnis: out/vergleich.md (pro Stolperstein: Ground Truth und Ausgabe je
Extraktor) sowie out/<pdf>.<extraktor>.txt mit dem Rohtext. Ist diese Datei jünger
als das PDF, wird sie wiederverwendet statt neu extrahiert (zum Erzwingen löschen).

Neue Extraktoren: Funktion `pdf -> list[str]` (ein String pro Seite) schreiben
und in EXTRACTORS eintragen. Optionale Abhängigkeiten werden übersprungen,
wenn sie nicht installiert sind.
"""

from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Callable

OUT = Path(__file__).resolve().parent / "out"
NAME = "stolpersteine"


def pypdf_pages(path: Path) -> list[str]:
    from pypdf import PdfReader

    return [p.extract_text() or "" for p in PdfReader(path).pages]


def pypdf_layout_pages(path: Path) -> list[str]:
    from pypdf import PdfReader

    return [p.extract_text(extraction_mode="layout") or "" for p in PdfReader(path).pages]


def pdfminer_pages(path: Path) -> list[str]:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer

    return ["".join(el.get_text() for el in page if isinstance(el, LTTextContainer)) for page in extract_pages(path)]


def pymupdf_pages(path: Path) -> list[str]:
    import pymupdf as fitz

    with fitz.open(path) as doc:
        return [page.get_text() for page in doc]


def pdftotext_pages(path: Path) -> list[str]:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext (poppler) nicht installiert")
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, check=True).stdout
    return out.decode("utf-8", errors="replace").split("\f")[:-1]


def _split_pages(path: Path, tmp: Path) -> list[Path]:
    import pikepdf

    out = []
    with pikepdf.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            single = pikepdf.new()
            single.pages.append(page)
            out.append(tmp / f"{i + 1:03d}.pdf")
            single.save(out[-1])
    return out


def markitdown_pages(path: Path) -> list[str]:
    # MarkItDown liefert ein Dokument ohne Seitengrenzen, daher seitenweise aufrufen.
    # Intern: pdfplumber für Seiten mit Tabellen/Formularen, sonst pdfminer.
    import tempfile

    from markitdown import MarkItDown

    md = MarkItDown()
    with tempfile.TemporaryDirectory() as tmp:
        return [md.convert(str(p)).text_content for p in _split_pages(path, Path(tmp))]


def docling_pages(path: Path) -> list[str]:
    # Layoutmodell + Tabellenerkennung + OCR für Bitmaps (Standardeinstellungen).
    from docling.document_converter import DocumentConverter

    doc = DocumentConverter().convert(str(path)).document
    return [doc.export_to_markdown(page_no=i) for i in range(1, doc.num_pages() + 1)]


def unstructured_pages(path: Path) -> list[str]:
    # hi_res: Layoutmodell (YOLOX) + Textlayer, OCR (Tesseract) für Bildbereiche.
    from unstructured.partition.pdf import partition_pdf

    import pikepdf

    with pikepdf.open(path) as pdf:
        pages = [[] for _ in pdf.pages]
    for el in partition_pdf(str(path), strategy="hi_res", infer_table_structure=True, languages=["deu"]):
        text = el.text
        if el.category == "Table" and el.metadata.text_as_html:
            text = el.metadata.text_as_html
        elif el.category == "Title":
            text = "# " + text
        elif el.category == "ListItem":
            text = "- " + text
        pages[(el.metadata.page_number or 1) - 1].append(text)
    return ["\n\n".join(p) for p in pages]


def tesseract_pages(path: Path) -> list[str]:
    # Klassische OCR auf gerenderten Seiten (300 dpi), Textlayer wird ignoriert.
    import tempfile

    import pytesseract
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "300", "-png", str(path), f"{tmp}/s"], check=True)
        return [pytesseract.image_to_string(Image.open(p), lang="deu") for p in sorted(Path(tmp).glob("s-*.png"))]


def from_file(name: str) -> Callable[[Path], list[str]]:
    """Vorberechnete Ausgabe, z. B. von einem multimodalen LLM auf den Seitenbildern.

    Erwartet out/<pdf-name>.<name>.txt im Format "===== Seite N =====" (wie die
    übrigen .txt-Dateien). Existiert die Datei nicht, wird der Extraktor übersprungen.
    """

    def load(path: Path) -> list[str]:
        f = OUT / f"{path.stem}.{name}.txt"
        if not f.exists():
            raise FileNotFoundError(f"{f.name} fehlt (siehe README, Abschnitt multimodales LLM)")
        parts = re.split(r"\n?===== Seite \d+ =====\n", f.read_text())
        return parts[1:]

    load.precomputed = True
    return load


EXTRACTORS: dict[str, Callable[[Path], list[str]]] = {
    "pypdf": pypdf_pages,
    "pypdf-layout": pypdf_layout_pages,
    "pdfminer": pdfminer_pages,
    "pymupdf": pymupdf_pages,
    "pdftotext": pdftotext_pages,
    "markitdown": markitdown_pages,
    "docling": docling_pages,
    "unstructured": unstructured_pages,
    "tesseract": tesseract_pages,
    "haiku": from_file("haiku"),
    "sonnet": from_file("sonnet"),
}


def visible(s: str) -> str:
    """Macht Steuer- und unsichtbare Zeichen im Report sichtbar."""
    return "".join(f"<U+{ord(ch):04X}>" if (ord(ch) < 32 and ch not in "\n\t") or ch in "­​" else ch for ch in s)


# Kopf- und Fußzeile (siehe pitfalls/kopf_fusszeile.py) werden vor dem Vergleich entfernt,
# sonst bestraft der Wert jeden Extraktor, der sie korrekt mitliefert, auf jeder Seite.
# Trennzeichen tolerant, weil OCR "·" und "–" anders liest.
HEADER_FOOTER = re.compile(
    r"Musterfirma GmbH\s*\W?\s*Stolperstein-Testdokument|VERTRAULICH\s*\W?\s*nur für den internen Gebrauch"
    r"|Dokument-ID: MF-2026-0815\s*\W?\s*Version 3\.2|^\W*Seite [ivx\d]+\s*$",
    re.MULTILINE,
)


def similarity(a: str, b: str) -> float:
    b = HEADER_FOOTER.sub(" ", b)
    norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[*#|\-_]", " ", s)).strip()
    return difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()


def ground_truth_sections() -> dict[str, str]:
    text = (OUT / f"{NAME}.ground_truth.md").read_text()
    parts = re.split(r"<!-- (\w+): Seite\(n\) [\d, ]+ -->\n", text)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def run(path: Path) -> dict[str, list[str] | str]:
    results: dict[str, list[str] | str] = {}
    for name, fn in EXTRACTORS.items():
        cached = OUT / f"{path.stem}.{name}.txt"
        if not getattr(fn, "precomputed", False) and cached.exists() and cached.stat().st_mtime > path.stat().st_mtime:
            # Ergebnis ist jünger als das PDF: nicht neu rechnen (Docling braucht Minuten)
            results[name] = re.split(r"\n?===== Seite \d+ =====\n", cached.read_text())[1:]
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pages = fn(path)
            results[name] = pages
            if getattr(fn, "precomputed", False):
                continue
            (OUT / f"{path.stem}.{name}.txt").write_text(
                "".join(f"\n===== Seite {i + 1} =====\n{p}" for i, p in enumerate(pages))
            )
        except Exception as e:  # noqa: BLE001 – Fehler sind hier ein Ergebnis
            results[name] = f"FEHLER: {type(e).__name__}: {e}"
    return results


def report(main: dict, variants: dict[str, dict]) -> str:
    pages = json.loads((OUT / f"{NAME}.seiten.json").read_text())
    gt = ground_truth_sections()
    lines = ["# Vergleich der Extraktoren\n", "Ähnlichkeit = grober difflib-Wert gegen die Ground Truth (0–1), ohne Kopf-/Fußzeile, "
        "Markdown-Zeichen und Leerraum. Nur ein Wegweiser, die Ausgaben unten sind maßgeblich.\n"]

    names = list(main)
    lines.append("| Stolperstein | " + " | ".join(names) + " |")
    lines.append("|---|" + "---|" * len(names))
    for pid, nums in pages.items():
        row = []
        for n in names:
            res = main[n]
            if isinstance(res, str):
                row.append("Fehler")
            else:
                text = "\n".join(res[p - 1] for p in nums if p - 1 < len(res))
                row.append(f"{similarity(gt.get(pid, ''), text):.2f}")
        lines.append(f"| {pid} | " + " | ".join(row) + " |")

    if variants:
        lines.append("\n## Varianten\n")
        for vname, res in variants.items():
            lines.append(f"### {vname}\n")
            for n, r in res.items():
                status = r if isinstance(r, str) else f"{len(r)} Seiten, {sum(len(p) for p in r)} Zeichen"
                lines.append(f"- **{n}**: {status}")
            lines.append("")

    for pid, nums in pages.items():
        lines.append(f"\n## {pid} (Seite {', '.join(map(str, nums))})\n")
        lines.append("**Ground Truth**\n\n```\n" + gt.get(pid, "") + "\n```\n")
        for n in names:
            res = main[n]
            text = res if isinstance(res, str) else "\n".join(res[p - 1] for p in nums if p - 1 < len(res))
            lines.append(f"**{n}**\n\n```\n{visible(text).strip()}\n```\n")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            for n, r in run(Path(arg)).items():
                print(f"== {n}\n{r if isinstance(r, str) else ''.join(r)}")
        return
    main_res = run(OUT / f"{NAME}.pdf")
    variants = {p.stem: run(p) for p in sorted(OUT.glob(f"{NAME}--*.pdf"))}
    (OUT / "vergleich.md").write_text(report(main_res, variants))
    print(f"-> {OUT / 'vergleich.md'}")


if __name__ == "__main__":
    main()
