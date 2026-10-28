"""Tests for tsc.validity.

Expected values come from hand computations and scikit-learn's silhouette.
"""

import numpy as np
import pytest
from sklearn.metrics import silhouette_score

from tsc.distances import dtw
from tsc.group import average_linkage, distance_matrix, load_demand
from tsc.validity import check_dissimilarity, silhouette_from_matrix


def test_silhouette_hand_case():
    # point 0: a=2, b=4 -> 1/2. point 1: a=2, b=6 -> 2/3. point 2: singleton -> 0.
    D = np.array([[0, 2, 4], [2, 0, 6], [4, 6, 0]], dtype=float)
    labels = np.array([0, 0, 1])
    assert silhouette_from_matrix(D, labels) == pytest.approx(7 / 18)


def test_silhouette_matches_sklearn():
    _, X, _ = load_demand()
    D = distance_matrix(X, lambda a, b: dtw(a, b, 4))
    labels = average_linkage(D, 2)
    expected = silhouette_score(D, labels, metric="precomputed")
    assert silhouette_from_matrix(D, labels) == pytest.approx(expected, abs=1e-12)


def test_silhouette_all_zero_matrix():
    assert silhouette_from_matrix(np.zeros((3, 3)), np.array([0, 0, 1])) == 0.0


GOOD = np.array([[0, 2, 4], [2, 0, 6], [4, 6, 0]], dtype=float)
OK_LABELS = np.array([0, 0, 1])


def test_good_input_has_no_problems():
    assert check_dissimilarity(GOOD, OK_LABELS) == []


def bad_nan():
    D = GOOD.copy(); D[0, 1] = D[1, 0] = np.nan
    return D, OK_LABELS


def bad_asymmetric():
    D = GOOD.copy(); D[0, 1] = 3.0
    return D, OK_LABELS


def bad_diagonal():
    D = GOOD.copy(); D[1, 1] = 0.5
    return D, OK_LABELS


def bad_negative():
    D = GOOD.copy(); D[0, 2] = D[2, 0] = -1.0   # soft-DTW-like
    return D, OK_LABELS


@pytest.mark.parametrize("make, keyword", [
    (bad_nan, "not finite"),
    (bad_asymmetric, "not symmetric"),
    (bad_diagonal, "diagonal"),
    (lambda: (np.zeros((2, 3)), np.array([0, 1])), "not square"),
    (bad_negative, "negative"),
    (lambda: (GOOD, np.array([0, 0, 0])), "clusters"),
    (lambda: (GOOD, np.array([0, 1, 2])), "clusters"),
    (lambda: (GOOD, np.array([0, 1])), "label count"),
])
def test_invalid_matrices_rejected(make, keyword):
    D, labels = make()
    problems = check_dissimilarity(D, labels)
    assert any(keyword in p for p in problems), problems
    with pytest.raises(ValueError):
        silhouette_from_matrix(D, labels)
