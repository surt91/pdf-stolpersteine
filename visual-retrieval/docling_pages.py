"""Docling-Text pro Seite für die Ablenker. Läuft im venv des übergeordneten Projekts:

    uv run --project .. --group parsers python docling_pages.py
"""

import json
import re
from pathlib import Path

from docling.document_converter import DocumentConverter

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
STOLPER = HERE.parent / "out"

target = DATA / "text" / "docling.json"
target.parent.mkdir(parents=True, exist_ok=True)
corpus = json.loads(target.read_text()) if target.exists() else {}

pages = re.split(r"\n?===== Seite \d+ =====\n", (STOLPER / "stolpersteine.docling.txt").read_text())[1:]
corpus.update({f"stolpersteine-{i + 1:03d}": p for i, p in enumerate(pages)})

converter = DocumentConverter()
for pdf in sorted((DATA / "ablenker").glob("*.pdf")):
    if f"{pdf.stem}-001" in corpus:
        continue
    doc = converter.convert(str(pdf)).document
    for i in range(1, doc.num_pages() + 1):
        corpus[f"{pdf.stem}-{i:03d}"] = doc.export_to_markdown(page_no=i)
    print(pdf.name, doc.num_pages(), flush=True)
    target.write_text(json.dumps(corpus, ensure_ascii=False, indent=1))
target.write_text(json.dumps(corpus, ensure_ascii=False, indent=1))
