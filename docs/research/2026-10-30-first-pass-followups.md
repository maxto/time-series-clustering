# First pass: follow-ups per lesson

Collected from the reports of the first pass, 2026-10-30. Input for the Codex review and the second pass.
All 15 lessons are drafts. Numbers below must come from the fixture through `numbers.json`, never by hand.

## Figures and numbers requested

Done 2026-10-30: `preprocess-views`, `lockstep-matrices`, `cross-correlation`, `lcss-alignment`, `acf-bars`,
`ordinal-patterns`, `shapelet-map`, `nearest-window`, `dendrogram`, `partitions`, `silhouette-bars`, `contingency`,
`window-sensitivity`, `recipe-flow`. Still open from the list below: the second panels (wrong shift on raw data, MSM or
ERP alignment, periodogram and SAX per day, AR coefficients), Ward on DTW against Euclidean, the Euclidean matrix after
z-normalisation, the DTW_D against DTW_I panel (needs a second fixture channel), the Keogh and Lin random-walk test.

- `preprocessing`: one series before and after z-normalisation, differencing, 5-point smoothing, resampling to 2 h.
  Euclidean matrix of the 12 days before and after z-normalisation. Number: Euclidean `mon`-`sat` after z-normalisation.
- `lock-step`: 12 by 12 Euclidean matrix on raw values next to correlation distance. Manhattan, Chebyshev and
  correlation distance for `mon`-`sat` and `mon`-`wed`.
- `sliding`: cross-correlation curve against shift for `mon`-`sat` on z-normalised data with the best shift marked,
  second panel with the wrong shift on raw data. SBD for both pairs, best shift in samples.
- `edit-based`: `mon`-`sat` aligned by LCSS, matched pairs drawn, unmatched points marked, at a stated epsilon. Second
  panel under MSM or ERP. LCSS, EDR, ERP, MSM, TWE for both pairs on z-normalised days.
- `features`: per day, ACF up to lag L, normalised periodogram, SAX word. ACF, periodogram and SAX distances against
  Euclidean for two or three pairs.
- `models`: AR coefficients of two days next to their permutation-pattern histograms. Piccolo distance, permutation
  entropy, NCD under a stated encoding.
- `learned`: the 12 days with two shapelets, the 12 by 2 distance map as a scatter. k-means split of that map.
- `multivariate-subsequence`: DTW_D against DTW_I (needs a second fixture channel), matrix profile of `mon` against `sat`,
  sliding-window k-means centres from the fixture against a random walk (the Keogh and Lin test).
- `match-the-algorithm`: one DTW matrix fed to k-medoids, average linkage and DBSCAN, partitions side by side. Ward on
  the DTW matrix against Ward on the Euclidean matrix. Adjusted Rand between algorithms, DBSCAN eps scan.
- `internal-indices`: silhouette per day for the DTW w = 4 two-group cut. Per-day values, and CH, DB, Dunn on the same cut.
- `external-and-stability`: 2 by 2 contingency of the cut against `hour_group` and `shape_group`, with pair counts.
  ARI, RI, Jaccard, FM against both, ARI between cuts at w = 0, 4, 10 and no window.
- `recipe-energy`: the two-group cut and a silhouette at w = 0, 2, 4, 6, 10 and no window.
- `recipe-finance`: decision flow of the four steps, no data.

## Doubts to check

- `same-series-different-questions`: no limitations list, no source found.
- `preprocessing`, `lock-step`, `sliding`: three results are the writer's own maths, not cited: Euclidean distance on
  z-normalised series equals sqrt(2n(1-rho)), the Canberra relative-gap example, the Cauchy-Schwarz bound for NCCc.
- `lock-step`, `multivariate`, `match-the-algorithm`: the Mantegna distance differs between sources. The arXiv text gives
  sqrt(1-rho^2), Onnela et al. (2003) give sqrt(2(1-rho)). Lock-step says so.
- Epps (1979) removed from the limits of `preprocessing` and `lock-step`: never read, and secondary quotes disagreed.
- Forbes and Rigobon (2002), a limit in `lock-step`, read at abstract level. The rule asks for a source read.
- Hyndman and Athanasopoulos cited by name and URL, without the edition year.
- `sliding`: the only limit is a non-financial synthetic k-Shape example.
- `edit-based`: LCSS table follows Holder et al., since Vlachos's formula was garbled. EDR border not written out. "MSM is a
  metric" rests on Holder et al.
- `models`: the cepstrum recursion was rebuilt from a garbled extraction. The CDM formula is not written.
- `internal-indices`: formulas from secondary sources (scikit-learn, R docs), Dunn's definition from Wikipedia. Originals
  seen as Crossref metadata only.
- `external-and-stability`: the toy example's RI and Jaccard are the writer's arithmetic, ARI and FM match the scikit-learn
  docs. Stability limits are "Marti et al. report" statements from their introduction.
- `match-the-algorithm`: MPdist win stated only as what the authors propose. Several algorithm sources cited by name and
  DOI, not read: Lloyd, Kaufman and Rousseeuw, Bezdek et al., Ertoz et al., Fraley and Raftery, Kohonen.
- Weak fits in finance lists: Brandouy et al. (2015, complexity, not a pairwise distance), Wu, Shang and Chen (2019, CID
  inside a multifractal spectrum), Zunino, Alves (permutation entropy per series), Goldani (2025 preprint, forecast
  intervals), Karademir (2015, conference paper), Nalici et al. (2025, DOI not in Crossref).
- Years to confirm: Kakushadze and Yu, Verma et al., Gates, Wiroonsri and Preedasawakul, Ratanamahatana and Keogh.
- Checked by Claude: the DTW w = 4 two-group cut equals `hour_group` and differs from `shape_group` (reference code).
- The finance report in this folder is in Italian. The repo is English only: translate or keep out of the public history.
