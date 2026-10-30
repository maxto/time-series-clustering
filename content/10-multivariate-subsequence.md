---
id: multivariate-subsequence
module: B
title: Multivariate and subsequence
kicker: Compare sequences
sector: health
lede: With several channels, you decide whether they warp together or apart. With a long series, you decide whether to compare whole series or the patterns they contain, and cutting a series into sliding windows to cluster them does not work.
ignores: order of matching subsequences (MPdist), timing differences between channels (independent warping)
keeps: channel scale after z-normalisation, local shape of subsequences (MPdist)
python: tslearn.metrics.dtw, aeon.distances.dtw_distance, stumpy.mpdist, tslearn.matrix_profile.MatrixProfile
r: tsmp::mpdist
---

## One line

For a series with several channels the decision is whether they share one warping path or each warps alone, and for a long series it is whether to compare the series as wholes or through the subsequences they share: never cluster the windows of a sliding window.

## What it measures

Two problems that look alike. A multivariate series has $M$ channels observed at the same times, such as the axes of an accelerometer, and a distance must decide how the channels are matched in time. A subsequence is a window of length $L$ inside a longer series, and a subsequence distance compares series by the windows they contain, wherever they occur.

For the first, [Shokoohi-Yekta et al. (2017)](https://doi.org/10.1007/s10618-016-0455-0) name the two common generalisations of DTW, dependent and independent warping. For the second, [Gharghabi et al. (2018)](https://doi.org/10.1109/ICDM.2018.00119) propose MPdist, which considers two series similar if they share many similar subsequences, regardless of the order of the matching subsequences. The matrix profile it builds on comes from [Yeh et al. (2016)](https://doi.org/10.1109/ICDM.2016.0179).

## When to use it

Use it when:

- Several channels are recorded together and the joint behaviour matters, as with wearable sensors.
- Channels have different units, as long as each one is z-normalised first. Shokoohi-Yekta et al. z-normalise each dimension before computing DTW.
- A long series holds a pattern that appears at different positions, in a different order, or with spurious or missing stretches in between. With missing data, MPdist is still defined as long as each series has at least one region longer than $L$.

Avoid it when:

- The order of events is the point. MPdist ignores the order of the matching subsequences.
- You intend to cut each series with a sliding window and cluster the windows. That is the subsequence clustering shown to be meaningless (see below).
- You need a metric. MPdist is a measure, not a metric, and it does not obey the triangle inequality (Gharghabi et al., 2018). DTW is not a metric either.

## Definition

Take two series $x$ and $y$ with $M$ channels. In dependent warping (DTW$_D$) all channels share one warping path. The local cost is the squared Euclidean distance between the two $M$-vectors, and the recurrence and the root are those of the DTW lesson:

$$
c(i, j) = \sum_{m=1}^{M} (x_{i,m} - y_{j,m})^2
$$

In independent warping (DTW$_I$) each channel warps alone and the distances add up:

$$
\mathrm{DTW}_I(x, y) = \sum_{m=1}^{M} \mathrm{DTW}(x_m, y_m)
$$

The `tslearn` function `dtw` computes the first form for multivariate input. For MPdist, join $A$ and $B$ and let $P_{ABBA}$ hold, for every subsequence of length $L$ of $A$, the Euclidean distance to its nearest neighbour in $B$, and the same from $B$ to $A$. It has $2(n - L + 1)$ values for series of length $n$. The distance is the $k$-th smallest value, with $k$ set to 5 percent of $2n$ in the paper, or the largest one when $P_{ABBA}$ is not longer than $k$:

$$
\mathrm{MPdist}_L(A, B) =
\begin{cases}
k\text{-th smallest value of } P_{ABBA} & \text{if } |P_{ABBA}| > k \\
\max P_{ABBA} & \text{otherwise}
\end{cases}
$$

The largest value would be brittle to one spike or dropout, the smallest would barely discriminate. When $L$ equals the series length, MPdist is the Euclidean distance.

::: deep Which window length
$L$ is the length of the pattern that should count as shared, in samples, so it comes from the question as the DTW window does. In their experiments Gharghabi et al. report that a clustering of eight noisy sensor series with missing data stays correct for $L$ anywhere from 60 to 600, and that the same data defeats Euclidean distance. This is one dataset. They also learn $L$ on a training split for classification.
:::

## Dependent or independent

The two forms answer different things. Dependent warping forces all channels to warp identically. Independent warping gives each channel the freedom to warp alone. Shokoohi-Yekta et al. give an example of each. In the MFCC coefficients of a bird call, all the relevant peaks and valleys move by exactly the same amount in time, which suggests dependent warping. In the acceleration of the two wrists of a cricket umpire signalling, one hand may lag the other or the two may be only loosely coupled, which suggests independent warping.

They show on classification that neither dominates: the two methods can produce different classifications, class by class or even exemplar by exemplar, and they propose a rule that picks one at classification time. Their evidence is nearest-neighbour classification on gesture, handwriting and similar data, not clustering and not finance. For clustering the choice is yours, so decide it from the question, and report which one you used together with the window.

## Whole series or subsequences

[Keogh and Lin (2005)](https://doi.org/10.1007/s10115-004-0172-7) separate whole clustering, where each object is a series, from subsequence clustering, where subsequences are cut from one series by a sliding window and then clustered. They show that the second is meaningless: the clusters are forced to obey a constraint that is pathologically unlikely to be satisfied by any dataset, so the clusters of any algorithm are essentially random. They propose a method based on time series motifs that clusters subsequences meaningfully on some datasets.

MPdist is a different use of subsequences: the series stay the objects to cluster, and the windows only enter the distance. Gharghabi et al. (2018) show a behaviour of an insect whose pattern has a variable number of peaks, clustered with three smoothed random walks. The clustering by Euclidean distance looks essentially random, and DTW cannot warp three peaks into five. MPdist is the measure they propose for this kind of data.

## Which clustering algorithm

Both families give a matrix of pairwise distances, so the matrix-based algorithms apply: agglomerative hierarchical clustering, k-medoids and DBSCAN, as with DTW. The details of each are in the lesson on matching the algorithm to the distance.

One limit is worth knowing. TADPole relies on DTW bounds defined only for univariate series of equal length, so it does not accept multivariate series (`dtwclust` documentation).

## In finance

These tools address the joint pattern of several simultaneous series and the recurrence of patterns inside a long series. They are not measures of contemporaneous dependence, since a warping path pairs observations of different dates. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Multivariate clustering of stocks.** [D'Urso, De Giovanni and Massari (2021)](https://doi.org/10.1007/s10479-019-03284-1) cluster multivariate financial series with a fuzzy partitioning-around-medoids method on a DTW distance, with a trimming step that flags series far from the bulk. They apply it to stocks of the FTSE MIB index to find common time patterns and possible outliers.
- **Matrix profile on markets.** [Cartwright, Crane and Ruskin (2021)](https://doi.org/10.3390/engproc2021005045) apply the matrix profile to financial series, including multivariate ones. It identifies periods of similar behaviour across market sectors and indexes, and they discuss general market behaviour in times of financial crisis.
- **Motifs of different lengths.** [Cartwright, Crane and Ruskin (2022)](https://doi.org/10.3390/forecast4010013) extend the matrix profile with SAX and minimum description length to find motifs whose two sides differ in length, to read local volatility patterns, with S&P 500 data as an example.
- **Exchange rates.** [Cartwright, Crane and Ruskin (2019)](https://www.iccs-meeting.org/archive/iccs2019/papers/115400736.pdf) run the motif algorithm VALMOD on a GBP-USD exchange rate dataset to illustrate measures for evaluating motifs.

Limitations in financial time series:

- **Subsequence clustering.** On S&P 500 closing values, the cluster centres of different k-means runs on sliding-window subsequences were not significantly more similar to each other than to centres from random walk data (Keogh and Lin, 2005).
- **Choice between forms of DTW.** Dependent and independent warping can give different results and neither dominates (Shokoohi-Yekta et al., 2017). The evidence is from classification on non-financial data.
- **Metric properties.** MPdist does not obey the triangle inequality (Gharghabi et al., 2018), so the speed-ups that rely on it do not apply. The statement is general and not specific to finance.

## Common mistake

Cutting a long series into overlapping windows and clustering them, then reading the centres as typical patterns. The centres are essentially random, as on S&P 500 closing values. Cluster whole series, or compare series through a subsequence distance such as MPdist, and for several channels choose and report dependent or independent warping.
