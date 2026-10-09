"""Baut stolpersteine.pdf aus den Modulen in pitfalls/.

    uv run build.py

Erzeugt im Verzeichnis out/:
- stolpersteine.pdf               das Testdokument
- stolpersteine--<id>.pdf         Varianten (kaputt, verschlüsselt, …)
- stolpersteine.ground_truth.md   was ein perfekter Extraktor liefern sollte
- stolpersteine.seiten.json       welcher Stolperstein auf welchen Seiten steht

Ablauf (siehe README.md):
1. draw():            jeder Stolperstein zeichnet seine Seite(n) mit reportlab
2. on_every_page():   Hooks, die auf jeder Seite zeichnen (Kopf-/Fußzeile)
3. postprocess():     Nachbearbeitung mit pikepdf (Fonts tauschen, Metadaten, …)
4. finalize():        Eingriffe auf Byte-Ebene (inkrementelle Updates, …)
5. variant():         erzeugt aus dem fertigen PDF eine separate Datei
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

import pikepdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

from pitfalls import load_pitfalls
from pitfalls._lib import LEFT, page_label

OUT = Path(__file__).resolve().parent / "out"
NAME = "stolpersteine"


@dataclass
class TocEntry:
    number: int
    title: str
    first_page: int


@dataclass
class Context:
    """Wird an draw() und on_every_page() übergeben."""

    c: Canvas
    pitfalls: list[ModuleType]
    toc: list[TocEntry]
    page: int = 1  # physische Seite, 1-basiert
    number: int = 0  # laufende Nummer des aktuellen Stolpersteins
    current: ModuleType | None = None
    pages: dict[str, list[int]] = field(default_factory=dict)
    width: float = A4[0]
    height: float = A4[1]

    def begin_page(self) -> None:
        assert self.current is not None
        self.pages.setdefault(self.current.ID, []).append(self.page)
        for m in self.pitfalls:
            if hasattr(m, "on_every_page"):
                m.on_every_page(self.c, self)

    def new_page(self) -> None:
        """Für Stolpersteine, die mehr als eine Seite brauchen."""
        self.c.showPage()
        self.page += 1
        self.begin_page()

    def title(self) -> float:
        """Zeichnet die Seitenüberschrift und gibt die y-Position darunter zurück."""
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(LEFT, self.height - 100, self.heading())
        return self.height - 130

    def heading(self) -> str:
        assert self.current is not None
        return f"{self.number}. {self.current.TITLE}"

    @property
    def label(self) -> str:
        return page_label(self.page)


def render(pitfalls: list[ModuleType], toc: list[TocEntry]) -> tuple[bytes, Context, list[TocEntry]]:
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4, pageCompression=0, invariant=1)
    ctx = Context(c=c, pitfalls=pitfalls, toc=toc)
    new_toc = []
    first = True
    for m in pitfalls:
        if not hasattr(m, "draw"):
            continue
        if not first:
            c.showPage()
            ctx.page += 1
        first = False
        ctx.number += 1
        ctx.current = m
        new_toc.append(TocEntry(ctx.number, m.TITLE, ctx.page))
        ctx.begin_page()
        m.draw(c, ctx)
    c.save()
    return buf.getvalue(), ctx, new_toc


def ground_truth(pitfalls: list[ModuleType], ctx: Context, toc: list[TocEntry]) -> str:
    out = [
        "# Ground Truth\n",
        "Inhalt, den ein perfekter Extraktor liefern sollte: das, was ein Mensch beim Lesen\n"
        "als Inhalt wahrnimmt. Ohne Kopf-/Fußzeilen, Wasserzeichen, unsichtbaren oder\n"
        "geschwärzten Text.\n",
    ]
    for m, entry in zip([m for m in pitfalls if hasattr(m, "draw")], toc):
        gt = m.GROUND_TRUTH
        if callable(gt):
            gt = gt(ctx)
        pages = ", ".join(str(p) for p in ctx.pages[m.ID])
        out.append(f"<!-- {m.ID}: Seite(n) {pages} -->\n## {entry.number}. {m.TITLE}\n\n{gt.strip()}\n")
    return "\n".join(out)


def main() -> None:
    pitfalls = load_pitfalls()
    # Zwei Durchläufe: der erste ermittelt die Seitenzahlen für das Inhaltsverzeichnis.
    _, _, toc = render(pitfalls, [])
    data, ctx, toc = render(pitfalls, toc)

    pdf = pikepdf.open(io.BytesIO(data))
    for m in pitfalls:
        if hasattr(m, "postprocess"):
            pages = [pdf.pages[p - 1] for p in ctx.pages.get(m.ID, [])]
            m.postprocess(pdf, pages)
    buf = io.BytesIO()
    # Klassische xref-Tabelle ohne Objekt-Streams, damit finalize() anhängen kann.
    pdf.save(buf, object_stream_mode=pikepdf.ObjectStreamMode.disable, compress_streams=False, deterministic_id=True)
    data = buf.getvalue()

    for m in pitfalls:
        if hasattr(m, "finalize"):
            data = m.finalize(data, ctx.pages.get(m.ID, []))

    OUT.mkdir(exist_ok=True)
    (OUT / f"{NAME}.pdf").write_bytes(data)
    for m in pitfalls:
        if hasattr(m, "variant"):
            (OUT / f"{NAME}--{m.ID}.pdf").write_bytes(m.variant(data))

    (OUT / f"{NAME}.ground_truth.md").write_text(ground_truth(pitfalls, ctx, toc))
    (OUT / f"{NAME}.seiten.json").write_text(json.dumps(ctx.pages, indent=2, ensure_ascii=False))
    print(f"{ctx.page} Seiten, {len(pitfalls)} Stolpersteine -> {OUT}")


if __name__ == "__main__":
    main()
