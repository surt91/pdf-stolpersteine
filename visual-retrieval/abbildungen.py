"""Abbildungen für artikel.md.

    uv run abbildungen.py

speicher.png: Speicherbedarf für 100.000 Seiten.
ergebnisse.png: Treffer unter den ersten drei je Art von Seite und Pipeline, beide Durchgänge
    (braucht data/ergebnisse.json und data/visuelle_stolpersteine/ergebnisse.json).
wege.png: Übersicht über die drei Wege vom PDF zur Antwort (Schema, ohne Daten).
maxsim.png: Schema zu MaxSim mit ausgedachten Ähnlichkeiten.
patches.png: Schema, wie aus dem Seitenbild ein Vektor pro Patch wird.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)

# Farben wie im PDF-Artikel (Referenzpalette des dataviz-Skills, helle Variante)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8984"
RULE = "#dcdbd6"
ACCENT = "#2a78d6"
TEXT_COL = "#8a8984"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.labelcolor": INK_2})


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(colors=INK_2, length=0)
    ax.grid(axis="x", color=RULE, linewidth=0.8)
    ax.set_axisbelow(True)


def speicher():
    # (Beschriftung, GB für 100.000 Seiten, Text-Pipeline?)
    rows = [
        ("Visuell, ein Vektor (2048 Dim., fp16)", 0.41, False),
        ("Text, 3 Chunks à 1024 Dim. (fp32)", 1.23, True),
        ("ColPali, binarisiert", 1.65, False),
        ("ColPali, Token-Pooling ×3 (fp16)", 8.8, False),
        ("ColQwen2 (fp16, ~750 Vektoren)", 19.2, False),
        ("ColPali (fp16)", 26.4, False),
        ("ColPali (fp32)", 52.7, False),
    ]
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    style(ax)
    y = range(len(rows))[::-1]
    for yi, (label, gb, text) in zip(y, rows):
        ax.barh(yi, gb, height=0.62, color=TEXT_COL if text else ACCENT)
        val = f"{gb:.1f} GB".replace(".", ",")
        ax.text(gb + 0.6, yi, val, va="center", ha="left", color=INK, fontsize=9)
    ax.set_yticks(list(y), [r[0] for r in rows])
    ax.set_xlabel("Speicher für 100.000 Seiten (GB)")
    ax.set_xlim(0, 60)
    fig.tight_layout()
    fig.savefig(IMG / "speicher.png", facecolor=SURFACE)


def ergebnisse():
    """Beide Durchgänge in einer Abbildung: Zeilen sind die Arten von Seiten, Spalten die Pipelines.

    Braucht data/ergebnisse.json und data/visuelle_stolpersteine/ergebnisse.json. Gezählt wird die richtige
    Seite unter den ersten drei, bei den Rechnungsnummern auf Platz 1 (die vier Rechnungen sind
    Geschwister, unter den ersten drei landen sie fast immer).
    """
    p1 = HERE / "data" / "ergebnisse.json"
    p2 = HERE / "data" / "visuelle_stolpersteine" / "ergebnisse.json"
    if not (p1.exists() and p2.exists()):
        return
    res = json.loads(p1.read_text())
    geg = json.loads(p2.read_text())
    pipelines = [
        ("docling hybrid", "Docling\nBM25 + BGE-M3"),
        ("tesseract hybrid", "Tesseract\nBM25 + BGE-M3"),
        ("colqwen2", "ColQwen2"),
        ("qwen3vl", "Qwen3-VL-\nEmbedding"),
    ]
    n_text = 2

    def erster(g):
        return lambda key: [q["rank"] <= 3 for q in res[key] if q["gruppe"] == g]

    def zweiter(g, v, k=3):
        return lambda key: [q["rang"][key] <= k for q in geg if q["gruppe"] == g and q["variante"] == v]

    bloecke = [
        ("Stolpersteine für die Textextraktion", [
            ("Zeichen", erster("zeichen")),
            ("Scan, Bild, Formular", erster("bild")),
            ("Layout", erster("layout")),
            ("Tabellen", erster("tabelle")),
            ("Seitengrenze", erster("seitengrenze")),
            ("Nummern", erster("ids")),
            ("Kontrolle (Gesetze)", erster("kontrolle")),
        ]),
        ("Stolpersteine für visuelle Modelle", [
            ("Fußnote in 8 pt", zweiter("fussnote", "8 pt")),
            ("Fußnote in 6 pt", zweiter("fussnote", "6 pt")),
            ("Fußnote in 4,5 pt", zweiter("fussnote", "4,5 pt")),
            ("1 Seite pro Blatt", zweiter("nup", "1 pro Blatt")),
            ("2 Seiten pro Blatt", zweiter("nup", "2 pro Blatt")),
            ("4 Seiten pro Blatt", zweiter("nup", "4 pro Blatt")),
            ("Ähnliche Rechnungen: Nummer", zweiter("nummer", None, 1)),
            ("Ähnliche Rechnungen: Inhalt", zweiter("vorlage", None)),
            ("Hellgrauer Text", zweiter("hellgrau", None)),
            ("Fast weißer Text", zweiter("fast_weiss", None)),
            ("Um 90° gedreht", zweiter("gedreht", None)),
            ("Kontrolle (Gesetze)", zweiter("kontrolle", None)),
        ]),
    ]
    fig, ax = plt.subplots(figsize=(8, 8.6), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0, colors=INK_2)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", "#2a78d6", "#0d3a73"])
    y = 0.0
    ticks, labels = [], []
    for titel, zeilen in bloecke:
        ax.text(0, y + 0.55, titel, ha="left", va="center", fontsize=9.5, color=INK, fontweight="bold")
        y += 1
        oben = y
        for label, treffer in zeilen:
            for j, (key, _) in enumerate(pipelines):
                t = treffer(key)
                frac = sum(t) / len(t)
                ax.add_patch(plt.Rectangle((j + 0.04, y + 0.06), 0.92, 0.88, color=cmap(frac), linewidth=0))
                ax.text(j + 0.5, y + 0.5, f"{sum(t)}/{len(t)}", ha="center", va="center", fontsize=9,
                        color="white" if frac > 0.55 else INK)
            ticks.append(y + 0.5)
            labels.append(label)
            y += 1
        ax.plot([n_text, n_text], [oben, y], color=INK_2, linewidth=1.2)
        y += 0.5
    ax.set_xlim(0, len(pipelines))
    ax.set_ylim(y - 0.5, 0)
    ax.set_xticks([j + 0.5 for j in range(len(pipelines))], [p[1] for p in pipelines], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks(ticks, labels, fontsize=8.5)
    ax.set_title("Richtige Seite unter den ersten drei Treffern", fontsize=10, color=INK_2, pad=14)
    fig.tight_layout()
    fig.savefig(IMG / "ergebnisse.png", facecolor=SURFACE)


if __name__ == "__main__":
    speicher()
    ergebnisse()


def offset():
    """Similarity Maps von ColQwen2 für „Durchwahl“ mit Text darüber, darunter und auf dichter Seite."""
    import numpy as np
    from PIL import Image

    d = HERE / "data" / "offset"
    if not d.exists():
        return
    res = json.loads((HERE / "data" / "similarity_offset_colqwen2.json").read_text())
    import similarity_offset as so

    boxes = {}
    for i, (bed, _, targets) in enumerate(so.seiten()):
        for wort, box in targets:
            boxes[(i, wort)] = box
    faelle = [(1, "Text darüber"), (2, "Text darunter"), (12, "dicht beschriebene Seite")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.0), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    for ax, (i, titel) in zip(axes, faelle):
        img = Image.open(next(d.glob(f"{i:02d}-*.png")))
        sim = np.load(d / f"{i:02d}-Durchwahl-colqwen2.npy")
        w, h = img.size
        x0, y0, x1, y1 = boxes[(i, "Durchwahl")]
        ax.imshow(img, extent=(0, w, h, 0))
        ax.imshow(sim, extent=(0, w, h, 0), cmap="magma", alpha=0.55, interpolation="nearest")
        ax.add_patch(plt.Rectangle((x0 - 6, y0 - 6), x1 - x0 + 12, y1 - y0 + 12, fill=False,
                                   edgecolor=ACCENT, linewidth=1.6))
        r, c = divmod(int(sim.argmax()), sim.shape[1])
        ch, cw = h / sim.shape[0], w / sim.shape[1]
        ax.add_patch(plt.Rectangle((c * cw, r * ch), cw, ch, fill=False, edgecolor="white", linewidth=1.6,
                                   linestyle="--"))
        cy = (y0 + y1) / 2
        ax.set_xlim(0, w)
        ax.set_ylim(cy + 330, cy - 330)
        ax.set_title(titel, fontsize=9, color=INK)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(IMG / "similarity_offset.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.05)


if __name__ == "__main__":
    offset()


def vorschau():
    """Vorschau-Ausschnitt um das Maximum der Similarity Map (ColQwen2) auf echten Testseiten.

    Oben: Fenster von ±3 Patch-Reihen und ±1 Spalte um das Maximum.
    Unten: Band über die ganze Seitenbreite, ±3 Patch-Reihen um das Maximum.
    Gestrichelt: tatsächliche Position des Worts (Tesseract).
    """
    import numpy as np
    from PIL import Image

    d = HERE / "data" / "offset"
    faelle = [(3, "Durchwahl"), (6, "Garantie"), (24, "Mustermann")]
    if not all((d / f"echt-{s:03d}-{w}-colqwen2.npy").exists() for s, w in faelle):
        return
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    for row, (variante, rx) in enumerate([("Fenster 7 × 3 Patches", 1), ("Band über die Seitenbreite", None)]):
        for ax, (seite, wort) in zip(axes[row], faelle):
            img = Image.open(HERE / "data" / "seiten" / f"stolpersteine-{seite:03d}.png").convert("RGB")
            sim = np.load(d / f"echt-{seite:03d}-{wort}-colqwen2.npy")
            bx, by, bw, bh = json.loads((d / f"echt-{seite:03d}-{wort}-box.json").read_text())
            w, h = img.size
            nr, nc = sim.shape
            ch, cw = h / nr, w / nc
            r, c = divmod(int(sim.argmax()), nc)
            y0, y1 = max(0, (r - 3) * ch), min(h, (r + 4) * ch)
            x0, x1 = (0, w) if rx is None else (max(0, (c - rx) * cw), min(w, (c + rx + 1) * cw))
            ax.imshow(img, extent=(0, w, h, 0))
            # alles außerhalb des Ausschnitts abdunkeln
            veil = np.ones((h, w, 4), dtype=float)
            veil[..., :3] = 0.35
            veil[..., 3] = 0.45
            veil[int(y0):int(y1), int(x0):int(x1), 3] = 0
            ax.imshow(veil, extent=(0, w, h, 0))
            ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=ACCENT, linewidth=2))
            ax.add_patch(plt.Rectangle((bx - 6, by - 6), bw + 12, bh + 12, fill=False, edgecolor=INK,
                                       linewidth=1.2, linestyle="--"))
            ax.set_xlim(0, w)
            ax.set_ylim(h * 0.42, 0)
            ax.set_title(f"{variante}: „{wort}“", fontsize=9, color=INK)
            ax.axis("off")
    fig.tight_layout()
    fig.savefig(IMG / "similarity_vorschau.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.05)


if __name__ == "__main__":
    vorschau()


def vorschau_dicht():
    """Fenster 3 × 3 Patches um das Maximum (ColQwen2) auf echten, dicht beschriebenen Gesetzesseiten."""
    import numpy as np
    from PIL import Image

    path = HERE / "data" / "similarity_dicht.json"
    if not path.exists():
        return
    res = {(x["seite"], x["wort"]): x for x in json.loads(path.read_text())}
    faelle = [("BDSG-027", "Zivilprozessordnung"), ("BDSG-018", "Anhaltspunkte"), ("BDSG-045", "ausschließlich")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.9), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    for ax, key in zip(axes, faelle):
        x = res[key]
        img = Image.open(HERE / "data" / "seiten" / f"{key[0]}.png").convert("RGB")
        sim = np.load(HERE / "data" / "offset" / f"dicht-{key[0]}-{key[1]}.npy")
        w, h = img.size
        nr, nc = sim.shape
        ch, cw = h / nr, w / nc
        r, c = x["max"]
        y0, y1 = max(0, (r - 1) * ch), min(h, (r + 2) * ch)
        x0, x1 = max(0, (c - 1) * cw), min(w, (c + 2) * cw)
        ax.imshow(img, extent=(0, w, h, 0))
        veil = np.zeros((h, w, 4))
        veil[..., :3] = 0.35
        veil[..., 3] = 0.45
        veil[int(y0):int(y1), int(x0):int(x1), 3] = 0
        ax.imshow(veil, extent=(0, w, h, 0))
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=ACCENT, linewidth=2))
        bx, by, bw, bh = x["box"]
        ax.add_patch(plt.Rectangle((bx - 6, by - 6), bw + 12, bh + 12, fill=False, edgecolor="#d1242f",
                                   linewidth=1.6))
        ax.set_title(f"„{key[1]}“ ({key[0]})", fontsize=9, color=INK)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(IMG / "similarity_vorschau_dicht.png", facecolor=SURFACE, bbox_inches="tight", pad_inches=0.05)


if __name__ == "__main__":
    vorschau_dicht()


def wege():
    """Übersicht: drei Wege vom PDF zur Antwort. Hervorgehoben ist der Schritt, in dem aus der Seite Text wird."""
    from matplotlib.patches import FancyBboxPatch

    tint = "#cde2fb"
    fig, ax = plt.subplots(figsize=(10, 4.45), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(-4, 44.6)

    # Spalten: Mitte und Breite. Gleiche Schritte stehen in allen Wegen untereinander.
    col = {"pdf": (4.5, 8), "bild": (16.5, 11), "lesen": (31.5, 14), "text": (47, 12),
           "emb": (62, 13), "index": (76.5, 11), "llm": (92.5, 14)}
    hoehe = 7.4

    def kasten(key, y, label, lesen=False):
        x, w = col[key]
        ax.add_patch(FancyBboxPatch((x - w / 2, y - hoehe / 2), w, hoehe, boxstyle="round,pad=0,rounding_size=1.0",
                                    facecolor=tint if lesen else "white", edgecolor=ACCENT if lesen else RULE,
                                    linewidth=1.3 if lesen else 1.0))
        ax.text(x, y, label, ha="center", va="center", fontsize=8.5, color=INK, linespacing=1.25)

    def pfeil(a, b, y):
        xa = col[a][0] + col[a][1] / 2
        xb = col[b][0] - col[b][1] / 2
        ax.annotate("", xy=(xb - 0.25, y), xytext=(xa + 0.25, y),
                    arrowprops=dict(arrowstyle="-|>", color=INK_2, linewidth=1.0, mutation_scale=9,
                                    shrinkA=0, shrinkB=0))

    text_rest = [("text", "Text,\nChunks", False), ("emb", "Text-\nEmbedding", False),
                 ("index", "Index\n(Chunks)", False), ("llm", "LLM bekommt\nText-Chunks", False)]
    wege = [
        ("Text-Pipeline", 32.5,
         [("pdf", "PDF", False), ("lesen", "Parser liest\nden Textlayer", True)] + text_rest),
        ("Modell als Parser", 19.0,
         [("pdf", "PDF", False), ("bild", "Seitenbild", False), ("lesen", "OCR oder VLM\nliest das Bild", True)]
         + text_rest),
        ("Visuelles Retrieval", 5.5,
         [("pdf", "PDF", False), ("bild", "Seitenbild", False), ("emb", "visuelles\nEmbedding", False),
          ("index", "Index\n(Seiten)", False), ("llm", "multimodales LLM\nliest die Treffer", True)]),
    ]
    for titel, y, schritte in wege:
        ax.text(0.5, y + hoehe / 2 + 1.9, titel, ha="left", va="center", fontsize=9.5, color=INK, fontweight="bold")
        for key, label, lesen in schritte:
            kasten(key, y, label, lesen)
        for (a, _, _), (b, _, _) in zip(schritte, schritte[1:]):
            pfeil(a, b, y)

    trenn = 84.0
    ax.plot([trenn, trenn], [0.5, 43.8], color=RULE, linewidth=1.0)
    ax.text(0.5, 42.9, "Indexierung: einmal für jede Seite", ha="left", va="center", fontsize=8.5, color=INK_2)
    ax.text(trenn + 1.5, 42.9, "Anfrage: nur die Treffer", ha="left", va="center", fontsize=8.5, color=INK_2)

    ax.add_patch(FancyBboxPatch((0.5, -3.4), 3.2, 2.2, boxstyle="round,pad=0,rounding_size=0.5",
                                facecolor=tint, edgecolor=ACCENT, linewidth=1.3))
    ax.text(5.0, -2.3, "Hier wird aus der Seite Text.", ha="left", va="center", fontsize=8.5, color=INK_2)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    fig.savefig(IMG / "wege.png", facecolor=SURFACE)


def maxsim():
    """Schema zu MaxSim: Tokens der Frage gegen Patches der Seite. Die Werte sind ausgedacht."""
    import numpy as np

    tokens = ["Kündigungs", "frist", "Miet", "vertrag"]
    patches = ["", "Miet", "vertrag", "", "Die Kün", "digungs", "frist be", "trägt drei", "Monate"]
    sim = np.array([
        [0.12, 0.18, 0.21, 0.15, 0.71, 0.88, 0.34, 0.17, 0.11],
        [0.10, 0.14, 0.19, 0.13, 0.42, 0.67, 0.91, 0.22, 0.12],
        [0.16, 0.83, 0.58, 0.14, 0.21, 0.25, 0.19, 0.15, 0.13],
        [0.14, 0.61, 0.86, 0.17, 0.18, 0.23, 0.24, 0.16, 0.12],
    ])
    nr, nc = sim.shape
    komma = lambda v: f"{v:.2f}".replace(".", ",")

    fig, ax = plt.subplots(figsize=(8, 3.3), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    ax.set_xlim(-2.2, nc + 1.9)
    ax.set_ylim(nr + 1.25, -2.3)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", "#2a78d6", "#0d3a73"])

    # Patches als kleine Ausschnitte der Seite
    ax.text(nc / 2, -2.0, "Patches der Seite", ha="center", va="center", fontsize=9, color=INK_2)
    for j, text in enumerate(patches):
        ax.add_patch(plt.Rectangle((j + 0.06, -1.42), 0.88, 0.88, facecolor="white", edgecolor=RULE, linewidth=1.0))
        ax.text(j + 0.5, -0.98, text, ha="center", va="center", fontsize=6.5, color=INK, family="DejaVu Serif")

    # Zeilenbeschriftung senkrecht neben den Tokens, damit sie nicht wie ein Titel der Patch-Reihe wirkt
    ax.text(-1.9, nr / 2, "Tokens der Frage", ha="center", va="center", rotation=90, fontsize=9, color=INK_2)
    for i, token in enumerate(tokens):
        ax.text(-0.2, i + 0.5, token, ha="right", va="center", fontsize=9.5, color=INK)
        best = int(sim[i].argmax())
        for j in range(nc):
            v = sim[i, j]
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, color=cmap(v), linewidth=0))
            ax.text(j + 0.5, i + 0.5, komma(v), ha="center", va="center", fontsize=8.5,
                    color="white" if v > 0.38 else INK_2, fontweight="bold" if j == best else "normal")
        ax.add_patch(plt.Rectangle((best + 0.04, i + 0.06), 0.92, 0.88, fill=False, edgecolor=INK, linewidth=1.8))
        ax.text(nc + 1.45, i + 0.5, komma(sim[i, best]), ha="right", va="center", fontsize=9.5, color=INK)

    ax.text(nc + 1.45, -0.25, "Maximum", ha="right", va="center", fontsize=9, color=INK_2)
    ax.plot([nc + 0.55, nc + 1.55], [nr + 0.12, nr + 0.12], color=INK_2, linewidth=1.0)
    ax.text(nc + 1.45, nr + 0.62, komma(sim.max(axis=1).sum()), ha="right", va="center", fontsize=9.5, color=INK,
            fontweight="bold")
    ax.text(nc + 0.45, nr + 0.62, "Summe der Maxima = Score der Seite", ha="right", va="center", fontsize=9,
            color=INK_2)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(IMG / "maxsim.png", facecolor=SURFACE)


def patches():
    """Schema: Seitenbild -> Raster aus Patches -> Modell mit der ganzen Seite als Kontext -> ein Vektor pro Patch.

    Das Raster ist zur Anschauung 8x11, bei ColPali sind es 32x32 auf der quadratisch skalierten Seite.
    Die Vektoren sind ausgedacht. Braucht data/seiten/stolpersteine-002.png.
    """
    import numpy as np
    from PIL import Image

    src = HERE / "data" / "seiten" / "stolpersteine-002.png"
    if not src.exists():
        return
    seite = np.asarray(Image.open(src).convert("RGB"))
    h, w = seite.shape[:2]
    nx, ny = 8, 11
    pw, ph = w / nx, h / ny
    # gezeigte Patches (Spalte, Zeile); der hervorgehobene steht in der Mitte der Liste
    zeigen = [(1, 1), (2, 1), (4, 2), (2, 3), (5, 3), (4, 3)]
    hervor = 3

    fig, ax = plt.subplots(figsize=(8, 3.9), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    ax.set_xlim(0, 10.2)
    ax.set_ylim(5.3, -0.55)
    ax.set_aspect("equal")

    # 1. Seite mit Raster
    sh = 4.4
    sw = sh * w / h
    x0, y0 = 0.15, 0.2
    ax.imshow(seite, extent=(x0, x0 + sw, y0 + sh, y0), zorder=1)
    for i in range(nx + 1):
        ax.plot([x0 + i * sw / nx] * 2, [y0, y0 + sh], color=MUTED, linewidth=0.5, zorder=2)
    for j in range(ny + 1):
        ax.plot([x0, x0 + sw], [y0 + j * sh / ny] * 2, color=MUTED, linewidth=0.5, zorder=2)
    cx, cy = zeigen[hervor]
    ax.add_patch(plt.Rectangle((x0 + cx * sw / nx, y0 + cy * sh / ny), sw / nx, sh / ny, fill=False,
                               edgecolor=ACCENT, linewidth=2.0, zorder=3))
    ax.text(x0 + sw / 2, -0.25, "Seitenbild im Raster", ha="center", va="center", fontsize=9, color=INK_2)

    # 2. Patches als Folge von Bild-Tokens
    px = 4.05
    groesse = 0.52
    hoehe = groesse * (sh / ny) / (sw / nx)  # gleiches Seitenverhältnis wie im Raster
    zeilen = [0.4 + k * 0.63 for k in range(len(zeigen))]
    punkte_y = zeilen[-1] + 0.62
    for k, (c, r) in enumerate(zeigen):
        ausschnitt = seite[int(r * ph):int((r + 1) * ph), int(c * pw):int((c + 1) * pw)]
        ax.imshow(ausschnitt, extent=(px, px + groesse, zeilen[k] + hoehe, zeilen[k]), zorder=1)
        ax.add_patch(plt.Rectangle((px, zeilen[k]), groesse, hoehe, fill=False, zorder=3,
                                   edgecolor=ACCENT if k == hervor else RULE, linewidth=2.0 if k == hervor else 1.0))
    ax.text(px + groesse / 2, punkte_y + 0.12, "⋮", ha="center", va="center", fontsize=12, color=INK_2)
    ax.text(px + groesse / 2, -0.25, "Patches", ha="center", va="center", fontsize=9, color=INK_2)
    ax.annotate("", xy=(px - 0.12, y0 + sh / 2), xytext=(x0 + sw + 0.12, y0 + sh / 2),
                arrowprops=dict(arrowstyle="->", color=INK_2, linewidth=1.0))

    # 3. Modell: jeder Ausgang hängt an allen Patches
    mx0, mx1 = px + groesse + 0.35, px + groesse + 3.2
    ax.add_patch(matplotlib.patches.FancyBboxPatch((mx0, 0.25), mx1 - mx0, 3.85, boxstyle="round,pad=0.02,rounding_size=0.12",
                                                   facecolor="white", edgecolor=RULE, linewidth=1.0, zorder=0))
    mitte = [z + hoehe / 2 for z in zeilen]
    li, re = mx0 + 0.12, mx1 - 0.12
    # Jeder Ausgang gehört zu seinem eigenen Patch (waagerechte Linie), die übrigen Patches sind Kontext.
    for a, ya in enumerate(mitte):
        for b, yb in enumerate(mitte):
            if b != hervor and a != b:
                ax.plot([li, re], [ya, yb], color=RULE, linewidth=0.5, zorder=1)
    for a, ya in enumerate(mitte):
        if a != hervor:
            ax.plot([li, re], [ya, ya], color=MUTED, linewidth=1.0, zorder=2)
            ax.plot([li, re], [ya, mitte[hervor]], color=ACCENT, linewidth=0.8, alpha=0.55, linestyle=(0, (3, 2)), zorder=3)
    ax.plot([li, re], [mitte[hervor]] * 2, color=ACCENT, linewidth=1.4, zorder=4)
    ax.text((mx0 + mx1) / 2, -0.25, "Bild-Encoder + Sprachmodell", ha="center", va="center", fontsize=9, color=INK_2)
    ly = 4.82
    ax.plot([mx0 + 0.1, mx0 + 0.42], [ly, ly], color=ACCENT, linewidth=1.4)
    ax.text(mx0 + 0.52, ly, "Ausgangspunkt: der Patch", ha="left", va="center", fontsize=7.5, color=INK_2)
    ax.plot([mx0 + 0.1, mx0 + 0.42], [ly + 0.29, ly + 0.29], color=ACCENT, linewidth=0.8, alpha=0.55, linestyle=(0, (3, 2)))
    ax.text(mx0 + 0.52, ly + 0.29, "übrige Seite als Kontext", ha="left", va="center", fontsize=7.5, color=INK_2)

    # 4. Ein Vektor pro Patch
    vx = mx1 + 0.35
    n, zelle = 9, 0.2
    rng = np.random.default_rng(3)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", "#2a78d6", "#0d3a73"])
    for k, ym in enumerate(mitte):
        for d in range(n):
            ax.add_patch(plt.Rectangle((vx + d * zelle, ym - zelle / 2), zelle * 0.9, zelle, color=cmap(rng.random()), linewidth=0))
        ax.text(vx + n * zelle + 0.06, ym, "…", ha="left", va="center", fontsize=9, color=INK_2)
        if k == hervor:
            ax.add_patch(plt.Rectangle((vx - 0.05, ym - zelle / 2 - 0.05), n * zelle + 0.08, zelle + 0.1, fill=False,
                                       edgecolor=ACCENT, linewidth=2.0))
    ax.text(vx + n * zelle / 2, punkte_y + 0.12, "⋮", ha="center", va="center", fontsize=12, color=INK_2)
    ax.text(vx + n * zelle / 2, -0.25, "ein Vektor pro Patch", ha="center", va="center", fontsize=9, color=INK_2)
    ax.text(vx + n * zelle / 2, 4.95, "ColPali: 1024 Patches,\nje 128 Dimensionen", ha="center", va="center", fontsize=8,
            color=INK_2, linespacing=1.3)
    ax.text(x0 + sw / 2, 4.95, "hier 8×11 zur Anschauung,\nbei ColPali 32×32", ha="center", va="center", fontsize=8,
            color=INK_2, linespacing=1.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(IMG / "patches.png", facecolor=SURFACE)


if __name__ == "__main__":
    wege()
    maxsim()
    patches()
