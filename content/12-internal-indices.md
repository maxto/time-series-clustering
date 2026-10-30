---
id: internal-indices
module: D
title: Internal indices
kicker: Validate the grouping
sector: energy
lede: An internal index scores a partition using only the data and the distance that produced it. It tells you how well the groups fit that distance, not whether the distance was the right one.
ignores: the question behind the distance, labels, anything outside the data and the partition
keeps: compactness and separation, as measured by the distance you gave it
python: sklearn.metrics.silhouette_score, sklearn.metrics.calinski_harabasz_score, sklearn.metrics.davies_bouldin_score
r: cluster::silhouette, fpc::cluster.stats, e1071::fclustIndex, dtwclust::cvi
---

## One line

An internal validity index summarises, in one number, how compact the groups are and how far apart they sit, and the hidden decision is the input it needs: a dissimilarity matrix, centroids in a vector space, or fuzzy memberships.

## What it measures

Every index below compares two things: how close the members of a group are to each other (compactness) and how far the groups are from one another (separation). They differ in how they measure each, and so in what they need. Silhouette and Dunn work from pairwise dissimilarities. Calinski-Harabasz and Davies-Bouldin use cluster centres. Xie-Beni uses the memberships and centres of a fuzzy partition.

![The 12 by 12 DTW matrix with w = 4, ordered by group. Higher opacity means a smaller distance](figures/dtw-matrix.svg)

Take the two-group cut of the fixture, average linkage on the DTW matrix of [Elastic: DTW and its window](lesson:dtw). Its mean silhouette is {{n:silhouette_dtw4_k2}}. That number says how well the six early days and the six late days separate under DTW with $w = 4$. It says nothing about whether DTW was the comparison your question needed, which is the point of [Same series, different questions](lesson:same-series-different-questions): a score computed under one distance measures the fit to that distance.

## When to use it

Use it when:

- You compare partitions of the same data under the same distance, for example the same algorithm cut at different numbers of groups.
- No labels are available. Internal indices use only the data and the partition.
- You want a check that the groups are compact and separated in the sense of your distance.

Avoid it when:

- You want to choose between distances, normalisations or representations. The scores then come from different dissimilarities, and a study of seven relative validity indices, Silhouette and Davies-Bouldin among them, on more than 2.7 million partitions of feature-vector and time-series data found them unsuitable for that purpose ([Yerbury et al., 2025](https://doi.org/10.1145/3748726)).
- The groups are not convex. Silhouette, Calinski-Harabasz and Davies-Bouldin are generally higher for convex clusters than for density-based ones such as those from DBSCAN (scikit-learn documentation).
- The partition has a single group. Silhouette is defined only for between 2 and $n - 1$ groups, and Dunn's separation term needs at least two.

## Definition

Let the partition have $k$ groups $C_1, \dots, C_k$ of $n_q$ points each, $n$ points in total, and let $d$ be the dissimilarity.

**Silhouette** ([Rousseeuw, 1987](https://doi.org/10.1016/0377-0427(87)90125-7)). For a point $i$ in group $C_I$, let $a(i)$ be its mean dissimilarity to the other points of its own group and $b(i)$ the smallest mean dissimilarity from $i$ to the points of any other group:

$$
a(i) = \frac{1}{n_I - 1} \sum_{j \in C_I,\, j \ne i} d(i, j), \qquad
b(i) = \min_{J \ne I} \frac{1}{n_J} \sum_{j \in C_J} d(i, j)
$$

$$
s(i) = \frac{b(i) - a(i)}{\max\{a(i),\, b(i)\}}, \qquad \mathrm{S} = \frac{1}{n} \sum_{i=1}^{n} s(i)
$$

A point alone in its group gets $s(i) = 0$. Needs: a dissimilarity matrix, nothing else.

**Dunn** ([Dunn, 1974](https://doi.org/10.1080/01969727408546059)). The smallest distance between points of different groups over the largest distance between two points of the same group:

$$
\mathrm{DI} = \frac{\min_{p \ne q}\ \min_{x \in C_p,\, y \in C_q} d(x, y)}{\max_{r}\ \max_{x, y \in C_r} d(x, y)}
$$

Needs: a dissimilarity matrix. Variants replace the separation or the diameter with mean distances or distances to centroids.

**Calinski-Harabasz** ([Calinski and Harabasz, 1974](https://doi.org/10.1080/03610927408827101)). With centres $c_q$ and global centre $c$, the ratio of between-group to within-group dispersion, corrected for the number of groups:

$$
\mathrm{CH} = \frac{\operatorname{tr}(B_k)}{\operatorname{tr}(W_k)} \cdot \frac{n - k}{k - 1}, \quad
\operatorname{tr}(B_k) = \sum_{q=1}^{k} n_q \lVert c_q - c \rVert^2, \quad
\operatorname{tr}(W_k) = \sum_{q=1}^{k} \sum_{x \in C_q} \lVert x - c_q \rVert^2
$$

Needs: points in a vector space, the group centres and a global centre.

**Davies-Bouldin** ([Davies and Bouldin, 1979](https://doi.org/10.1109/TPAMI.1979.4766909)). With $s_i$ the mean distance of the points of group $i$ to its centre and $d_{ij}$ the distance between centres:

$$
\mathrm{DB} = \frac{1}{k} \sum_{i=1}^{k} \max_{j \ne i} \frac{s_i + s_j}{d_{ij}}
$$

Needs: group centres. The use of centre distances limits the metric to Euclidean space (scikit-learn documentation).

**Xie-Beni** ([Xie and Beni, 1991](https://doi.org/10.1109/34.85677)). For a fuzzy partition with memberships $\mu_{ij}$ of point $i$ in group $j$ and centres $v_j$, as stated by [Wiroonsri and Preedasawakul (2026)](https://arxiv.org/abs/2308.14785):

$$
\mathrm{XB} = \frac{\sum_{j=1}^{k} \sum_{i=1}^{n} \mu_{ij}^2 \, \lVert x_i - v_j \rVert^2}{n \cdot \min_{j \ne l} \lVert v_j - v_l \rVert^2}
$$

Needs: the memberships and centres of a fuzzy clustering.

::: deep Same name, different input
Some software computes an index with the distance and the centre that the clustering used, not with Euclidean distance and the arithmetic mean. In `dtwclust`, the internal indices are computed with the distance and centroid chosen during clustering (documentation of `cvi`). Calinski-Harabasz has also been generalised to dissimilarities by Hennig and Liao (2013), a form `fpc::cluster.stats` reports. Check which distance and which centre sit behind a number before you compare it with one from another tool.
:::

## Reading a score

Each index has a direction and the numbers mean little without it.

- **Silhouette.** Lies between $-1$ and $1$. Values near 0 indicate overlapping clusters, and a negative $s(i)$ suggests the point sits nearer another group (scikit-learn and `cluster::silhouette` documentation).
- **Dunn.** Higher is better. Because the denominator is a maximum, one badly spread group lowers it, so it is a worst-case indicator.
- **Calinski-Harabasz.** Higher when groups are dense and well separated.
- **Davies-Bouldin.** Lower is better, with a minimum of zero.
- **Xie-Beni.** Lower is better.

The scores are comparable only between partitions of the same data under the same dissimilarity. Computed for several numbers of groups, they give one value per cut. This lesson does not rank the indices or recommend one.

## Which outputs it can be computed on

Not every partition offers every input.

- **Hierarchical clustering.** Cut the tree to get labels. Silhouette and Dunn then need only the matrix the tree was built from. Centre-based indices need centres, which a tree does not provide.
- **k-medoids.** A dissimilarity matrix and labels, so Silhouette and Dunn apply. The medoid is a real series, which gives a centre for the other indices only if you accept it as the centroid.
- **k-means.** Centres exist, so Calinski-Harabasz and Davies-Bouldin apply. The mean is a centre under Euclidean distance. Under DTW it needs a DTW-consistent average, as in the lesson on DTW.
- **Fuzzy c-means.** Memberships and centres exist, so Xie-Beni applies, and a fuzzy partition can be converted to a crisp one so that the hard indices apply too (documentation of `dtwclust::cvi`).
- **DBSCAN.** Labels, with noise points to place somewhere. The convexity bias above applies.

## In finance

Internal indices answer one question about a set of assets: do the groups fit the dissimilarity you chose? Where the question is different, the literature offers several other checks. To ask whether the groups correspond to an economic classification, compare them with sectors using an external index. To ask whether the groups persist when the data are perturbed, measure stability. To ask whether the groups are useful, define an outcome-oriented criterion for the task, which [Yerbury et al. (2025)](https://doi.org/10.1145/3748726) suggest instead of relative indices when selecting a similarity paradigm. The next lesson covers the first two.

Empirical applications:

- **Choosing k for stock series.** [Ozkok and Celik (2021)](https://doi.org/10.1142/S0219622021500449) combine Dunn, Silhouette, the C index and Davies-Bouldin into one hybrid index to choose the number of groups in k-means on time series. They test it on nine datasets, one of daily closing prices from Yahoo Finance and eight from the UCR archive, and report promising results against other validity indexes.

Limitations in financial time series:

- **Comparing similarity choices.** Relative validity indices are unreliable for selecting a normalisation, representation and distance, a limit shown on feature-vector and time-series data that are not specifically financial ([Yerbury et al., 2025](https://doi.org/10.1145/3748726)).
- **High dimension.** Distance-based internal measures can give unreliable evaluations in high-dimensional spaces, and scores computed in different embedding spaces are not reliably comparable. The result is stated for deep clustering ([Wang and Ye, 2024](https://arxiv.org/abs/2403.14830)).
- **Convex bias.** Silhouette, Calinski-Harabasz and Davies-Bouldin are generally higher for convex clusters than for density-based ones, a statement of the scikit-learn documentation about general data.

## Common mistake

Using an internal index to decide which distance, normalisation or representation is right. The index is computed from the dissimilarity you picked, so a high score confirms that the groups fit it and nothing more. Decide the distance from the question, then use the index to compare partitions under that distance.
