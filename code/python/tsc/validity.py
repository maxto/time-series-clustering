"""Checks on a dissimilarity matrix and the silhouette computed from it."""

import numpy as np


def check_dissimilarity(D: np.ndarray, labels: np.ndarray) -> list[str]:
    """List what is wrong with (D, labels) for a silhouette. Empty list = fine."""
    D = np.asarray(D, dtype=float)
    labels = np.asarray(labels)
    problems = []
    if D.ndim != 2 or D.shape[0] != D.shape[1]:
        # The other checks need a square matrix, so stop here.
        return [f"matrix is not square: shape {D.shape}"]
    n = D.shape[0]
    if labels.shape != (n,):
        problems.append(f"label count {labels.size} differs from matrix rows {n}")
    if not np.all(np.isfinite(D)):
        problems.append("matrix has entries that are not finite (nan or inf)")
    else:
        if np.any(D < 0):
            problems.append("matrix has negative entries")
        if not np.allclose(D, D.T, rtol=0, atol=1e-12):
            problems.append("matrix is not symmetric (tolerance 1e-12)")
        if not np.allclose(np.diag(D), 0, rtol=0, atol=1e-12):
            problems.append("matrix has a non-zero diagonal")
    if labels.shape == (n,):
        n_clusters = len(np.unique(labels))
        if not 2 <= n_clusters <= n - 1:
            problems.append(f"{n_clusters} clusters, need between 2 and {n - 1}")
    return problems


def silhouette_from_matrix(D: np.ndarray, labels: np.ndarray) -> float:
    """Mean silhouette (Rousseeuw, 1987) from a precomputed distance matrix.

    For each point i:
      a = mean distance to the other members of its own cluster,
      b = smallest mean distance to the members of any other cluster,
      s = (b - a) / max(a, b).
    A point alone in its cluster scores 0, and so does a = b = 0.
    """
    problems = check_dissimilarity(D, labels)
    if problems:
        raise ValueError("; ".join(problems))
    D = np.asarray(D, dtype=float)
    labels = np.asarray(labels)
    scores = []
    for i in range(len(labels)):
        own = (labels == labels[i])
        own[i] = False                      # exclude the point itself
        if not own.any():                   # singleton cluster
            scores.append(0.0)
            continue
        a = D[i, own].mean()
        b = min(D[i, labels == other].mean()
                for other in np.unique(labels) if other != labels[i])
        scores.append(0.0 if a == b == 0 else (b - a) / max(a, b))
    return float(np.mean(scores))
