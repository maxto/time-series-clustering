"""Tests for tsc.group and the fixture's authored properties.

Expected values come from the fixture's design (declared groups), hand
computations, or ARI as an independent scorer (scikit-learn).
"""

import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score

from tsc.distances import dtw, euclidean, sbd, znorm
from tsc.group import average_linkage, distance_matrix, load_demand

ids, X, groups = load_demand()


def test_question_a_recovers_hour_groups():
    """Question A (when does demand peak?): raw Euclidean, k=2."""
    labels = average_linkage(distance_matrix(X, euclidean), 2)
    assert adjusted_rand_score(groups["hour_group"], labels) == 1.0


def test_question_b_recovers_shape_groups():
    """Question B (what shape?): z-normalisation plus SBD, k=2."""
    Z = np.array([znorm(x) for x in X])
    labels = average_linkage(distance_matrix(Z, sbd), 2)
    assert adjusted_rand_score(groups["shape_group"], labels) == 1.0


def test_the_two_questions_disagree():
    assert adjusted_rand_score(groups["hour_group"], groups["shape_group"]) < 0.2


def test_mon_sat_pair():
    """This pair's result in the fixture, not a general DTW guarantee."""
    mon, sat = X[ids.index("mon")], X[ids.index("sat")]
    assert dtw(mon, sat, w=4) < 0.5 * euclidean(mon, sat)


def test_average_linkage_too_few_clusters():
    # 4 identical series: all distances 0, maxclust gives one cluster
    with pytest.raises(ValueError):
        average_linkage(np.zeros((4, 4)), 2)
    # 3 points with distinct distances and k=3: every point alone
    D = np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]], dtype=float)
    assert sorted(average_linkage(D, 3)) == [0, 1, 2]


def test_average_linkage_labels_are_zero_based_first_appearance():
    # points 0 and 2 are close, point 1 is far: first point gets label 0
    D = np.array([[0, 9, 1], [9, 0, 9], [1, 9, 0]], dtype=float)
    assert list(average_linkage(D, 2)) == [0, 1, 0]
