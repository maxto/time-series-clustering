---
id: preprocessing
module: A
title: What preprocessing erases
kicker: Define similarity
sector: weather
lede: Before any distance sees a series, preprocessing has already decided what cannot matter. Each step removes something, and no distance can bring it back.
ignores: level, scale, trend, short-term variation, sampling detail
keeps: shape, order of events, timing
python: scipy.stats.zscore, scipy.signal.detrend, numpy.diff, pandas.DataFrame.interpolate, pandas.DataFrame.resample, pandas.DataFrame.rolling
r: base::scale, base::diff, stats::filter, dtwclust::zscore
---

## One line

Every preprocessing step erases one property of the series before the distance is computed, so the steps are part of the definition of similarity and the choice of what to erase comes from the question.

## What each step removes

- **Z-normalisation** removes level and scale: each series gets mean 0 and standard deviation 1.
- **Detrending** removes a fitted trend, for instance a straight line, and keeps the deviations from it.
- **Differencing** replaces each value by its change from the previous one, which removes the level and reduces trend. Seasonal differencing compares a value with the one from the same season.
- **Smoothing** removes short-term variation by averaging neighbouring values. A larger window gives a smoother curve and erases more.
- **Resampling** moves the series to a coarser or finer grid, and aggregation erases what happens inside each interval.
- **Missing-value handling** fills or drops the gaps, and what fills them is an assumption, not an observation.

Take the pair `mon` and `sat` of the fixture, which share a two-peak profile with the peaks of `sat` three samples later. Their Euclidean distance on raw values is {{n:euclid_mon_sat}}, and DTW with $w = 4$ gives {{n:dtw4_mon_sat}}. The gap is almost all timing, and z-normalisation would not change it: it erases level and scale and keeps timing.

![One day of the fixture, mon, through four of these steps, each panel on its own vertical scale. Z-normalisation changes only the axis, differencing leaves the changes, the moving average over five points softens the peaks, the two-hour means keep only their rough place](figures/preprocess-views.svg)

## When to use it

Use it when:

- The property to erase is one the question says is irrelevant: the baseline of a meter, the unit of a sensor, a slow drift.
- The distance does not already erase it. Euclidean distance on raw values keeps level and scale, and a correlation-based distance does not (see the lesson on lock-step measures).

Avoid it when:

- The property is the question. If load level decides who is close to whom, z-normalisation destroys the answer.
- A series is constant. Its standard deviation is zero and z-normalisation is undefined.
- Two steps remove the same property. Z-normalisation and differencing both remove the level, so applying both is redundant.

## Definition

For a series $x_1, \dots, x_n$, with mean $\bar{x}$ and standard deviation $s_x$:

$$
z_t = \frac{x_t - \bar{x}}{s_x}
$$

In SciPy, `scipy.stats.zscore` uses `ddof=0` by default, that is, the population deviation.

The first difference, and the difference at seasonal period $p$:

$$
\Delta x_t = x_t - x_{t-1}, \qquad \Delta_p x_t = x_t - x_{t-p}
$$

A centred moving average of order $m = 2k + 1$ replaces each value by the mean of the values within $k$ periods of it. An even order is not symmetric, and the usual remedy is to follow it with a moving average of order 2, as described in [Hyndman and Athanasopoulos, *Forecasting: Principles and Practice*](https://otexts.com/fpp3/moving-averages.html):

$$
\tilde{x}_t = \frac{1}{2k + 1} \sum_{j=-k}^{k} x_{t+j}
$$

Resampling a series to blocks of $b$ samples by the mean, and filling one gap between observed values $x_a$ and $x_c$ by linear interpolation:

$$
\begin{gathered}
y_u = \frac{1}{b} \sum_{j=1}^{b} x_{(u-1)b + j} \\[6pt]
\hat{x}_t = x_a + \frac{t - a}{c - a}\,(x_c - x_a)
\end{gathered}
$$

::: deep Differencing and the series length
Differencing once shortens a series by one value, and seasonal differencing by $p$ values, a moving average without padding by $2k$. A distance that needs equal lengths needs the same step on both series, so apply the step to every series in the same way and check the output length.
:::

## What to erase

The order of steps matters, and so does the question that justifies each one. A short guide, by what the question tolerates:

- **A different level or unit between series.** Z-normalise, and do it for each series on its own. Normalising with one mean and one deviation for the whole dataset keeps the differences in level and scale between series.
- **A slow drift that is not the object of study.** Detrend or difference. They are not the same: detrending keeps deviations around a fitted shape, differencing keeps changes.
- **Noise that hides the shape.** Smooth, and choose the window from the time scale of the events you want to keep.
- **Different sampling grids.** Resample to a common grid first. Aggregation erases what happens inside each interval, and interpolation invents values between observations.
- **Gaps.** Know why they are there. In *Forecasting: Principles and Practice* the authors note that missingness can be tied to events and then bias a model, and that some methods accept missing values while others fail on them. Replacing gaps by estimates is a choice to report next to the distance. The default of `pandas.DataFrame.interpolate` is `linear`, which treats the values as equally spaced and ignores the index, so on an irregular time index the `time` method is the one that follows the timestamps.

![The twelve days of the fixture, 48 half-hour readings each, all on one shared scale from 0 kW](figures/demand-12.svg)

On the twelve days, inside each kind of day the base level, the height and the timing differ a little. A question about shape wants level and scale erased, a question about the hours of load wants them kept. The data does not choose.

## In finance

Preprocessing answers the question of what a price series is compared on: its level, or its changes. Prices carry a trend, returns do not. In their textbook, Hyndman and Athanasopoulos define a stationary series as one whose statistical properties do not depend on the time of observation, state that series with trends are not stationary, and show the daily change in a stock price as a stationary example. The same question, with several answers, appears for the choice of the change itself: [Mantegna (1999)](https://arxiv.org/abs/cond-mat/9802256) uses the daily difference of the logarithm of the closing price and notes that it almost coincides with the return.

Empirical applications:

- **Stocks.** Mantegna (1999) clusters the stocks of the Dow Jones Industrial Average and of the S&P 500 index, from July 1989 to October 1995, on correlations of daily log price differences, not of prices.
- **Stocks, time windows.** [Onnela et al. (2003)](https://arxiv.org/abs/cond-mat/0302546) build trees from correlations of daily returns of stocks traded on the New York Stock Exchange from 1980 to 1999, in moving windows. They report that during market crashes the global correlation is strong and the mean occupation layer of the tree drops.
- **Currencies.** [Mizuno, Takayasu and Takayasu (2006)](https://arxiv.org/abs/physics/0508164) build minimal spanning trees from foreign exchange data. They find clusters that largely follow geographic regions.

Limitations in financial time series:

- **Levels of random walks.** [Granger and Newbold (1974)](https://doi.org/10.1016/0304-4076(74)90034-7) simulate regressions between independent random walks of length 50. The usual t test at the 5% level rejects the absence of a relationship in about three quarters of the cases. They recommend taking first differences of highly autocorrelated variables. The study concerns regression of economic series, not distances between series.

## Common mistake

Preprocessing a dataset as a whole, with one rule, because it is convenient, and then reading the distance as if nothing had been erased. Each step takes out a property of every series. Decide the steps from the question, apply them to each series on its own, and write them next to the distance.
