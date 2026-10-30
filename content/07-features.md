---
id: features
module: B
title: Features: ACF, spectra, wavelets, SAX, catch22
kicker: Compare structure
sector: energy
lede: Feature-based measures replace each series by a few numbers or symbols that describe it, and compare those instead. What is compared is exactly what the features keep, and nothing else.
ignores: timing of single events, level and scale (normalised versions), whatever the features do not describe
keeps: serial dependence, cycle content, scale-wise energy, coarse shape (depending on the feature)
python: statsmodels.tsa.stattools.acf, scipy.signal.periodogram, pywt.wavedec, tslearn.piecewise.SymbolicAggregateApproximation, pycatch22.catch22_all
r: TSclust::diss.ACF, TSclust::diss.PER, TSclust::diss.DWT, TSclust::diss.MINDIST.SAX, Rcatch22::catch22_all
---

## One line

Feature-based measures compare series through descriptors such as autocorrelations, periodogram ordinates, wavelet coefficients, SAX words or a feature vector, and the real decision is which property of the series the descriptor keeps.

## What it measures

Euclidean distance and DTW compare values at, or near, the same positions. A feature-based measure first reduces each series to a description and then compares descriptions, so two series with different timing and different length can be close if they share the same dependence, the same cycles or the same coarse shape. [Montero and Vilar (2014)](https://doi.org/10.18637/jss.v062.i01) call the first kind shape-based, dominated by local comparisons of the geometric profile, and the second kind structure-based, which compares underlying dependence structures.

![The twelve days of the fixture, 48 half-hour readings each, all on one shared scale from 0 kW](figures/demand-12.svg)

Each day of this fixture could be described by its autocorrelations, by the weight of its half-day and daily cycles, or by a short word of symbols. Two days can then be close in one description and far in another, and that is the point: the feature is the question.

## When to use it

Use it when:

- The question is about structure, not about where each event falls: persistence, cycle content, roughness, the scale at which variation lives.
- Series have different lengths or are not aligned in time. The descriptors have a fixed size.
- The set is large. Descriptors are computed once per series and compared cheaply, and a lower bound such as SAX MINDIST can prune a search.
- Shape-based comparison fails. Montero and Vilar report that shape-based dissimilarities work well on short series and can fail on long ones with noise or anomalous records, where a structure-based dissimilarity is more appropriate.

Avoid it when:

- The shape of the profile is the question. A descriptor that drops the timing of events cannot tell two different profiles apart if they share the descriptor.
- You cannot say what the descriptor discards. Every choice of feature is a choice of what to ignore.
- The series are short and aligned. Montero and Vilar report that shape-based dissimilarities work well on short series.

## Definition

The five families below differ in the descriptor.

**Autocorrelation.** With $\hat\rho_{\ell, x}$ the sample autocorrelation of $x$ at lag $\ell$, and $L$ a lag beyond which it is close to zero, Galeano and Peña (2000) define:

$$
d_{\mathrm{ACF}}(x, y) = \sqrt{\sum_{\ell=1}^{L} \big(\hat\rho_{\ell, x} - \hat\rho_{\ell, y}\big)^2}
$$

Geometric weights $p(1-p)^{\ell}$ on the squared terms put more weight on short lags, and the same construction applies to the partial autocorrelations.

**Periodogram.** With $I_x(\lambda_k)$ the periodogram of $x$ at the Fourier frequencies $\lambda_k = 2\pi k / T$, and $\hat\gamma_{0,x}$ the sample variance, Caiado, Crato and Peña (2006) compare the normalised ordinates, which drops the scale and keeps the correlation structure, or their logarithms:

$$
d_{\mathrm{NP}}(x, y) = \sqrt{\frac{1}{n} \sum_{k=1}^{n} \left(\frac{I_x(\lambda_k)}{\hat\gamma_{0,x}} - \frac{I_y(\lambda_k)}{\hat\gamma_{0,y}}\right)^2}
$$

**Wavelets.** The discrete wavelet transform decomposes each series by scale. The approximation coefficients $a_{k, j^\ast}$ at a chosen scale $j^\ast$ form the descriptor:

$$
d_{\mathrm{DWT}}(x, y) = \sqrt{\sum_{k} \big(a^{(x)}_{k, j^\ast} - a^{(y)}_{k, j^\ast}\big)^2}
$$

Zhang et al. (2006) propose to choose $j^\ast$ as the highest scale at which the energy of the detail coefficients, summed over the series, is smaller than at the scale below. The rule trades dimension against the energy lost.

**SAX.** The series is z-normalised and cut into $w$ segments, each replaced by its mean (piecewise aggregate approximation, PAA). The means are mapped to $\alpha$ letters using the quantiles of $N(0, 1)$, so that the letters are about equally likely. With a table $\mathrm{dist}(\cdot, \cdot)$ that is 0 for equal or adjacent letters and the gap between the breakpoints otherwise, [Lin et al. (2003)](https://doi.org/10.1145/882082.882086) define:

$$
\mathrm{MINDIST}(\hat x, \hat y) = \sqrt{\frac{T}{w}} \sqrt{\sum_{i=1}^{w} \mathrm{dist}(\hat x_i, \hat y_i)^2}
$$

They show that it lower-bounds the Euclidean distance between the original series.

**catch22.** [Lubba et al. (2019)](https://doi.org/10.1007/s10618-019-00647-x) select 22 features from a library of 4,791, using 93 classification datasets. They cover linear and non-linear autocorrelation, successive differences, value distributions, outliers and fluctuation scaling. A series becomes a vector of 22 numbers, and the distance is taken between vectors.

::: deep What a periodogram keeps and what it drops
The periodogram is the squared modulus of the discrete Fourier transform. A circular shift of the series changes only the phase of each coefficient and leaves the modulus unchanged, so $d_{\mathrm{NP}}$ does not see where in the window a cycle sits, only how much of it there is. Dividing by the sample variance removes the scale. What remains is the distribution of variance across frequencies, which is why this family fits questions about cycles and persistence and not about the shape of a profile.
:::

## What the features keep

The choice of descriptor is the decision of this lesson. In short:

- **ACF and PACF.** Linear serial dependence at the lags you include. Insensitive to level and scale, blind to non-linear structure and to the order of events beyond the lags.
- **Periodogram.** Cycle content. The normalised version also drops scale, and the logarithm is motivated by the variance of an ordinate being proportional to the spectrum at its frequency.
- **Wavelets.** Variation by scale, with time localisation kept in the coefficients. The scale $j^\ast$ is the parameter, and Montero and Vilar describe its choice as a key point for an accurate clustering.
- **SAX.** Coarse shape at resolution $T / w$, on $\alpha$ levels. Timing within a segment and small amplitude changes are lost.
- **catch22.** Whatever the 22 features capture. The set was selected for classification across many domains, not for a given question.

Pick the descriptor from the question, then check on two or three series that two series you consider alike are close in it.

## Which clustering algorithm

Feature vectors live in an ordinary vector space, which opens options that a pairwise elastic distance does not:

- **k-means.** The ACF vector, the periodogram ordinates, the DWT approximations and the catch22 vector are points, so a centroid is defined. The centroid is an average description, not a series.
- **Agglomerative hierarchical.** Works with any of these distances. Ward's criterion assumes Euclidean distances between objects, which holds for the Euclidean descriptors above.
- **k-medoids and DBSCAN.** Run on the distance matrix (Ester et al., 1996), including for SAX words, where the MINDIST matrix is the input.
- **k-Shape.** Not a match: it is built on SBD (Paparrizos and Gravano, 2015).

Different features can have very different units. A distance between feature vectors is only meaningful once each feature is on a comparable scale.

## In finance

Feature-based measures answer whether two assets share a dependence structure, a volatility pattern or a coarse shape, not whether they move together on the same dates. For same-date dependence the literature offers several measures: Pearson correlation for linear association, the rank correlations of [Spearman (1904)](https://doi.org/10.2307/1412159) and [Kendall (1938)](https://doi.org/10.1093/biomet/30.1-2.81) for monotonic association, dynamic conditional correlation for time-varying dependence ([Engle, 2002](https://doi.org/10.1198/073500102288618487)), and copulas for dependence beyond correlation ([Embrechts, McNeil and Straumann, 2002](https://doi.org/10.1017/CBO9780511615337.008)).

Empirical applications:

- **Volatility and spectra.** [Caiado and Crato (2010)](https://doi.org/10.1080/14697680903567152) cluster the stocks of the Dow Jones Industrial Average with a distance built from the periodogram of squared returns and the parameters of a TARCH model, and compare the result with groupings from correlations of returns and of squared returns.
- **Wavelet scales.** [Michis (2022)](https://doi.org/10.3390/jrfm15010024) estimates partial correlations between returns at different wavelet scales and clusters on them, using the S&P 500 sector indices together with precious metals and energy futures. The cluster formations vary by time scale.
- **SAX on European stocks.** [Hobbelhagen and Diamantis (2024)](https://doi.org/10.3934/QFE.2024027) compare SAX with topological data analysis on the daily closes of 60 European stocks over one year. They find that SAX captures broader trends better and TDA local movements better.
- **SAX on a stock exchange.** [Nalici, Söylemez and Ünlü (2025)](https://doi.org/10.23055/ijietap.2025.32.2.10273) combine SAX with a dendrogram on three years of data for 81 BIST100 companies. The groups are sector-based and also cut across sectors.

Limitations in financial time series:

- **Information loss.** Hobbelhagen and Diamantis (2024), in a study on stocks, state that SAX makes comparison easier with the major drawback being loss of information.
- **Distributional assumptions.** Standard SAX takes the z-normalised values to be Gaussian and the symbols to be equiprobable. [Bountrogiannis, Tzagkarakis and Tsakalides (2022)](https://doi.org/10.1109/TKDE.2022.3174630) call these two assumptions restrictive. Their evidence is from general benchmark data, not from financial series.
- **Wavelet scale.** The result depends on the scale chosen, and Montero and Vilar (2014) describe it as the key point of wavelet-based clustering. Their discussion is not specific to finance.
- **Fixed feature sets.** catch22 trades accuracy for speed, with an average reduction of 7 percent in classification accuracy against the full library of 4,791 features. The figure is from 93 classification datasets, not from financial data.
- **Backtest overfitting.** The higher the number of configurations tried, the greater the probability that a backtest is overfit, and analysts rarely report that number ([Bailey et al., 2014](https://doi.org/10.1090/noti1105)). The lags, the wavelet scale, the word length and the alphabet size are all such configurations.

## Common mistake

Comparing raw feature vectors whose entries are on different scales, or computing a feature with no clear reason to expect it to separate the groups of interest, and then reading the clusters as if they described the whole series. State what the features keep, and check that a pair you expect to be alike is close in them.
