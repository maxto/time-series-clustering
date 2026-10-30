# DTW applications in derivatives, futures, FX, commodities, rates, credit and crypto markets

Scope note: about 20 tool calls (web search and fetch). Reading status is stated per study: FULL = full text read (PDF or arXiv/publisher text), ABSTRACT = abstract or catalogue record only, SECONDARY = known only through another paper's or a search engine's description. Abstract-level items are paraphrased from fetch summaries, not verbatim. The overall literature is thin and clustered in a few author groups (Vatsa/Miljkovic, Gronwald, Mastroeni, Wang/Xie). Absences are findings and are listed per question.

## Is DTW used on futures (trend following, spread trading, contract similarity, term structure shapes)?

### Takeaway
Yes, but almost only for lead-lag and price discovery between futures and spot (energy, agricultural, equity-index futures) and, in one 2019 paper, for DTW-based direction forecasting of crude oil. I found no published study using DTW for trend following, calendar or inter-commodity spread trading, futures-contract similarity matching, or term-structure shape comparison.

### Cited Findings
- Vatsa, Miljkovic and Miljkovic (2024), "Price discovery redux: Analyzing energy spot and futures prices using a dynamic programming approach", Energy Economics 140, DOI 10.1016/j.eneco.2024.107965. DTW used to test whether crude oil and natural gas futures lead spot prices. Findings: natural gas futures led spot more often in 2019-2023 than in the preceding five years. Crude oil futures more often lagged spot. Futures did not consistently perform price discovery, and short-term contracts looked more influential than long-term ones. Authors argue DTW copes with small samples and different integration orders and detects nonlinear relations. Read: ABSTRACT only (IDEAS page, full text is paywalled). Data frequency, period, and DTW settings not confirmed by me. — [IDEAS](https://ideas.repec.org/a/eee/eneeco/v140y2024ics014098832400673x.html)
- Miljkovic and Vatsa (2026), "Price Discovery in the United States Ethanol Markets: A Dynamic Time Warping Approach", Journal of Agricultural and Resource Economics 51(3), DOI 10.22004/ag.econ.376276. Ethanol spot and futures prices in three US markets (Chicago, Omaha, Stockton per a search summary), lead-lag varies significantly across regions and over time, ties to market structure and supply/energy volatility, method can identify fast reversals in leadership. Read: NOT read. The IDEAS record has no abstract and no year, the details come from a search-engine summary of the USC repository page, so treat as unconfirmed. Note: a search summary also said crude oil futures enter as a lead-lag variable, which I could not confirm. — [IDEAS record](https://ideas.repec.org/a/ags/jlaare/376276.html); [USC repository](https://research.usc.edu.au/esploro/outputs/journalArticle/Price-Discovery-in-the-United-States/991214651102621)
- Same group on corn: "An investigation of the price discovery role of futures markets: a dynamic time warping analysis of the United States corn markets", Agribusiness (DOI 10.1002/agr.21939). Reported by a search summary: futures are critical to price discovery but spot dominates intermittently. Authors, year and details NOT confirmed. Read: NOT read. — [citedrive](https://www.citedrive.com/en/discovery/an-investigation-of-the-price-discovery-role-of-futures-markets-a-dynamic-time-warping-analysis-of-the-united-states-corn-markets)
- Xiao, Ma and Mi (2023), "The time-varying lead-lag relationship between index futures and the cash index and its factors", Economic Research - Ekonomska istrazivanja 36(1), 1549-1569. CSI 300 index futures vs CSI 300 cash index, intraday and daily, with a new DTW-based method. Findings: futures usually lead cash by 0 to 5 minutes, occasionally lag. The lead shrinks as market volatility rises and as futures trading activity grows relative to cash. Read: ABSTRACT only. Exact sample period and DTW settings not confirmed. (Equity-index futures: borderline for this strand, flagged for the equity researchers.) — [Hrcak](https://hrcak.srce.hr/en/304178)
- Howard, Putnins and Alexeev (2022): per Zhang et al., DTW found that global price discovery oscillates between S&P 500 futures and FTSE 100 futures. SECONDARY only, I could not locate the original paper, venue unknown. — [arXiv 2309.08800 via search summary](https://arxiv.org/pdf/2309.08800v1.pdf)
- Zhang, Cucuringu, Shestopaloff and Zohren (2023), "Dynamic Time Warping for Lead-Lag Relationships in Lagged Multi-Factor Models", arXiv:2309.08800 (q-fin.ST), preprint, not shown as peer-reviewed on the page. Proposes a DTW-based clustering method for lead-lag detection, linked to the multireference alignment problem. Abstract claims detection in financial markets and "significant economic benefits" in trading. Data, DTW settings and numbers not visible in what I fetched (abstract page only). A search summary says it was presented at ICAIF 2023 (unconfirmed). Arxiv comment notes substantial text overlap with arXiv:2305.06704. Whether instruments include futures is NOT confirmed. Read: ABSTRACT only. — [arXiv](https://arxiv.org/abs/2309.08800)
- "A hybrid method for crude oil price direction forecasting using multiple timeframes dynamic time wrapping and genetic algorithm", Applied Soft Computing 82 (2019), article 105566. Multiple DTW over daily and weekly data to retrieve similar series, genetic algorithm tunes parameters, simulated trading, forecast treated as strong only when timeframes agree. Authors, instrument (spot or futures), period and trading results NOT confirmed. Read: search summary only. — [Unpaywall record](https://unpaywall.org/10.1016%2Fj.asoc.2019.105566)
- Retail tool pages (LuxAlgo, MQL5, StrategyQuant) offer DTW pattern-matching indicators and warn that backtests of DTW analog systems overfit easily (window length, band width and normalisation add degrees of freedom). Not research. — [LuxAlgo](https://www.luxalgo.com/library/concept/dynamic-time-warping-similarity/)

### Inferences
- The futures literature uses DTW as a time-varying lead-lag detector (the alignment offset along the warping path is read as lead or lag), not as a similarity metric between contracts.
- Evidence of trading profitability from DTW on futures is limited to unverified claims in one preprint abstract and one 2019 oil paper.

### Gaps
- No study found on DTW for trend following, calendar spreads, inter-commodity spreads, roll yield, contract similarity or futures term-structure (curve) shapes. Searches for "futures contracts similarity" returned only the lead-lag/price-discovery papers above.
- Full texts of Vatsa et al. 2024, the ethanol and corn papers, Xiao et al. 2023, Zhang et al. 2023 and the 2019 oil paper not read, so data, window constraints and numeric results are missing.

## Is DTW used on options or volatility (implied volatility surfaces, VIX, realised volatility patterns)?

### Takeaway
Essentially no peer-reviewed work found. The only hits are a student project page on VIX regimes and a fuzzy-clustering paper on DTW applied to financial series (volatility not confirmed as its object).

### Cited Findings
- A Virginia Tech student project applies DTW, soft-DTW and GAK k-means to VIX, the dollar index and oil to find regimes, and reports interpretable regimes for macro assets. Not peer-reviewed, details not verified. — [project page](https://sites.google.com/vt.edu/regime-detection/results)
- Prakash, James, Menzies and Gilad, "Structural clustering of volatility regimes for dynamic trading strategies" (arXiv 2004.09963) clusters volatility segments and matches current distributions to past regimes. A search snippet did not say it uses DTW, so I treat it as non-DTW and do not claim otherwise. — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.09963)
- "Trimmed fuzzy clustering of financial time series based on dynamic time warping" (Sapienza repository record) clusters multivariate financial series with DTW and PAM. Authors, year, venue and whether volatility series are the object were NOT confirmed (a search summary suggested volatility among applications). Read: NOT read. — [Sapienza](https://research.uniroma1.it/en/node/52748)

### Inferences
- An absence of DTW on implied-volatility surfaces, term structures of vol, skew or option prices is a finding for the course: not found in these searches.

### Gaps
- No DTW paper on implied volatility surfaces, VIX futures term structure, realised-volatility pattern matching or option pricing found. Only two search queries targeted this (plus one broad one). A deeper SSRN/Google Scholar pass could still find something.

## Is DTW used on FX, commodities, rates or credit (yield curve shapes, CDS spreads)?

### Takeaway
FX and commodities: yes, with a handful of clustering/network studies. Rates and credit: nothing found. Searches for yield-curve, term-structure, sovereign bond and CDS DTW returned no DTW application (only unrelated wavelet/Nelson-Siegel papers and computational-geometry DTW papers).

### Cited Findings
- Wang, Xie, Han and Sun (2012), "Similarity measure and topology evolution of foreign exchange markets using dynamic time warping method: Evidence from minimal spanning tree", Physica A 391(16), 4136-4146. DTW similarity networks and MSTs of 35 major currencies, June 2005 to May 2011, split before, during and after the US sub-prime crisis, New Zealand dollar as numeraire. USD and EUR remain dominant, USD loses its central position over the crisis, EUR is a stable centre, after the crisis the Singapore dollar becomes a new centre. Motivation: avoid the synchronous restriction of Pearson correlation. Read: ABSTRACT only (frequency, DTW settings not confirmed). — [IDEAS](https://ideas.repec.org/a/eee/phsmap/v391y2012i16p4136-4146.html)
- Landmesser and Orlowski (FENS 2021 contribution): DTW distances and hierarchical clustering of currencies to see how COVID-19 relates to exchange-rate changes, per a search summary. Read: NOT read, details unconfirmed. — [FENS2021 PDF](https://indico.fis.agh.edu.pl/event/69/contributions/243/attachments/168/268/FENS2021_J_Landmesser_A_Orlowski.pdf)
- Karademir (2015) conference paper combining DTW with longest common subsequence to cluster countries (G8, BRICS, Turkey) before studying exchange rate and stock price links, per a search summary. Not read, unverified. — [IDEAS](https://ideas.repec.org/p/sek/iacpro/2804863.html)
- Smiech (2014), "Co-movement of commodity prices - results from dynamic time warping classification", MPRA Paper 56546 (Cracow University of Economics working paper). FULL text read. Data: 54 World Bank monthly commodity price series (energy, metals, food, raw materials; spot/index prices, not futures), Jan 2001 to Feb 2014 (abstract mentions 1990 to Feb 2014 for the broader data), indexed to 2007 = 1, split into 2001:1-2008:6 and 2009:1-2014:2. DTW distances (Euclidean local distance, no window mentioned in what I read) then Ward, complete linkage and PAM, cluster count by silhouette. Findings: co-movement more evident in the pre-crisis period, only a few paths determine commodity prices. Pre-crisis three clusters, average silhouette 0.43. Post-crisis clusters look more like energy, metals and food groups, with WTI oil in a different cluster from the other oil prices. Limit: working paper, spot indices, no out-of-sample or economic test. — [MPRA](https://mpra.ub.uni-muenchen.de/56546/1/MPRA_paper_56546.pdf)
- Mastroeni, Mazzoccoli, Quaresima and Vellucci (2021), "Decoupling and recoupling in the crude oil price benchmarks: An investigation of similarity patterns", Energy Economics 94, 105036, DOI 10.1016/j.eneco.2020.105036. DTW to detect WTI-Brent decoupling episodes, proposes Relative-Alignment Index and Warping Index, finds benchmarks decouple and recouple in line with local WTI market conditions, not fully integrated at all times. Read: ABSTRACT only (data and settings not confirmed). — [Roma Tre IRIS](https://iris.uniroma3.it/handle/11590/417942)
- Gronwald and Zhu (2026), "One Great Pool or Many? Measuring Global Oil Market Integration Using a Dynamic Time Warping-Hierarchical Cluster Approach", CESifo Working Paper 12723 (June 2026; paper dated May 2026). FULL text read. Data: monthly nominal spot crude prices, ten grades (Algerian Saharan, Bonny Light, Brent, Dubai, Oman, Saudi Heavy, Tapis, West Texas Sour, WTI Cushing, WTI Midland), Jan 2000 to Mar 2026, Bloomberg and DataStream. Settings: z-normalisation of each series, Sakoe-Chiba constraint |i-k - j-k| <= r (value of r not found in what I read), Ward.D2 hierarchical clustering, silhouette width and cophenetic correlation as validation, 60-month rolling windows with 1-month step, Adjusted Rand Index between consecutive windows (ARI 0.961 quoted for one comparison), also Warping Index (mean |i_k - j_k| along the path, introduced by Mastroeni et al.) and Warping Path Distance. Findings: markets cluster by geography (West Africa, Middle East, US, Brent intermediate), integration increases over time, regional structure stable, during 2020-2024 integration rises but the geographic pattern weakens. Limit stated: with k fixed at 3 a residual third cluster is forced. Spot prices, not futures. Very recent, not peer-reviewed. — [CESifo PDF](https://www.ifo.de/sites/default/files/docbase/docs/cesifo1_wp12723.pdf)

### Inferences
- In the oil work DTW is used to measure integration and (de)coupling, and the Warping Index (average distance of the path from the diagonal) is a ready-made measure of lead-lag/misalignment that fits the course's DTW lesson.
- Wang et al. (2012) is a good example of a crisis-split comparison of similarity networks in FX.

### Gaps
- No DTW study found on yield curves, term structures, government bond yields, interest-rate swaps, CDS spreads or credit spreads. Absence reported after a general query and a yield-curve/term-structure query, no CDS-specific DTW query returned anything.
- No DTW FX study found that tests trading or forecasting value. Details of Landmesser-Orlowski and Karademir not verified.
- Mastroeni et al. 2021 data and window settings not read.

## Is DTW used on crypto assets (clustering, lead-lag)?

### Takeaway
Yes, in a few papers. Mostly applied as clustering or as a lead-lag module inside a forecaster. Evidence of predictive or trading value is weak or from preprints and student work.

### Cited Findings
- Sigaki, Perc and Ribeiro (2019), "Clustering patterns in efficiency and the coming-of-age of the cryptocurrency market", arXiv:1901.04967v1 (q-fin.ST); I believe it was later published in Scientific Reports but did not confirm the venue. FULL text read. DTW is applied not to prices but to a time-varying informational-efficiency series E_t (built from permutation entropy and statistical complexity over 500-day windows of log returns, then a 360-day window) for 167 cryptocurrencies (those with more than 460 observations, from 400+ studied). Average-linkage hierarchical clustering of the DTW matrix, cut at the DTW distance 5.7 chosen by maximal silhouette coefficient gives four groups (43%, 26%, 12%, 19% of coins): constant high efficiency, high-low-high, decreasing, increasing. Example distances: BitcoinDark vs Diamond 3.64. Implementation: Python dtaidistance and SciPy. No window constraint value found. Limit: clusters describe efficiency profiles, not prices. — [arXiv PDF](https://arxiv.org/pdf/1901.04967)
- Li, Gong, Xu, Zhou, Shanqing and Xuan (2022), "Cross Cryptocurrency Relationship Mining for Bitcoin Price Prediction", arXiv:2205.00974 (q-fin.ST), preprint. DTW detects lead-lag between Bitcoin and altcoins, building a Lead-lag Variance Kernel to aggregate altcoin information (module C2RM). Authors report significant improvements for existing predictors. Data and numbers NOT read (abstract page only). — [arXiv](https://arxiv.org/abs/2205.00974)
- Liston, Gretton and Lensky (2024), pattern-based trading with continual learning of price and volume patterns grouped with DTW, tested on BTCUSDT 2017-2023 and 2023-2024 per a search summary. Title, venue and results only seen in a repository snippet, not read. — [ANU repository](https://openresearch-repository.anu.edu.au/entities/publication/52f2798c-dec4-4fe2-9b3c-fb5be1e43e1c)
- "Analysis of the Top 30 cryptocurrencies" (MDPI Mathematics 10(19), 3672, 2022) applies DTW before clustering and forecasting per a search summary. The MDPI page returned 403 so I did not read it, title and authors unconfirmed. — [MDPI](https://mdpi.com/2227-7390/10/19/3672)
- "Deep Fusion of Lead-lag Graphs: Application to Cryptocurrencies" (arXiv 2201.02040) uses DTW for lead-lag extraction among altcoins per a search summary. Not read. — [mirror](https://arxiv.deeppaper.ai/papers/2201.02040v2)
- A 2025 CCT College Dublin thesis (DTW asset clustering plus cross-correlation, Granger and VAR lead-lag) reports mostly homogeneous clusters and lead-lag that appeared only occasionally and shifted across regimes. Student thesis, not read. — [CCT](https://arc.cct.ie/ict/121)
- Parasrampuria and Williams, "The Application of Dynamic Time Warping on Ethereum Price Prediction", Journal of Student Research (high school). DTW retrieves similar past sequences for an LSTM. Student journal, not read. — [JSR](https://www.jsr.org/hs/index.php/path/article/view/8196)

### Inferences
- I found no independent out-of-sample evidence that DTW pattern matching predicts crypto returns. Treat the crypto prediction claims as preprint-level.

### Gaps
- Full texts of Li et al. 2022, the Top-30 paper, the ANU paper and the deep-fusion paper not read, so data and gains are not quantified. No DTW study found on crypto derivatives (perpetuals, options).

## Is DTW used for market contagion, crisis comparison or regime similarity (comparing a crash to past crashes), or macro nowcasting relevant to markets?

### Takeaway
Crisis-period comparison appears indirectly (before/after-crisis splits in Smiech 2014, Wang et al. 2012, Gronwald-Zhu 2026), and one industry note aligns stock bubble episodes. I found no academic study that ranks a specific crash against past crashes with DTW or applies DTW to contagion in derivatives, and no DTW nowcasting paper relevant to markets.

### Cited Findings
- State Street research note on time warping stock price bubbles: aligns thousands of bubble episodes and compares them (over 6 million pairs per the search summary) to estimate the stage of a bubble. Page returned 404 on fetch, details come from a search summary only, so authors, date and data are unconfirmed. Industry research, not peer reviewed. Equity-focused, flagged for the equity researchers. — [State Street](https://www.statestreet.com/br/en/insurer/insights/time-warping-stock-price-bubbles)
- Franses and Wiemann (2020), Computational Economics (Springer, DOI link 10.1007/s10614-020-09986-0): DTW on US state business cycles around the Great Recession, finds timing of cycles differs across states and recoveries clustered differently. Macro, not market, series. Per a search summary only, not read. — [Springer](https://link.springer.com/article/10.1007/s10614-020-09986-0)
- A Politecnico di Torino master's thesis reports that DTW-based signals do not transfer across assets without recalibration. Not read, student thesis. — [Polito](https://webthesis.biblio.polito.it/39690/1/tesi.pdf)
- Evidence on crisis-split sub-periods: Smiech (2014) and Wang et al. (2012) above (FULL and ABSTRACT).

### Inferences
- Comparing a current drawdown with past crashes via DTW is common in practitioner material but I found no peer-reviewed validation in these searches.

### Gaps
- Nothing found on DTW for contagion measurement across derivatives or sovereign CDS, nor for macro nowcasting. Franses-Wiemann and State Street details unverified beyond search summaries.

## Cross-cutting observations for the course
- DTW settings are rarely reported. Of the studies I could read in full, Gronwald-Zhu z-normalise and use a Sakoe-Chiba band (r not found), Smiech indexes to 2007 = 1, Sigaki et al. use dtaidistance without stated band.
- Most studies are descriptive or clustering-based, with lead-lag from the warping path as the main finance-specific use.
- Source quality: only Energy Economics, Physica A, Economic Research-Ekonomska istrazivanja and Applied Soft Computing items are journal-confirmed, and for these I read only abstracts or records. Items from arXiv, CESifo and MPRA are preprints or working papers.
