"""Settlement extents from built-up evidence (skill section 3).

`dbscan` is a plain DBSCAN on metric points (scipy cKDTree; no scikit-learn dependency).
`morph_close` is the binary morphological close used on built-up masks (GHS-BUILT-S style).
Every parameter is an A-geo assumption passed in by the caller (`docs/assumptions.md`).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


def dbscan(xy: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    """DBSCAN labels (-1 = noise) for an (n, 2) metric array."""
    n = len(xy)
    if n == 0:
        return np.empty(0, dtype=int)
    tree = cKDTree(xy)
    pairs = tree.query_pairs(eps, output_type="ndarray")
    deg = np.bincount(pairs.ravel(), minlength=n) + 1  # a point counts itself
    core = deg >= min_samples
    labels = np.full(n, -1, dtype=int)
    if not core.any():
        return labels
    cp = pairs[core[pairs[:, 0]] & core[pairs[:, 1]]]
    idx = np.flatnonzero(core)
    remap = -np.ones(n, dtype=int)
    remap[idx] = np.arange(len(idx))
    g = coo_matrix(
        (np.ones(len(cp)), (remap[cp[:, 0]], remap[cp[:, 1]])), shape=(len(idx), len(idx))
    )
    _, comp = connected_components(g, directed=False)
    labels[idx] = comp
    # border points join the cluster of their first core neighbour
    border = pairs[core[pairs[:, 0]] ^ core[pairs[:, 1]]]
    for a, b in border:
        c, o = (a, b) if core[a] else (b, a)
        if labels[o] == -1:
            labels[o] = labels[c]
    return labels


def clusters_near(xy: np.ndarray, labels: np.ndarray, point: tuple[float, float], snap_m: float):
    """Indices of points in every cluster with a member within snap_m of the point."""
    d = np.hypot(xy[:, 0] - point[0], xy[:, 1] - point[1])
    near = set(labels[(d <= snap_m) & (labels >= 0)].tolist())
    return np.flatnonzero(np.isin(labels, list(near))) if near else np.empty(0, dtype=int)


def morph_close(mask: np.ndarray, kernel: int) -> np.ndarray:
    """Binary close with a square kernel of `kernel` cells (odd)."""
    if kernel <= 1:
        return mask.astype(bool)
    st = np.ones((kernel, kernel), dtype=bool)
    pad = kernel
    m = np.pad(mask.astype(bool), pad)
    return ndimage.binary_closing(m, structure=st)[pad:-pad, pad:-pad]
