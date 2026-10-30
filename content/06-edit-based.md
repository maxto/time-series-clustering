---
id: edit-based
module: B
title: Edit-based: LCSS, EDR, ERP, MSM, TWE
kicker: Compare sequences
sector: industry
lede: Edit-based measures treat two series as sequences to be edited into each other. Matching, deleting and inserting points each carry a cost, and the way that cost is set decides what the measure forgives.
ignores: differences below the tolerance (LCSS, EDR), unmatched points (LCSS), local timing
keeps: order of events, level, scale
python: aeon.distances.lcss_distance, aeon.distances.edr_distance, aeon.distances.erp_distance, aeon.distances.msm_distance, aeon.distances.twe_distance, tslearn.metrics.lcss
r: TSdist::LCSSDistance, TSdist::EDRDistance, TSdist::ERPDistance
---

## One line

Edit-based measures compare two series by the cheapest sequence of match, delete and insert operations that turns one into the other, and the real decision is the tolerance or penalty that prices those operations.

## What it measures

DTW stretches the time axis. The edit view of the same idea says that a stretch is a gap, a point of one series left without a partner. The measures of this lesson differ in how they price a match and a gap. LCSS, from [Vlachos, Kollios and Gunopulos (2002)](https://doi.org/10.1109/ICDE.2002.994784), lets some points stay unmatched, where Euclidean distance and DTW must match every point, outliers included. EDR ([Chen, Özsu and Oria, 2005](https://doi.org/10.1145/1066157.1066213)) keeps the threshold but charges a constant penalty for each gap. ERP ([Chen and Ng, 2004](https://doi.org/10.1016/B978-012088469-8.50070-X)) drops the threshold and prices a gap by the distance of the point from a constant $g$. MSM ([Stefan, Athitsos and Das, 2013](https://doi.org/10.1109/TKDE.2012.88)) prices a gap by the neighbouring values instead. TWE ([Marteau, 2009](https://doi.org/10.1109/TPAMI.2008.76)) adds a stiffness parameter that charges for the time-stamp distance between matched points.

## When to use it

Use it when:

- A few readings are wrong or missing and should not dominate the distance: sensor spikes, dropouts, repaired gaps. LCSS and EDR can leave such points unmatched at a bounded cost.
- You want local timing tolerance and a penalty on warping in the same measure. ERP, MSM and TWE price every gap.
- A metric helps: indexing, pruning by the triangle inequality, or an algorithm that assumes one. ERP, MSM and TWE are metrics, LCSS and EDR are not.
- Series are z-normalised, or the tolerance can be stated in the units of the data.

Avoid it when:

- No natural tolerance exists. LCSS and EDR need $\varepsilon$ and results move with it.
- The size of small differences matters. Below $\varepsilon$ a pair counts as a match whatever its gap, so LCSS and EDR do not see how close it is.
- The whole series is shifted by one constant lag. A sliding measure such as SBD handles that at lower cost.
- Plain DTW with a window already answers the question. The edit-based measures add parameters, and each one is a choice to defend.

## Definition

Write $x$ and $y$ for series of length $n$, indexed from 1. Every measure fills a table $D(i, j)$ for the cost of editing the first $i$ points of $x$ into the first $j$ points of $y$. The first row and column hold the cost of deleting a whole prefix.

**LCSS** counts matches. A pair matches when the values differ by at most $\varepsilon$. Vlachos et al. add a time window $\delta$ so that only pairs with $|i - j| \le \delta$ can match:

$$
\begin{aligned}
& L(i, j) = \\
& \begin{cases}
L(i-1, j-1) + 1 \quad \text{if } |x_i - y_j| \le \varepsilon \\
\max\{L(i-1, j),\ L(i, j-1)\} \quad \text{otherwise}
\end{cases} \\[6pt]
& d_{\mathrm{LCSS}}(x, y) = 1 - \frac{L(n, n)}{n}
\end{aligned}
$$

**EDR** keeps the threshold and charges 1 for a mismatch and 1 for a gap:

$$
\begin{gathered}
D(i, j) = \min
\begin{cases}
D(i-1, j-1) + s(i, j) \\
D(i-1, j) + 1 \\
D(i, j-1) + 1
\end{cases} \\[6pt]
s(i, j) = \begin{cases} 0 & |x_i - y_j| \le \varepsilon \\ 1 & \text{otherwise} \end{cases}
\end{gathered}
$$

**ERP** has no threshold. A gap costs the distance of the deleted value from a constant $g$:

$$
D(i, j) = \min
\begin{cases}
D(i-1, j-1) + |x_i - y_j| \\
D(i-1, j) + |x_i - g| \\
D(i, j-1) + |y_j - g|
\end{cases}
$$

**MSM** moves a value at cost $|x_i - y_j|$ and splits or merges at a cost that depends on the neighbours. With a constant $c$ and $C(u, v, w)$ the cost of splitting or merging the value $u$ next to $v$ and $w$:

$$
\begin{aligned}
& C(u, v, w) = \\
& \begin{cases}
c \quad \text{if } v \le u \le w \text{ or } v \ge u \ge w \\
c + \min\{|u - v|,\ |u - w|\} \quad \text{otherwise}
\end{cases}
\end{aligned}
$$

$$
D(i, j) = \min
\begin{cases}
D(i-1, j-1) + |x_i - y_j| \\
D(i-1, j) + C(x_i, x_{i-1}, y_j) \\
D(i, j-1) + C(y_j, x_i, y_{j-1})
\end{cases}
$$

**TWE** works on pairs of value and time stamp, $(x_i, t_i)$ and $(y_j, s_j)$. With stiffness $\nu > 0$ and a deletion penalty $\lambda \ge 0$, and by convention $x_0 = y_0 = 0$ and $t_0 = s_0 = 0$:

$$
\begin{aligned}
D(i, j) &= \min\{D_1,\ D_2,\ D_3\} \\[6pt]
D_1 &= D(i-1, j) + |x_i - x_{i-1}| \\
&\quad + \nu (t_i - t_{i-1}) + \lambda \\[6pt]
D_2 &= D(i-1, j-1) + |x_i - y_j| \\
&\quad + |x_{i-1} - y_{j-1}| \\
&\quad + \nu \big(|t_i - s_j| + |t_{i-1} - s_{j-1}|\big) \\[6pt]
D_3 &= D(i, j-1) + |y_j - y_{j-1}| \\
&\quad + \nu (s_j - s_{j-1}) + \lambda
\end{aligned}
$$

Marteau shows that TWE is a distance for $\nu > 0$ and $\lambda \ge 0$, and that its time and space cost match DTW and ERP.

::: deep Which of the five are metrics
A metric satisfies non-negativity, symmetry and the triangle inequality. Chen and Ng built ERP to be one, to combine local time shifting with a measure that can be indexed by triangle-inequality pruning. Stefan et al. report that MSM is a metric, and Marteau proves it for TWE. EDR is not a metric, because treating values within $\varepsilon$ as equal breaks the triangle inequality. Vlachos et al. show the same for LCSS and prove only a weaker version of the inequality.

For clustering the property matters in two places. Indexing and pruning, when you search a large set. And any algorithm whose guarantees assume a metric. A hierarchical or medoid method will run on a non-metric matrix, but the result then rests on the data and not on the geometry.
:::

## The tolerance and the penalties

Each measure has its own parameters, and they are all in the units of the data, so they are not comparable across series on different scales. [Holder, Middlehurst and Bagnall (2023)](https://doi.org/10.1007/s10115-023-01952-0) give the variability of parameter effects with the values of the series as one argument for normalising all series first.

- **$\varepsilon$ in LCSS and EDR.** The largest gap you are willing to call noise. Too small and nothing matches, too large and everything does.
- **$\delta$ in LCSS.** The same role as the DTW window: how far apart in time two points may be and still match.
- **$g$ in ERP.** The reference value for gaps. Marteau reports that the authors of ERP set $g = 0$.
- **$c$ in MSM.** The price of one split or merge, in the units of the data. A larger $c$ discourages gaps.
- **$\nu$ and $\lambda$ in TWE.** The stiffness $\nu$ charges for time distance between matched points. Marteau places Euclidean distance at infinite stiffness and DTW at no stiffness, and TWE lies between them. The penalty $\lambda$ is a constant for each deletion.

Pick the tolerance from the question: the size of an error, or of a gap, that you would call the same event.

## Which clustering algorithm

All five give a pairwise distance matrix. None has a natural centroid, so the options follow the same logic as DTW:

- **k-medoids.** Works on any dissimilarity matrix. In the study of Holder et al., k-medoids improved all nine elastic measures compared with k-means on arithmetic-mean centroids, on the 112 UCR datasets used there. With k-medoids, MSM and TWE were the best performers, and the authors prefer MSM for its shorter run time.
- **Agglomerative hierarchical.** Needs only the matrix, with single, complete or average linkage. Ward's criterion is defined for Euclidean geometry, so on this matrix software will run it without that meaning.
- **k-means.** Needs an average that is consistent with the measure. The arithmetic mean is not one, and Holder et al. report their k-means results with standard averaging.
- **DBSCAN.** Runs on a precomputed matrix (Ester et al., 1996), with its radius set on the scale of the chosen measure.
- **k-Shape.** Not a match: it is built on SBD (Paparrizos and Gravano, 2015).

The same study finds that LCSS and EDR perform poorly on all its clustering tests, and reads this as the simple edit threshold being not sensitive enough to recover the class labels. The finding is from general benchmark data, not from financial series.

## In finance

Edit-based measures answer the question of which stretches of two price paths agree, within a tolerance and in the same order, while ignoring the stretches that do not. They are not a measure of contemporaneous dependence, since matching pairs observations from different dates. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Exchange rates and stock indices.** [Karademir (2015)](https://ideas.repec.org/p/sek/iacpro/2804863.html) clusters G8, BRICS and Turkish markets with DTW and LCSS on daily data from 2005 to 2015, as a pre-processing step for the link between exchange rates and stock prices. The paper reports that Turkish exchange rate and stock price movements correspond more closely to those of Russia and China than to the other countries. It is a conference paper.
- **Short-term trend retrieval.** [Udagawa (2018)](https://personales.upv.es/thinkmind/ALLDATA/ALLDATA_2018/alldata_2018_2_10_80026.html) revises the longest common subsequence algorithm to retrieve partially matching numerical sequences, with the position of the price relative to its 5-day and 25-day moving averages. Tests on daily Nikkei Stock Average data suggest that it helps to forecast short-term trends.
- **Prediction intervals.** [Goldani (2025)](https://arxiv.org/abs/2507.16655) uses similarity measures to build confidence intervals around Ridge regression forecasts for 42 US mega cap companies. LCSS intervals cover about 95 percent of the actual values, as the standard deviation method does, but are much wider. TWED intervals are narrower and cover about 67 percent. The paper is a preprint.

Limitations in financial time series:

- **Threshold.** Goldani (2025), in a study on US stocks, describes LCSS as strongly dependent on the similarity threshold, with a zero-and-one notion of similarity that can lead to poor results. This is the author's description of the method, not a result of the study.
- **Clustering accuracy.** On clustering benchmarks, LCSS and EDR performed poorly in all tests of Holder et al. (2023). The evidence is not specific to finance.
- **Scale of the parameters.** The threshold, $g$ and $c$ are in the units of the series, and Holder et al. (2023) normalise all series for that reason. The evidence is from general benchmark data, not from financial series.
- **Backtest overfitting.** The higher the number of configurations tried, the greater the probability that a backtest is overfit, and analysts rarely report that number ([Bailey et al., 2014](https://doi.org/10.1090/noti1105)). Threshold, penalties and number of clusters are all such configurations.

## Common mistake

Running LCSS or EDR with a default $\varepsilon$ on series that are not on a common scale, so that the threshold forgives a different amount of noise in each series. Decide the tolerance from the question, in the units of the data, and report it with the distance.
