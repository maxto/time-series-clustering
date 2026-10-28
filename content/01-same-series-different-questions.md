---
id: same-series-different-questions
module: A
title: Same series, different questions
kicker: Define similarity
lede: Twelve days of electricity demand, two sensible questions, two different groupings. The data stays the same. The question changes, and so does the answer.
ignores: B: level, B: scale, B: global shift (tolerated)
keeps: A: level, A: scale, A: timing, A: shape, B: shape
python: numpy, scipy.spatial.distance, scipy.cluster.hierarchy, aeon.distances
r: stats::dist, stats::hclust, dtwclust::zscore, dtwclust::SBD
---

## One line

Before you pick a distance, decide *what two series must share to count as similar*. That decision is a choice about what to ignore, and the data cannot make it for you.

## Lesson

To cluster anything you need a rule for "close". With time series that rule is not given by the data. Two days of demand can be close in one sense and far apart in another, and both senses can be useful.

This lesson shows it on one small dataset. The rest of the course is built on what it shows.

### Twelve days of demand

Here are twelve daily profiles of electricity demand. Each panel is one day: 48 readings, one every half hour, in kW on an illustrative scale. The names are labels only, not calendar days.

![The twelve days of the fixture, 48 half-hour readings each, all on one shared scale from 0 kW](figures/demand-12.svg)

Look for two things. First, the shape: some days have two short peaks, others one flat block. Second, the timing: in the early days the activity is centred on 08:00, in the late days on 13:00, five hours later.

That makes four kinds of day, three of each. Inside each kind the three days differ a little: a higher base level, a taller or flatter profile, activity slightly earlier or later (up to an hour and a half), and some noise.

This dataset is authored. It was built to show what a choice of comparison does, and it says nothing about how well any method works on real data.

### Two questions

Two people look at the same twelve days.

- **Question A.** A grid operator asks: which days put load on the grid *at the same hours*?
- **Question B.** An analyst of usage patterns asks: which days *have the same shape*, even if one happens earlier than another?

Both questions are reasonable. They lead to two different pipelines, and each pipeline is a set of choices about what to keep and what to ignore.

### Question A: raw values, Euclidean distance

For question A the hour matters, so the days are compared as they are. No preprocessing. The comparison is the Euclidean distance, which lines the two days up half hour by half hour:

$$
d_{\mathrm{E}}(x, y) = \sqrt{\sum_{t=1}^{48} (x_t - y_t)^2}
$$

A day busy at 08:00 and a day busy at 13:00 are far apart under this distance: at many half hours one is high while the other is low. Level, size and timing all count. Nothing is ignored.

To turn distances into groups, both pipelines use the same rule, average linkage cut at two groups. It starts with every day on its own and keeps merging the two groups whose members are closest on average, until two groups are left.

![Question A: average linkage on raw Euclidean distances, two groups. Group 1 in ink, group 2 in accent](figures/question-a.svg)

The result splits the days by timing. Group 1 holds the six early days, two-peak and flat alike. Group 2 holds the six late days. In this fixture, the hour of activity outweighs the shape.

### Question B: z-normalisation plus SBD

For question B two steps change, not one.

The preprocessing changes. Each day is z-normalised: subtract its mean, divide by its standard deviation.

$$
z_t = \frac{x_t - \bar{x}}{s_x}
$$

After this step every day has mean 0 and standard deviation 1. A higher base level or a taller profile no longer shows.

The comparison changes too. The shape-based distance (SBD) of [Paparrizos and Gravano (2015)](https://doi.org/10.1145/2723372.2737793) slides one day along the other, finds the shift where they match best, and turns that best match into a distance:

$$
\mathrm{SBD}(x, y) = 1 - \max_{s} \frac{\mathrm{CC}_s(x, y)}{\lVert x \rVert \, \lVert y \rVert}
$$

Here $\mathrm{CC}_s(x, y)$ is the sum of products $x_t y_{t-s}$ after shifting $y$ by $s$ samples, with zeros where the two days no longer overlap. The value lies between 0 and 2, and 0 means the same shape. SBD searches over global shifts. With finite windows and zero padding, boundary and overlap changes can still affect the distance.

The grouping rule is the same as before: average linkage, two groups.

![Question B: average linkage on SBD distances between z-normalised days, two groups. Group 1 in ink, group 2 in accent](figures/question-b.svg)

Now the days split by shape. Group 1 holds the six two-peak days, early and late. Group 2 holds the six flat-block days. On this fixture the grouping follows shape despite the five-hour shift that decided question A.

Both changes are needed here. On this fixture, z-normalisation followed by Euclidean distance still splits early from late, and so does SBD on the raw values. Only the two together answer question B.

### Two answers, both right

Neither grouping is a mistake. Timing dominates the raw-Euclidean grouping on this fixture. With normalisation and SBD, the recovered groups instead follow shape. The fixture file even stores both intended labels, an hour group and a shape group, because both are correct answers to their own question.

So "which grouping is better?" has no answer until you say which question you are asking. A validity score does not settle it either. A score computed under one distance tells you how well the groups fit that distance, not whether that distance matched your question. Module E comes back to this.

### What do you want to ignore?

The difference between the two pipelines fits in one line: question B ignores level and scale and tolerates a global shift, question A ignores none of them. That is the lens this course uses for every measure. When you meet a new distance, ask what it lets you ignore:

- the **level** of a series, its baseline
- its **scale**, how large the swings are
- a **global shift**, the whole series earlier or later
- **local timing**, parts of the series running a little early or late
- **noise**, small fast wiggles
- **length**, series of different durations

Each choice sits somewhere in the pipeline: the object you cluster, preprocessing, representation, comparison, grouping and validation. Here, question B made its choice in two places, preprocessing and comparison. The course map on the home page shows the whole pipeline.

The comparison step has many options. The survey by [Paparrizos et al. (2024)](https://arxiv.org/abs/2412.20574) sorts more than 100 distance measures into seven families: lock-step, sliding, elastic, kernel, feature-based, model-based and embedding. This lesson used two of them. Euclidean distance is lock-step: it compares the same time steps. SBD is sliding: it compares the best of all shifted versions. Later lessons take the families one at a time, each with what it ignores and what it keeps.

## Common mistake

Asking "which distance is best for time series?" before asking what the grouping is for. On these twelve days the same data gives two different groupings, and both are correct. A distance can only be judged against what you need it to ignore.

## In finance

Our finance example asks about contemporaneous co-movement. A match obtained only after shifting returns answers a different question. [Mantegna (1999)](https://arxiv.org/abs/cond-mat/9802256) built a hierarchy of stocks from the correlation of their daily returns over the same period. Correlation keeps the time steps aligned, so no shift or warping belongs in that comparison.
