"""Parity of site/kernels.js with the Python reference (tsc.distances).

Expected values are computed by the Python reference in this process. The
JavaScript values come from a separate `node tests/kernels_cli.mjs` process.
The hand cases (ties) are computed on paper.
"""

import itertools
import json
import pathlib
import subprocess

import pytest

from tsc.distances import dtw, dtw_path, euclidean
from tsc.group import load_demand

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLI = ROOT / "tests" / "kernels_cli.mjs"
TOL = 1e-9

ids, X, _ = load_demand()
SERIES = {name: X[k].tolist() for k, name in enumerate(ids)}


def run_cli(cases):
    """Run the cases through node. Assert exit 0 and one result per case."""
    proc = subprocess.run(["node", str(CLI)], input=json.dumps(cases), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    results = json.loads(proc.stdout)
    assert len(results) == len(cases)
    return results


def case(op, x, y, w=None):
    return {"op": op, "x": x, "y": y, "w": w}


def test_fixture_rows_parity():
    pairs = list(itertools.combinations(ids, 2))
    assert len(pairs) == 66
    cases, expected = [], []
    for a, b in pairs:
        x, y = SERIES[a], SERIES[b]
        cases += [case("dtw", x, y, 4), case("euclidean", x, y)]
        expected += [dtw(x, y, 4), euclidean(x, y)]
    for res, exp in zip(run_cli(cases), expected):
        assert abs(res["value"] - exp) <= TOL


PAIRS = [("mon", "sat"), ("mon", "wed")]
WINDOWS = list(range(13)) + [None]


def test_reachable_states_parity():
    cases, expected = [], []
    for a, b in PAIRS:
        x, y = SERIES[a], SERIES[b]
        for w in WINDOWS:
            cases += [case("dtw", x, y, w), case("dtwPath", x, y, w)]
            expected += [dtw(x, y, w), [list(p) for p in dtw_path(x, y, w)]]
    assert len(cases) == 56
    for c, res, exp in zip(cases, run_cli(cases), expected):
        if c["op"] == "dtw":
            assert abs(res["value"] - exp) <= TOL
        else:
            assert res["value"] == exp


@pytest.mark.parametrize("pair, rounded", [(("mon", "sat"), 3.71), (("mon", "wed"), 4.15)])
def test_window_zero_is_euclidean(pair, rounded):
    x, y = SERIES[pair[0]], SERIES[pair[1]]
    d, p = run_cli([case("dtw", x, y, 0), case("dtwPath", x, y, 0)])
    assert abs(d["value"] - euclidean(x, y)) <= TOL
    assert round(d["value"], 2) == rounded
    assert p["value"] == [[i, i] for i in range(len(x))]


@pytest.mark.parametrize("pair, rounded", [(("mon", "sat"), 0.22), (("mon", "wed"), 0.26)])
def test_no_window(pair, rounded):
    x, y = SERIES[pair[0]], SERIES[pair[1]]
    d, p = run_cli([case("dtw", x, y, None), case("dtwPath", x, y, None)])
    assert abs(d["value"] - dtw(x, y, None)) <= TOL
    assert round(d["value"], 2) == rounded
    assert p["value"] == [list(q) for q in dtw_path(x, y, None)]


def test_ties_hand_cases():
    res = run_cli([
        case("dtwPath", [0, 0], [0, 0], None),
        case("dtwPath", [0, 0], [0, 0], 0),
        case("dtwPath", [0, 0, 0], [0, 0], None),
    ])
    assert res[0]["value"] == [[0, 0], [1, 1]]
    assert res[1]["value"] == [[0, 0], [1, 1]]
    assert res[2]["value"] == [[0, 0], [1, 0], [2, 1]]


def test_invalid_inputs():
    nan, inf = {"special": "NaN"}, {"special": "Infinity"}
    cases = [
        case("dtw", [], [1], None),
        case("dtw", [nan], [1], None),
        case("dtw", [1], [inf], None),
        case("dtw", [1, 2], [1, 2], -1),
        case("dtw", [1, 2], [1, 2], 1.5),
        case("dtw", [1, 2, 3], [1, 2], 0),
        case("euclidean", [1, 2, 3], [1, 2]),
    ]
    for res in run_cli(cases):
        assert res["error"].startswith("invalid:")


def test_transport_failure():
    proc = subprocess.run(["node", str(CLI)], input=json.dumps([case("sbd", [1], [1])]), capture_output=True, text=True)
    assert proc.returncode == 2
    assert proc.stdout == ""
