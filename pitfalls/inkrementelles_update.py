"""Inkrementelles Update: alte Fassung steckt noch in der Datei.

PDFs können geändert werden, indem neue Objekte ans Dateiende angehängt werden.
Die alte Fassung bleibt in den Bytes erhalten. Hier wird der Vertragswert von
50.000 auf 75.000 EUR geändert. Normale Parser lesen die neueste Revision; wer
aber "rohe" Strings sucht, Dateien repariert oder Revisionen vergleicht, findet
beide Werte.
Siehe STOLPERSTEINE.md#inkrementelles_update.
"""

import io
import re

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from pitfalls._lib import LEFT, para

TITLE = "Inkrementelles Update"

OLD, NEW = "50.000", "75.000"
TEXT = "Der Vertragswert beträgt {} EUR netto. Die Laufzeit beträgt 24 Monate."


def draw(c: Canvas, ctx) -> None:
    y = ctx.title()
    para(c, LEFT, y, TEXT.format(OLD))


def _unparse(value) -> str:
    # pikepdf liefert Skalare als Python-Werte; über ein Array bekommen wir PDF-Syntax.
    return pikepdf.Array([value]).unparse(resolved=False).decode()[1:-1].strip()


def finalize(data: bytes, pages: list[int]) -> bytes:
    pdf = pikepdf.open(io.BytesIO(data))
    page = pdf.pages[pages[0] - 1].obj
    content = page.Contents.read_bytes().replace(OLD.encode(), NEW.encode())
    new_num = int(pdf.trailer.Size)
    page_num = page.objgen[0]

    entries = []
    for key, value in page.items():
        if key == "/Contents":
            entries.append(f"/Contents {new_num} 0 R")
        else:
            entries.append(f"{key} {_unparse(value)}")
    page_obj = f"{page_num} 0 obj\n<< {' '.join(entries)} >>\nendobj\n".encode()
    stream_obj = (
        f"{new_num} 0 obj\n<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream\nendobj\n"
    )

    prev = int(re.findall(rb"startxref\s+(\d+)", data)[-1])
    out = bytearray(data)
    if not out.endswith(b"\n"):
        out += b"\n"
    page_off = len(out)
    out += page_obj
    stream_off = len(out)
    out += stream_obj
    xref_off = len(out)
    trailer = pdf.trailer
    out += (
        "xref\n0 1\n0000000000 65535 f \n"
        f"{page_num} 1\n{page_off:010d} 00000 n \n"
        f"{new_num} 1\n{stream_off:010d} 00000 n \n"
        f"trailer\n<< /Size {new_num + 1} /Root {trailer.Root.unparse(resolved=False).decode()} "
        f"/Info {trailer.Info.unparse(resolved=False).decode()} /ID {trailer.ID.unparse().decode()} /Prev {prev} >>\n"
        f"startxref\n{xref_off}\n%%EOF\n"
    ).encode()
    return bytes(out)


GROUND_TRUTH = TEXT.format(NEW)
