"""Similarity Maps auf dicht beschriebenen echten Seiten (Gesetzestexte aus den Ablenkern).

    uv run similarity_dicht.py

Für eine Stichprobe von Gesetzesseiten werden per Tesseract Wörter ausgewählt, die genau einmal
auf der Seite stehen. Für jedes Wort wird „Was steht zu <Wort>?“ eingebettet und mit den
gespeicherten ColQwen2-Seiten-Embeddings (data/emb/colqwen2.pt) verglichen. Gemessen wird, wie
weit das Maximum der Similarity Map vom Wort entfernt liegt und wie oft verschieden große
Ausschnitte um das Maximum das Wort enthalten.
Ausgabe: data/similarity_dicht.json, Maps unter data/offset/dicht-*.npy.
"""

import json
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pytesseract
import torch
from PIL import Image
from sentence_transformers import MultiVectorEncoder
from sentence_transformers.multi_vector_encoder.interpretability import get_n_patches, real_query_token_slice

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SEITEN = DATA / "seiten"
OUT = DATA / "offset"
N_SEITEN = 12
PRO_SEITE = 3


def kandidaten(img):
    ocr = pytesseract.image_to_data(img, lang="deu", output_type=pytesseract.Output.DICT)
    words = [(re.sub(r"[^\wäöüÄÖÜß]", "", w), i) for i, w in enumerate(ocr["text"])]
    zaehl = Counter(w.lower() for w, _ in words if w)
    out = []
    for w, i in words:
        if len(w) >= 9 and w.isalpha() and zaehl[w.lower()] == 1 and float(ocr["conf"][i]) > 80:
            out.append((w, (ocr["left"][i], ocr["top"][i], ocr["width"][i], ocr["height"][i])))
    return out


def wort_slice(tok, ids, wort):
    for variante in (" " + wort, wort):
        wid = tok(variante, add_special_tokens=False)["input_ids"]
        for j in range(len(ids)):
            if ids[j : j + len(wid)] == wid:
                return slice(j, j + len(wid))
    raise ValueError(wort)


def main():
    torch.set_num_threads(4)
    rnd = random.Random(7)
    emb = torch.load(DATA / "emb" / "colqwen2.pt", weights_only=False)
    gesetze = [i.stem for i in sorted((DATA / "seiten").glob("*.png")) if not i.stem.startswith("stolpersteine")]
    auswahl = sorted(rnd.sample(gesetze, N_SEITEN))
    model = MultiVectorEncoder("vidore/colqwen2-v1.0", device="cpu", model_kwargs={"dtype": torch.float32})
    tok = model.processor.tokenizer
    pad = tok.convert_tokens_to_ids("<|image_pad|>")
    OUT.mkdir(exist_ok=True)
    res = []
    for sid in auswahl:
        img = Image.open(SEITEN / f"{sid}.png").convert("RGB")
        W, H = img.size
        doc = emb["pages"][sid].float()
        mask = model[0].preprocess([img])["input_ids"][0] == pad
        assert len(mask) == doc.shape[0]
        nc, nr = get_n_patches(model, img.size)
        D = doc[mask]
        assert D.shape[0] == nr * nc
        cands = kandidaten(img)
        for wort, (bx, by, bw, bh) in rnd.sample(cands, min(PRO_SEITE, len(cands))):
            frage = f"Was steht zu {wort}?"
            q = model.encode_query([frage])[0].float()[real_query_token_slice(model, frage)]
            ids = tok(frage, add_special_tokens=False)["input_ids"][: len(q)]
            sim = (q[wort_slice(tok, ids, wort)] @ D.T).max(dim=0).values.reshape(nr, nc).numpy()
            np.save(OUT / f"dicht-{sid}-{wort}.npy", sim)
            r, c = divmod(int(sim.argmax()), nc)
            ch, cw = H / nr, W / nc
            rlo, rhi = int(by // ch), int((by + bh - 1) // ch)
            clo, chi = int(bx // cw), int((bx + bw - 1) // cw)
            dy = 0 if rlo <= r <= rhi else (r - rhi if r > rhi else r - rlo)
            dx = 0 if clo <= c <= chi else (c - chi if c > chi else c - clo)
            row = dict(seite=sid, wort=wort, box=[bx, by, bw, bh], max=[r, c], dy=dy, dx=dx)
            print(row, flush=True)
            res.append(row)
    (DATA / "similarity_dicht.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))

    n = len(res)
    print(f"\n{n} Wörter auf {N_SEITEN} Seiten")
    print("Ausschnitt um das Maximum            enthält Wort   Anteil der Seitenfläche")
    for ry, rx in [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (1, None), (2, None), (3, None)]:
        hit = sum(abs(x["dy"]) <= ry and (rx is None or abs(x["dx"]) <= rx) for x in res)
        flaeche = (2 * ry + 1) * (nc if rx is None else 2 * rx + 1) / (nr * nc)
        name = f"±{ry} Reihen, " + ("volle Breite" if rx is None else f"±{rx} Spalten")
        print(f"{name:36s} {hit:2d}/{n}          {flaeche:5.1%}")


if __name__ == "__main__":
    main()
