"""Zusatzauswertungen: Kopfzeile ("Was ist vertraulich?") und Zeitmessung ohne Konkurrenz.

    uv run extra.py
"""

import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from evaluate import bm25_scores, load_texts

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FRAGE = "Was ist vertraulich?"
torch.set_num_threads(8)


def anteil(scores, ids, k=37):
    top = [ids[j] for j in np.argsort(-scores)[:k]]
    return sum(t.startswith("stolpersteine") for t in top)


def main():
    texts = load_texts()
    ids = sorted(texts["pypdf"])
    for n, c in texts.items():
        print(f"{n} + BM25: {anteil(bm25_scores(c, ids, [FRAGE])[0], ids)}/37 Stolperstein-Seiten unter den ersten 37")

    from sentence_transformers import MultiVectorEncoder, SentenceTransformer

    seiten = [Image.open(DATA / "seiten" / f"stolpersteine-{i:03d}.png").convert("RGB") for i in (3, 15, 21)]
    for name, cls, mid, kw in [
        ("colmodernvbert", MultiVectorEncoder, "ModernVBERT/colmodernvbert", {}),
        ("colqwen2", MultiVectorEncoder, "vidore/colqwen2-v1.0", {}),
        ("qwen3vl", SentenceTransformer, "Qwen/Qwen3-VL-Embedding-2B", {"processor_kwargs": {"max_pixels": 768 * 32 * 32}}),
    ]:
        model = cls(mid, device="cpu", model_kwargs={"dtype": torch.float32}, **kw)
        e = torch.load(DATA / "emb" / f"{name}.pt", weights_only=False)
        if name == "qwen3vl":
            q = torch.nn.functional.normalize(model.encode_query([FRAGE], convert_to_tensor=True).float(), dim=-1)[0]
            p = torch.nn.functional.normalize(torch.stack([e["pages"][i].float() for i in ids]), dim=-1)
            s = (p @ q).numpy()
        else:
            q = model.encode_query([FRAGE])[0].float()
            s = np.array([float((q @ e["pages"][i].float().T).max(dim=1).values.sum()) for i in ids])
        print(f"{name}: {anteil(s, ids)}/37 Stolperstein-Seiten unter den ersten 37")
        model.encode_document([seiten[0]])  # Aufwärmen
        t = time.perf_counter()
        for img in seiten:
            model.encode_document([img])
        print(f"{name}: {(time.perf_counter() - t) / len(seiten):.1f} s/Seite (CPU, ohne parallele Last)")
        del model


if __name__ == "__main__":
    main()
