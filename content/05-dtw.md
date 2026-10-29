---
id: dtw
module: B
title: Elastic: DTW and its window
kicker: Compare sequences
sector: energy
lede: Dynamic time warping lets one series run a little early or late against another before it measures the gap. How much timing it forgives is a choice you make, through the window.
ignores: local timing within the window
keeps: level, scale, order of events, timing beyond the window
python: dtaidistance, tslearn.metrics.dtw, aeon.distances.dtw_distance, dtw-python
r: dtw::dtw, dtwclust::dtw_basic
---

## One line

DTW compares two series after letting their time axes stretch locally, and the window $w$ says *how far* the stretch may go: that window is the real decision, not a detail.

## When timing shifts

The Euclidean distance of [lesson 1](lesson:same-series-different-questions) lines up half hour $i$ of one day with half hour $i$ of the other. If the same profile happens an hour and a half later, the peaks miss each other and the distance is large, even though the two days look alike.

Dynamic time warping (DTW) is the main member of the elastic family. It lets one sample of a series match several samples of the other, as long as the order of events is kept. It then measures the gap along the best of these alignments.

## Two days, one shift

In the fixture, `mon` and `sat` have the same two-peak profile. The peaks of `sat` come 1.5 hours later, three samples, and each day has its own small noise. This pair was authored to show what warping does: the shift was built in, and it fits inside the window used below.

![mon (ink) and sat (accent), linked sample by sample (top) and along the DTW path with w = 4 (bottom). Every second link is drawn](figures/lockstep-vs-dtw.svg)

In the top panel each sample of `mon` is linked to the sample of `sat` at the same half hour. Around the peaks the links join a high value to a low one. The Euclidean distance is {{n:euclid_mon_sat}}.

In the bottom panel the links lean: each peak of `mon` is matched with the later peak of `sat`. The DTW distance with a window of $w = 4$ samples is {{n:dtw4_mon_sat}}. DTW divided by Euclidean is {{n:ratio_mon_sat}}.

That ratio is this pair's result, not a promise. For two series of the same length, DTW is never larger than the Euclidean distance under this course's convention, because the straight lock-step path is always one of the allowed alignments. How much smaller it gets depends on the pair. Here it is small because the only real difference between the two days is a shift that the window can absorb.

## What DTW aligns

An alignment, or warping path, is a list of pairs $(i, j)$: sample $i$ of the first series is matched with sample $j$ of the second. DTW picks the path with the smallest total cost. Four rules define it, and each one is a choice that changes the numbers.

- **Local cost.** Each matched pair costs $(x_i - y_j)^2$, the squared difference. The path's cost is the sum over its pairs.
- **Closed endpoints.** The path starts at the first samples, $(0, 0)$, and ends at the last ones, $(n-1, m-1)$. Every sample of both series is matched at least once. Nothing at the start or the end can be skipped.
- **Three steps.** From $(i, j)$ the path moves to $(i+1, j)$, $(i, j+1)$ or $(i+1, j+1)$: forward in one series, in the other, or in both. It never moves back, so the order of events is kept. The three steps carry no weights.
- **The window.** The path may only use cells with $|i - j| \le w$, the band of [Sakoe and Chiba (1978)](https://doi.org/10.1109/TASSP.1978.1163055). In this course $w = 4$ samples, two hours at half-hour sampling.

The distance is the square root of the smallest total cost. There is no length normalisation: the total is a sum over the path, not divided by the path length or by $n + m$.

The best path does not need a search over every possible path. A dynamic programme fills a table of partial costs one cell at a time, as the measure card below shows.

Libraries do not share one convention. On this pair, `aeon.distances.dtw_distance` returns the total cost before the square root, and `dtw-python` by default uses absolute differences and a step pattern that counts a diagonal step twice. Check the local cost, the steps, the window, the root and any normalisation before you compare DTW numbers from two sources.

## The window is a decision

The window says how much local timing you are willing to ignore. It is not a speed trick to tune away at the end.

A window too narrow forbids alignments you want. For equal-length series, with $w = 0$ the only allowed path is the diagonal, and DTW is the Euclidean distance again. With a window smaller than the three-sample shift of `sat`, the peaks cannot be fully matched.

A window too wide allows alignments you do not want. With no window, a peak at 08:00 may be matched with a peak at 13:00, and a day busy in the morning can look close to a day busy at midday. That is exactly the difference question A of lesson 1 wanted to keep.

So the window comes from the question, in the units of the data. "Demand may run up to two hours early or late and still count as the same day" means $w = 4$ at half-hour sampling. The same rule on hourly data is $w = 2$. When the two series differ in length, the window must be at least the difference in length, or no path from start to end exists.

## Reading the cost grid

![The cost grid of mon against sat: only the band |i − j| ≤ 4 is drawn, opacity shows the local squared cost, the line is the DTW path](figures/dtw-window.svg)

This figure shows the table DTW works on. Each cell is one pair $(i, j)$.

- The rows are the samples of `mon`, drawn along the left edge with time running upward. The columns are the samples of `sat`, drawn below.
- Only the band $|i - j| \le 4$ is drawn. Outside it DTW never computes a cost.
- The opacity of a cell shows its local cost $(x_i - y_j)^2$: the more opaque the cell, the larger the gap. It is not the accumulated cost. The shading follows the square root of the cost, so small differences stay visible.
- The dashed diagonal is lock-step matching. The solid line is the DTW path, from the bottom-left corner to the top-right one.

Across the peaks the path runs three columns to the right of the diagonal: `mon` at half hour $i$ is matched with `sat` at half hour $i + 3$, the 1.5-hour shift. In the flat night hours it also moves a sample or two off the diagonal. There every match costs little, so these small detours follow the noise and mean nothing.

## The twelve days under DTW

The same distance, applied to every pair of the twelve days, gives a 12 by 12 matrix. Average linkage cut at two groups, the rule of lesson 1, then splits the days.

![The 12 by 12 DTW matrix with w = 4, ordered by group. Higher opacity means a smaller distance](figures/dtw-matrix.svg)

The two groups are the six early days and the six late days, the same split as question A in lesson 1. Across groups the gap of five hours is larger than the two-hour window, so DTW still sees it. Inside a group, days that differ in base level or in size stay at a clear distance: `tue` is much farther from `mon` than `sat` is. DTW forgives timing within the window, not level or scale.

This is the window doing its job, not a failure of DTW. A window of two hours says that a five-hour gap is a real difference. If your question says otherwise, the window, or the measure, has to change, and that change has to be argued from the question.

## Soft-DTW, a short extension

DTW takes a hard minimum over paths, so it is not differentiable everywhere. [Cuturi and Blondel (2017)](https://arxiv.org/abs/1703.01541) replace the minimum with a soft minimum controlled by a smoothing parameter $\gamma > 0$. This smooths the accumulated cost, without the final square root used for our DTW distance. The result, soft-DTW, can be used as a loss and for averaging and clustering under the DTW geometry.

There is a catch for clustering checks. Raw soft-DTW values can be negative, and the value is not smallest when the two series are equal ([Blondel, Mensch and Vert, 2021](https://arxiv.org/abs/2010.08354)). Their soft-DTW divergence subtracts self-comparison terms, giving zero for identical series. Its guarantees depend on the ground cost, so check the assumptions and the resulting matrix before scoring. A raw soft-DTW matrix is therefore not a dissimilarity matrix you can hand to a validity index, as the check below shows.

## Can the groups be scored?

Each validity index answers three questions: can it be computed on this input, what geometry does it assess, and does that geometry answer your question?

**Silhouette on the DTW matrix: admissible.** The [silhouette of Rousseeuw (1987)](https://doi.org/10.1016/0377-0427(87)90125-7) needs only a dissimilarity matrix. The DTW matrix with $w = 4$ passes every check of `check_dissimilarity` in `code/python/tsc/validity.py`: square, finite, non-negative, symmetric, zero diagonal, and $k = 2$ lies between 2 and $n - 1 = 11$. The triangle inequality is not required. A singleton receives silhouette zero. For the two groups of average linkage, the mean silhouette is {{n:silhouette_dtw4_k2}}.

**Caliński-Harabasz: not on this matrix.** The standard index of [Caliński and Harabasz (1974)](https://doi.org/10.1080/03610927408827101) needs a vector space with centroids: it compares the spread of the group centroids with the spread of points around them. It cannot read a precomputed DTW matrix. Feeding the matrix rows as if they were vectors does give a number, but for a different geometry: Euclidean distances between distance profiles, not DTW.

**Raw soft-DTW: rejected before scoring.** A matrix with a negative entry, which raw soft-DTW can produce, fails the non-negativity check, so `silhouette_from_matrix` raises an error instead of returning a score.

The last question stays open. The silhouette of {{n:silhouette_dtw4_k2}} says how well the two groups separate under DTW with $w = 4$. It does not say that DTW was the right distance. A higher silhouette under one distance does not prove that distance is better than another: each score is measured in its own geometry.

## In finance

Our finance example asks about contemporaneous co-movement: do two assets move together on the same dates? Warping the returns would match one asset's day with another asset's different day, and that destroys the simultaneity the question is about. Compare assets on the same dates, for instance with the correlation of their returns. A DTW match between two return series is not a trading signal.

## Measure card

DTW with window $w$ between a series $x$ of length $n$ and a series $y$ of length $m$, indexed from 0 as in the course code. Local cost:

$$
c(i, j) = (x_i - y_j)^2
$$

Start, closed at the first samples:

$$
D(0, 0) = c(0, 0)
$$

Recurrence, for every other cell inside the window $|i - j| \le w$, with $p$, $q$, $r$ the three ways in:

$$
\begin{aligned}
D(i, j) &= c(i, j) + \min\{p, q, r\} \\
p &= D(i-1, j) \\
q &= D(i, j-1) \\
r &= D(i-1, j-1)
\end{aligned}
$$

A cell outside the window, or with a negative index, counts as $D = \infty$. End, closed at the last samples, then the square root, with no normalisation:

$$
\mathrm{DTW}_w(x, y) = \sqrt{D(n-1, m-1)}
$$

With no window the table has $n m$ cells. With the window only the band is filled, at most $(2w + 1)$ cells per row. Reference code: `dtw` and `dtw_path` in `code/python/tsc/distances.py`, `dtw_distance` in `code/r/distances.R`.

## Code

```python
import csv
from tsc.distances import dtw, euclidean

with open("fixtures/demand-12.csv") as f:
    rows = {r["id"]: [float(r[f"v{i:02d}"]) for i in range(48)] for r in csv.DictReader(f)}

mon, sat = rows["mon"], rows["sat"]
print(round(euclidean(mon, sat), 2), round(dtw(mon, sat, w=4), 2))
```

```r
source("code/r/distances.R")

d <- read.csv("fixtures/demand-12.csv", row.names = "id")
cols <- sprintf("v%02d", 0:47)
mon <- as.numeric(d["mon", cols])
sat <- as.numeric(d["sat", cols])
cat(round(euclidean(mon, sat), 2), round(dtw_distance(mon, sat, w = 4), 2), "\n")
```

## Common mistake

Running DTW with no window, or with whatever window a library uses by default, and calling the result "shape similarity". The window sets how much timing is ignored: decide it from the question, in samples, and report it with the distance.
