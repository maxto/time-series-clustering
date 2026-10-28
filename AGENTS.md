# Time series clustering: agent instructions

A concept-first, English-only mini-course on time series similarity (static site plus reference code in Python and R). Pilot first. Design: `docs/superpowers/specs/2026-10-28-course-design.md`. Plan: `docs/superpowers/plans/2026-10-28-pilot.md`. Public repo.

## Layout

- `content/`: lessons (`NN-id.md`), `_course.md` (course data), `figures/` (generated SVG and `numbers.json`).
- `site/`: `theme.css` (all colour and figure classes), `page.html`, `home.html`.
- `scripts/`: `build.py` (writes `dist/`, holds `SITE_URL`), `figures.py`, `make_fixtures.py`, `katex.mjs`, `parity_dtw.py`.
- `code/python/tsc/`: reference package (`distances.py`, `group.py`, `validity.py`). Tests in `code/python/tests/`.
- `code/r/`: R reference code (`distances.R`, `check_dtw.R`).
- `fixtures/`: saved numbers (`demand-12.csv`). Frozen once the fixture checks pass. The CSV is the source of truth, the generator only documents it.
- `tests/`: `e2e.mjs` and `shots.mjs` (headless Chrome via `playwright-core`, set `CHROME_PATH` if Chrome is not at `/usr/bin/google-chrome`). `tests/output/` is git-ignored.
- `dist/`, `node_modules/`, `.venv/`: git-ignored.
- `README.md` and the PDF are the original material: leave them alone unless asked.

## Commands

- `uv sync`, `npm install`: set up (Python 3.13 pinned, `.python-version`).
- `npm run build`: `uv run python scripts/build.py`.
- `npm test`: build, then `node tests/e2e.mjs`.
- `npm run shots`: screenshots in `tests/output/`.
- `uv run pytest`: Python tests.
- Every Python command runs through `uv run`.

## Global constraints

- English only.
- No CDN or external request at runtime: fonts and KaTeX CSS and fonts are copied into `dist/assets/`.
- Light and dark themes. Preference stored in `localStorage` under `tsc:theme` (never `aicourse:`: both courses share the `maxto.github.io` origin). With no stored preference, follow `prefers-color-scheme`.
- Light tokens (brand, from ai-one-token-at-a-time): `--bg #f5f6fa`, `--surface #ffffff`, `--ink #161a23`, `--ink-2 #464d5e`, `--muted #6f7689`, `--rule #dde1ea`, `--accent #3b5bdb`, `--accent-soft #edf2ff`, `--line #aeb6c6`. Dark: `--bg #10131a`, `--surface #171b24`, `--ink #e8eaf1`, `--ink-2 #b6bccb`, `--muted #8a91a5`, `--rule #2a303d`, `--accent #7d97ff`, `--accent-soft #1d2440`, `--line #4c5568`.
- Type: Geist (text), Geist Mono (labels, code). Fallbacks `system-ui`, `ui-monospace`.
- Figures: SVG styled only through classes defined in `site/theme.css`. No `fill`/`stroke` colour attributes, no inline `style`, no `width`/`height` on the root. Each figure has `role="img"` and a `<title>`. Readable at 375 px.
- Prose (lesson text, captions, notes) has no semicolons and no em-dashes, outside code and math.
- Visual style: minimal, flat, 2D, low density, few colours with constant meaning (series A `ink`, series B `accent`, third group `line`).
- Fixtures are saved numbers in `fixtures/`. The fixture is an authored demonstration, and the lessons say so: it shows what a choice does, it is not evidence that a method performs well.
- DTW convention everywhere: local cost = squared difference, closed endpoints (0, 0) and (n-1, m-1), steps (1, 0), (0, 1), (1, 1) with no weights, Sakoe-Chiba window `|i - j| <= w` in samples, result = square root of the accumulated cost, no length normalisation. Course window: `w = 4` samples (2 hours at 30-minute sampling). Inputs: non-empty, finite, `w` a non-negative integer or `None` (no window), else `ValueError`.
- SBD inputs must have non-zero norm, else `ValueError` (the formula is undefined).
- Site address: `https://maxto.github.io/time-series-clustering/` (GitHub Pages, a custom domain may replace it later). One constant, `SITE_URL` in `scripts/build.py`, for the canonical link and Open Graph tags.

## Rules

- Correctness first. Every factual claim is checked against a primary source (papers, specs, official docs) before it goes in, and a claim that cannot be confirmed stays out. Every content change gets a review by another model, and the reviewer's claims are checked too.
- Tests: write one only when its expected value comes from an independent source (a hand computation, a known-good value, a real file, the spec, an independent package). No test that mirrors the implementation. The owner chooses which edge cases become tests: propose a short list, do not add them unasked. Every bug actually hit gets a regression test that fails before the fix and passes after it.
- Commits stay local. No push, no repo rename, no GitHub Pages activation without the owner's separate explicit go-ahead for each.
- Do not edit `HANDOFF.md` or `LOG.md` unless you are the main agent closing a piece of work.
