---
id: recipe-finance
module: E
title: Recipe: a stock universe
kicker: A procedure
sector: finance
lede: A procedure for grouping a universe of stocks by how their returns move together. There is no dataset here and no result. Each step names its decisions and what each one depends on.
ignores: mean and volatility of each return series, when Pearson correlation is the measure
keeps: co-movement on the same dates
python: scipy.cluster.hierarchy.linkage, scipy.cluster.hierarchy.fcluster, scipy.stats.spearmanr, sklearn.metrics.adjusted_rand_score
r: stats::cor, stats::hclust, stats::cutree, mclust::adjustedRandIndex
---

## One line

Grouping stocks means choosing four things in order, the question, the dissimilarity, the algorithm and the checks, and every choice depends on the one before it, so write each one down with its reason.

## Define

![The four steps and what each one hands to the next](figures/recipe-flow.svg)

Three decisions, in this order.

**The question.** The usual one is contemporaneous co-movement: which stocks move together on the same dates. [Mantegna (1999)](https://doi.org/10.1007/s100510050929) builds a taxonomy of stocks from the synchronous correlation of daily differences of the logarithm of the closing price. If the question is about one series leading another, warping or shifting is part of the answer and the comparison changes, as in [Elastic: DTW and its window](lesson:dtw). The question fixes what must be ignored, as in [Same series, different questions](lesson:same-series-different-questions).

**The object to cluster.** Prices, returns or correlations are all possible inputs. [Kakushadze and Yu (2016)](https://arxiv.org/abs/1607.04883) ask exactly this for statistical industry classification and report that their backtests suggest the details make a sizable difference. The choice therefore belongs in the record of the study.

**The universe and the sample.** The number of stocks $N$ and the number of dates $T$ matter together. [Marti et al. (2015)](https://arxiv.org/abs/1509.05475) note that the properties of clustering algorithms, such as consistency, are generally unknown in the asymptotic regimes that matter in finance, among them high dimension with a low or moderate sample size. [Laloux et al. (1999)](https://doi.org/10.1103/PhysRevLett.83.1467) find that the eigenvalue density of the empirical correlation matrix of S&P 500 stocks agrees remarkably with a random matrix, and conclude that it raises serious doubts on the blind use of empirical correlation matrices for risk management. Both depend on $N$ and $T$, so fix the period, the sampling frequency and the list of stocks before looking at any grouping. Marti et al. also list the period choices that are worth varying later: a sliding window, economic regimes, the sampling frequency.

## Measure

Correlation is not a distance, so a function of it is used. [Mantegna (1999)](https://doi.org/10.1007/s100510050929) uses a function that is zero when the correlation is complete in absolute value, so that two stocks that are mirror images of each other are at zero distance. [Marti et al. (2015)](https://arxiv.org/abs/1509.05475) use one that keeps the sign, for Pearson's $\rho_{ij}$ or Spearman's:

$$
D_{ij} = \frac{1 - \rho_{ij}}{2}
$$

The decisions and what each depends on:

- **Sign.** Keep it if a stock that moves against another must be far from it. Drop it if opposite movers belong to the same group.
- **Pearson or Spearman.** On credit default swap prices, Marti et al. report that if dependence is the only focus, Spearman should be preferred to Pearson and a Euclidean distance should not be used for comparing financial time series. The evidence is from that data, not from stocks.
- **What the measure ignores.** A correlation is unchanged by the level and scale of each series, so the groups say nothing about which stocks are more volatile.

The output of this step is an $N \times N$ dissimilarity matrix, with the estimation window written next to it.

## Group

The matrix is all that the grouping step receives, which points to algorithms that run on a matrix. The literature on stocks offers several.

- **Minimum spanning tree and its ultrametric.** [Mantegna (1999)](https://doi.org/10.1007/s100510050929) obtains the minimal spanning tree of the distance matrix and the associated subdominant ultrametric hierarchical tree, and finds a taxonomy that is meaningful economically.
- **Average linkage.** [Tumminello et al. (2007)](https://doi.org/10.1142/S0218127407018415) associate a spanning tree with the average linkage analysis, the Average Linkage Minimum Spanning Tree, and report that it recognises sectors and sub-sectors as communities slightly better than the minimum spanning tree on 300 NYSE stocks.
- **Directed Bubble Hierarchical Tree.** [Musmeci, Aste and Di Matteo (2015)](https://doi.org/10.1371/journal.pone.0116201) find that it can outperform other hierarchical methods in retrieving the industrial classification. [Verma, Buonocore and Di Matteo (2017)](https://arxiv.org/abs/1712.02138) use it to fix the number of clusters without assuming it beforehand.

What the choice depends on is the property you need. A hierarchy keeps all the cut levels, so the number of groups can be decided later. A method that fixes the number of groups itself removes that decision and puts it into the algorithm. Record the algorithm, its settings and the number of groups, and the reason for each. No result is claimed here for any of them on a specific universe.

## Validate

Each check answers a different question, and none of them stands alone.

- **Fit to the dissimilarity.** An internal index such as the silhouette says how well the groups fit $D_{ij}$. It cannot say that $D_{ij}$ was the right measure.
- **Agreement with a classification.** [Musmeci, Aste and Di Matteo (2015)](https://doi.org/10.1371/journal.pone.0116201) use the adjusted Rand index between the clustering and an industrial classification as a proxy for the information the method filters. They state that the market mode, which drives all stocks, hides the classification to some extent, and they repeat the analysis on detrended data and on a second classification. Marti et al. caution that clustering may produce clusters that a classification does not contain.
- **Stability.** [Marti et al. (2015)](https://arxiv.org/abs/1509.05475) propose perturbing the data in time and in the population of series and check whether the clustering persists. [Tumminello et al. (2007)](https://doi.org/10.1142/S0218127407018415) estimate the reliability of the links of a correlation-based graph from bootstrap replicas.

Decide before the run which of these you will report and what result would make you drop the grouping. The Validate lessons give the definitions.

## Common mistake

Choosing the dissimilarity and the algorithm by the score they obtain against a sector classification or an internal index, and calling the best-scoring pair the right one. The classification is a proxy, the index depends on the dissimilarity, and the number of configurations tried is itself a decision to record. Fix the question first, then report the checks that follow from it.
