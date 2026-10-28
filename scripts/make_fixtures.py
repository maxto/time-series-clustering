"""Generate fixtures/demand-12.csv, the pilot fixture of the course.

The fixture is an authored demonstration. It is built so that two sensible
questions ("which days happen at similar hours?" and "which days have a
similar shape?") get two different answers, and it is NOT evidence that any
method performs well on real data. The CSV is the source of truth: the seed
below only documents how it was made, and the file is frozen once the
Task 3 checks pass.

Design: 2 shapes x 2 timings x 3 variants = 12 rows.
Unit: kW, an illustrative scale, the same for both shapes. 48 half-hour
samples, v00 = 00:00, v47 = 23:30. Four decimals.

Run: uv run python scripts/make_fixtures.py
"""

from pathlib import Path

import numpy as np

SEED = 20261028
T = np.arange(48) / 2.0  # hours since midnight, one value per half hour

# Timing: the centre of the active period. Early and late are 5 hours apart
# (inside the 4 to 6 hour range) so that raw Euclidean distance separates the
# timing groups, while a shift of this size is still small enough for each
# series to stay inside the 24 hour day.
CENTRE = {"early": 8.0, "late": 13.0}


def bump(centre, width):
    return np.exp(-0.5 * ((T - centre) / width) ** 2)


def twopeak(centre, shift=0.0):
    """Residential: two narrow peaks 4 h apart around `centre`, low base.

    Peak width 0.8 h (sigma) is about 1.6 samples, wide enough that a
    1.5 h (3 sample) displacement is within the course DTW window of
    4 samples and can be absorbed by warping.
    """
    return (
        0.4
        + 1.6 * bump(centre - 2.0 + shift, 0.8)
        + 1.4 * bump(centre + 2.0 + shift, 0.8)
    )


def plateau(centre, shift=0.0):
    """Commercial: a flat-topped block of about 7 h with soft edges.

    Built as a difference of two logistic steps, so the top is flat (the
    opposite of the two-peak shape) and the edges are not instant.
    """
    c = centre + shift
    up = 1.0 / (1.0 + np.exp(-(T - (c - 3.5)) / 0.35))
    down = 1.0 / (1.0 + np.exp(-(T - (c + 3.5)) / 0.35))
    return 0.4 + 1.2 * (up - down)


SHAPES = {"twopeak": twopeak, "plateau": plateau}

# Variants per (shape, timing) cell: offset, scale, small timing change.
# (id, shape, timing, offset kW, scale, timing shift h, noise sd kW)
ROWS = [
    ("mon", "twopeak", "early", 0.00, 1.00, 0.0, 0.03),
    ("tue", "twopeak", "early", 0.25, 0.90, -0.5, 0.03),
    # sat: same shape and timing group as mon, peaks 1.5 h later.
    ("sat", "twopeak", "early", 0.00, 1.00, 1.5, 0.03),
    ("wed", "twopeak", "late", 0.00, 1.00, 0.0, 0.03),
    ("thu", "twopeak", "late", 0.25, 1.15, 0.5, 0.03),
    ("fri", "twopeak", "late", 0.10, 0.90, -0.5, 0.03),
    ("sun", "plateau", "early", 0.00, 1.00, 0.0, 0.03),
    ("d08", "plateau", "early", 0.25, 1.10, 0.5, 0.03),
    ("d09", "plateau", "early", 0.10, 0.90, -0.5, 0.03),
    ("d10", "plateau", "late", 0.00, 1.00, 0.0, 0.03),
    ("d11", "plateau", "late", 0.25, 0.90, 0.5, 0.03),
    ("d12", "plateau", "late", 0.10, 1.10, -0.5, 0.03),
]


def main():
    rng = np.random.default_rng(SEED)
    out = ["id,hour_group,shape_group," + ",".join(f"v{i:02d}" for i in range(48))]
    for rid, shape, timing, offset, scale, shift, noise in ROWS:
        base = SHAPES[shape](CENTRE[timing], shift)
        y = offset + scale * base + rng.normal(0.0, noise, 48)
        y = np.clip(y, 0.05, None)  # demand is never negative
        out.append(f"{rid},{timing},{shape}," + ",".join(f"{v:.4f}" for v in y))
    path = Path(__file__).resolve().parent.parent / "fixtures" / "demand-12.csv"
    path.write_text("\n".join(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
