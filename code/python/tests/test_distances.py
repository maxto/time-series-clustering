"""Tests for tsc.distances.

Expected values come from hand computations, literals, or independent
packages (dtw-python for DTW, aeon for SBD), never from the code under test.
"""

import csv
import itertools
import math
from pathlib import Path

import numpy as np
import pytest
from dtw import dtw as dtw_python
from dtw import symmetric1
from aeon.distances import sbd_distance

from tsc.distances import dtw, dtw_path, euclidean, sbd, znorm

FIXTURE = Path(__file__).parents[3] / "fixtures" / "demand-12.csv"


def fixture_series():
    """The 12 fixture rows as float arrays (the loader lives in tsc.group)."""
    with open(FIXTURE, newline="") as f:
        return [np.array([float(r[k]) for k in r if k.startswith("v")])
                for r in csv.DictReader(f)]


def fixture_pairs():
    return list(itertools.combinations(fixture_series(), 2))


def test_dtw_hand_cases():
    # path (0,0),(1,1),(1,2),(2,3), admissible for w >= 1, cost 0
    assert dtw([0, 1, 2], [0, 1, 1, 2]) == 0.0
    # only path (0,0),(1,0): cost 1 + 1
    assert dtw([0, 2], [1]) == pytest.approx(math.sqrt(2))


def test_euclidean_and_znorm_literals():
    assert euclidean([0, 0], [3, 4]) == 5.0
    assert np.allclose(znorm([1, 2, 3]), [-1.224744871391589, 0, 1.224744871391589])


@pytest.mark.parametrize("w", [0, 4, None])
def test_dtw_matches_dtw_python(w):
    window = {} if w is None else {"window_type": "sakoechiba",
                                   "window_args": {"window_size": w}}
    for a, b in fixture_pairs():
        cost = (a[:, None] - b[None, :]) ** 2
        ref = dtw_python(cost, step_pattern=symmetric1, **window)
        assert dtw(a, b, w) == pytest.approx(math.sqrt(ref.distance), rel=1e-12)


def test_sbd_matches_aeon():
    for a, b in fixture_pairs():
        za, zb = znorm(a), znorm(b)
        assert sbd(za, zb) == pytest.approx(
            sbd_distance(za, zb, standardize=False), abs=1e-9)


# A. DTW inputs
def test_dtw_rejects_bad_inputs():
    with pytest.raises(ValueError):
        dtw([], [1])
    with pytest.raises(ValueError):
        dtw([float("nan"), 1], [1, 2])
    with pytest.raises(ValueError):
        dtw([0, 1], [0, 1], w=-1)
    with pytest.raises(ValueError):
        dtw([0, 1], [0, 1], w=1.5)


def test_dtw_no_admissible_path():
    with pytest.raises(ValueError):
        dtw([0, 1, 2, 3, 4], [0, 1], w=1)


def test_dtw_unequal_lengths_no_window():
    assert dtw([0, 2], [1]) == pytest.approx(math.sqrt(2))
    assert dtw([0, 2], [1], w=1) == pytest.approx(math.sqrt(2))


# B. DTW path structure (invariants, not independent values)
def test_dtw_path_structure():
    a, b = fixture_pairs()[0]
    path = dtw_path(a, b, 4)
    assert path[0] == (0, 0)
    assert path[-1] == (len(a) - 1, len(b) - 1)
    for (i0, j0), (i1, j1) in zip(path, path[1:]):
        assert (i1 - i0, j1 - j0) in {(1, 0), (0, 1), (1, 1)}
    assert all(abs(i - j) <= 4 for i, j in path)
    total = sum((a[i] - b[j]) ** 2 for i, j in path)
    assert math.sqrt(total) == pytest.approx(dtw(a, b, 4), rel=1e-12)


# C. SBD
def test_sbd_rejects_zero_norm():
    with pytest.raises(ValueError):
        sbd([0, 0, 0], [1, 2, 3])


def test_sbd_delayed_pulse():
    bump = [1.0, 3.0, 2.0, 0.5]  # deliberately not symmetric
    early = np.array([0.0] * 40 + bump + [0.0] * 40)
    late = np.roll(early, 6)  # stays inside the zero margin
    assert sbd(early, late) == pytest.approx(0, abs=1e-12)
