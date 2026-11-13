"""Docling-Text pro Seite für die Seiten der Gegenprobe. Läuft im venv des übergeordneten Projekts:

    uv run --project .. --group parsers python docling_visuelle_stolpersteine.py
"""

import json
from pathlib import Path

from docling.document_converter import DocumentConverter

VIS = Path(__file__).resolve().parent / "data" / "visuelle_stolpersteine"
target = VIS / "text" / "docling.json"
corpus = json.loads(target.read_text()) if target.exists() else {}

converter = DocumentConverter()
for pdf in sorted(VIS.glob("*.pdf")):
    if f"{pdf.stem}-001" in corpus:
        continue
    doc = converter.convert(str(pdf)).document
    for i in range(1, doc.num_pages() + 1):
        corpus[f"{pdf.stem}-{i:03d}"] = doc.export_to_markdown(page_no=i)
    print(pdf.name, doc.num_pages(), flush=True)
    target.write_text(json.dumps(corpus, ensure_ascii=False, indent=1))
