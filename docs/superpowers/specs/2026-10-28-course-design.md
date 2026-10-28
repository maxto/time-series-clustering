# Time series clustering: a concept-first mini-course (design)

Status: approved 2026-10-28 (the owner chose the look in section 6 and gave
the go-ahead to start production). Codex design review folded in the same
day. Pilot plan: [../plans/2026-10-28-pilot.md](../plans/2026-10-28-pilot.md).
Owner: Max Todaro (`maxto`). Codex reviews:
[taxonomy](../../research/2026-10-28-codex-taxonomy-review.md),
[this design](../../research/2026-10-28-codex-design-review.md).

## 1. Intent

The repo `maxto/Time-Series-Clustering` (public, 49 stars, 7 forks, last
content push 2025-06) is today one README (~19 KB) of reference tables plus
a PDF. People keep starring and forking it, so it already serves as a
reference. The owner wants to turn it into a short, modern, English-only
mini-course in the spirit of their other course
(`~/projects/personal/ai-one-token-at-a-time`, live at
https://maxto.github.io/ai-one-token-at-a-time/), but specialised.

**Audience:** people in statistics, machine learning and data analysis who
need to cluster time series and want to understand the options before
applying them.

**Why:** the right distance measure decides what "similar" means, and
everything downstream (algorithm, validity index) depends on it. Most
material online is either a package manual or a paper. A clear, visual,
concept-first map is missing.

**Success (owner's words, summarised):** a reader in that audience thinks
"nice, I want this", reads it through, comes away knowing the families of
measures, what each captures and where it applies, which validity indices
make sense for which geometry, and leaves with reference code in Python and
R to build their own functions.

A testable version (proposed by Codex, adopted as a check, not a gate): a
reader can choose between two plausible distances for a dataset, explain
the assumption behind the choice, reject an incompatible algorithm or
index, and reproduce a small result with the reference code.

## 2. Goals, non-goals, anti-goals

**Goals**

- Concepts first, code second. The core is the taxonomy of distance and
  similarity measures and the validity indices. Algorithms get a shorter
  treatment focused on which algorithm is compatible with which distance.
- A modern, corrected taxonomy (section 5).
- Clean visuals: minimal, flat, 2D, low density, topics clearly laid out.
  One overview graphic in the README.
- Reference code in Python and R that gives the same numbers on the same
  inputs.
- A current map of Python and R packages per measure, with status.

**Non-goals (first release)**

- No Italian version. English only.
- Not exhaustive. The survey literature lists 100+ measures. The course
  teaches families through representatives and points to an atlas for the
  rest.
- No from-scratch code for every measure. Only the representatives
  (section 7).
- No in-browser numerical engine or live interactive widgets. Precomputed
  results only.
- No deep-learning implementation. Learned representations are explained
  conceptually.
- No leaderboard claiming a universal winner.

**Anti-goals (failure even if it works)**

- Dense, busy visuals or walls of tables.
- Claiming one method is best in general.
- A finance example that reads as a trading signal or ignores the known
  problems of financial returns.
- Breaking the existing entry point that the 49 stars and 7 forks rely on.
- Recommending install of archived packages as the default path.

## 3. Constraints and verified facts

- Repo default branch is `master` (verified 2026-10-28). No licence file.
  13 commits. Local clone: `~/projects/personal/time-series-clustering/`.
- GitHub repo names are case-insensitive: `github.com/maxto/time-series-clustering`
  and the raw README URL in lowercase already resolve (verified
  2026-10-28). Decided: rename the repo to all lowercase
  `time-series-clustering`, before enabling GitHub Pages, so the site URL is
  `https://maxto.github.io/time-series-clustering/`. The rename is a remote
  action and needs the owner's explicit go-ahead when it happens.
- R packages `TSclust` and `TSdist`, cited throughout the current README,
  were archived on CRAN on 2026-01-16 (verified on the CRAN pages
  2026-10-28). `dtwclust` is listed on CRAN.
- The existing PDF's content and rights have not been checked.

## 4. Approaches considered

| Approach | Trade-off |
|---|---|
| **A. Reuse the ai-one-token-at-a-time engine** (Markdown lessons + SVG, Python build script, static page on GitHub Pages) | Consistent with the owner's other course, full control of the minimal look, small known engine (~225-line `scripts/build.py` + one template). Needs adapting: English only, longer lessons, math rendering, flexible figure sizes. |
| B. Quarto book | Executes R and Python at build time, native math, familiar to statisticians. Looks like a textbook, needs theme work for the minimal look, concept figures still hand-drawn. |
| C. Plain Markdown in the repo, no site | Fastest, nothing to maintain. No search or curated navigation, limited math, unlikely to produce the "I want this" reaction. |

**Chosen: A** (owner, 2026-10-28), with one idea taken from B: data
figures (groups, distance matrices, alignments) are generated by scripts
from the same fixtures the reference code uses. Concept figures (taxonomy
map, invariance diagrams) are hand-made SVG.

## 5. Content model

### 5.1 Taxonomy

Two axes, replacing the current single tree:

1. **Families of measures** (navigation, following Paparrizos et al., *A
   Survey on Time-Series Distance Measures*, 2024,
   https://arxiv.org/abs/2412.20574): lock-step, sliding, elastic, kernel,
   feature-based, model-based, embedding (learned). The course says these
   are not all at the same conceptual level.
2. **What do you want to ignore?** (the decision lens the reader carries):
   level, amplitude/scale, a global shift, local timing variation, noise,
   length differences, local vs global patterns, channel synchrony.

The overall pipeline frames everything: object, preprocessing,
representation, comparison, grouping, validation.

Corrections to the current README tables (from the Codex review, to be
re-verified by the builder against the cited sources):

- Cross-correlation and SBD move from lock-step / elastic to sliding.
- `dist(method="binary")` is not Hamming distance. Fix or drop the row.
- KNN is not a clustering algorithm. Remove it from the schema.
- "Structure-based" is split: model comparison, complexity correction
  (CID), ordinal patterns, compression.
- GAK is a kernel, shapelets are a representation. Neither sits with DTW.
- Add: MSM, TWE, ERP, EDR beside DTW and LCSS (Holder, Middlehurst &
  Bagnall 2024 review of elastic distances for clustering), multivariate
  measures (d'Hondt et al., SIGMOD 2025), soft-DTW and its divergence as
  a short extension.

### 5.2 Validity indices (core, not an appendix)

Decided by the owner: validity indices are a full module, organised by
the geometry they assume, not as a long list. Each index is taught through
three questions: can it be computed on this input, what geometry does it
assess, does that geometry answer the domain question?

- Calinski-Harabasz and Davies-Bouldin, in their standard Euclidean
  vector/centroid form, are not meaningful on a DTW matrix. Feeding rows of
  a DTW matrix as feature vectors evaluates a different geometry.
- Silhouette needs finite, nonnegative, symmetric dissimilarities with a
  zero diagonal and `2 <= k <= n-1`, with singletons handled explicitly.
  Triangle inequality is not required. Kernel similarities, raw soft-DTW
  (can be negative), asymmetric costs or matrices with missing values must
  not enter it silently.
- A higher silhouette under distance X does not prove X is better than Y.
- ARI and NMI compare partitions of the same objects, also repeated runs
  without ground truth. NMI is not chance-adjusted. The two electricity
  questions get different declared reference partitions.
- Stability: say what is perturbed, keep temporal dependence. Stable groups
  can still be irrelevant. Density methods: declare how noise points enter
  the evaluation.

### 5.3 Running examples (two, decided by the owner)

- **Main example, where clustering works cleanly:** synthetic daily
  electricity-demand profiles (about 12), one base family plus controlled
  variants (offset, scale, global lag, local timing, noise). Missing values
  appear as a deliberate preprocessing failure case, not as silent `NaN`
  support everywhere. Two legitimate questions give different groupings
  ("which days stress the grid at the same hour?" vs "which days have the
  same shape even if shifted?"). It is an explanatory fixture, not evidence
  that a family performs well. The recurring four-panel figure (series,
  permitted alignment, distance matrix, groups) is used where it explains a
  full comparison, a simpler mechanism figure elsewhere.
- **Finance companion, with its limits stated (task decided by the owner
  2026-10-28):** group assets or sectors by contemporaneous co-movement,
  using the correlation of returns over the same date window. Precedents:
  Mantegna (1999, hierarchical structure of stock returns,
  https://arxiv.org/abs/cond-mat/9802256) and López de Prado
  (hierarchical risk parity, optimal number of clusters on correlation
  matrices). Data: synthetic returns from a factor model, saved in the
  repo as a fixture, plus an optional script that downloads real data
  (e.g. Kenneth French sector portfolios) at run time without
  redistributing it. The caveats of financial returns are stated: low
  signal-to-noise, non-stationarity and regime changes, heavy tails,
  volatility clustering, look-ahead and survivorship bias. The key
  contrast is task-specific: shifting or warping returns destroys the
  simultaneity that co-movement is about (correlation distance is itself a
  comparison of normalised synchronous trajectories:
  `||u-v||^2 = 2(1-r)` for centred unit-norm vectors). Volatility or model
  features are evaluated against their own stated objective. Attractive
  clusters prove nothing. It must not read as a trading signal.

### 5.4 Module outline (starting point, the builder may adjust)

Based on the Codex outline, with the validity part expanded.

| Module | Lessons |
|---|---|
| A. Define similarity | 1. Same series, different questions. 2. What preprocessing erases (normalisation, sampling, missing values, unequal length). |
| B. Compare sequences | 3. Lock-step (Euclidean, L1, correlation). 4. Sliding (cross-correlation, SBD). 5. Elastic: DTW and windows (soft-DTW as extension). 6. Edit-based: LCSS, EDR, ERP, MSM, TWE. |
| C. Compare representations | 7. Features (ACF, spectral, wavelets, SAX, catch22). 8. Models (AR and others, complexity, ordinal, compression pointers). 9. Learned representations (concept only). 10. Multivariate and subsequence. |
| D. Group | 11. Match the algorithm to the geometry (medoids, compatible linkages, barycentres, k-Shape, kernel and density routes). |
| E. Validate | 12. Internal indices by geometry. 13. External indices, stability and domain checks, the full decision guide. |
| Code labs | 14. Python reference lab. 15. R reference lab. |

Each concept lesson: one-line idea, explanation, one mechanism figure, a
small numerical example where useful, a common mistake, the finance
companion note where relevant. Lessons 6, 7, 10 and 11 are dense: each gets
one learning outcome and one worked representative, the rest as contrasts
and pointers. Detailed derivations live in optional "measure cards", but
what a decision needs (local cost, normalisation, DTW path constraints, the
meaning of a validation score) stays in the main text. Lesson 11 keeps a
short sourced note on KASBA (Holder & Bagnall 2026,
https://doi.org/10.1007/s10618-026-01189-9) so centroid methods do not stop
at DBA and k-Shape.

### 5.5 README

The README stays the entry point for existing readers:

- Course link and the overview graphic at the top.
- The corrected reference tables below, with Python and R columns and
  package status. Keep the main section anchors.
- The PDF stays, labelled as the dated legacy version.

## 6. Visual style (owner's preference)

Minimal, flat, 2D, clean, low density: the topics must read at a glance.
No 3D, no gradients, no clutter, generous whitespace, few colours with
consistent meaning. Light and dark themes as in the other course. Figures
must stay readable on mobile. Not identical to ai-one-token-at-a-time
(owner, 2026-10-28).

**Decided (owner, 2026-10-28): Notebook layout, brand blue palette.**
Three drafts were shown (local, git-ignored `.mockups/`): 1 Notebook
(lesson page, single reading column, margin notes), 2 Atlas (map-first
home, warm dark), 3 Field guide (catalogue of cards, white and teal). The
owner rejected the dark Atlas (it resembles maxto.io, which is not required,
and the dark look did not fit) and the Field guide,
and kept the Notebook structure with new colours. Of three colour variants
(white and blue, cool grey, white and sage) the owner chose white and blue,
which is the brand palette shared with ai-one-token-at-a-time: courses keep
a consistent palette. The reference page is `.mockups/notebook-brand.html`
(generated by `.mockups/gen_palettes.py`): exact brand tokens from
`ai-one-token-at-a-time/site/template.html`, light and dark, Geist type
(proposed, so the layout and type differ from the other course while the
palette matches). Why Notebook: lessons here are longer than in the other
course (figure, formula, finance note, code), and a reading column with
margin notes keeps the text light. The dark tokens are provisional: the
owner is reworking the brand's dark palette (2026-10-28) and the new values
replace them in one place.

Site address: GitHub Pages, `https://maxto.github.io/time-series-clustering/`
(owner, 2026-10-28). A custom domain may replace it later.

## 7. Code

- Two folders, `code/python/` and `code/r/`, same functions, same
  contracts.
- From-scratch, readable implementations only for the representatives:
  Euclidean, L1, correlation distance, SBD, constrained DTW, one feature
  pipeline, silhouette on a distance matrix. These run in both languages
  with a parity check (decided by the owner 2026-10-28).
- Package-backed runnable examples only where the method exists in both
  languages (e.g. DTW). Everything else is a documented table of packages
  and status. A missing R (or Python) counterpart is marked as a gap, not
  papered over. Coverage matrix columns: explained, implemented from
  scratch, Python package, R package, numerically checked.
- Shared fixtures (saved numeric inputs, not seeds) and a cross-language
  check that Python and R agree within a stated tolerance. Hand-computable
  cases, constant series, unequal lengths, zero lag, ties.
- Package shortlist to verify (from the Codex review): Python `aeon`,
  `tslearn`, `sktime`, `dtaidistance`, `dtw-python`, `pycatch22`,
  `tsfresh`, `stumpy`. R `dtw`, `dtwclust`, `Rcatch22`, `tsfeatures`,
  `feasts`, `cluster`. `TSclust`, `TSdist` as archived references only.

## 8. Licence

Proposed, owner to confirm: MIT for code, CC BY 4.0 for content, as in the
other course. The PDF stays published only after its content and rights are
checked. The new content licence is never applied silently to third-party
material.

## 9. Delivery order

1. Pilot: README overview graphic, lesson 1 and lesson 5 (DTW) with their
   figures, in the adapted engine. Plus three specimens (not full lessons):
   one finance note, one measure card with rendered math, one short
   validity example showing an admissible and an inadmissible input.
   Before the definitive DTW figures: save the pilot fixtures, hand-check a
   tiny DTW result, compare the Python and R kernels. The owner reviews
   look and depth before the rest is written.
2. Remaining lessons, module by module.
3. Code labs and cross-language checks.
4. README rewrite, licence, repo rename, GitHub Pages (remote steps each
   with the owner's go-ahead).

## 10. Left to the builder

- How to adapt `build.py` and the template (math library, figure sizes,
  removing the bilingual schema), as long as no CDN is required at runtime.
  Known work (Codex review): the engine is a fixed lesson-schema renderer
  (`site/template.html` escapes text and supports bold only,
  `scripts/build.py` has fixed fields and an SVG element whitelist). It
  needs links, math, measure cards, finance notes, code blocks, an export
  path for generated SVG, and a deliberate keep-or-drop of the quizzes.
  Use a storage key namespace other than `aicourse:`: both courses share
  the `maxto.github.io` origin.
- Exact lesson split within a module, lesson length.
- Figure-generation tooling, as long as the output is SVG in the agreed
  style.
- Test setup for the build and the cross-language checks.
