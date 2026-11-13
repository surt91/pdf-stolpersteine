"""Liegt es an der Auflösung? Bettet die Seiten mit kleiner Schrift noch einmal mit mehr
Bild-Tokens ein und wertet die zugehörigen Fragen neu aus.

    uv run aufloesung.py colqwen2 4     # 4 x 768 Bild-Tokens, also doppelte dpi
    uv run aufloesung.py qwen3vl 4      # ebenfalls 4 x 768 = 3072 Bild-Tokens, das 2,4-Fache
                                        # seiner Voreinstellung von rund 1280

Neu eingebettet werden nur die Fußnoten-Seiten und die Blätter mit zwei und vier Seiten. Alle
anderen Seiten bleiben wie in data/emb/ bei der Voreinstellung des Modells. Bei den Modellen mit vielen
Vektoren ist das ein Vorteil für die neu eingebetteten Seiten, weil MaxSim über mehr Patches
ein höheres Maximum findet. Die Zahlen sind deshalb eine Diagnose und kein fairer Vergleich.
Ergebnis: data/aufloesung/<name>_x<faktor>.pt (fortsetzbar) und eine Tabelle auf der Konsole.
"""

import json
import sys
import time

import numpy as np
import torch
from PIL import Image

from embed_visual import MODELS
from evaluate import DATA, HERE, VIS
from evaluate_visuelle_stolpersteine import VARIANTEN, im_korpus, ziele

# Bild-Tokens in der Voreinstellung und Kantenlänge eines Tokens in Pixeln
BASIS = {"qwen3vl": (768, 32), "colqwen2": (768, 28)}
SEITEN = [s for v in VARIANTEN["fussnote"].values() for s in v] + VARIANTEN["nup"]["2 pro Blatt"] + VARIANTEN["nup"]["4 pro Blatt"]
SPALTEN = [("fussnote", v) for v in VARIANTEN["fussnote"]] + [("nup", "2 pro Blatt"), ("nup", "4 pro Blatt")]


def load(name, faktor):
    kind, model_id, kwargs = MODELS[name]
    tokens, px = BASIS[name]
    pk = {"max_pixels": faktor * tokens * px * px}
    if kind == "multi":
        from sentence_transformers import MultiVectorEncoder

        return MultiVectorEncoder(model_id, device="cpu", model_kwargs={"dtype": torch.float32}, processor_kwargs=pk)
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_id, device="cpu", model_kwargs=kwargs, processor_kwargs=pk)


def score(kind, q, p):
    if kind == "multi":
        return float((q.float() @ p.float().T).max(dim=1).values.sum())
    return float(torch.nn.functional.cosine_similarity(q.float(), p.float(), dim=0))


def main(name, faktor):
    torch.set_num_threads(8)
    kind = MODELS[name][0]
    basis = torch.load(DATA / "emb" / f"{name}.pt", weights_only=False)
    target = DATA / "aufloesung" / f"{name}_x{faktor}.pt"
    target.parent.mkdir(exist_ok=True)
    neu = torch.load(target, weights_only=False) if target.exists() else {}
    offen = [s for s in SEITEN if s not in neu]
    if offen:
        model = load(name, faktor)
        t = time.perf_counter()
        for n, s in enumerate(offen):
            img = Image.open(VIS / "seiten" / f"{s}.png").convert("RGB")
            kw = {"convert_to_tensor": True} if kind == "single" else {}
            neu[s] = model.encode_document([img], batch_size=1, **kw)[0]
            torch.save(neu, target)
            print(f"{name} x{faktor} {n + 1}/{len(offen)} {s} {tuple(neu[s].shape)} {(time.perf_counter() - t) / (n + 1):.0f} s/Seite", flush=True)

    fragen = json.loads((HERE / "fragen_visuelle_stolpersteine.json").read_text())
    ids = sorted(basis["pages"])
    print(f"\n{name}: richtige Seite unter den ersten drei, Bild-Tokens x1 und x{faktor}")
    for gruppe, variante in SPALTEN:
        drin = im_korpus(ids, gruppe, variante)
        kept = [i for i, d in zip(ids, drin) if d]
        treffer = {"alt": 0, "neu": 0}
        idx = [f for f in fragen if f["gruppe"] == gruppe]
        for f in idx:
            q = basis["queries"][f["frage"]]
            for art, seiten in (("alt", basis["pages"]), ("neu", basis["pages"] | neu)):
                s = np.array([score(kind, q, seiten[i]) for i in kept])
                ranked = [kept[j] for j in np.argsort(-s)]
                treffer[art] += min(ranked.index(z) for z in ziele(f, variante)) < 3
        print(f"  {gruppe:9s} {variante:12s} {treffer['alt']}/{len(idx)} -> {treffer['neu']}/{len(idx)}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
