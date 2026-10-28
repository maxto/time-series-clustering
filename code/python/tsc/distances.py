"""Reference distances for the course: Euclidean, DTW and SBD.

The loops are plain on purpose. This is the version to read and study.
"""

import numpy as np
from numpy.typing import ArrayLike


def _as_series(x: ArrayLike) -> np.ndarray:
    """Return x as a float vector, or raise ValueError if empty or not finite."""
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or x.size == 0:
        raise ValueError("a series must be a non-empty 1-D sequence")
    if not np.all(np.isfinite(x)):
        raise ValueError("a series must contain only finite numbers")
    return x


def znorm(x: ArrayLike) -> np.ndarray:
    """Subtract the mean and divide by the population std (zeros if std is 0)."""
    x = _as_series(x)
    std = x.std()  # population std (ddof=0)
    if std == 0:
        return np.zeros_like(x)
    return (x - x.mean()) / std


def euclidean(x: ArrayLike, y: ArrayLike) -> float:
    """Straight-line distance between two series of equal length."""
    x, y = _as_series(x), _as_series(y)
    if len(x) != len(y):
        raise ValueError("euclidean needs series of equal length")
    return float(np.sqrt(np.sum((x - y) ** 2)))


def _check_dtw_inputs(x, y, w):
    """Validate DTW inputs once. Return the series and the effective window."""
    x, y = _as_series(x), _as_series(y)
    if w is None:
        return x, y, max(len(x), len(y))  # wide enough to never bind
    if isinstance(w, bool) or not isinstance(w, (int, np.integer)):
        raise ValueError("w must be a non-negative integer or None")
    if w < 0:
        raise ValueError("w must be a non-negative integer or None")
    if w < abs(len(x) - len(y)):
        raise ValueError("no admissible path: w < |len(x) - len(y)|")
    return x, y, int(w)


def _accumulated_cost(x: np.ndarray, y: np.ndarray, w: int) -> np.ndarray:
    """Accumulated squared cost D, with D[i, j] = best cost of reaching (i, j).

    Cells outside the Sakoe-Chiba window |i - j| <= w stay at infinity.
    """
    n, m = len(x), len(y)
    D = np.full((n, m), np.inf)
    for i in range(n):
        for j in range(max(0, i - w), min(m, i + w + 1)):
            local = (x[i] - y[j]) ** 2
            if i == 0 and j == 0:
                D[i, j] = local  # closed start
            else:
                # cheapest way in: from the left, from above, or diagonally
                up = D[i - 1, j] if i > 0 else np.inf
                left = D[i, j - 1] if j > 0 else np.inf
                diag = D[i - 1, j - 1] if i > 0 and j > 0 else np.inf
                D[i, j] = local + min(up, left, diag)
    return D


def dtw(x: ArrayLike, y: ArrayLike, w: int | None = None) -> float:
    """DTW distance: square root of the accumulated squared cost.

    w is the Sakoe-Chiba half-width in samples (None means no window).
    """
    x, y, w = _check_dtw_inputs(x, y, w)
    D = _accumulated_cost(x, y, w)
    return float(np.sqrt(D[-1, -1]))


def dtw_path(x: ArrayLike, y: ArrayLike, w: int | None = None) -> list[tuple[int, int]]:
    """One optimal warping path from (0, 0) to (n-1, m-1).

    Walking back from the end, ties are broken in the order diagonal,
    then (1, 0) (previous i), then (0, 1) (previous j).
    """
    x, y, w = _check_dtw_inputs(x, y, w)
    D = _accumulated_cost(x, y, w)
    i, j = len(x) - 1, len(y) - 1
    path = [(i, j)]
    while (i, j) != (0, 0):
        # predecessors in tie-break order: diagonal, (1, 0), (0, 1)
        candidates = [(i - 1, j - 1), (i - 1, j), (i, j - 1)]
        candidates = [(a, b) for a, b in candidates if a >= 0 and b >= 0]
        i, j = min(candidates, key=lambda c: D[c])  # min keeps the first on ties
        path.append((i, j))
    return path[::-1]


def sbd(x: ArrayLike, y: ArrayLike) -> float:
    """Shape-based distance: 1 - max normalised cross-correlation over all lags.

    Inputs are used as given (z-normalise them first if you want that).
    """
    x, y = _as_series(x), _as_series(y)
    norm = np.linalg.norm(x) * np.linalg.norm(y)
    if norm == 0:
        raise ValueError("sbd is undefined for a series with zero norm")
    # Cross-correlation of all lags through the FFT, zero-padded to avoid wrap-around.
    size = len(x) + len(y) - 1
    cc = np.fft.irfft(np.fft.rfft(x, size) * np.conj(np.fft.rfft(y, size)), size)
    return float(1.0 - cc.max() / norm)
