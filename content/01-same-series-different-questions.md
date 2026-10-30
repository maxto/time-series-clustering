---
id: same-series-different-questions
module: A
title: Same series, different questions
kicker: Define similarity
sector: energy
lede: Twelve days of electricity demand, two sensible questions, two different groupings. The data stays the same. The question changes, and so does the answer.
ignores: B: level, B: scale, B: global shift (tolerated)
keeps: A: level, A: scale, A: timing, A: shape, B: shape
python: numpy, scipy.spatial.distance, scipy.cluster.hierarchy, aeon.distances
r: stats::dist, stats::hclust, dtwclust::zscore, dtwclust::SBD
---

## One line

Before you pick a distance, decide what two series must share to count as similar: that is a choice about what to ignore, and the data cannot make it for you.

## Twelve days of demand

Twelve daily profiles of electricity demand. Each panel is one day: 48 readings, one every half hour, in kW on an illustrative scale. The names are labels only, not calendar days.

![The twelve days of the fixture, 48 half-hour readings each, all on one shared scale from 0 kW](figures/demand-12.svg)

There are two things to see. The shape: some days have two short peaks, others one flat block. The timing: in the early days the activity is centred on 08:00, in the late days on 13:00, five hours later. That makes four kinds of day, three of each. Inside a kind the days differ a little in base level, in height, in timing (up to an hour and a half) and in noise.

The dataset is authored. It was built to show what a choice of comparison does, and it says nothing about how well any method works on real data.

## Two questions

- **Question A.** A grid operator asks: which days put load on the grid at the same hours?
- **Question B.** An analyst of usage patterns asks: which days have the same shape, even if one happens earlier than another?

Both are reasonable, and each leads to its own pipeline: a set of choices about what to keep and what to ignore. To turn distances into groups, both pipelines use the same rule, average linkage cut at two groups: start with every day alone and keep merging the two groups whose members are closest on average, until two are left.

## Question A: raw values, Euclidean distance

For question A the hour matters, so the days are compared as they are, half hour by half hour:

$$
d_{\mathrm{E}}(x, y) = \sqrt{\sum_{t=1}^{48} (x_t - y_t)^2}
$$

A day busy at 08:00 and a day busy at 13:00 are far apart: at many half hours one is high while the other is low. Level, size and timing all count, and nothing is ignored.

![Question A: average linkage on raw Euclidean distances, two groups. Group 1 in ink, group 2 in accent](figures/question-a.svg)

The days split by timing. Group 1 holds the six early days, two-peak and flat alike, and group 2 the six late days. In this fixture the hour of activity outweighs the shape.

## Question B: z-normalisation plus SBD

For question B two steps change. First, each day is z-normalised, so that a higher base level or a taller profile no longer shows:

$$
z_t = \frac{x_t - \bar{x}}{s_x}
$$

Second, the comparison is the shape-based distance (SBD) of [Paparrizos and Gravano (2015)](https://doi.org/10.1145/2723372.2737793). It slides one day along the other, finds the shift where they match best, and turns that match into a distance:

$$
\mathrm{SBD}(x, y) = 1 - \max_{s} \frac{\mathrm{CC}_s(x, y)}{\lVert x \rVert \, \lVert y \rVert}
$$

Here $\mathrm{CC}_s(x, y)$ is the sum of products $x_t y_{t-s}$ after shifting $y$ by $s$ samples, with zeros where the two days no longer overlap. The value lies between 0 and 2, and 0 means the same shape.

![Question B: average linkage on SBD distances between z-normalised days, two groups. Group 1 in ink, group 2 in accent](figures/question-b.svg)

Now the days split by shape. Group 1 holds the six two-peak days, early and late, and group 2 the six flat-block days, despite the five-hour shift that decided question A. Both changes are needed. On this fixture, z-normalisation followed by Euclidean distance still splits early from late, and so does SBD on the raw values.

## What do you want to ignore?

Neither grouping is a mistake: each answers its own question, and the fixture file stores both intended labels, an hour group and a shape group. So "which grouping is better?" has no answer until the question is stated. A validity score does not settle it either: a score computed under one distance says how well the groups fit that distance, not whether that distance matched the question.

The difference fits in one line. Question B ignores level and scale and tolerates a global shift, question A ignores none of them. That is the lens of this course: for every measure, ask what it lets you ignore.

- the **level** of a series, its baseline
- its **scale**, how large the swings are
- a **global shift**, the whole series earlier or later
- **local timing**, parts of the series running a little early or late
- **noise**, small fast wiggles
- **length**, series of different durations

Euclidean distance compares the same time steps. SBD compares the best of all shifted versions. The lessons that follow take the measures one at a time, each with what it ignores and what it keeps.

## In finance

The finance version of question A asks which assets move together over the same period. Mantegna (1999, [arXiv version](https://arxiv.org/abs/cond-mat/9802256)) answers it with the correlation of synchronous daily changes of the logarithm of the closing price. A match found only after shifting one series answers a different question, so no shift belongs in that comparison. The finance version of question B asks which assets follow one another with a delay. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Same-date co-movement, stocks.** Mantegna (1999) builds a hierarchical tree of the stocks of the Dow Jones Industrial Average and of the S&P 500 index from July 1989 to October 1995, using daily correlations. The groups found make sense in economic terms, with an energy group of Chevron, Texaco and Exxon among them.
- **Lead and lag, stocks.** [Lo and MacKinlay (1990)](https://doi.org/10.1093/rfs/3.2.175) study weekly US stock returns. They find strong cross-autocorrelations and report that the returns of large stocks lead those of smaller stocks.

## Common mistake

Asking "which distance is best for time series?" before asking what the grouping is for. On these twelve days the same data gives two different groupings, and both are correct. A distance can only be judged against what you need it to ignore.
