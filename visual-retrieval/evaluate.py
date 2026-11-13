"""Recall@1/@3 auf Seitenebene für Text- und visuelle Pipelines.

    uv run evaluate.py

Korpus ist das vollständige Testdokument: die 37 Stolperstein-Seiten für die Textextraktion,
die Ablenker und die Seiten mit visuellen Stolpersteinen (visuelle_stolpersteine.py). Gefragt
wird hier mit fragen.json, die Fragen zu den visuellen Stolpersteinen wertet
evaluate_visuelle_stolpersteine.py auf demselben Korpus aus.

Text: pypdf, Docling, Tesseract jeweils mit BM25 (ganze Seite) und BGE-M3
(Chunks à ~800 Zeichen, Seitenscore = bester Chunk).
Visuell: alle Embeddings in data/emb/*.pt (embed_visual.py).
"<Parser> hybrid": BM25 und BGE-M3 auf demselben Text, mit Reciprocal Rank Fusion kombiniert.
Hybrid: Reciprocal Rank Fusion (k=60) und zum Vergleich die Summe der pro Frage
standardisierten Scores (z-Scores).
"""

import json
import re
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
VIS = DATA / "visuelle_stolpersteine"
PARSER = ["pypdf", "docling", "tesseract"]


def load_texts():
    """Text pro Seite für jeden Parser, über das ganze Testdokument."""
    return {
        n: json.loads((DATA / "text" / f"{n}.json").read_text()) | json.loads((VIS / "text" / f"{n}.json").read_text())
        for n in PARSER
    }


def targets(f):
    if "ids" in f:
        return set(f["ids"])
    return {f"stolpersteine-{s:03d}" for s in f["seiten"]}


def tokenize(s):
    return re.findall(r"\w+", s.lower())


def chunks(text, size=800, overlap=200):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return [""]
    return [text[i : i + size] for i in range(0, max(len(text) - overlap, 1), size - overlap)]


def bm25_scores(corpus, ids, fragen):
    from rank_bm25 import BM25Okapi

    bm = BM25Okapi([tokenize(corpus[i]) for i in ids])
    return np.array([bm.get_scores(tokenize(q)) for q in fragen])


def dense_scores(model, corpus, ids, fragen):
    owner, texts = [], []
    for n, i in enumerate(ids):
        for c in chunks(corpus[i]):
            owner.append(n)
            texts.append(c)
    emb = model.encode(texts, batch_size=16, normalize_embeddings=True, convert_to_numpy=True)
    q = model.encode(fragen, normalize_embeddings=True, convert_to_numpy=True)
    sim = q @ emb.T
    out = np.full((len(fragen), len(ids)), -np.inf)
    for col, n in enumerate(owner):
        out[:, n] = np.maximum(out[:, n], sim[:, col])
    return out


def bge_scores(texts, ids, fragen, cache):
    """BGE-M3-Scores (Fragen × Seiten) pro Parser, in cache zwischengespeichert."""
    if cache.exists():
        c = dict(np.load(cache, allow_pickle=True))
        if list(c["fragen"]) == fragen and list(c["ids"]) == ids and all(n in c for n in texts):
            return {n: c[n] for n in texts}
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3", device="cpu")
    out = {n: dense_scores(model, corpus, ids, fragen) for n, corpus in texts.items()}
    np.savez(cache, fragen=np.array(fragen, dtype=object), ids=np.array(ids, dtype=object), **out)
    return out


def visual_scores(name, ids, fragen):
    e = torch.load(DATA / "emb" / f"{name}.pt", weights_only=False)
    if e["kind"] == "multi":
        pages = [e["pages"][i].float() for i in ids]
        return np.array([[float((e["queries"][q].float() @ p.T).max(dim=1).values.sum()) for p in pages] for q in fragen])
    p = torch.nn.functional.normalize(torch.stack([e["pages"][i].float() for i in ids]), dim=-1)
    q = torch.nn.functional.normalize(torch.stack([e["queries"][f].float() for f in fragen]), dim=-1)
    return (q @ p.T).numpy()


def ranks(scores):
    return np.argsort(-scores, axis=1)


def rrf(*score_mats, k=60):
    out = np.zeros_like(score_mats[0])
    for s in score_mats:
        r = np.argsort(np.argsort(-s, axis=1), axis=1)
        out += 1.0 / (k + r + 1)
    return out


def zsum(*score_mats):
    return sum((s - s.mean(axis=1, keepdims=True)) / s.std(axis=1, keepdims=True) for s in score_mats)


def main():
    fragen = json.loads((HERE / "fragen.json").read_text())
    texts = load_texts()
    ids = sorted(texts["pypdf"])
    qs = [f["frage"] for f in fragen]

    results = {}
    bge = bge_scores(texts, ids, qs, DATA / "bge.npz")
    for n, corpus in texts.items():
        results[f"{n} + BM25"] = bm25_scores(corpus, ids, qs)
        results[f"{n} + BGE-M3"] = bge[n]
    for n in texts:
        results[f"{n} hybrid"] = rrf(results[f"{n} + BM25"], results[f"{n} + BGE-M3"])
    for p in sorted((DATA / "emb").glob("*.pt")):
        results[p.stem] = visual_scores(p.stem, ids, qs)
    if "colqwen2" in results:
        results["Hybrid (Docling+BGE-M3, ColQwen2)"] = rrf(results["docling + BGE-M3"], results["colqwen2"])
        results["Hybrid (Docling+BM25+BGE-M3, ColQwen2)"] = rrf(
            results["docling + BM25"], results["docling + BGE-M3"], results["colqwen2"]
        )

    if "colqwen2" in results:
        results["Hybrid (Tesseract+BM25, ColQwen2)"] = rrf(results["tesseract + BM25"], results["colqwen2"])
        results["z-Scores (Tesseract+BM25, ColQwen2)"] = zsum(results["tesseract + BM25"], results["colqwen2"])
    if "qwen3vl" in results:
        results["Hybrid (Tesseract+BM25, Qwen3-VL)"] = rrf(results["tesseract + BM25"], results["qwen3vl"])
        results["z-Scores (Tesseract+BM25, Qwen3-VL)"] = zsum(results["tesseract + BM25"], results["qwen3vl"])
    results["Hybrid (Tesseract: BM25, BGE-M3)"] = rrf(results["tesseract + BM25"], results["tesseract + BGE-M3"])
    results["z-Scores (Tesseract: BM25, BGE-M3)"] = zsum(results["tesseract + BM25"], results["tesseract + BGE-M3"])
    rows = {}
    for name, s in results.items():
        r = ranks(s)
        per_q = []
        for qi, f in enumerate(fragen):
            t = targets(f)
            ranked = [ids[j] for j in r[qi]]
            rank = min(ranked.index(x) for x in t) + 1
            per_q.append({"rank": rank, "top3": ranked[:3]})
        rows[name] = per_q

    groups = ["zeichen", "bild", "layout", "tabelle", "seitengrenze", "ids", "kontrolle"]
    print(f"{len(ids)} Seiten, {len(fragen)} Fragen")
    print(f"{'Pipeline':42s} R@1   R@3   | " + " ".join(f"{g[:8]:>8s}" for g in groups))
    for name, per_q in rows.items():
        r1 = np.mean([q["rank"] <= 1 for q in per_q])
        r3 = np.mean([q["rank"] <= 3 for q in per_q])
        g = []
        for grp in groups:
            idx = [i for i, f in enumerate(fragen) if f["gruppe"] == grp]
            g.append(f"{sum(per_q[i]['rank'] <= 3 for i in idx)}/{len(idx)}")
        print(f"{name:42s} {r1:.2f}  {r3:.2f}  | " + " ".join(f"{x:>8s}" for x in g))

    (DATA / "ergebnisse.json").write_text(
        json.dumps({n: [dict(frage=f["frage"], gruppe=f["gruppe"], stein=f["stein"], **pq) for f, pq in zip(fragen, v)] for n, v in rows.items()}, ensure_ascii=False, indent=1)
    )


if __name__ == "__main__":
    main()
