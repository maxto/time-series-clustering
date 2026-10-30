# Time series clustering

An operational mini-course on time series similarity and clustering. Given a kind of data and a goal, it tells you which measure to use, which clustering algorithm fits that measure, how to build the pipeline and how to validate the result. Written for data scientists and other technical readers, with formulas and worked figures.

**Read the course: https://maxto.github.io/time-series-clustering/**

## The pipeline

The course follows the four decisions of any clustering study, then puts them together in two recipes. Each measure lesson is a card: what it measures, when to use it, the definition with its formula, an example figure, which clustering algorithms fit, its use in finance, and a common mistake.

| Step | Lessons |
|---|---|
| Define | [Same series, different questions](https://maxto.github.io/time-series-clustering/same-series-different-questions/), [What preprocessing erases](https://maxto.github.io/time-series-clustering/preprocessing/) |
| Measure | [Lock-step: Euclidean, L1, correlation](https://maxto.github.io/time-series-clustering/lock-step/), [Sliding: cross-correlation and SBD](https://maxto.github.io/time-series-clustering/sliding/), [Elastic: DTW and its window](https://maxto.github.io/time-series-clustering/dtw/), [Edit-based: LCSS, EDR, ERP, MSM, TWE](https://maxto.github.io/time-series-clustering/edit-based/), [Features: ACF, spectra, wavelets, SAX, catch22](https://maxto.github.io/time-series-clustering/features/), [Models, complexity, ordinal patterns, compression](https://maxto.github.io/time-series-clustering/models/), [Learned representations](https://maxto.github.io/time-series-clustering/learned/), [Multivariate and subsequence](https://maxto.github.io/time-series-clustering/multivariate-subsequence/) |
| Group | [Match the algorithm to the distance](https://maxto.github.io/time-series-clustering/match-the-algorithm/) |
| Validate | [Internal indices](https://maxto.github.io/time-series-clustering/internal-indices/), [External indices and stability](https://maxto.github.io/time-series-clustering/external-and-stability/) |
| Recipes | [Recipe: daily load profiles](https://maxto.github.io/time-series-clustering/recipe-energy/), [Recipe: a stock universe](https://maxto.github.io/time-series-clustering/recipe-finance/) |

The worked figures use a small authored dataset of twelve daily demand profiles, `fixtures/demand-12.csv`. It shows what each choice does. It is not evidence that a method performs well.

## Versions

The course is built in passes. Version 1 covers every topic in a first form, later versions raise the level lesson by lesson. Corrections are welcome: open an issue with the lesson and, where you can, a source.

## The original list

This repository started as a catalogue of distances, algorithms and R packages. It is kept in [docs/original-list.md](docs/original-list.md), with the [original PDF](Time%20Series%20Clustering.pdf).

## Build

Requirements: Python 3.13 with [uv](https://docs.astral.sh/uv/), Node.js. For the browser tests, Chrome.

```sh
uv sync && npm install
npm run preview   # -> preview/index.html
uv run pytest     # build and reference code tests
npm test          # browser checks, contrast and widths
```

Lessons are Markdown files in `content/`, one per lesson, and the figures are generated from the dataset by `scripts/figures.py`.

## Licence

Code (scripts, site, tests): [MIT](LICENSE). Course content (`content/`): [CC BY 4.0](content/LICENSE.md).

The content was written with AI assistance.
