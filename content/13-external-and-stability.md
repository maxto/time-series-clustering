---
id: external-and-stability
module: D
title: External indices and stability
kicker: Validate the grouping
sector: energy
lede: An external index compares a partition with a reference partition. A stability check compares the partition with itself after the data are perturbed. Neither tells you the groups are right, and each rests on a choice you make.
ignores: the distance and the algorithm that produced the partition, label names and order
keeps: which pairs of series are grouped together
python: sklearn.metrics.rand_score, sklearn.metrics.adjusted_rand_score, sklearn.metrics.fowlkes_mallows_score
r: mclust::adjustedRandIndex, fpc::cluster.stats, dtwclust::cvi
---

## One line

An external index counts the pairs of series that two partitions treat alike, and a stability check repeats the clustering on perturbed data: the decision hidden in each is which reference to trust and what to perturb.

## What it measures

External indices compare two labelings of the same series: the clustering and a reference, such as a known class, a sector or another clustering. They look only at which pairs are put together or apart, so a relabelling of the groups changes nothing. Stability asks a different question: if the data are slightly different, do the same groups come back?

On the twelve fixture days the reference exists, because the fixture file stores two intended labelings, an hour group and a shape group (see [Same series, different questions](lesson:same-series-different-questions)). The two-group cut of average linkage on the DTW matrix, described in [Elastic: DTW and its window](lesson:dtw), puts the six early days against the six late days. Compared with the hour group, every pair is treated alike and an external index returns its maximum. Compared with the shape group, it does not. The fixture is authored, so this shows how an index behaves, not that a method works.

![The two-group cut against the hour group and the shape group, as contingency tables](figures/contingency.svg)

The tables give the same reading in numbers. Against the hour group the adjusted Rand index is {{n:ari_hour}} and the Jaccard index {{n:jaccard_hour}}. Against the shape group they are {{n:ari_shape}} and {{n:jaccard_shape}}, and a negative adjusted Rand index means agreement below its expected value under chance.

## When to use it

Use it when:

- A reference partition exists and you want to know how close the clustering is to it.
- You want to compare two clusterings of the same series, for example the groups at two windows of DTW.
- You want evidence that the groups do not depend on one sample, one period or one set of series.

Avoid it when:

- The reference is a proxy, not the truth. External indices require knowledge of the ground-truth classes, which is almost never available in practice (scikit-learn documentation).
- You treat a high stability as a proof of validity. Stability shows reproducibility. A reference or an outcome is what tells you the groups mean something.

## Definition

Let two partitions of $N$ series have contingency counts $n_{ij}$, the number of series in group $i$ of the first and group $j$ of the second, with row sums $a_i$ and column sums $b_j$. All the indices below are functions of four pair counts, written as in [Gates (2025)](https://arxiv.org/abs/2511.03000):

$$
\begin{gathered}
A = \sum_i \binom{a_i}{2}, \quad B = \sum_j \binom{b_j}{2} \\[6pt]
T = \sum_{i,j} \binom{n_{ij}}{2}, \quad M = \binom{N}{2}
\end{gathered}
$$

$A$ counts the pairs together in the first partition, $B$ in the second, $T$ in both, and $M$ is all pairs. The pairs apart in both are $M - A - B + T$.

**Rand** ([Rand, 1971](https://doi.org/10.1080/01621459.1971.10482356)). The fraction of pairs on which the partitions agree, together or apart:

$$
\mathrm{RI} = \frac{T + (M - A - B + T)}{M}
$$

**Adjusted Rand** ([Hubert and Arabie, 1985](https://doi.org/10.1007/BF01908075)). Subtracts the agreement expected for random labelings with the same group sizes, $E[T] = AB / M$, and rescales:

$$
\mathrm{ARI} = \frac{T - AB/M}{\tfrac{1}{2}(A + B) - AB/M}
$$

Random labelings score close to 0 and the range is $[-0.5, 1]$ (scikit-learn documentation). The unadjusted index is often close to 1 even when the clusterings differ, because most pairs are apart in both.

**Jaccard** ([Jaccard, 1912](https://doi.org/10.1111/j.1469-8137.1912.tb05611.x)). The overlap coefficient applied to pairs, as in [Ben-Hur, Elisseeff and Guyon (2002)](https://doi.org/10.1142/9789812799623_0002), who ignore the pairs apart in both:

$$
\mathrm{J} = \frac{T}{A + B - T}
$$

**Fowlkes-Mallows** ([Fowlkes and Mallows, 1983](https://doi.org/10.1080/01621459.1983.10478008)). The geometric mean of the two shares of together-pairs that agree:

$$
\mathrm{FM} = \sqrt{\frac{T}{A} \cdot \frac{T}{B}}
$$

The scikit-learn documentation gives a small case: reference labels `[0, 0, 0, 1, 1, 1]` against `[0, 0, 1, 1, 2, 2]`. Here $A = 6$, $B = 3$, $T = 2$ and $M = 15$, so $\mathrm{RI} = 10/15$, $\mathrm{ARI} = 0.8/3.3 \approx 0.24$, $\mathrm{FM} \approx 0.47$ and $\mathrm{J} = 2/7$. The ARI and FM values match the documented outputs.

**Other pair-counting indices** use the same counts ([Desgraupes, 2017](https://cran.r-project.org/web/packages/clusterCrit/vignettes/clusterCrit.pdf)). Czekanowski-Dice is the harmonic mean of the two shares of Fowlkes-Mallows. Hubert's $\hat\Gamma$ is the correlation between the two partitions read as together or apart for each pair, the same quantity as the phi coefficient. Sokal-Sneath has two versions:

$$
\begin{gathered}
\mathrm{Dice} = \frac{2T}{A + B} \\[6pt]
\hat\Gamma = \frac{MT - AB}{\sqrt{AB(M - A)(M - B)}} \\[6pt]
\mathrm{SS}_1 = \frac{T}{2A + 2B - 3T} \\[6pt]
\mathrm{SS}_2 = \frac{M - A - B + 2T}{M + T - \tfrac{1}{2}(A + B)}
\end{gathered}
$$

::: deep What the four indices weigh
All four are functions of the same four pair counts and differ only in how they weight them. Rand counts the pairs apart in both partitions as agreement, Jaccard and Fowlkes-Mallows focus on the pairs together, and the adjusted Rand index subtracts the agreement expected when the group sizes are fixed and the labelings are independent, the hypergeometric model behind $E[T] = AB/M$ ([Gates, 2025](https://arxiv.org/abs/2511.03000)). Fuzzy versions of RI and ARI exist in `dtwclust::cvi`.
:::

## What to perturb

Stability repeats the clustering on perturbed data and compares the results. The procedure of [Ben-Hur, Elisseeff and Guyon (2002)](https://doi.org/10.1142/9789812799623_0002) draws two subsamples, each a fraction of the data not much smaller than 1, clusters both, and measures the similarity of the two labelings on the points common to both. Repeating this gives a distribution of similarities for each number of groups. A partition that captures real structure gives a distribution concentrated near 1, and they look for the largest number of groups that is still stable. Any similarity from the previous section can serve, they discuss correlation, matching and Jaccard.

[Lange et al. (2004)](https://doi.org/10.1162/089976604773717621) frame the same idea as the reproducibility of a clustering on a second sample, interpreted as a classification risk, and choose the number of groups that minimises it.

For time series the decision is what to perturb. [Marti et al. (2015)](https://arxiv.org/abs/1509.05475) list perturbations on the time axis, a sliding window, the odd against the even days, economic regimes, the heart against the tails of the market and the sampling frequency, and on the population, adding or removing series. Each answers a different question. A sliding window asks whether the groups move when the market is steady, odd against even days asks whether two samples of the same phenomenon agree, and regimes ask whether the structure persists. A clustering that fails the perturbation relevant to your use is a clustering you should not rely on.

## Which outputs it can be computed on

- **External indices.** Only labels are needed, so any algorithm works. No assumption is made on the cluster structure, so a k-means partition and a spectral one can be compared (scikit-learn documentation).
- **Stability.** It can be used with any clustering algorithm, as it only needs the algorithm to be run again (Ben-Hur, Elisseeff and Guyon, 2002).
- **Fuzzy partitions.** They need a crisp conversion, or a fuzzy version of the index.

## In finance

External indices and stability answer two questions: do the groups match an economic classification, and do they persist when the data change? Where the question is different, the literature offers several alternatives. For fit to the chosen distance, use an internal index, covered in the previous lesson. For the usefulness of the groups, define an outcome-oriented criterion for the task. For the reliability of single links in a correlation network, use bootstrap replicas of the data.

Empirical applications:

- **Recovering sectors.** [Musmeci, Aste and Di Matteo (2015)](https://doi.org/10.1371/journal.pone.0116201) compare hierarchical clustering methods on correlations between stock returns with the industrial sector classification, using the adjusted Rand index, and find that the Directed Bubble Hierarchical Tree can outperform the others, retrieving more information with fewer clusters.
- **Bootstrap reliability.** [Tumminello et al. (2007)](https://doi.org/10.1142/S0218127407018415) attach a reliability value to the links of correlation-based graphs with bootstrap replicas, on the 300 most capitalised NYSE stocks in 2001 to 2003. The Average Linkage Minimum Spanning Tree recognises sectors and sub-sectors as communities slightly better than the minimum spanning tree, whose links have a slightly higher average reliability.
- **Stability on credit default swaps.** [Marti et al. (2015)](https://arxiv.org/abs/1509.05475) perturb a database of credit default swap price series to assess clustering validity, and report that clustering can be persistent through a wide range of perturbations provided that an appropriate distance is used.

Limitations in financial time series:

- **Market mode.** The market mode, which drives all stocks regardless of their sector, hides to some extent the sector structure, so Musmeci, Aste and Di Matteo also run detrended analyses. They treat the similarity with the sector classification as a proxy for the information filtered by the method.
- **Clusters outside the classification.** Statistical clustering can produce clusters that do not exist in an industrial classification, such as a group of Portugal, Ireland, Italy, Greece and Spain assets during the European debt crisis, a point they raise against choosing a method by its score against a classification ([Marti et al., 2015](https://arxiv.org/abs/1509.05475)).
- **Sensitivity to noise.** On financial time series, adding small noise to a sample and re-running the same algorithm is reported to yield different clusters, and the consistency of clustering algorithms is generally unknown in the asymptotic regimes that matter in finance (Marti et al., 2015).
- **What stability proves.** Marti et al. cite work that warns that stability depends only on the uniqueness of the minimiser of the clustering objective for large samples, and other work arguing that it remains useful for small finite samples.

## Common mistake

Reading an adjusted Rand index against a sector classification, or a stable clustering, as proof that the groups are right. The first measures agreement with a reference that is itself a proxy. The second measures reproducibility under the perturbation you chose. State the reference or the perturbation next to the score, and keep in mind what each one cannot show.
