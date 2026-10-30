---
id: lock-step
module: B
title: "Lock-step: Euclidean, L1, correlation"
kicker: Compare sequences
sector: finance
lede: Lock-step measures compare sample t of one series with sample t of the other, nothing else. The family is simple and fast, and its members differ in one thing that matters: what a single large gap does to the total.
ignores: nothing by itself (correlation: level and scale)
keeps: timing, order of events, level and scale (correlation: timing)
python: scipy.spatial.distance.euclidean, scipy.spatial.distance.cityblock, scipy.spatial.distance.minkowski, scipy.spatial.distance.chebyshev, scipy.spatial.distance.canberra, scipy.spatial.distance.correlation, aeon.distances.euclidean_distance, aeon.distances.manhattan_distance
r: stats::dist, stats::cor
---

## One line

A lock-step measure pairs each time step of one series with the same time step of the other and combines the gaps, so the decision is how to combine them: a sum of squares, a sum of absolute values, a maximum, relative gaps, or a correlation.

## What it measures

Under a lock-step measure two series are close when they are close at the same times. A profile that is right but an hour and a half late is far away, because at many time steps one series is high while the other is low.

![mon (ink) and sat (accent), linked sample by sample (top) and along the DTW path with w = 4 (bottom). Every second link is drawn](figures/lockstep-vs-dtw.svg)

In the fixture, an authored demonstration, the Euclidean distance between `mon` and `sat` is {{n:euclid_mon_sat}}, and between `mon` and `wed` it is {{n:euclid_mon_wed}}. The peaks of `sat` come three samples after those of `mon`, the peaks of `wed` ten samples after. Lock-step distance gives similar values for both. DTW with $w = 4$ gives {{n:dtw4_mon_sat}} for the first pair and {{n:dtw4_mon_wed}} for the second, because the window forgives a shift of three samples and not of ten.

## When to use it

Use it when:

- Time steps are comparable across series: the same clock, calendar or event, so that sample $t$ means the same thing everywhere.
- The series have the same length and a regular grid.
- Timing is part of the question, as in "which days load the grid at the same hours".
- Speed matters. One pair costs $O(n)$ and $N$ series need $N(N-1)/2$ pairs.

Avoid it when:

- The same events may occur earlier or later. Use a sliding or an elastic measure.
- Level or scale should not count and you did not remove them first. Raw Euclidean distance keeps both.
- Series have different lengths.

## Definition

For $x, y \in \mathbb{R}^n$ the Minkowski distance of order $p \ge 1$ contains the others:

$$
d_p(x, y) = \Big( \sum_{t=1}^{n} |x_t - y_t|^p \Big)^{1/p}
$$

- **Manhattan**, $p = 1$: the sum of absolute gaps.
- **Euclidean**, $p = 2$: the square root of the sum of squared gaps. A large gap counts more than several small ones.
- **Chebyshev**, $p \to \infty$: $\max_t |x_t - y_t|$, only the largest gap counts.
- **Canberra**: each gap is divided by the magnitudes of its two values, so every term lies between 0 and 1.

$$
d_{\mathrm{Can}}(x, y) = \sum_{t=1}^{n} \frac{|x_t - y_t|}{|x_t| + |y_t|}
$$

- **Correlation distance**: one minus the Pearson correlation $\rho$, in the definition of `scipy.spatial.distance.correlation`.

$$
\begin{gathered}
d_{\rho}(x, y) = 1 - \rho(x, y) \\[6pt]
\rho(x, y) = \frac{\sum_t (x_t - \bar{x})(y_t - \bar{y})}{\sqrt{\sum_t (x_t - \bar{x})^2}\ \sqrt{\sum_t (y_t - \bar{y})^2}}
\end{gathered}
$$

Correlation and Euclidean distance are tied. If both series are z-normalised with the population standard deviation, so that $\sum_t z_t^2 = n$, then

$$
\lVert z^{x} - z^{y} \rVert_2 = \sqrt{2n\,(1 - \rho(x, y))}
$$

so Euclidean distance on z-normalised series orders pairs exactly as correlation distance does.

::: deep Correlation as a distance in finance
[Mantegna (1999)](https://arxiv.org/abs/cond-mat/9802256) notes that the correlation coefficient itself cannot be used as a distance, because it does not satisfy the axioms of a metric, and in the arXiv version he defines $d = \sqrt{1 - \rho^2}$. This treats a pair with $\rho = -1$ like a pair with $\rho = 1$. [Onnela et al. (2003)](https://arxiv.org/abs/cond-mat/0302546) use $d = \sqrt{2(1 - \rho)}$, with values between 0 and 2. A strongly anticorrelated pair is then far apart. Which one fits depends on whether an asset that moves opposite to another counts as close.
:::

::: deep Libraries count zeros differently
On terms where both values are zero, Canberra is undefined. The R function `stats::dist` omits such terms and treats them as missing, while `scipy.spatial.distance.canberra` counts them as 0. Check the treatment of zeros before you compare numbers from two sources.
:::

## Choosing the member

The family has one real choice, how gaps are combined, and one question before it: do level and scale count?

- **Level and scale count.** Use a Minkowski distance on raw values. The unit of the series matters, so series in different units cannot be mixed.
- **Level and scale do not count.** Z-normalise first and use Euclidean distance, or use correlation distance, which gives the same ordering. These measures keep timing and drop level and scale.
- **Relative gaps count.** Canberra weighs a gap by the size of the values. A gap between 0.1 and 0.2 weighs as much as a gap between 100 and 200, so it is a relative measure.
- **One gap should dominate, or be ignored.** Chebyshev keeps only the largest gap. Manhattan weighs gaps linearly, Euclidean quadratically.

On the order $p$: the study of [Aggarwal, Hinneburg and Keim (2001)](https://doi.org/10.1007/3-540-44503-X_27) shows that in high dimensional space the contrast between near and far points depends on the order of the norm, and concludes that the Manhattan distance is consistently preferable to the Euclidean distance for high dimensional data mining applications. Their setting is general high dimensional data, not time series in particular.

## Which clustering algorithm

All members give a pairwise distance matrix, and Euclidean distance also gives a mean that is a point of the same space. That opens the options:

- **k-means.** Built on Euclidean distance and on the arithmetic mean as centre, and the comparison in [Paparrizos and Gravano (2015)](https://doi.org/10.1145/2723372.2737793) includes it with Euclidean distance as k-AVG+ED. The mean is the centre for squared Euclidean distance, so with another member the centre has to be redefined.
- **Agglomerative hierarchical.** Needs only the matrix. Ward's criterion is defined for Euclidean geometry, so on the other members software will run it without that meaning. Mantegna (1999) builds the minimal spanning tree and the hierarchical tree of its subdominant ultrametric space from the correlation distance.
- **k-medoids.** Works on any dissimilarity matrix, and each centre is a real series (Kaufman and Rousseeuw, 1990).
- **DBSCAN.** Runs on a precomputed matrix (Ester et al., 1996), with its radius set on the scale of the chosen member.

## In finance

Correlation distance answers a question about contemporaneous co-movement: which assets rise and fall together over the same period. It does not answer questions about lead and lag, nor about dependence beyond linear association. For these the literature offers several measures: the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)). A sliding or an elastic measure fits the lead-lag question.

Empirical applications:

- **Stocks.** Mantegna (1999) builds a hierarchical tree from correlations of daily changes of the logarithm of the closing price, for the stocks of the Dow Jones Industrial Average and of the S&P 500 index from July 1989 to October 1995. The groups found make sense in economic terms.
- **Stocks, over time.** Onnela et al. (2003) follow the trees built from correlations of daily returns of NYSE stocks, from 1980 to 1999, in moving windows. They report that during market crashes the global correlation is strong and the mean occupation layer of the tree drops.
- **Currencies.** [Mizuno, Takayasu and Takayasu (2006)](https://arxiv.org/abs/physics/0508164) build minimal spanning trees from foreign exchange data and find clusters that largely follow geographic regions.
- **Portfolio optimisation.** [Tola et al. (2008)](https://doi.org/10.1016/j.jedc.2007.01.034) filter the correlation matrix with clustering algorithms before optimising a portfolio. They report that predicted risk is closer to realised risk, in a bootstrap analysis over a wide range of the number of assets $N$ and of the parameter $T$.

Limitations in financial time series:

- **Volatility.** [Forbes and Rigobon (2002)](https://doi.org/10.1111/0022-1082.00494) show that correlation coefficients between stock markets are conditional on market volatility, and that heteroskedasticity biases tests of contagion based on them.
- **Dimension.** Aggarwal, Hinneburg and Keim (2001) find that the meaning of proximity weakens as dimension grows. The result is for high dimensional data in general, not for financial series.

## Common mistake

Using raw Euclidean distance and reading it as similarity of shape. It keeps level, scale and timing together, so two series with the same shape at different levels, or one hour apart, come out far. Say which of these you want to keep, then pick z-normalisation, correlation distance or a sliding measure to match.
