"""Fragen zu den visuellen Stolpersteinen: Seiten mit intaktem Textlayer, die für ein visuelles
Modell schwer zu lesen sind.

    uv run evaluate_visuelle_stolpersteine.py

Korpus ist wie in evaluate.py das vollständige Testdokument. Von den Fußnoten-Seiten und den
n-up-Seiten gibt es je drei Varianten desselben Inhalts. Bei den Fragen zu diesen Seiten wird
jede Variante einzeln gewertet, und die beiden inhaltsgleichen Schwesterseiten werden dabei
aus der Rangfolge genommen (sonst stünde immer die am besten lesbare Variante vorn). Alle
anderen Seiten bleiben im Korpus. "<Parser> hybrid" ist BM25 und BGE-M3 auf demselben Text,
mit Reciprocal Rank Fusion kombiniert.
"""

import json
import numpy as np
import torch

from evaluate import DATA, HERE, VIS, bge_scores, bm25_scores, load_texts, rrf, visual_scores


VARIANTEN = {
    "fussnote": {
        "8 pt": [f"fussnoten-{i:03d}" for i in (1, 4, 7)],
        "6 pt": [f"fussnoten-{i:03d}" for i in (2, 5, 8)],
        "4,5 pt": [f"fussnoten-{i:03d}" for i in (3, 6, 9)],
    },
    "nup": {
        "1 pro Blatt": [f"nup1-{i:03d}" for i in range(1, 9)],
        "2 pro Blatt": [f"nup2-{i:03d}" for i in range(1, 5)],
        "4 pro Blatt": [f"nup4-{i:03d}" for i in range(1, 3)],
    },
}
VISUELL = ["colmodernvbert", "colqwen2", "qwen3vl"]


def ziele(f, variante):
    if f["gruppe"] == "fussnote":
        k = list(VARIANTEN["fussnote"]).index(variante)
        return {f"fussnoten-{3 * (f['fakt'] - 1) + k + 1:03d}"}
    if f["gruppe"] == "nup":
        s = f["seite"]
        return {{"1 pro Blatt": f"nup1-{s:03d}", "2 pro Blatt": f"nup2-{(s + 1) // 2:03d}", "4 pro Blatt": f"nup4-{(s + 3) // 4:03d}"}[variante]}
    return set(f["ids"])


def im_korpus(ids, gruppe, variante):
    """Alle Seiten außer den inhaltsgleichen Schwesterseiten der gefragten Variante."""
    raus = {i for v, seiten in VARIANTEN.get(gruppe, {}).items() if v != variante for i in seiten}
    return np.array([i not in raus for i in ids])


def main():
    fragen = json.loads((HERE / "fragen_visuelle_stolpersteine.json").read_text())
    qs = [f["frage"] for f in fragen]
    texts = load_texts()
    ids = sorted(texts["pypdf"])

    fest = {f"{n} + BGE-M3": s for n, s in bge_scores(texts, ids, qs, VIS / "bge.npz").items()}
    for name in VISUELL:
        try:
            fest[name] = visual_scores(name, ids, qs)
        except (FileNotFoundError, KeyError) as e:
            print(f"{name} fehlt oder ist unvollständig ({e!r}), bitte embed_visual.py {name} laufen lassen")

    spalten = []  # (Gruppe, Variante, Frage-Indizes)
    for g in dict.fromkeys(f["gruppe"] for f in fragen):
        idx = [i for i, f in enumerate(fragen) if f["gruppe"] == g]
        spalten += [(g, v, idx) for v in VARIANTEN.get(g, {None: None})]

    pipelines = [f"{n} {art}" for n in texts for art in ("+ BM25", "+ BGE-M3", "hybrid")] + [v for v in VISUELL if v in fest]
    raenge = {p: {} for p in pipelines}
    for g, v, idx in spalten:
        drin = im_korpus(ids, g, v)
        kept = [i for i, d in zip(ids, drin) if d]
        for p in pipelines:
            if p.endswith("BM25"):
                s = bm25_scores(texts[p.split(" + ")[0]], kept, [qs[i] for i in idx])
            elif p.endswith("hybrid"):
                n = p.split()[0]
                s = rrf(bm25_scores(texts[n], kept, [qs[i] for i in idx]), fest[f"{n} + BGE-M3"][np.ix_(idx, drin)])
            else:
                s = fest[p][np.ix_(idx, drin)]
            order = np.argsort(-s, axis=1)
            for row, i in enumerate(idx):
                ranked = [kept[j] for j in order[row]]
                raenge[p][f"{i}|{v}"] = min(ranked.index(z) for z in ziele(fragen[i], v)) + 1

    kopf = [f"{g[:9]}{'' if v is None else ' ' + v.split()[0]}" for g, v, _ in spalten]
    for k, titel in ((1, "Platz 1"), (3, "unter den ersten drei")):
        print(f"\nRichtige Seite {titel} ({len(ids)} Seiten, Schwesterseiten der gefragten Variante ausgenommen)")
        print(f"{'Pipeline':20s} " + " ".join(f"{h:>12s}" for h in kopf))
        for p in pipelines:
            zellen = [f"{sum(raenge[p][f'{i}|{v}'] <= k for i in idx)}/{len(idx)}" for g, v, idx in spalten]
            print(f"{p:20s} " + " ".join(f"{z:>12s}" for z in zellen))

    out = []
    for g, v, idx in spalten:
        for i in idx:
            out.append({"gruppe": g, "variante": v, "frage": qs[i], "rang": {p: raenge[p][f"{i}|{v}"] for p in pipelines}})
    (VIS / "ergebnisse.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
