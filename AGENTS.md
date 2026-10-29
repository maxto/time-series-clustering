# Time series clustering: agent instructions

A concept-first, English-only mini-course on time series similarity (static site plus reference code in Python and R). Pilot first. Design: `docs/superpowers/specs/2026-10-28-course-design.md`. Plan: `docs/superpowers/plans/2026-10-28-pilot.md`. Public repo.

## Layout

- `content/`: `_map.toml` and `_sectors.toml` (map of the field and sector questions, draft until reviewed), lessons (`NN-id.md`), `_course.md` (course data), `figures/` (generated SVG, their `*.preview.svg`, and `numbers.json`).
- `site/`: `theme.css` (tokens, light and dark, layout, the figure classes between the `figure-classes` markers), `theme.js` (theme button, `tsc:theme`), `page.html` (lesson), `home.html`, `favicon.svg`.
- `scripts/`: `build.py` (content to `dist/`, holds `SITE_URL`), `buildlib/` (build helpers: `atlas.py` map and sector data with derived review state, `content.py` schema, sections, prose and links, `svg.py` figure rules and previews, `katex.py` math batch), `katex.mjs` (TeX to HTML and MathML, called once per build), `make_fixtures.py`, `parity_dtw.py`, `figures.py` (figures and `numbers.json` from the fixture).
- `code/python/tsc/`: reference package (`distances.py`, `group.py`, `validity.py`). Tests in `code/python/tests/`.
- `code/r/`: R reference code (`distances.R`, `check_dtw.R`).
- `fixtures/`: saved numbers (`demand-12.csv`). Frozen once the fixture checks pass. The CSV is the source of truth, the generator only documents it.
- `tests/`: `e2e.mjs` (headless Chrome via `playwright-core`, set `CHROME_PATH` if Chrome is not at `/usr/bin/google-chrome`), `test_build.py` (build validation), `fixtures/smoke/` (a tiny permanent course that exercises every engine feature), `shots.mjs` (full-page screenshots for review). `tests/output/` is git-ignored.
- `.github/workflows/pages.yml`: build and deploy to GitHub Pages on push to `master` (inactive until push and Pages are approved).
- `dist/`, `node_modules/`, `.venv/`: git-ignored.
- `README.md` and the PDF are the original material: leave them alone unless asked.

## Content format

- `content/_course.md`: front matter `title`, `tagline`. Body: `## <Letter>. <Module title>`, then one `- <id> | published|planned | <title>` per lesson. Published lessons need `NN-<id>.md` with `NN` = position in this list, planned ones must not have a file.
- Lesson front matter: `id`, `module`, `title`, `kicker`, `sector`, `lede`, `ignores`, `keeps`, `python`, `r` (the last four are comma lists). `sector` is one of `energy`, `finance`, `weather`, `retail`, `industry`, `health`. Blocks in this order: `## One line` (required, one paragraph), one or more content sections `## <title>` (any title), then optional `## In finance` (margin note), optional `## Measure card`, optional `## Code`, and `## Common mistake` (required, one paragraph, last). `One line`, `In finance`, `Measure card`, `Code` and `Common mistake` are reserved names, matched in any letter case, so a content section cannot use them. `## Lesson` and `## Check` are no longer sections: the build rejects them.
- `## Code`: at most one fence with info `python` and one with info `r`, plus optional paragraphs. Any other fence info is an error.
- Heading ids: every heading gets the slug of its text, `-2`, `-3` on repeats. A slug equal to a block id (`one-line`, `in-finance`, `measure-card`, `code`, `common-mistake`) is an error. A content section's id is the id of its `##` heading.
- Figures: `![caption](figures/<name>.svg)` alone in a paragraph, inside a content section or `## In finance`. `figures/overview.svg`, when present, is shown on the home. Numbers: `{{n:<key>}}` from `figures/numbers.json`. Math: `$...$`, `$$...$$`. Links: `lesson:<id>`, `#<heading-id>` (the target must exist in the same lesson), `https://` or `mailto:` (no `http://`).
- Citations: `[@key, locator]` in prose, list items and figure captions (not in code). The locator is required (page, section, theorem). `key` must exist in `content/_sources.toml`, one table per source with `authors` (`"Family, Given"`), `year`, `title`, `venue`, `topics` (from `survey, compare, group, validate, finance, software`) and at least one of `doi`, `arxiv`, `ssrn`, `url` (`https://` only). Optional `manual = { date, by, what }` (a TOML date and two non-empty strings) records a hand check of an SSRN id or an author URL. Titles and venues are verbatim metadata, exempt from the prose punctuation rule.
- Review gate: `content/_reviews.toml` holds the review records. Every build needs a `[[lesson]]` record whose fingerprint equals the current lesson fingerprint (whole file text after number substitution plus the identity of each cited source, whitespace-normalised) and a `[[citation]]` record for each citation (lesson, key, locator, paragraph fingerprint, source identity). So any edit to a lesson, and any change to a cited source, reopens its review. Write records only with `uv run python scripts/review.py show|record --content DIR --lesson ID` after the second-model review is done. The script verifies nothing else, it only refuses a fingerprint that is not the current one.
- The build rejects (one line per problem, exit 1): schema errors, TeX errors, semicolons or em-dashes in prose, SVG outside the figure rules, a missing figure or number.

## Commands

- `uv sync`, `npm install`: set up (Python 3.13 pinned, `.python-version`).
- `npm run build`: the release build, `uv run python scripts/build.py` (content/ to dist/, writes figure previews). It fails, one line per item or fit, on any map item or sector fit without a review record for its current text, so it fails while the map is a draft. Options: `--content DIR`, `--dist DIR`, `--previews`, `--preview`. With no `content/_course.md` it prints a note and exits 0.
- `npm run preview`: the preview build, `uv run python scripts/build.py --preview` (output in `preview/`, git-ignored). It allows draft map items and fits and marks them. It refuses a `--dist` equal to or inside `dist/`.
- `npm test`: `node tests/e2e.mjs`, which builds fresh itself (the smoke fixture into `tests/output/smoke-dist/`, the real content in preview mode into `tests/output/content-preview/` when `content/_course.md` exists, never reading an old `dist/`) and checks each from `file://` and over HTTP under `/time-series-clustering/`.
- `uv run python scripts/check_sources.py`: network check, not part of the build. Compares each DOI (Crossref) and arXiv id (arXiv API) of `content/_sources.toml` with the registry by normalised title and year. Outcome per identifier: `matched`, `mismatch` (reported with both values, never fixed by editing the registry), `unavailable`, `manual-needed` (SSRN ids and author URLs, unless the source has a dated `manual` record). Exit 1 on any `mismatch`. A Crossref 404 is `unavailable` (the DOI may belong to another agency). Writes `content/_sources-check.json`: the script's output, kept as an audit trail, never read by the build.
- `uv run pytest`: Python tests (reference code and `tests/test_build.py`).
- `npm run shots`: builds (preview mode, into `tests/output/shots-site/`), then full-page screenshots of the home and every published lesson, light and dark, 1280 and 375 px, in `tests/output/shots/` (cleared first, `manifest.json` records the commit).
- Every Python command runs through `uv run`.

## Global constraints

- English only.
- No CDN or external request at runtime: fonts and KaTeX CSS and fonts are copied into `dist/assets/`.
- Light and dark themes. Preference stored in `localStorage` under `tsc:theme` (never `aicourse:`: both courses share the `maxto.github.io` origin). With no stored preference, follow `prefers-color-scheme`.
- Light tokens (brand, from ai-one-token-at-a-time): `--bg #f5f6fa`, `--surface #ffffff`, `--ink #161a23`, `--ink-2 #464d5e`, `--muted #6f7689`, `--rule #dde1ea`, `--accent #3b5bdb`, `--accent-soft #edf2ff`, `--line #aeb6c6`. Dark (dimmed, from `docs/design/dark-theme.md`, no near-black): `--bg #1c2029`, `--surface #262b37`, `--ink #f2f4f8`, `--ink-2 #ccd2de`, `--muted #a3aabb`, `--rule #3e4657`, `--chip #333a49`, `--accent #8ca3ff`, `--accent-ink #0b0e14`, `--accent-soft #2c3768`, `--line #8d98b0`. Light adds `--chip #eef0f5`.
- Figure variables (dark / light): `--fig-bg #171a21` / `var(--surface)`, `--fig-box #353c4c` / `var(--surface)`, `--fig-soft #333a49` / `var(--chip)`, `--fig-muted #ccd2de` / `var(--muted)` (small figure text and muted lines), `--fig-ghost #8d98b0` / `var(--chip)`, `--soft-mix 28%` / `16%`. Figure classes map only to these and the page variables. Small text reaches 4.5:1 on every fill it can sit on, body text 10:1.
- Type: Geist (text), Geist Mono (labels, code). Fallbacks `system-ui`, `ui-monospace`.
- Figures: SVG styled only through classes defined in `site/theme.css`. No `fill`/`stroke` colour attributes, no inline `style`, no `width`/`height` on the root. Each figure has `role="img"` and a `<title>`. Readable at 375 px.
- Prose (lesson text, captions, notes) has no semicolons and no em-dashes, outside code and math.
- Visual style: minimal, flat, 2D, low density, few colours with constant meaning. In figures comparing two series: series A `ink`, series B `accent`. In figures about groups: colour encodes the group (first group `ink`, second `accent`, third `line`), stated by the panel headings.
- Fixtures are saved numbers in `fixtures/`. The fixture is an authored demonstration, and the lessons say so: it shows what a choice does, it is not evidence that a method performs well.
- DTW convention everywhere: local cost = squared difference, closed endpoints (0, 0) and (n-1, m-1), steps (1, 0), (0, 1), (1, 1) with no weights, Sakoe-Chiba window `|i - j| <= w` in samples, result = square root of the accumulated cost, no length normalisation. Course window: `w = 4` samples (2 hours at 30-minute sampling). Inputs: non-empty, finite, `w` a non-negative integer or `None` (no window), else `ValueError`.
- SBD inputs must have non-zero norm, else `ValueError` (the formula is undefined).
- Site address: `https://maxto.github.io/time-series-clustering/` (GitHub Pages, a custom domain may replace it later). One constant, `SITE_URL` in `scripts/build.py`, for the canonical link and Open Graph tags.

## Rules

- Correctness first. Every factual claim is checked against a primary source (papers, specs, official docs) before it goes in, and a claim that cannot be confirmed stays out. Every content change gets a review by another model, and the reviewer's claims are checked too.
- Draft map exception (owner, 2026-10-29, design 5.1). The map (`content/_map.toml`) and the sector fits (`content/_sectors.toml`) may hold the mockup's unconfirmed text in local preview builds only, so the owner sees the real size of the map before step 2 verifies it. There is no status field: an item or a fit is reviewed only when `content/_reviews.toml` holds a record for its current fingerprint (`scripts/review.py show-map`, `record-item`, `record-fit`), and a reviewed item also needs a located, non-candidate source for each factual field. Editing it makes it a draft again. The release build rejects every draft and the Pages workflow runs it, so nothing unconfirmed is published. Lessons are not covered by the exception.
- Tests: write one only when its expected value comes from an independent source (a hand computation, a known-good value, a real file, the spec, an independent package). No test that mirrors the implementation. The owner chooses which edge cases become tests: propose a short list, do not add them unasked. Every bug actually hit gets a regression test that fails before the fix and passes after it.
- Commits stay local. No push, no repo rename, no GitHub Pages activation without the owner's separate explicit go-ahead for each.
- Do not edit `HANDOFF.md` or `LOG.md` unless you are the main agent closing a piece of work.
