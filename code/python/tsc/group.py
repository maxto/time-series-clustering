"""Load the demo fixture, build distance matrices, group with average linkage."""

import csv
from collections.abc import Callable
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

# Resolved from this file, so it works from any working directory.
DEFAULT_PATH = Path(__file__).resolve().parents[3] / "fixtures" / "demand-12.csv"


def load_demand(path=DEFAULT_PATH):
    """Read the fixture: (ids, 12x48 values, declared groups by column).

    The groups are the two labelings the fixture was authored with:
    "hour_group" (when demand peaks) and "shape_group" (what the day looks like).
    """
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    value_cols = [c for c in rows[0] if c.startswith("v")]
    ids = [r["id"] for r in rows]
    X = np.array([[float(r[c]) for c in value_cols] for r in rows])
    groups = {g: [r[g] for r in rows] for g in ("hour_group", "shape_group")}
    return ids, X, groups


def distance_matrix(X: np.ndarray, metric: Callable) -> np.ndarray:
    """Pairwise distances between the rows of X, as a symmetric n x n matrix."""
    n = len(X)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            D[i, j] = D[j, i] = metric(X[i], X[j])
    return D


def average_linkage(D: np.ndarray, k: int) -> np.ndarray:
    """Cut an average-linkage tree built on D into k clusters.

    Labels are 0-based, numbered in order of first appearance (point 0 gets 0).
    Raises ValueError if D is not a square symmetric matrix, or if the cut
    gives fewer than k clusters (for example when many distances are tied).
    """
    D = np.asarray(D, dtype=float)
    if D.ndim != 2 or D.shape[0] != D.shape[1]:
        raise ValueError(f"D is not square: shape {D.shape}")
    if not np.allclose(D, D.T, rtol=0, atol=1e-12):
        raise ValueError("D is not symmetric")
    # squareform would silently read only the upper triangle, so we checked first.
    tree = linkage(squareform(D, checks=False), method="average")
    raw = fcluster(tree, t=k, criterion="maxclust")
    if len(set(raw)) < k:
        raise ValueError(f"asked for {k} clusters, got {len(set(raw))}")
    # Renumber 1.. labels from scipy to 0.. in order of first appearance.
    order = {}
    for label in raw:
        order.setdefault(label, len(order))
    return np.array([order[label] for label in raw])
