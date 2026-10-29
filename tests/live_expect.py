"""Expected state of a live figure, from its data file and the reference package only.

Usage: uv run python tests/live_expect.py <file.live.json> <pair-index> <w|none> [<pair-index> <w|none> ...]

Prints a JSON list with one object per requested state: the pair, w, the band cells [i, j]
(row i is series A from the bottom, column j series B from the left), the opacity of each
cell at 2 decimals (same order), the warping path, the kept link steps (path steps k with k
even or k the last step), both distances at 2 decimals, and the two series. It is written from
the geometry contract in AGENTS.md and tsc.distances, never from a figure.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code" / "python"))

from tsc.distances import dtw, dtw_path, euclidean  # noqa: E402


def state(data, pair, w):
    na, nb = data["pairs"][pair]
    a, b = data["series"][na], data["series"][nb]
    n = len(a)
    reach = n if w is None else w
    cells = [[i, j] for i in range(n) for j in range(n) if abs(i - j) <= reach]
    costs = [(a[i] - b[j]) ** 2 for i, j in cells]
    cmax = max(costs)
    opacity = [round(0.12 + 0.78 * (math.sqrt(c / cmax) if cmax > 0 else 0.0), 2) for c in costs]
    path = [list(step) for step in dtw_path(a, b, w)]
    links = [k for k in range(len(path)) if k % 2 == 0 or k == len(path) - 1]
    return {"pair": [na, nb], "w": w, "n": n, "cells": cells, "opacity": opacity, "path": path, "links": links,
            "euclidean": f"{euclidean(a, b):.2f}", "dtw": f"{dtw(a, b, w):.2f}", "series": {na: a, nb: b}}


def main(argv):
    if len(argv) < 4 or len(argv) % 2 != 0:
        raise SystemExit(__doc__)
    data = json.loads(Path(argv[1]).read_text())
    states = []
    for k in range(2, len(argv), 2):
        states.append(state(data, int(argv[k]), None if argv[k + 1] == "none" else int(argv[k + 1])))
    print(json.dumps(states))


if __name__ == "__main__":
    main(sys.argv)
