---
id: learned
module: B
title: Learned representations
kicker: Compare sequences
sector: industry
lede: A learned representation replaces each series by a short vector, found by a search or by training a network. What the vector keeps and what it ignores is set by the objective that produced it, so that objective is the choice to make.
ignores: position of a pattern inside the series (shapelets), whatever the training objective does not reward (embeddings)
keeps: local patterns (shapelets), whatever the training objective rewards (embeddings)
python: tslearn.shapelets.LearningShapelets, aeon.clustering.deep_learning.AEFCNClusterer
r:
---

## One line

A learned representation turns each series into a vector and clusters the vectors, and the objective that produced the vector, not you, decides what counts as similar: state that objective before you read any cluster.

## What it measures

Two families share the idea. A shapelet is a short subsequence, and a series is described by how closely it contains each of a few shapelets. The classic definition is a subsequence that is maximally representative of a class ([Ye and Keogh, 2009](https://doi.org/10.1145/1557019.1557122)). An embedding is the output of a trained network, a vector of fixed size for a series of any length. Both give a vector space, so any algorithm that works on vectors can follow.

For clustering there are no class labels, which changes the shapelet search. [Zakaria, Mueen and Keogh (2012)](https://doi.org/10.1109/ICDM.2012.26) show that shapelets can be found in unlabelled series, and call them unsupervised-shapelets or u-shapelets. Their journal version ([Zakaria et al., 2015](https://doi.org/10.1007/s10618-015-0411-4)) motivates them with noise, dropouts and extraneous data in whole-series distances, and with series that do not have equal length. A u-shapelet uses only some local patterns and deliberately ignores the rest of the series.

For embeddings, [Franceschi, Dieuleveut and Jaggi (2019)](https://arxiv.org/abs/1901.10738) train a causal dilated convolutional encoder without labels, on multivariate series of variable length. Another route is an autoencoder followed by an ordinary clusterer on the latent vector.

## When to use it

Use it when:

- The information is a local pattern, and where it occurs in the series does not matter. A shapelet is matched at its best position.
- Series differ in length or carry noise and extraneous stretches around the pattern.
- You need one fixed-size vector per series, for an algorithm that wants vectors.

Avoid it when:

- The whole series matters, with its timing and its level. A u-shapelet ignores the rest of the series on purpose.
- You cannot state what the training objective rewards. The result then has no definition you can report.
- The set is large and the search is brute force. Searching all subsequences for u-shapelets can be untenably slow without the speed-ups of Zakaria et al. (2015).

## Definition

The distance between a shapelet $S$ of length $l$ and a series $T$ of length $n$ is the distance to the closest subsequence of $T$ (Zakaria et al., 2015). In their work every subsequence is z-normalised first:

$$
\mathrm{sdist}(S, T) = \min_{1 \le i \le n - l + 1} \mathrm{dist}\left(S, T_{i,l}\right)
$$

With $m$ shapelets, series $T_1, \dots, T_N$ become the rows of an $N \times m$ matrix of $\mathrm{sdist}$ values, which they call the distance map. It goes to an off-the-shelf algorithm such as k-means. To find a u-shapelet, they search the subsequence that splits the set into a group $D_A$ that contains it and a group $D_B$ that does not, by maximising the gap between the two groups of distances, with mean $\mu$ and standard deviation $\sigma$:

$$
\mathrm{gap} = \mu_B - \sigma_B - (\mu_A + \sigma_A)
$$

The search removes the series it separated and repeats on the rest until no data remains to be separated.

For an embedding, the unsupervised loss of Franceschi et al. (2019) takes a random subseries $x^{\mathrm{ref}}$ of a series, a subseries $x^{\mathrm{pos}}$ of it, and $K$ subseries $x^{\mathrm{neg}}_k$ drawn from other series. With encoder $f$ and sigmoid $\sigma$ it minimises:

$$
\begin{aligned}
& -\log \sigma\left(f(x^{\mathrm{ref}})^\top f(x^{\mathrm{pos}})\right) \\
& - \sum_{k=1}^{K} \log \sigma\left(-f(x^{\mathrm{ref}})^\top f(x^{\mathrm{neg}}_k)\right)
\end{aligned}
$$

::: deep Learned shapelets
A shapelet can also be learned by gradient descent instead of searched, as proposed by [Grabocka et al. (2014)](https://doi.org/10.1145/2623330.2623613). The `tslearn` implementation computes the $i$-th coordinate of the transform as the smallest squared Euclidean distance between $s_i$ and a window of the series, and puts a logistic regression layer on top. Shapelets and weights are optimised together on a cross-entropy loss, so this model is fitted on class labels. It describes a classifier. For clustering it is a source of labelled shapelets only when some labels exist.
:::

## What the representation keeps

Every learned representation answers one question, and the clustering inherits it.

- **Shapelets.** The length $l$ is in samples and is the shortest pattern that carries the meaning you want, so it comes from the question as the DTW window does. The number $m$ is the dimension of the vector. In the u-shapelet search it is not set in advance, because the search stops when no data remains to be separated.
- **Embeddings.** The loss above asks that subseries of one series be close and that subseries of different series be apart. Nothing in it says which differences between series are the ones you care about. Dimension, depth and training set are further choices.

Franceschi et al. (2019) evaluate the representations by training a support vector machine on them and by a nearest-neighbour classifier with the $\ell_2$ distance between representations, which tests classification, not clustering. They also show a day of electricity consumption split into six clusters by k-means on representations of a sliding window.

## Which clustering algorithm

The output is a matrix of vectors, so the algorithms that need vectors apply: k-means, Gaussian mixtures and fuzzy c-means, and also the algorithms that only need a distance matrix, on the Euclidean distances between the rows. Zakaria et al. (2015) name k-means as an example for the distance map, the default of the `aeon` autoencoder clusterer is also k-means with Euclidean distance, and Franceschi et al. use k-means on the representations. There is no need for a DTW-aware centre: the elastic part, if any, was done before.

What does not follow is a statement about the original series. Two series that fall in one cluster are close in the learned space, and the space was built by the objective.

## In finance

A learned representation addresses the question of which assets or periods share a recurring pattern or a learned profile. It does not measure contemporaneous dependence. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Directional forecasting.** [Kim et al. (2025)](https://arxiv.org/abs/2509.15040) cluster multivariate series to extract recurring patterns and train a shapelet-based classifier on their initial part to forecast direction, on Bitcoin and three S&P 500 equities. They report that the method ranks first or second in 11 of 12 metric and dataset combinations.
- **Asset embeddings.** [Dolphin, Smyth and Dong (2024)](https://arxiv.org/abs/2407.18645) learn embeddings from daily returns of 611 US stocks, 2000 to 2018, with a contrastive loss whose pairs come from the similarity of returns over many subwindows. The embeddings beat the baselines on industry classification and on portfolio optimisation.
- **Stock embeddings.** [Dolphin, Smyth and Dong (2022)](https://arxiv.org/abs/2202.08968) learn stock embeddings from historical returns with a neural model inspired by natural language processing, and report gains over several benchmarks on two financial analytics tasks.

Limitations in financial time series:

- **Scale of the contrastive pairs.** Dolphin et al. (2024) state that the pairwise similarity computation over several windows can become intractable as the number of assets or the length of the series grows, and that window size and stride reduce the number of comparisons.
- **Search cost.** The brute-force search for unsupervised-shapelets can be untenably slow (Zakaria et al., 2015). The statement is general and the paper is not about finance.

## Common mistake

Clustering the vectors from a pretrained encoder, or shapelets chosen for another task, and reading the groups as similarity under your own question. The vector keeps what its training rewarded. Report the objective, the training data and, for shapelets, their length together with the clusters.
