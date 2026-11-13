"""MaxSim (Late Interaction) in NumPy, wie im Artikel."""
import time

import numpy as np


def maxsim(q, d):
    """q: (n_q, dim) Frage-Token, d: (n_p, dim) Patches einer Seite."""
    sim = q @ d.T  # (n_q, n_p): jedes Frage-Token gegen jeden Patch
    return sim.max(axis=1).sum()  # bester Patch pro Token, aufsummiert


def normalize(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


rng = np.random.default_rng(0)
n_pages, n_patches, dim = 1000, 1030, 128
pages = normalize(rng.standard_normal((n_pages, n_patches, dim))).astype(np.float32)
query = normalize(rng.standard_normal((20, dim))).astype(np.float32)

t = time.perf_counter()
scores = np.array([maxsim(query, p) for p in pages])
t_multi = time.perf_counter() - t

single = normalize(rng.standard_normal((n_pages, dim))).astype(np.float32)
t = time.perf_counter()
scores_single = single @ query[0]
t_single = time.perf_counter() - t

print(f"MaxSim:      {t_multi*1000:.1f} ms für {n_pages} Seiten")
print(f"Single-Vec:  {t_single*1000:.3f} ms für {n_pages} Seiten")
print(f"Multiplikationen pro Seite: {20*n_patches*dim:,} vs. {dim:,}")
