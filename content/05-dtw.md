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

DTW compares two series after letting their time axes stretch locally, and the window $w$ sets how far the stretch may go: that window is the real decision.

## What it measures

Euclidean distance matches sample $i$ of one series with sample $i$ of the other, so the same profile an hour and a half later gives a large distance. DTW instead finds the alignment with the smallest cost, under which one sample may match several samples of the other series, as long as the order of events is kept. The classic reference is [Sakoe and Chiba (1978)](https://doi.org/10.1109/TASSP.1978.1163055).

![mon (ink) and sat (accent), linked sample by sample (top) and along the DTW path with w = 4 (bottom). Every second link is drawn](figures/lockstep-vs-dtw.svg)

In the fixture, an authored demonstration, `mon` and `sat` share a two-peak profile and the peaks of `sat` come three samples later. Euclidean distance is {{n:euclid_mon_sat}}, DTW with $w = 4$ is {{n:dtw4_mon_sat}}. That ratio is this pair's result, not a promise: the two days differ almost only by a shift that fits in the window.

## When to use it

Use it when:

- The same events occur in the same order, locally early or late: daily load profiles, gait cycles, heartbeats.
- Level and scale are comparable, or you z-normalise first. DTW forgives timing, not level or scale.
- Sampling is regular. Lengths may differ if $w$ is at least the difference in length.

Avoid it when:

- The date itself matters, so a match across different dates is wrong.
- The whole series is shifted by one constant lag. A sliding measure such as SBD handles that at lower cost.
- Events may occur in a different order. DTW keeps the order.
- The set is large and the window is wide. Each pair fills up to $n(2w + 1)$ cells, and $N$ series give $N(N-1)/2$ pairs.

## Definition

An alignment, or warping path, is a list of pairs $(i, j)$ that starts at $(0, 0)$, ends at $(n-1, m-1)$ and moves by $(1, 0)$, $(0, 1)$ or $(1, 1)$, with no weights. Each pair costs the squared difference:

$$
c(i, j) = (x_i - y_j)^2
$$

A dynamic programme fills the table of smallest accumulated costs, inside the window $|i - j| \le w$. Cells outside it, or with a negative index, count as $\infty$:

$$
\begin{aligned}
D(0, 0) &= c(0, 0) \\
D(i, j) &= c(i, j) + \min\{D(i-1, j),\ D(i, j-1),\ D(i-1, j-1)\}
\end{aligned}
$$

The distance is the square root of the last cell, with no length normalisation, so that $w = 0$ gives back the Euclidean distance for equal lengths:

$$
\mathrm{DTW}_w(x, y) = \sqrt{D(n-1, m-1)}
$$

::: deep Libraries count differently
Two libraries can return different numbers for the same pair. In `aeon`, `dtw_distance` returns the accumulated squared cost, with no square root, and its `window` is a fraction of the series length, not a number of samples. The Python package `dtw` by default uses the absolute difference and the `symmetric2` step pattern, where a diagonal step counts twice. Check the local cost, the steps, the window, the root and any normalisation before you compare DTW numbers from two sources.
:::

## The window

The band $|i - j| \le w$ is the adjustment window of Sakoe and Chiba. It states how much local timing you are willing to ignore, so it comes from the question, in the units of the data: "up to two hours early or late" means $w = 4$ at half-hour sampling and $w = 2$ on hourly data.

![Try it: choose a pair of days, move the window, or remove it. Top: the two days linked along the DTW path. Bottom: the cost grid, the band |i − j| ≤ w and the path](figures/dtw-explorer.svg)

Start with `mon` and `sat` and move the window up from 0. At $w = 0$ the distance is the Euclidean one, {{n:euclid_mon_sat}}, and at $w = 4$ it is {{n:dtw4_mon_sat}}. A wider window only adds paths, so the distance never grows.

Then choose `mon` and `wed`, whose peaks are ten samples apart. At $w = 4$ DTW is {{n:dtw4_mon_wed}}, near their Euclidean {{n:euclid_mon_wed}}: the window refuses the shift. At $w = 10$ it falls to {{n:dtw10_mon_wed}}, the same as with no window at all ({{n:dtwnone_mon_wed}}), and a morning day looks like a midday day. Too narrow forbids alignments you want, too wide allows those you do not.

::: deep Reading the cost grid
The lower part of the figure is the table DTW works on. Each cell is one pair $(i, j)$.

- Rows are the samples of the first day, with time running upward. Columns are the samples of the second day.
- Only the band is drawn. Outside it DTW never computes a cost.
- Opacity shows the local cost, not the accumulated one, on a square-root scale so that small gaps stay visible.
- The dashed diagonal is lock-step matching. The solid line is the DTW path.

For `mon` and `sat` at $w = 4$, across the peaks the path runs three columns right of the diagonal, the 1.5-hour shift. In the flat night hours it moves a sample or two off the diagonal. There every match costs little, so these detours follow the noise.
:::

## Which clustering algorithm

DTW gives a pairwise distance matrix and no natural centroid. It is also not a metric, since the triangle inequality can fail. That decides the options:

- **Agglomerative hierarchical.** Needs only the matrix, with single, complete or average linkage. Ward's criterion is defined for Euclidean geometry, so on a DTW matrix software will run it without that meaning.
- **k-medoids.** Works on any dissimilarity matrix, and each centre is a real series (Kaufman and Rousseeuw, 1990).
- **k-means.** The arithmetic mean is not a centre under DTW, so it needs a DTW-consistent average such as DBA ([Petitjean, Ketterlin and Gançarski, 2011](https://doi.org/10.1016/j.patcog.2010.09.013)).
- **DBSCAN.** Runs on a precomputed matrix (Ester et al., 1996), with its radius set on the DTW scale.
- **k-Shape.** Not a match: it is built on SBD (Paparrizos and Gravano, 2015).

![The 12 by 12 DTW matrix with w = 4, ordered by group. Higher opacity means a smaller distance](figures/dtw-matrix.svg)

On the twelve fixture days, average linkage cut at two groups splits the six early days from the six late ones. The five-hour gap between groups is wider than the two-hour window, so DTW still sees it. Inside a group, `tue` stays farther from `mon` than `sat` does, because it differs in level and scale.

## In finance

DTW addresses lead-lag structure and similarity of shape across time. It is not a measure of contemporaneous dependence, since warping pairs observations from different dates. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Statistical arbitrage.** [Stübinger (2019)](https://doi.org/10.1080/14697688.2018.1537503) selects lead-lag pairs of S&P 500 constituents on minute data through a causal variant of the warping path, and trades the follower on the leader. Reported returns after assumed costs decline sharply after 2009.
- **Lead-lag in factor models.** [Zhang et al. (2023)](https://arxiv.org/abs/2309.08800) detect lead-lag clusters in daily returns of 679 US equities. Sharpe ratios are modest, moderately above a cross-correlation baseline, and gross of costs.
- **Portfolio diversification.** [Lim and Ong (2021)](https://doi.org/10.3905/jfds.2020.1.054) apply agglomerative clustering with DTW to group stocks into like-trending clusters, as an input to allocation and stock selection.
- **Chart pattern recognition.** [Tsinaslanidis (2018)](https://doi.org/10.1016/j.eswa.2017.10.055) labels NYSE price and volume sequences by subsequence DTW against historical patterns. Out of sample, only the bearish predictions are significant.
- **Price discovery.** [Vatsa, Miljkovic and Miljkovic (2024)](https://doi.org/10.1016/j.eneco.2024.107965) test whether crude oil and natural gas futures lead spot prices, and find that the leading market varies over time.
- **Market integration.** Gronwald and Zhu (2026) cluster ten spot crude oil grades on z-normalised prices in a rolling window.
- **ETF classification.** Chen, Lim and Kam (2021) cluster 143 Chinese ETFs hierarchically and recover groups that largely follow industry type.
- **Regime-based allocation.** [Alexander, Scherer and Thompson (2026)](https://arxiv.org/abs/2604.03946) use DTW to define market states in a Markov allocation model. Their reported gain is smallest on the mutual fund universe.

Limitations in financial time series:

- **Volatility regime.** On equity indices, DTW similarity increases in high-volatility periods and decreases in low-volatility ones ([Tsinaslanidis et al., 2014](https://kar.kent.ac.uk/43498)), so a similarity reading depends on the regime in which it is measured.
- **Normalisation.** Meaningful comparison requires both series to be normalised, and each subsequence must be normalised on its own: normalising the whole dataset is not sufficient ([Rakthanmanon et al., 2012](https://doi.org/10.1145/2339530.2339576)). The result comes from general time series benchmarks, not from financial data.
- **Warping window.** On classification benchmarks, accuracy peaks at small windows and wider constraints do not improve it ([Ratanamahatana and Keogh, 2004](https://www.cs.ucr.edu/~eamonn/DTW_myths.pdf)). The evidence is not specific to finance.
- **Subsequence clustering.** Clusters of subsequences extracted by a sliding window are essentially random, as shown also on S&P 500 closing values ([Keogh and Lin, 2005](https://doi.org/10.1007/s10115-004-0172-7)). The result does not apply to clustering whole series.
- **Backtest overfitting.** The higher the number of configurations tried, the greater the probability that a backtest is overfit, and analysts rarely report that number ([Bailey et al., 2014](https://doi.org/10.1090/noti1105)). Window, normalisation and number of clusters are all such configurations.

## Common mistake

Running DTW with no window, or with whatever window a library uses by default, and calling the result "shape similarity". The window sets how much timing is ignored: decide it from the question, in samples, and report it with the distance.
