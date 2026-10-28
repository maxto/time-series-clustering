"""Write the 12x12 DTW matrix (w = 4) of the demo fixture for the R parity check."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code" / "python"))

from tsc.distances import dtw  # noqa: E402
from tsc.group import distance_matrix, load_demand  # noqa: E402

OUT = ROOT / "tests" / "output" / "py-dtw-w4.csv"


def main():
    ids, X, _ = load_demand()
    D = distance_matrix(X, lambda a, b: dtw(a, b, 4))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", *ids])
        for name, row in zip(ids, D):
            writer.writerow([name, *(format(v, ".17g") for v in row)])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
