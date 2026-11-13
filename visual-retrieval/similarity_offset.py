"""Wie weit liegt das Maximum einer Similarity Map neben dem gesuchten Wort?

    uv run similarity_offset.py [colqwen2|colmodernvbert|colpali]

ColQwen2 hat ein Sprachmodell mit kausaler Attention über den Bild-Tokens, ColModernVBERT
einen bidirektionalen Encoder, ColPali (PaliGemma) ein Prefix-LM mit voller Attention über dem Bild. Beide zerlegen die Seite in ein Raster von gut 50 px.

Synthetische Seiten (1241×1754 px wie die Testseiten bei 150 dpi), auf denen ein Zielwort an
bekannter Stelle steht, unter vier Bedingungen:

  allein    nur das Zielwort auf weißer Seite
  darüber   sechs Zeilen Gesetzestext über dem Zielwort, darunter nichts
  darunter  Zielwort, darunter sechs Zeilen Gesetzestext
  dicht     ganze Seite Gesetzestext, Zielwörter mitten in Zeilen eingestreut

Für jedes Zielwort wird die Frage „Was steht bei <Wort>?“ eingebettet, die Ähnlichkeit der
Teil-Tokens des Worts mit allen Patches berechnet (Maximum über die Teil-Tokens) und gemessen,
wie viele Patch-Reihen/-Spalten das Maximum vom Kasten des Worts entfernt liegt.
Ausgabe: data/similarity_offset_<modell>.json und eine Tabelle auf stdout.
"""

import json
import random
import re
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
from sentence_transformers import MultiVectorEncoder
from sentence_transformers.multi_vector_encoder.interpretability import get_n_patches, real_query_token_slice

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FONT = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 24)  # etwa 11 pt bei 150 dpi
W, H = 1241, 1754
LINE = 40
MARGIN = 120
WOERTER = ["Durchwahl", "Mustermann", "Zitronenbaum", "Wasserrohrbruch"]


def fuelltext():
    d = json.loads((DATA / "text" / "pypdf.json").read_text())
    t = " ".join(v for k, v in d.items() if not k.startswith("stolpersteine"))
    t = re.sub(r"\s+", " ", t)
    return t.split(" ")


def zeilen(woerter, n, start):
    """n Zeilen Fließtext ab Wortindex start, umbrochen auf die Satzspiegelbreite."""
    out, cur, i = [], [], start
    while len(out) < n:
        w = woerter[i % len(woerter)]
        i += 1
        if FONT.getlength(" ".join(cur + [w])) > W - 2 * MARGIN:
            out.append(cur)
            cur = []
        cur.append(w)
    return out


def zeichne(seite, zeilenliste, y0, ziel=None):
    """Zeichnet Zeilen ab y0. ziel = (zeile, wortposition, wort) ersetzt ein Wort. Gibt die Box zurück."""
    d = ImageDraw.Draw(seite)
    box = None
    for z, words in enumerate(zeilenliste):
        words = list(words)
        if ziel and ziel[0] == z:
            words[ziel[1]] = ziel[2]
        x = MARGIN
        y = y0 + z * LINE
        for k, w in enumerate(words):
            if ziel and ziel[0] == z and ziel[1] == k:
                box = d.textbbox((x, y), w, font=FONT)
            d.text((x, y), w, fill="black", font=FONT)
            x += FONT.getlength(w + " ")
    return box


def seiten():
    """Liefert (bedingung, bild, [(wort, box)])."""
    rnd = random.Random(1)
    fw = fuelltext()
    for n, wort in enumerate(WOERTER):
        y = 500 + 250 * n  # Zielzeile wandert über die Seite
        # allein
        s = Image.new("RGB", (W, H), "white")
        box = zeichne(s, [["Siehe", wort]], y, None)
        box = ImageDraw.Draw(s).textbbox((MARGIN + FONT.getlength("Siehe "), y), wort, font=FONT)
        yield "allein", s, [(wort, box)]
        # darüber: sechs Zeilen Text, dann die Zeile mit dem Wort
        s = Image.new("RGB", (W, H), "white")
        z = zeilen(fw, 6, rnd.randrange(len(fw)))
        zeichne(s, z, y - 6 * LINE)
        box = zeichne(s, [["Siehe", wort]], y, None)
        box = ImageDraw.Draw(s).textbbox((MARGIN + FONT.getlength("Siehe "), y), wort, font=FONT)
        yield "darüber", s, [(wort, box)]
        # darunter: Zeile mit dem Wort, dann sechs Zeilen Text
        s = Image.new("RGB", (W, H), "white")
        zeichne(s, [["Siehe", wort]], y)
        box = ImageDraw.Draw(s).textbbox((MARGIN + FONT.getlength("Siehe "), y), wort, font=FONT)
        zeichne(s, zeilen(fw, 6, rnd.randrange(len(fw))), y + LINE)
        yield "darunter", s, [(wort, box)]
    # dicht: zwei volle Seiten, je vier Zielwörter an verschiedenen Stellen
    for rep in range(2):
        s = Image.new("RGB", (W, H), "white")
        n_lines = (H - 2 * MARGIN) // LINE
        z = zeilen(fw, n_lines, rnd.randrange(len(fw)))
        targets = []
        for k, wort in enumerate(WOERTER):
            zi = 4 + k * 9 + rep * 4
            pos = rnd.randrange(0, max(1, len(z[zi]) - 2))
            targets.append((zi, pos, wort))
        boxes = []
        for zi, pos, wort in targets:
            z[zi][pos] = wort
        for zi, pos, wort in targets:
            boxes.append((wort, zeichne(Image.new("RGB", (W, H)), z, MARGIN, (zi, pos, wort))))
        zeichne(s, z, MARGIN)
        yield "dicht", s, boxes


def abstand(r, lo, hi):
    return 0 if lo <= r <= hi else (r - hi if r > hi else r - lo)


MODELLE = {
    "colqwen2": "vidore/colqwen2-v1.0",
    "colmodernvbert": "ModernVBERT/colmodernvbert",
    "colpali": "vidore/colpali-v1.3-hf",
}


def patch_raster(name, model, img, doc):
    """Bild-Token-Embeddings in Rasterreihenfolge (Zeilen × Spalten × Dim)."""
    feats = model[0].preprocess([img])
    ids = feats["input_ids"][0]
    tok = model.processor.tokenizer
    if name == "colqwen2":
        mask = ids == tok.convert_tokens_to_ids("<|image_pad|>")
        nc, nr = get_n_patches(model, img.size)
        return doc[mask].reshape(nr, nc, -1)
    if name == "colpali":
        # PaliGemma: Seite auf 448×448 gestreckt, 32×32 Patches zeilenweise
        mask = ids == tok.convert_tokens_to_ids("<image>")
        nc, nr = get_n_patches(model, img.size)
        return doc[mask].reshape(nr, nc, -1)
    # Idefics3-Kacheln: Kacheln zeilenweise, je 8×8 Tokens, am Ende ein globales Vorschaubild
    mask = ids == tok.convert_tokens_to_ids("<image>")
    n_tiles = feats["pixel_values"].shape[1] - 1
    text = tok.decode(ids)
    rows = max(int(r) for r in re.findall(r"<row_(\d+)_col_\d+>", text))
    cols = n_tiles // rows
    D = doc[mask][: n_tiles * 64].reshape(rows, cols, 8, 8, -1)
    return D.permute(0, 2, 1, 3, 4).reshape(rows * 8, cols * 8, -1)


def wort_tokens(tok, ids, wort):
    for variante in (" " + wort, wort):
        wid = tok(variante, add_special_tokens=False)["input_ids"]
        for j in range(len(ids)):
            if ids[j : j + len(wid)] == wid:
                return slice(j, j + len(wid))
    raise ValueError(wort)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "colqwen2"
    torch.set_num_threads(4)
    model = MultiVectorEncoder(MODELLE[name], device="cpu", model_kwargs={"dtype": torch.float32})
    tok = model.processor.tokenizer
    out_dir = DATA / "offset"
    out_dir.mkdir(exist_ok=True)
    res = []
    for i, (bed, img, targets) in enumerate(seiten()):
        img.save(out_dir / f"{i:02d}-{bed}.png")
        doc = model.encode_document([img])[0].float()
        R = patch_raster(name, model, img, doc)
        nr, nc = R.shape[:2]
        cw, ch = W / nc, H / nr
        D = R.reshape(nr * nc, -1)
        for wort, (x0, y0, x1, y1) in targets:
            frage = f"Was steht bei {wort}?"
            q = model.encode_query([frage])[0].float()[real_query_token_slice(model, frage)]
            ids = tok(frage, add_special_tokens=False)["input_ids"][: len(q)]
            sim = (q[wort_tokens(tok, ids, wort)] @ D.T).max(dim=0).values.reshape(nr, nc).numpy()
            r, c = divmod(int(sim.argmax()), nc)
            rlo, rhi = int(y0 // ch), int((y1 - 1) // ch)
            clo, chi = int(x0 // cw), int((x1 - 1) // cw)
            top5 = np.argsort(-sim.ravel())[:5]
            im_kasten = sum(rlo <= t // nc <= rhi and clo <= t % nc <= chi for t in top5)
            row = dict(bedingung=bed, wort=wort, dy=abstand(r, rlo, rhi), dx=abstand(c, clo, chi),
                       top5_im_kasten=int(im_kasten), seite=i)
            print(row, flush=True)
            res.append(row)
            np.save(out_dir / f"{i:02d}-{wort}-{name}.npy", sim)
    (DATA / f"similarity_offset_{name}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"\n{'Bedingung':10s} n  Treffer  dy (Reihen)        dx (Spalten)   Top-5 im Kasten")
    for bed in ["allein", "darüber", "darunter", "dicht"]:
        rs = [x for x in res if x["bedingung"] == bed]
        hit = sum(x["dy"] == 0 and x["dx"] == 0 for x in rs)
        print(f"{bed:10s} {len(rs)}  {hit}/{len(rs)}      {[x['dy'] for x in rs]!s:18s} {[x['dx'] for x in rs]!s:14s} "
              f"{sum(x['top5_im_kasten'] for x in rs)}/{5 * len(rs)}")


if __name__ == "__main__":
    main()
