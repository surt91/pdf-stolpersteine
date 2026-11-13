"""Bettet alle Seitenbilder und alle Fragen mit einem visuellen Modell ein.

    uv run embed_visual.py colmodernvbert
    uv run embed_visual.py colqwen2
    uv run embed_visual.py qwen3vl      # Single-Vector
    uv run embed_visual.py clip         # Single-Vector, Baseline

Seiten: data/seiten/ (Stolpersteine für die Textextraktion und Ablenker) und
data/visuelle_stolpersteine/seiten/. Fragen: fragen.json und fragen_visuelle_stolpersteine.json.
Ergebnis: data/emb/<name>.pt mit {"kind", "pages": {id: Tensor}, "queries": {frage: Tensor}}.
Fortsetzbar: fertige Seiten und Fragen werden nicht noch einmal gerechnet.
"""

import json
import sys
import time
from pathlib import Path

import torch
from PIL import Image

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SEITEN = [DATA / "seiten", DATA / "visuelle_stolpersteine" / "seiten"]
FRAGEN = [HERE / "fragen.json", HERE / "fragen_visuelle_stolpersteine.json"]

MODELS = {
    "colmodernvbert": ("multi", "ModernVBERT/colmodernvbert", {}),
    "colqwen2": ("multi", "vidore/colqwen2-v1.0", {}),
    # fp32 ist auf CPUs ohne bf16-Einheiten deutlich schneller. Beide Qwen-Modelle laufen mit
    # der Voreinstellung ihres Prozessors: ColQwen2 mit höchstens 768 Bild-Tokens, Qwen3-VL mit
    # höchstens 1.310.720 px (rund 1280 Bild-Tokens, 32 px pro Token nach dem Merge).
    "qwen3vl": ("single", "Qwen/Qwen3-VL-Embedding-2B", {"dtype": torch.float32}),
    "clip": ("clip", None, {}),
}


def load(kind, model_id, kwargs):
    if kind == "multi":
        from sentence_transformers import MultiVectorEncoder

        return MultiVectorEncoder(model_id, device="cpu", model_kwargs=kwargs)
    from sentence_transformers import SentenceTransformer

    if kind == "clip":
        return SentenceTransformer("clip-ViT-B-32", device="cpu"), SentenceTransformer(
            "sentence-transformers/clip-ViT-B-32-multilingual-v1", device="cpu"
        )
    return SentenceTransformer(model_id, device="cpu", model_kwargs=kwargs)


def main(name: str) -> None:
    kind, model_id, kwargs = MODELS[name]
    torch.set_num_threads(8)
    target = DATA / "emb" / f"{name}.pt"
    target.parent.mkdir(exist_ok=True)
    cache = torch.load(target, weights_only=False) if target.exists() else {"kind": kind, "pages": {}, "queries": {}}
    files = [f for d in SEITEN for f in sorted(d.glob("*.png")) if f.stem not in cache["pages"]]
    fragen = [f["frage"] for p in FRAGEN for f in json.loads(p.read_text())]
    fragen = [q for q in dict.fromkeys(fragen) if q not in cache["queries"]]
    if not files and not fragen:
        print(name, "ist vollständig")
        return
    model = load(kind, model_id, kwargs)
    if kind == "clip":
        img_model, txt_model = model
    if fragen:
        if kind == "multi":
            q = model.encode_query(fragen, batch_size=8)
        elif kind == "clip":
            q = txt_model.encode(fragen, convert_to_tensor=True)
        else:
            q = model.encode_query(fragen, convert_to_tensor=True)
        cache["queries"].update(zip(fragen, q, strict=True))
        torch.save(cache, target)
        print(f"{name}: {len(fragen)} Fragen", flush=True)
    t = time.perf_counter()
    for n, f in enumerate(files):
        img = Image.open(f).convert("RGB")
        if kind == "multi":
            cache["pages"][f.stem] = model.encode_document([img], batch_size=1)[0]
        elif kind == "clip":
            cache["pages"][f.stem] = img_model.encode([img], convert_to_tensor=True)[0]
        else:
            cache["pages"][f.stem] = model.encode_document([img], batch_size=1, convert_to_tensor=True)[0]
        if n % 10 == 9 or n == len(files) - 1:
            torch.save(cache, target)
        print(f"{name} {n + 1}/{len(files)} {f.stem} {tuple(cache['pages'][f.stem].shape)} {(time.perf_counter() - t) / (n + 1):.1f} s/Seite", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
