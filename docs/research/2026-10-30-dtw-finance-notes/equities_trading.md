# Published applications of DTW to equities and trading

Read level key: FULL = I read the full text (via pdftotext of the open PDF), ABS = abstract or publisher/catalogue record only, SNIP = only a search-result summary (unverified). KOSPI 200 futures, index futures and cash-index items are marked as borderline (derivatives are another researcher's strand). Search was limited (about 20 calls). Coverage is not exhaustive.

## 1. Pairs trading / statistical arbitrage pair selection with DTW, out-of-sample after costs

### Takeaway
One strong, peer-reviewed example exists: Stübinger (Quantitative Finance 2019) uses a causal variant of the DTW warping path to pick lead-lag pairs on S&P 500 minute data and reports positive after-cost returns. It is a constrained DTW variant, not plain DTW, and it is a lead-lag directional strategy rather than classic mean-reversion pairs trading. I found no other verified DTW pairs-trading study with after-cost out-of-sample results.

### Cited Findings
- Stübinger, J. (2019), "Statistical arbitrage with optimal causal paths on high-frequency data of the S&P 500", Quantitative Finance 19(6), 921-935, DOI 10.1080/14697688.2018.1537503 (peer-reviewed). Venue confirmed by [RePEc record](https://ideas.repec.org/a/taf/quantf/v19y2019i6p921-935.html) via search. Earlier version: FAU Discussion Paper 01/2018. Read level: FULL of the 2018 working paper (not the journal version, which is paywalled; numbers may differ in the final version). — [FAU working paper PDF](https://www.iwf.rw.fau.de/files/2018/01/01_2018-1.pdf)
  - What was done: develops an "optimal causal path" algorithm, a DTW-type warping path with a causality constraint, that gives the lag between two return series. All S&P 500 pairs (500*499/2 = 124,750 per study period) are scored in a formation period. The top s=10 pairs with the lowest standard deviation of the lag, non-zero lag and no lead-lag change, go to trading. In the trading period the leader's return predicts the follower's return. Trades open when the follower's expected move exceeds an economic threshold.
  - Data: minute-by-minute S&P 500 constituents, January 1998 to December 2015. Each study period is a 1-day formation (391 minutes) plus a 1-day out-of-sample trading period, rolled forward by one day. Input is minute returns.
  - DTW settings: no global window ("avoids any restrictions on the warping path"). Parameters d=20, k=2.5 (Bollinger-style bands), top 10 pairs.
  - Costs: 4 basis points per share per round trip (following Prager et al. 2012).
  - Results (working paper abstract and text): 54.98% p.a. after costs, annualised Sharpe 3.57, daily return 18 bp after costs vs 2 bp for the S&P 500, Newey-West t-stat at least 6.46 for all variants, hit ratio 57.37%, no loading on common risk factors. Benchmarks on correlation, Manhattan distance and lagged cross-correlation earn 8 bp/day or more after costs but less than the causal-path variant. By sub-period, OCP annualised returns after costs were above 120% (Sharpe 8.80) in 1998-2003, 59.70% in 2003-2008, and 14.66% in 2009-2015. The paper states that all strategies declined from January 2012 onward.
  - Limits (evident): performance decays strongly after 2009; kurtosis 631.89 driven by one outlier; the cost assumption (4 bp per share per round trip) may be optimistic for minute-level trading and no market impact or short-borrow costs seem modelled (I did not find them in the passage read; not confirmed absent). The 2018 version also tests Bitcoin, where the author says stock returns contain information about future bitcoin returns.
- The same paper says only two earlier academic studies used DTW in a statistical arbitrage setting: Chinthalapati (2012), a directional strategy on intraday data of 97 NYSE stocks on a single day (1 Jan 2006 as stated; the author notes it is not statistical arbitrage in the Avellaneda-Lee sense), and Kim and Heo (2017). — [FAU working paper](https://www.iwf.rw.fau.de/files/2018/01/01_2018-1.pdf)
- Kim, S. and Heo, J. (2017), "Time series regression-based pairs trading in the Korean equities market", Journal of Experimental & Theoretical Artificial Intelligence 29(4), 755-768. Per the FAU paper it uses DTW to detect similar patterns on daily prices of KOSPI 100 stocks, January 2005 to June 2015. Read level: only a citation by the FAU paper plus a bibliographic record. DTW settings, costs and results not confirmed. — [Korea University record](https://scholar.korea.ac.kr/handle/2021.sw.korea/86378) (not opened by me; surfaced in search)
- Li, S., Cheng, D., Liu, L. (arXiv 2601.13435, v4 March 2026, preprint), "A Learnable Wavelet Transformer for Long-Short Equity Trading and Risk-Adjusted Return Optimization". DTW is only a stock filter: within each industry, stocks whose DTW distance (log-change series, fixed look-back) to the industry reference is below the training-period median are kept, then pruned with non-parametric Granger tests. Data: hourly OHLCV bars of US stocks, roughly 10 years (polygon.io), industry lists from StockAnalysis. Reported WaveLSFormer cumulative return 0.607 and Sharpe 2.157; transaction costs are explicitly ignored in the formulation I read. The DTW filter is not ablated in the passages I read. Read level: FULL text partly (data and method sections read; results not checked in depth). — [arXiv PDF](https://arxiv.org/pdf/2601.13435)
- NCCU (Taiwan) theses on DTW with K-medoids and fuzzy c-medoids for stock selection exist (reported higher-return stocks). Read level: SNIP only, thesis, not verified. — [NCCU thesis record](https://thesis.lib.nccu.edu.tw/thesis/detail/904f6462b130ef45af821b4dc9f0f47f)

### Inferences
- Plain-DTW pairs selection with verified after-cost out-of-sample results appears very rare. The one strong result uses a causal DTW variant and minute data, and a report writer should not present it as evidence for plain DTW on prices.
- The post-2009 decay in Stübinger is consistent with the general decline of pairs-trading profits.

### Gaps
- Journal-version numbers of Stübinger (2019) were not checked.
- Kim and Heo (2017) details unverified.
- No hit on "DTW vs cointegration/distance method" head-to-head after costs.

## 2. Stock clustering, peer or sector discovery, portfolio diversification

### Takeaway
Several peer-reviewed papers and many smaller studies use DTW for clustering stocks and building diversified portfolios, mostly reporting favourable backtests versus correlation-based clustering. I could read only abstracts for most, so details (settings, costs) are missing.

### Cited Findings
- Lim, T. and Ong, C. S. (2021), "Portfolio diversification using shape-based clustering", Journal of Financial Data Science 3(1), 111-126, DOI 10.3905/jfds.2020.1.054 (peer-reviewed). Agglomerative hierarchical clustering with DTW as the distance to group stocks into like-trending clusters. The abstract says results support portfolio allocation and rebalancing, dynamic predictive portfolio construction, and stock selection via outlier identification. Read level: ABS. Data and settings not obtained. — [EconBiz record](https://www.econbiz.de/Record/portfolio-diversification-using-shape-based-clustering-lim-tristan/10012486256)
- Lim, T. and Ng, H. (2023), "Financial Portfolio Management Based on Shaped-Based Unsupervised Machine Learning: A Dynamic Time Warping Barycenter Averaging Approach to International Markets and Periods of Downside Event Risks", Journal of Investing 32(2), DOI 10.3905/joi.2022.1.251. Abstract: DTW cluster diversification beat correlation-based diversification on mean and median returns and Sharpe in international developed markets, including downside periods. Read level: ABS via search summary only (publisher page returned 403, I did not bypass). Sample period and costs unknown. — [EBSCO record](https://www.ebsco.com/articles/business-and-management/f3b1bb79-f850-581d-85c0-852c4c161be0/financial-portfolio-management-based-on-shaped-based-unsupervised-machine-learning-a-dynamic-time-warping-baycenter-averaging-approach-to-international-markets-and-periods-of-downside-event-risks)
- Lee, S. and Jeong, J. (2025), "Portfolio optimization using a covariance structure based on dynamic time warping", Finance Research Letters 83, DOI 10.1016/j.frl.2025.107642 (peer-reviewed). Two DTW-based covariance estimators (Transformed DTW, Covariance DTW with a spatial covariance function), tested in Maximum Diversification, Equal Risk Contribution and Hierarchical Risk Parity portfolios on US stocks. Abstract: outperform traditional covariance structures and give smaller weight changes at rebalancing. Read level: ABS (fetched [IDEAS record](https://ideas.repec.org/a/eee/finlet/v83y2025ics1544612325009018.html)). Sample, window, costs unknown.
- Çelik, Özdemir Höl, Demir (2025), Abant Sosyal Bilimler Dergisi: DTW-based diversification vs Markowitz on 20 BIST30 stocks (Turkish, English abstract). Read level: SNIP. — [DergiPark](https://dergipark.org.tr/tr/download/article-file/4368499)
- Indonesian studies: Cluster analysis of Indonesian stock prices using DTW (Parameter journal, hierarchical clustering of the ten largest-cap IDX stocks as of February 2026; argues clusters cut across sector labels) — [OJS record](https://ojs3.unpatti.ac.id/index.php/parameter/article/view/25010); portfolio formation with K-medoid DTW (Jurnal Aplikasi Statistika & Komputasi, STIS), reported to beat comparison portfolios — [record](https://jurnal.stis.ac.id/index.php/jurnalasks/id/article/view/295); LQ45 K-medoids DTW thesis (Undip, abstract only). Read level: SNIP for all; small samples, low-tier venues.
- Vitulano et al. (Sapienza, working paper): hierarchical clustering of S&P 500 securities on the dynamics of their Sharpe ratios with DTW, then Most Diversified Portfolio weighting. Read level: SNIP. — [PDF](https://www.dss.uniroma1.it/it/system/files/pubblicazioni/Paper_VitulanoM.pdf)
- "Trimmed fuzzy clustering of financial time series based on dynamic time warping" (Annals of Operations Research per the catalogue records; I did not confirm authors or year). Read level: SNIP. — [Sapienza record](https://research.uniroma1.it/en/node/52748)
- A search summary of a JMP/SMU poster says no clustering method (DTW or Euclidean) consistently wins across datasets. Not verified at source. — [SMU record](https://ink.library.smu.edu.sg/sis_research/7238)
- He and Li: "A New Boosting Algorithm for Online Portfolio Selection Based on Dynamic Time Warping and Anti-correlation" (Anticor with DTW similarity). Read level: SNIP, venue and year unconfirmed. — [AMiner](https://aminer.org/pub/645d071ad68f896efaa33234/a-new-boosting-algorithm-for-online-portfolio-selection-based-on-dynamic-time)

### Inferences
- Within the peer-reviewed set (Lim and Ong 2021, Lim and Ng 2023, Lee and Jeong 2025) the claim is a diversification or Sharpe improvement versus correlation baselines, but I could not verify data, costs or statistical tests.
- Most clustering studies use price level or return shape; handling of prices vs returns is rarely stated in abstracts.

### Gaps
- No full text of any clustering paper was read; transaction costs, window and normalisation unknown.
- Whether DTW clusters recover sectors or add information beyond correlation was not established from a verified source.

## 3. Lead-lag detection between stocks or markets

### Takeaway
Zhang et al. (2023, arXiv) is the main DTW lead-lag paper on stocks, with weak (Sharpe below 1) results and no costs. Stübinger (section 1) is the other. Index-futures/cash studies exist (borderline scope).

### Cited Findings
- Zhang, Y., Cucuringu, M., Shestopaloff, A. Y., Zohren, S. (2023), "Dynamic Time Warping for Lead-Lag Relationships in Lagged Multi-Factor Models", arXiv:2309.08800 (q-fin.ST, preprint; a search snippet suggests an ICAIF-linked version, not confirmed). Read level: FULL (pdftotext). — [arXiv](https://arxiv.org/pdf/2309.08800v1.pdf)
  - What: cluster-based DTW (K-medoids on DTW distances) to detect lead-lag among assets in a lagged multi-factor model, then trading baskets built from leaders to predict laggards. Compared with cross-correlation-based benchmarks.
  - Data: daily close-to-close adjusted returns from CRSP, 679 US equities, 2000-01-03 to 2019-12-31 (5211 days); 14 ETFs, 2006-2019; 52 futures, 2000-2020. Returns are market excess returns (S&P Composite subtracted, beta assumed 1) and winsorised. Sliding window of length 21 days for the lead-lag matrix.
  - DTW settings: Sakoe-Chiba-style window size S, with a synthetic study showing error is lower for S around or above the true lag; squared/Euclidean point cost.
  - Results: on equities, the Dα strategy with DTW KMed Med reached Sharpe about 0.93 after 2008. Other Sharpes in the 0.3-0.9 range. On ETFs Sharpes of 0.78-0.8 for some variants, but no consistent profitability for the Gβ strategy; on futures no consistent profitable lead-lag. PnL excludes transaction costs (stated in the metric definition).
  - Limits: no costs, modest Sharpes, no profitability on ETFs/futures for the Gβ strategy, daily data only (authors suggest intraday as future work).
- Ma et al. (2022), "Measuring the dynamic lead-lag relationship between the cash market and stock index futures market", Finance Research Letters 47(PB): DTW-based nonparametric dynamic lead-lag measures between index futures and the cash index. Borderline scope (index futures). Read level: SNIP. — [IDEAS](https://ideas.repec.org/a/eee/finlet/v47y2022ipbs1544612322002008.html)
- Xiao, Ma, Mi (2023), Economic Research-Ekonomska Istraživanja 36(1), 1549-1569: uses that measure on CSI 300 futures. Futures lead the cash index by 0-5 minutes but sometimes lag. Borderline scope. Read level: SNIP. — [IDEAS](https://ideas.repec.org/a/taf/reroxx/v36y2023i1p1549-1569.html)
- Ito and Sakemoto (2019), Asia-Pacific Financial Markets: multinomial DTW for non-synchronous, time-varying lead-lag; the application asset class was not confirmed by me. Read level: SNIP. — [researchmap](https://researchmap.jp/rsakemoto/published_papers/27062709?lang=en)
- Gupta and Chatterjee (arXiv 2004.10560) propose a lead-lag measure for stock series and say exact best-path computation is intractable, so it is not strictly DTW. Read level: SNIP. — [arXiv](https://arxiv.org/pdf/2004.10560)

### Inferences
- Gains from DTW in lead-lag detection are concentrated at the high-frequency end (Stübinger) or modest at daily frequency (Zhang et al.).

### Gaps
- Zhang et al. publication status and the exact point cost/normalisation not pinned down. Ito and Sakemoto and Gupta details unverified.

## 4. Pattern matching, analogue forecasting, intraday profiles

### Takeaway
DTW chart-pattern and analogue approaches have peer-reviewed support from Tsinaslanidis (2017) and Tsinaslanidis and Guijarro (2021), with mixed significance. I found no verified DTW work on intraday volume or volatility curves.

### Cited Findings
- Tsinaslanidis, P. E. (2017/2018), "Subsequence dynamic time warping for charting: Bullish and bearish class predictions for NYSE stocks", Expert Systems with Applications 94, 193-204, DOI 10.1016/j.eswa.2017.10.055 (peer-reviewed). Subsequence DTW and derivative DTW on price and volume sequences label query patterns as bullish or bearish by what followed similar historical patterns. Many NYSE stocks, data 2006-2015, out-of-sample 2010-2015. Bearish predictions statistically significant with significant average maximum potential profits; bullish measures not significant. Read level: ABS (publisher-hosted abstract via [Canterbury record](https://pure.canterbury.ac.uk/en/publications/subsequence-dynamic-time-warping-for-charting-bullish-and-bearish-2/)). Window and costs unknown.
- Tsinaslanidis, P. E. and Guijarro, F. (2021), "What makes trading strategies based on chart pattern recognition profitable?", Expert Systems 38(5), DOI 10.1111/exsy.12596 (peer-reviewed). Generic pattern recognition with the UCR-suite fast DTW; 560 NYSE stocks; controls for data snooping and transaction costs; varies pattern length, take-profit and stop-loss and past-performance consensus. System dominates the market index in mean-variance terms on average; costs reduce profitability; 92.5% of experiments are profitable when parameters match technical-analysis conventions. Read level: ABS. DTW window, period and cost level not obtained. — [RiuNet record](https://riunet.upv.es/handle/10251/185285)
- Kim, Lee, Ko, Jeong, Byun, Oh (2018), "Pattern Matching Trading System Based on the Dynamic Time Warping Algorithm", Sustainability 10(12), 4641 (MDPI, peer-reviewed). DTW matches morning patterns to 13 and 27 representative patterns to choose the afternoon exit for KOSPI 200 index futures. Borderline scope (futures). Read level: ABS. Authors report stable, effective strategies with low trading frequency; numbers not obtained. — [IDEAS](https://ideas.repec.org/a/gam/jsusta/v10y2018i12p4641-d188468.html)
- Jeon, Hong, Chang (2018), Future Generation Computer Systems: DTW finds historical segments resembling the current pattern, selected features then feed a neural net to predict daily prices. Read level: SNIP (details unverified; I did not confirm full authors/title). — [XJTLU record](https://scholar.xjtlu.edu.cn:443/en/publications/pattern-graph-tracking-based-stock-price-prediction-using-big-dat)
- Chang et al. (2011), piecewise linear representation plus DTW and a neural network for turning-point buy/sell signals; Fu et al. (2007) compare template-based vs rule-based pattern matching; Udagawa (2017) modified longest common substring vs DTW on Nikkei patterns. Read level: SNIP; venues and results unverified. — [NSYSU PDF](https://par.cse.nsysu.edu.tw/resource/paper/2011/110919/Integrating%20a%20Piecewise%20Linear%20Representation%20Method%20with%20Dynamic%20Time%20warping%20system%20for%20Stock%20Trading%20Decision%20Making.pdf)
- Master's theses (not peer-reviewed): NOVA School of Business 2012 on DTW trading strategies on equity indexes, reported modest results; Politecnico di Torino thesis noting DTW's practical utility for recurring patterns is unsettled. Read level: SNIP. — [NOVA](https://run.unl.pt/handle/10362/9539), [Polito](https://webthesis.biblio.polito.it/39690/1/tesi.pdf)
- Intraday profiles: searched and found no DTW study on intraday volume or volatility curves of stocks. A Chinese paper (J. Data Acquisition and Processing, 2015) adds a trading-volume factor to DTW similarity for stock series (SNIP only). — [NUAA record](https://sjcj.nuaa.edu.cn/sjcjyclen/article/abstract/20150109)

### Inferences
- The strongest evidence for DTW-based pattern strategies, the Tsinaslanidis papers, is asymmetric (bearish only) or conditional on parameter choices, and costs reduce profits.

### Gaps
- Intraday volume or volatility curve applications: not found (absence of evidence in a limited search).
- No full text read for any section 4 paper.

## 5. Events (earnings, news)

### Takeaway
I found no published study applying DTW to earnings or news reactions of stocks.

### Cited Findings
- A search for DTW with earnings announcements returned only generic earnings-reaction literature, nothing DTW-specific. — search only, no source to cite.

### Gaps
- Need a targeted search ("event study" + "time series clustering", "DTW news sentiment") before concluding none exists.

## 6. Venue classification (peer-reviewed vs other)

### Takeaway
Peer-reviewed: Stübinger 2019 (Quantitative Finance), Lim and Ong 2021 (JFDS), Lim and Ng 2023 (Journal of Investing), Lee and Jeong 2025 (Finance Research Letters), Tsinaslanidis 2017 (ESWA), Tsinaslanidis and Guijarro 2021 (Expert Systems), Kim et al. 2018 (Sustainability, futures), Ma et al. 2022 (FRL, futures), Xiao et al. 2023 (futures), Kim and Heo 2017 (JETAI). Preprints: Zhang et al. 2023 (arXiv), Li et al. 2026 (arXiv), FAU discussion paper 2018. Theses: NCCU, NOVA, Polito, Undip. Regional or low-tier journals: Indonesian and Turkish items.

### Gaps
- No blog posts were examined. Zhang et al. possible conference publication not confirmed.
- Publisher pages (T&F, EBSCO, MDPI) returned 403 to fetches and were not bypassed.
