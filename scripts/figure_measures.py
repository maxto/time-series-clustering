"""Measures the lesson figures need and the reference package does not hold yet.

Used only by scripts/figures.py. Each follows the definition stated in its lesson. They move to
code/python/tsc/ in the code pass. Values were cross-checked once against scikit-learn and aeon.
"""

from itertools import permutations

import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform


def moving_average(x, k):
    """Centred moving average over 2k + 1 points. The first and last k samples have no full window: NaN."""
    out = np.full(len(x), np.nan)
    kernel = np.ones(2 * k + 1) / (2 * k + 1)
    out[k:len(x) - k] = np.convolve(x, kernel, mode="valid")
    return out


def block_mean(x, b):
    """Means of consecutive blocks of b samples."""
    return np.array([x[u:u + b].mean() for u in range(0, len(x) - b + 1, b)])


def correlation_distance(x, y):
    return 1.0 - float(np.corrcoef(x, y)[0, 1])


def ncc_curve(x, y):
    """Coefficient-normalised cross-correlation for s in -(m-1)..(m-1): CC_s = sum x_t y_(t-s)."""
    m = len(x)
    cc = np.correlate(x, y, mode="full")  # index m - 1 is shift 0
    return np.arange(-(m - 1), m), cc / (np.linalg.norm(x) * np.linalg.norm(y))


def lcss_pairs(x, y, eps, delta):
    """LCSS table of the lesson, with |i - j| <= delta, and one optimal set of matched pairs (i, j)."""
    n, m = len(x), len(y)
    L = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if abs(i - j) <= delta and abs(x[i - 1] - y[j - 1]) <= eps:
                L[i, j] = L[i - 1, j - 1] + 1
            else:
                L[i, j] = max(L[i - 1, j], L[i, j - 1])
    pairs, i, j = [], n, m
    while i > 0 and j > 0:
        if abs(i - j) <= delta and abs(x[i - 1] - y[j - 1]) <= eps and L[i, j] == L[i - 1, j - 1] + 1:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif L[i - 1, j] >= L[i, j - 1]:
            i -= 1
        else:
            j -= 1
    return int(L[n, m]), pairs[::-1]


def acf(x, lags):
    """Sample autocorrelation at lags 1..lags: sum (x_t - m)(x_(t+l) - m) / sum (x_t - m)^2."""
    c = x - x.mean()
    denom = float(c @ c)
    return np.array([float(c[:-k] @ c[k:]) / denom for k in range(1, lags + 1)])


def ordinal_histogram(x, d=3, tau=1):
    """Relative frequency of each ordinal pattern of length d, patterns in lexicographic order."""
    patterns = list(permutations(range(d)))
    counts = dict.fromkeys(patterns, 0)
    for t in range(len(x) - (d - 1) * tau):
        counts[tuple(int(v) for v in np.argsort(x[t:t + d * tau:tau], kind="stable"))] += 1
    total = sum(counts.values())
    return patterns, np.array([counts[p] / total for p in patterns])


def permutation_entropy(p):
    """Normalised permutation entropy of a pattern histogram: -sum p ln p / ln d!."""
    q = p[p > 0]
    return float(-(q * np.log(q)).sum() / np.log(len(p)))


def subsequence_distance(s, t):
    """Smallest Euclidean distance between the z-normalised shapelet s and any z-normalised window of t."""
    z = lambda v: (v - v.mean()) / v.std(ddof=0)
    l = len(s)
    return min(float(np.linalg.norm(z(s) - z(t[i:i + l]))) for i in range(len(t) - l + 1))


def nn_profile(a, b, l):
    """For each window of length l of a, the z-normalised Euclidean distance to its nearest window of b."""
    return np.array([subsequence_distance(a[i:i + l], b) for i in range(len(a) - l + 1)])


def k_medoids(D, k):
    """Exact PAM objective by enumeration of the medoid sets (small n). Labels 0..k-1 by first appearance."""
    from itertools import combinations
    best, best_set = np.inf, None
    for M in combinations(range(len(D)), k):
        cost = D[:, M].min(axis=1).sum()
        if cost < best - 1e-12:
            best, best_set = cost, M
    labels = D[:, best_set].argmin(axis=1)
    return first_seen(labels), [int(m) for m in best_set]


def dbscan(D, eps, min_pts):
    """DBSCAN on a distance matrix. A point counts in its own neighbourhood. -1 marks noise."""
    n = len(D)
    neighbours = [np.flatnonzero(D[i] <= eps) for i in range(n)]
    core = [len(neighbours[i]) >= min_pts for i in range(n)]
    labels = np.full(n, -1)
    c = 0
    for i in range(n):
        if labels[i] != -1 or not core[i]:
            continue
        labels[i] = c
        stack = [i]
        while stack:
            p = stack.pop()
            if core[p]:
                for q in neighbours[p]:
                    if labels[q] == -1:
                        labels[q] = c
                        stack.append(int(q))
        c += 1
    return labels


def first_seen(labels):
    """Relabel so that labels count up in order of first appearance. Negative labels are kept."""
    seen, out = {}, []
    for v in labels:
        v = int(v)
        if v < 0:
            out.append(v)
            continue
        out.append(seen.setdefault(v, len(seen)))
    return np.array(out)


def silhouette_samples(D, labels):
    """Silhouette s(i) of every point, as in tsc.validity.silhouette_from_matrix."""
    labels = np.asarray(labels)
    out = []
    for i in range(len(labels)):
        own = labels == labels[i]
        own[i] = False
        if not own.any():
            out.append(0.0)
            continue
        a = D[i, own].mean()
        b = min(D[i, labels == c].mean() for c in np.unique(labels) if c != labels[i])
        out.append(0.0 if a == b == 0 else (b - a) / max(a, b))
    return np.array(out)


def contingency(a, b):
    """Contingency table of two labellings, rows and columns in order of first appearance."""
    ra, rb = list(dict.fromkeys(a.tolist())), list(dict.fromkeys(b.tolist()))
    return np.array([[int(((a == p) & (b == q)).sum()) for q in rb] for p in ra]), ra, rb


def pair_counts(a, b):
    """Numbers of pairs: together in both, only in a, only in b, apart in both."""
    n = len(a)
    ss = sd = ds = dd = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_a, same_b = a[i] == a[j], b[i] == b[j]
            ss += same_a and same_b
            sd += same_a and not same_b
            ds += same_b and not same_a
            dd += not same_a and not same_b
    return int(ss), int(sd), int(ds), int(dd)


def adjusted_rand(a, b):
    """Hubert and Arabie's adjusted Rand index from the contingency table."""
    table, _, _ = contingency(a, b)
    comb = lambda v: v * (v - 1) / 2
    t = comb(table).sum()
    x, y = comb(table.sum(axis=1)).sum(), comb(table.sum(axis=0)).sum()
    m = comb(table.sum())
    e = x * y / m
    return float((t - e) / (0.5 * (x + y) - e))


def average_merges(D):
    """Average-linkage merge matrix of scipy: rows (left, right, height, size)."""
    return linkage(squareform(D, checks=False), method="average")
