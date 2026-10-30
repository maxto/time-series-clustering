# DTW applications to funds and asset management

Method note: about 14 tool calls. "Read" below means I read the text myself (PDF extracted with pdftotext, or a page fetched). "Snippet" means a search-engine summary only, not verified by me. Several publisher/repository pages refused access (bot checks, 403, 404, connection refused); none were bypassed. Overall finding: published DTW work that touches funds is thin, mostly working papers, theses and posters. No peer-reviewed study found that uses DTW on hedge funds, and none for fund replication, index tracking or factor timing.

## Is DTW used to classify or cluster mutual funds, hedge funds or ETFs (style analysis, style drift, peer groups)?

### Takeaway
Only two fund-level DTW clustering studies were confirmed to exist: a poster on 143 Chinese ETFs (read in full) and a Lisbon master's thesis on Luxembourg mutual funds (snippet only). The classic mutual fund style clustering paper (Pattarin et al. 2004) does not use DTW according to its abstract. Nothing found for hedge funds, style drift or peer groups with DTW.

### Cited Findings
- Li Chen, Lim Yong Kai, Kam Tin Seong (Singapore Management University), "An Analysis of ETFs in China Stock Market using Dynamic Time Warping", JMP Discovery Summit 2021 poster/paper (not peer-reviewed). Read the full text. Data: daily closes of 255 Shanghai and 111 Shenzhen ETFs, 2 Jan 2018 to 31 Dec 2020. 223 ETFs without complete 2018 prices were dropped, leaving 143 ETFs. The series clustered are 36 monthly returns per ETF (computed from daily prices). Method: agglomerative hierarchical clustering with DTW distance, compared with Euclidean distance with Ward linkage in SAS Enterprise Miner (max 16 clusters to match the DTW run, no standardisation). Dendrogram cut gave 14, 16 or 18 plausible clusters and 16 was chosen because beyond that singleton clusters appear. Result: DTW clusters "largely coincide with the type of industries that ETFs involve"; cluster price movement showed some industries did better in 2019 than 2018. DTW window or step pattern not stated in the text I read. Stated limits: one ETF had a -79.62% monthly "return" caused by a share split, which the authors note hurts the algorithm (extreme outlier sensitivity); only 3 years, 143 ETFs, no out-of-sample portfolio test. — [JMP community PDF](https://community.jmp.com/kvoqx44227/attachments/kvoqx44227/discovery-us-2021-content/55/1/Analysis%20of%20Stock%20Market%20with%20Unsupervised%20Learning.pdf)
- Same poster cites other ETF clustering work that did not use DTW (Solis 2011 k-means/factor analysis; Isakov 2019 correlation-based hierarchical clustering on weekly returns) and Javed, Lee and Rizzo (2020), which tested 8 clustering methods including Euclidean and DTW hierarchical clustering and concluded no single method wins on all datasets. — same PDF
- "Clustering of ETF Data for Portfolio Selection During Early Period of Corona Virus Outbreak" (Scribd upload, authors, venue and year not stated on the page I could see). 20 Tokyo Stock Exchange ETFs, early COVID-19 period, four clustering methods (the page does not name them). Three clusters found: a large loss-making one, an unaffected one, a loss-making-then-recovering one. A search snippet said the methods include k-means with Euclidean and with DTW; the page itself did not confirm DTW. Abstract-level only, provenance weak. — [Scribd](https://www.scribd.com/document/556473382/5801shirota)
- Lisbon master's thesis (ULisboa repository), compares a signature-based similarity method against DTW-based traditional clustering on time series of Luxembourg mutual funds. Snippet only: I could not open the page (Anubis bot check) so author, year, data details, DTW settings and findings are unconfirmed. — [ULisboa repository](https://repositorio.ulisboa.pt/entities/publication/33649f8b-2cb7-458a-8510-8d36655a289e)
- Pattarin, Paterlini, Minerva (2004), "Clustering financial time series: an application to mutual funds style analysis", Computational Statistics & Data Analysis 47(2), 353-372, doi 10.1016/j.csda.2003.11.009. Pipeline: PCA, robust evolutionary clustering, then style identification via Sharpe's constrained regression. Tested on Italian mutual funds; reported satisfactory agreement with the institutional classification and out-of-sample explanatory power. The abstract does not mention DTW, so this is a non-DTW benchmark for return-based fund peer groups. Abstract only; full text restricted. (A secondary paper claims it is a reference for fund style clustering; I did not verify any DTW use.) — [IDEAS](https://ideas.repec.org/a/eee/csdana/v47y2004i2p353-372.html)
- Hedge funds: the searches returned return-based clustering work without DTW (UMass dissertation using PAM on Lipper/TASS data; a self-organising-map study of 2,789 hedge funds 1999-2008 finding many funds inconsistent with their declared strategy; Fung and Hsieh 1997 style factors). None uses DTW. Snippets only. — [UMass](https://scholarworks.umass.edu/items/12a91e73-a079-4789-a373-e94c7fe19a32)

### Inferences
- DTW-based fund clustering exists mainly as student/poster/thesis work. Using DTW on monthly fund returns (36 points) gains little over lag-0 comparison, and none of these studies tests whether warping helps against Euclidean/correlation beyond cluster-label agreement with industry type.
- Style drift detection with DTW appears unexplored in the literature I could reach.

### Gaps
- No DTW study of hedge funds found. No study of style drift or peer-group construction with DTW found.
- Lisbon thesis details unverified (page blocked). Tokyo ETF paper authorship and venue unknown.
- Did not search Google Scholar-level coverage (not available); absence is "not found by web search", not proof of absence.

## Is DTW used for portfolio construction, diversification, asset allocation or risk management?

### Takeaway
Yes, but almost entirely on individual stocks, not funds: the Lim and Ong (2021) JFDS paper and Lim and Ng (2023) Journal of Investing paper, a Rome working paper, a 2025 Finance Research Letters paper and several Indonesian studies. One working paper uses DTW for regime clustering with mutual funds and sector indices as assets.

### Cited Findings
- Tristan Lim and Chin Sin Ong (2021), "Portfolio diversification using shape-based clustering", Journal of Financial Data Science 3(1), 111-126, doi 10.3905/jfds.2020.1.054. Agglomerative hierarchical clustering with DTW distance groups stocks by price-trend shape for diversification. Authors report support for allocation and rebalancing, dynamic predictive portfolio construction and outlier-based stock selection. Abstract/search-result level only (SMU repository page returned empty content to me). Universe, period and DTW settings not confirmed. — [SMU repository](https://ink.library.smu.edu.sg/sis_research/7238)
- Tristan Lim and Heber Ng (2023), "Financial Portfolio Management Based on Shaped-Based Unsupervised Machine Learning: A Dynamic Time Warping Barycenter Averaging Approach to International Markets and Periods of Downside Event Risks", Journal of Investing 32(2). Reported: DTW-cluster diversification with optimal weights beat correlation-based diversification on mean and median return and Sharpe metrics, with steadier results in downturns across developed markets. A University of Bahrain record (not opened, host unreachable) reportedly quotes +598 bp annualised mean return and +337% Sharpe versus industry diversification; I could not verify those figures or which paper they belong to. Underlying assets appear to be stocks, not funds (not confirmed). Abstract-level via listing (EBSCO page returned 403 to me). — [EBSCO listing](https://www.ebsco.com/articles/business-and-management/f3b1bb79-f850-581d-85c0-852c4c161be0/financial-portfolio-management-based-on-shaped-based-unsupervised-machine-learning-a-dynamic-time-warping-baycenter-averaging-approach-to-international-markets-and-periods-of-downside-event-risks)
- Vitulano (Sapienza University of Rome, DSS technical report, year not confirmed), hierarchical clustering of S&P 500 stocks on the time series of their Sharpe ratios over about a decade using DTW, then Most Diversified Portfolio (Choueifaty and Coignard 2008) to assess diversification gain. Snippet only (server refused connection); results not seen. — [PDF](https://www.dss.uniroma1.it/it/system/files/pubblicazioni/Paper_VitulanoM.pdf)
- Seokjune Lee and Jaehong Jeong (2025), "Portfolio optimization using a covariance structure based on dynamic time warping", Finance Research Letters 83, doi 10.1016/j.frl.2025.107642. Two covariance variants (Transformed DTW, Covariance DTW via a spatial covariance function) used in Maximum Diversification, Equal Risk Contribution and Hierarchical Risk Parity portfolios on US stock data. Reportedly outperforms traditional covariance and gives smaller weight changes on rebalancing. Abstract only; dataset and period not stated on the page. — [IDEAS](https://ideas.repec.org/a/eee/finlet/v83y2025ics1544612325009018.html)
- Nolan Alexander, William Scherer, Jamey Thompson, "Asset Allocation Using a Markov Process of Clustered Efficient Frontier Coefficients States", arXiv 2604.03946 (preprint, not peer-reviewed as far as I know). Read the full text. Months are the objects clustered: monthly efficient-frontier coefficients (three per month, from daily returns within each month) are converted to a month-by-month correlation-distance matrix, DTW is computed on that matrix, then hierarchical clustering defines market states; a Markov chain over states weights state-specific tangency portfolios. Re-clustered every month, expanding window. DTW window or step settings not stated in the text I read. Universes (Yahoo Finance data): (1) "GVMC", six Fidelity/Invesco/Heartland mutual funds covering growth/value and large/mid/small cap (e.g. Fidelity OTC Portfolio, Fidelity Growth & Income, Fidelity Growth Company, Fidelity Low-Priced Stock, Invesco Oppenheimer Discovery, Heartland Value), training from 1990; (2) nine S&P sector indices/instruments from 1999; (3) five global developed-market indices from 1988. Test starts 2000 and/or 2008. Backtest: leverage capped at 50%, 1% daily transaction fee, daily rebalancing. Findings: authors report outperformance of benchmarks (equal weight, S&P 500, monthly-run benchmarks); best for the Sectors universe, while for GVMC the model still suffered the drawdowns of the dot-com, 2008 and COVID shocks. Authors attribute weaker GVMC and Developed results to fewer, less linearly independent assets. — [arXiv PDF](https://arxiv.org/pdf/2604.03946)
- Indonesian stock studies pairing DTW with K-Medoids/PAM and mean-variance or MAD optimisation (e.g. STIS journal article, ITS thesis, UNHAS, UNPATTI 2026 saying DTW groupings give a better diversification basis than sector classification). Snippet-level only, stocks not funds. — [STIS](https://jurnal.stis.ac.id/index.php/jurnalasks/id/article/view/295), [UNPATTI](https://ojs3.unpatti.ac.id/index.php/parameter/article/view/25010)
- "Trimmed fuzzy clustering of financial time series based on dynamic time warping" (Annals of Operations Research, Sapienza, applied to FTSE MIB stocks, snippet only; cites Pattarin et al. 2004 for fund style). Equity, outside scope except as method precedent. — [Sapienza](https://research.uniroma1.it/node/52748)

### Inferences
- The Lim line (JFDS 2021, JoI 2023) is the clearest published "DTW clusters as diversification building blocks" work, but on stocks. Whether any variant was run on funds or ETFs is unknown.
- Alexander et al. is the only item found where mutual funds are among the assets, and DTW is used on a derived correlation matrix across months, not on fund return paths directly, so it is not a conventional shape-similarity use.

### Gaps
- Full texts of Lim and Ong, Lim and Ng, Vitulano and Lee and Jeong were not read; data, DTW windows and effect sizes are unconfirmed.
- No DTW in fund-of-funds construction, hierarchical risk parity on fund universes (beyond Lee and Jeong's stock data), or risk management/drawdown clustering of funds found.

## Is DTW used for regime detection or analogue-based allocation?

### Takeaway
Analogue matching with DTW exists as a blog demonstration and a master's thesis for single price series, and DTW state clustering exists in the Alexander et al. preprint. No peer-reviewed analogue-based allocation study on funds or ETFs found.

### Cited Findings
- Jonathan Kinlay blog post (2016, practitioner blog, not peer-reviewed). Read. DTW on daily SPY ETF log-returns from 1995; target is Q3 2016 (about 51 business days); best match found March 6 to April 7, 1995 (the post gives both 21 and 25 days for its length); the 35 days after the match are mapped on to project a gain of roughly 3.5% to 4% by end of September. No warping window or slope values given. Limits: single match, no backtest or out-of-sample test, no error statistics; author acknowledges 1995 and 2016 differ fundamentally. — [Kinlay](https://jonathankinlay.com/?p=2419)
- Politecnico di Torino master's thesis (2026) applies DTW to compare recent market windows with similar historical segments and builds outcome features for trading; reports DTW features are more useful in some regimes than others. Snippet only, trading focus (outside fund scope). — [Polito](https://webthesis.biblio.polito.it/39690/1/tesi.pdf)
- Tsinaslanidis and co-authors: DTW as a similarity measure for financial series, with similarity higher in high-volatility periods and lower in low-volatility periods (snippet). Methodological. — [Kent](https://kar.kent.ac.uk/id/document/26138)
- Alexander et al. (see previous section): DTW hierarchical clustering of monthly efficient-frontier states with Markov transition weighting is a regime-allocation method. — [arXiv](https://arxiv.org/pdf/2604.03946)
- A Rebellion Research blog title refers to "DTW S&P 500 sector ETF pattern matching trading strategy" and a search summary says it summarises a Journal of Financial Data Science paper building a Markowitz portfolio on sector ETF NAVs. The page returned 404 to me, so authors, year, and the underlying paper are unverified. — [Rebellion Research](https://blog.rebellionresearch.com/blog/dynamic-time-warping-s-p-500-sector-etf-pattern-matching-trading-strategy)

### Inferences
- Analogue forecasting with DTW is shown only informally; evidence of out-of-sample value is absent in what I could read.

### Gaps
- The Rebellion/JFDS sector-ETF paper needs a direct primary-source check.
- No study of macro-regime analogue allocation across funds or asset classes found.

## Is DTW used for fund replication, index tracking, or factor timing?

### Takeaway
Nothing found. Searches for DTW with fund replication, index tracking, factor timing and tactical asset allocation returned only the analogue-forecasting items above. Absence reported plainly.

### Cited Findings
- A search on those terms returned no relevant primary study; only Kinlay, the Polito thesis, Tsinaslanidis et al. and an indicator description (LuxAlgo), which itself warns that a close shape match is not a prediction. — [LuxAlgo](https://www.luxalgo.com/library/indicator/dynamic-time-warping-similarity/)
- QuantConnect forum thread describes using DTW with returns correlation to compare a live algorithm's equity curve with its backtest (strategy monitoring, not fund replication). Snippet only. — [QuantConnect](https://www.quantconnect.com/forum/discussion/7606/a-new-reconciliation-metric/)

### Inferences
- Replication/tracking is level- and lag-sensitive in practice, where warping would hide the mismatch that matters, which may explain the absence. This is my reasoning, not a sourced claim.

### Gaps
- Only a few web searches done on this question; a specialist database search (Scopus, SSRN) could still find something.

## Is DTW used by practitioners (asset managers, banks, index providers, white papers)?

### Takeaway
No asset-manager, bank or index-provider research note or white paper using DTW on funds or allocation was found. Practitioner-style items are individual blogs and forum posts.

### Cited Findings
- Practitioner-adjacent items found: Kinlay's blog (SPY analogue), Rebellion Research blog (unverified), QuantConnect thread, LuxAlgo charting indicator "Dynamic Time Warping Similarity". Alexander et al. lists a co-author as managing member/portfolio manager at Jocassee Quantitative, so the arXiv preprint has a practitioner author, but no firm use of the method is stated. — [arXiv](https://arxiv.org/pdf/2604.03946)

### Inferences
- Adoption by institutional managers is not evidenced in public sources I could reach; proprietary use cannot be ruled out.

### Gaps
- I did not search bank research portals or index-provider sites individually (search budget). Targeted searches (e.g. MSCI, S&P, Morningstar, Amundi, BlackRock research) are still open.

## Summary by asset class (for the report writer)
- Mutual funds: one working-paper use (Alexander et al., DTW on derived correlation matrix), one thesis (Lisbon, unverified). Pattarin et al. 2004 is the non-DTW benchmark.
- ETFs: one confirmed poster (China, 143 ETFs), one weak-provenance Tokyo item, one unverified sector-ETF item.
- Hedge funds: nothing found.
- Stocks-as-proxy for portfolio construction: a small published body (Lim and Ong 2021, Lim and Ng 2023, Lee and Jeong 2025), outside this strand's scope but the nearest methodological evidence.
