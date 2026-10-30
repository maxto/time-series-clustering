---
id: recipe-energy
module: E
title: Recipe: daily load profiles
kicker: A worked path
sector: energy
lede: Twelve days of demand, one question, four steps. Each step is a decision, and each decision is written down with the reason for it, so that the result can be read as an answer to the question and not as a property of the data.
ignores: local timing within two hours
keeps: level, scale, order of events, timing beyond two hours
python: scipy.cluster.hierarchy.linkage, scipy.cluster.hierarchy.fcluster, sklearn.metrics.silhouette_score
r: stats::hclust, stats::cutree, cluster::silhouette
---

## One line

Work through Define, Measure, Group and Validate on the twelve fixture days, and write down at each step what you chose to ignore, because the grouping you get is the answer to that choice.

## Define

Start from the question, not the method. Here the question is: which days follow the same daily pattern at the same time of day, allowing a day to run up to two hours early or late? That wording fixes what counts as similar.

![The twelve days of the fixture, 48 half-hour readings each, all on one shared scale from 0 kW](figures/demand-12.svg)

The decision, in the terms of [Same series, different questions](lesson:same-series-different-questions):

- Ignore local timing up to two hours. At half-hour sampling that is $w = 4$ samples.
- Keep level and scale. A day with a higher base load or taller peaks is a different day for this question, so the series are not z-normalised.
- Keep the order of events and any timing gap beyond the window.

If the question were instead "which days have the same shape, whatever the hour", level and scale would be ignored too and a sliding measure would replace this one. That is the other pipeline of lesson 1, and it gives another grouping on the same data.

## Measure

The question asks for forgiveness of local timing and nothing else, which is what dynamic time warping with a window does. The comparison is DTW with squared local cost, the Sakoe-Chiba window $|i - j| \le w$ with $w = 4$, and the square root of the accumulated cost, as defined in [Elastic: DTW and its window](lesson:dtw).

What the window changes shows on one pair. `mon` and `sat` share a profile whose peaks differ by three samples, a shift inside the window. Their Euclidean distance is {{n:euclid_mon_sat}} and their DTW distance with $w = 4$ is {{n:dtw4_mon_sat}}. `mon` and `wed` differ by ten samples, outside the window, so DTW with $w = 4$ is {{n:dtw4_mon_wed}}, close to their Euclidean {{n:euclid_mon_wed}}. The window refuses that shift, which is what the question asks for.

The output of this step is a 12 by 12 matrix of DTW distances, with the window written next to it.

## Group

The matrix is all the grouping step receives, and DTW gives no natural centre. That limits the choice to algorithms that run on a matrix, as set out in the DTW lesson. Average linkage hierarchical clustering qualifies. Ward's criterion does not mean what it says on a DTW matrix, and k-means needs a DTW-consistent average.

Cut at two groups, because the question separates days by the hour at which activity sits and the fixture was built with two such hours. In a real study the number of groups is also a decision, taken from the use of the result, with the validation step below as a check on it.

![The 12 by 12 DTW matrix with w = 4, ordered by group. Higher opacity means a smaller distance](figures/dtw-matrix.svg)

The cut splits the six early days from the six late days. The gap between the two timings is wider than the two-hour window, so DTW still sees it.

## Validate

Three checks, each answering a different question.

**Internal fit.** The mean silhouette of this partition on the DTW matrix is {{n:silhouette_dtw4_k2}}. It describes how well the two groups fit the DTW distance. It does not say that DTW with $w = 4$ was the right comparison, and the previous lessons explain why a score cannot say it.

**Agreement with a reference.** The fixture file stores an hour group and a shape group. The partition equals the hour group, so an external index such as the adjusted Rand index reaches its maximum against it, and it does not equal the shape group. This is the expected reading: the question asked for the hour, not the shape. The reference exists because the fixture was authored, and real data seldom has one.

**Sensitivity to the decision.** The window is the decision that moves the answer. At $w = 10$ the distance between `mon` and `wed` falls to {{n:dtw10_mon_wed}}, from {{n:dtw4_mon_wed}} at $w = 4$, so a wider window can bring days from the two timings close together. Whether the two-group cut changes at other windows is a check to run before trusting the result, with the stability idea of the previous lesson.

![Average linkage cut at two groups, at six windows. Colour is the group, the number at the right is the mean silhouette on that window's matrix](figures/window-sensitivity.svg)

From $w = 0$ to $w = 6$ the cut stays the hour group. At $w = 10$ and with no window it puts `thu` alone against the other eleven days, and the mean silhouette falls to {{n:sensitivity_sil_10}} and {{n:sensitivity_sil_none}}, from {{n:silhouette_dtw4_k2}} at $w = 4$. The result depends on the window, so report the window with it.

The fixture is an authored demonstration. It shows what each choice does, not that the method performs well on real load data.

## Common mistake

Treating the four steps as independent, picking a distance, an algorithm and an index from a list. Each step inherits the decision of the one before: the window comes from the question, the algorithm from what the matrix allows, and the validation from the distance. Change the question and the whole path changes with it.
