"""Similarity Maps (ColQwen2) für einige Stolperstein-Seiten.

    uv run similarity_maps.py

Ergebnis: img/similarity_maps.png (eine Zeile pro Seite: Seite, Heatmap für ein
Frage-Token).
"""

import json
from pathlib import Path

import torch
from PIL import Image
from sentence_transformers import MultiVectorEncoder
from sentence_transformers.multi_vector_encoder.interpretability import (
    get_n_patches,
    real_query_token_slice,
)

HERE = Path(__file__).resolve().parent
SEITEN = HERE / "data" / "seiten"
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)
FONT = "/usr/share/fonts/TTF/DejaVuSans.ttf"

# (Seite, Frage, Teil-Tokens des Worts für die Heatmap, Beschriftung)
FAELLE = [
    (3, "Wer ist die Ansprechpartnerin und welche Durchwahl hat sie?", [" Durch", "wahl"], "Fehlende ToUnicode-CMap", "Durchwahl"),
    (6, "Auf wie viele Monate verlängert sich die Garantie?", None, "Type-3-Schrift", "Garantie"),
    (24, "Als was ist Frau Mustermann beschäftigt?", None, "Scan ohne Textlayer", "Mustermann"),
]


def main() -> None:
    torch.set_num_threads(8)
    model = MultiVectorEncoder("vidore/colqwen2-v1.0", device="cpu", model_kwargs={"dtype": torch.float32})
    tok = model.tokenizer if hasattr(model, "tokenizer") else model.processor.tokenizer
    panels = []
    for seite, frage, teile, label, wort in FAELLE:
        img = Image.open(SEITEN / f"stolpersteine-{seite:03d}.png").convert("RGB")
        doc = model.encode_document([img])[0].float()
        q = model.encode_query([frage])[0].float()[real_query_token_slice(model, frage)]
        tokens = [tok.decode([i]) for i in tok(frage, add_special_tokens=False)["input_ids"]][: len(q)]
        # alle Teil-Tokens des Worts (z. B. " Gar", "ant", "ie")
        pos = [i for i, t in enumerate(tokens) if (teile and t in teile)]
        if not teile:
            joined = ""
            for i, t in enumerate(tokens):
                if wort.startswith((joined + t).strip()) and (joined + t).strip():
                    joined += t
                    pos.append(i)
                elif pos and joined.strip() != wort:
                    pos, joined = [], ""
        feats = model[0].preprocess([img]) if hasattr(model[0], "preprocess") else model.preprocess([img])
        mask = feats["input_ids"][0] == tok.convert_tokens_to_ids("<|image_pad|>")
        assert len(mask) == doc.shape[0]
        n_cols, n_rows = get_n_patches(model, img.size)
        sim = (q[pos] @ doc[mask].T).max(dim=0).values.reshape(n_rows, n_cols)
        print(seite, [tokens[i] for i in pos], divmod(int(sim.argmax()), n_cols))
        # tatsächliche Position des Worts per Tesseract, zum Vergleich in der Abbildung
        import pytesseract

        ocr = pytesseract.image_to_data(img, lang="deu", output_type=pytesseract.Output.DICT)
        box = next((ocr["left"][i], ocr["top"][i], ocr["width"][i], ocr["height"][i])
                   for i, w in enumerate(ocr["text"]) if wort in w)
        print("  Wort bei", box)
        import numpy as np

        (HERE / "data" / "offset").mkdir(parents=True, exist_ok=True)
        np.save(HERE / "data" / "offset" / f"echt-{seite:03d}-{wort}-colqwen2.npy", sim.numpy())
        (HERE / "data" / "offset" / f"echt-{seite:03d}-{wort}-box.json").write_text(json.dumps(box))
        panels.append((img, sim.numpy(), f"{label}: „{wort}“", box))

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(panels), figsize=(4 * len(panels), 2.9), dpi=200)
    fig.patch.set_facecolor("#fcfcfb")
    for ax, (img, sim, cap, box) in zip(axes, panels):
        w, h = img.size
        # nur das obere Drittel der Seite zeigen, dort steht der Inhalt
        crop = h * 0.42
        ax.imshow(img, extent=(0, w, h, 0))
        ax.imshow(sim, extent=(0, w, h, 0), cmap="magma", alpha=0.55, interpolation="nearest",
                  vmin=sim.min(), vmax=sim.max())
        bx, by, bw, bh = box
        ax.add_patch(plt.Rectangle((bx - 6, by - 6), bw + 12, bh + 12, fill=False, edgecolor="#2a78d6", linewidth=1.6))
        ax.set_xlim(0, w)
        ax.set_ylim(crop, 0)
        ax.set_title(cap, fontsize=9, color="#0b0b0b")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(IMG / "similarity_maps.png", facecolor="#fcfcfb", bbox_inches="tight", pad_inches=0.05)

if __name__ == "__main__":
    main()
