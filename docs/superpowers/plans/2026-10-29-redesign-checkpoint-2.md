# Redesign checkpoint 2 (lesson 5 end to end) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lesson 5 complete in the new format: one live DTW figure (two linked series and the cost grid with band and path, driven by one state, with the mon and wed pair for the too-wide window), deep-dive blocks the reader opens, and every claim of the lesson sourced and reviewed, ready for the owner.

**Architecture:** JavaScript DTW kernels in `site/kernels.js`, checked against the Python reference for every state the controls can reach. `scripts/figures.py` keeps writing the static SVG of the figure's initial state and also writes the figure's data (`<name>.live.json`). The build embeds that data inside the `<figure>` and marks it with its component name. `site/live.js` redraws the figure at the real column width and takes over from the static SVG only after a successful render. A new Markdown container `::: deep <title>` renders a native `<details>` block for parts of a section the reader may skip.

**Tech Stack:** Python 3.13 (`uv`, `markdown-it-py`, `mdit-py-plugins` container plugin), plain JavaScript and SVG, Node (for the kernel parity runner), `playwright-core` with the system Chrome, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-28-redesign-design.md` (approved 2026-10-29, section 4.1 amended 2026-10-29). Checkpoint 2 is design section 10, step 1.2. Sections to read: 1.1 (content direction), 4.3 (lesson page), 6 to 6.2 (live figures, kernels and parity, state contract), 8 (sources), 9 (testing). Checkpoint 1 plan and ledger for context: `docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md`, `docs/research/2026-10-29-sdd-cp1-ledger.md`.

**Owner decisions for this checkpoint (2026-10-29):**
- "Not a brick": lessons rich but not an endless scroll. Lever 1 (34em reading measure) is done. Lever 2, deep-dives the reader opens, is approved and built here. Lever 3 (a summary line per section) was not chosen.
- Soft-DTW leaves lesson 5 (a variant, design 1.1). It stays on the map as a draft item.
- The scoring section of lesson 5 stays, shorter: the silhouette on the DTW matrix only, with its source. Caliński-Harabasz and the soft-DTW case go to the validation module.
- Parity edge cases (owner: "decidi tu"): window 0, no window, ties. Constant series moves to checkpoint 3, where z-normalisation and SBD are built.

## Global Constraints

- Everything in `AGENTS.md` holds: English only, no semicolons or em-dashes in prose, no CDN or external request at runtime, no runtime data fetch, approved tokens, `tsc:theme`, Geist and Geist Mono, figure classes only, `uv run` for Python, commits local, `AGENTS.md` updated in the task that changes the rule.
- DTW convention (`AGENTS.md`): local cost squared difference, closed endpoints (0, 0) and (n-1, m-1), steps (1, 0), (0, 1), (1, 1) with no weights, Sakoe-Chiba window `|i - j| <= w` in samples, result the square root of the accumulated cost, no length normalisation. Path tie order walking back: diagonal, then (i-1, j), then (i, j-1) (`code/python/tsc/distances.py:dtw_path`). Course window `w = 4`.
- Reading column (design 4.1 as amended): 680 px next to the contents, 720 px without, running text 34em, 17 px text, 16 px on phones.
- Static figures are shown at most at their drawn size (`figure svg { max-width: 360px }`). A live figure redraws at the real column width and is exempt from that cap. Every figure label stays at or below 16 px on screen (existing e2e check, keep it passing for live figures too).
- Live figures (design 6): native range inputs, checkboxes and buttons, keyboard operable, visible focus, a text alternative that states the current state and updates with it, `prefers-reduced-motion` respected (no animation at all is the simplest way), static SVG fallback without JavaScript or when the script fails. Groupings and scores are never recomputed in the browser: anything shown next to a live control names the state it was computed for.
- Tests: expected values from an independent source (Python reference values written to a file by a separate process, a hand computation, the spec). No test that mirrors the implementation. Negative tests check that their mutation applied, then assert the specific diagnostic.
- Headless Chrome flags `--disable-gpu --disable-software-rasterizer --use-gl=swiftshader`.
- Lesson content: every claim follows design 1.1 and 8 (written, source found and read at the supporting point, confirmed by web search, reviewed by another model). Review records only through `scripts/review.py` after the review.
- First phase: no exercises, transfer tasks or predict-then-reveal blocks.

## Review Focus

Chosen by Claude under the owner's delegation (2026-10-29). Each line names its test and the task that owns it.

1. Keyboard only: Tab reaches the pair choice, the window slider, the no-window box and Reset. Arrow keys on the slider change `w` and the readout. Focus stays visible. Task 3.
2. The script fails or is blocked: the static figure, its caption and its numbers stay complete and readable. Task 3.
3. A width change while a state is set (a phone rotated, a window resized from 1440 to 375 px): the figure redraws at the new width and keeps the state. Task 3.
4. Two live figures on one page: each reads only its own embedded data (no global ids). Task 2 (smoke fixture with two live figures) and Task 3.
5. Deep-dive content: findable by search, reachable without JavaScript, measured by the contrast sweep when open, and a `#heading-id` link into a deep-dive refused (deep-dives have no headings). Task 4.

---

### Task 1: JavaScript DTW kernels and parity with Python

**Files:**
- Create: `site/kernels.js`, `tests/kernels_cli.mjs`, `tests/test_kernels.py`
- Modify: `scripts/build.py` (copy `kernels.js` into `assets/`), `AGENTS.md` (Layout, Commands)

**Interfaces:**
- Produces, in `site/kernels.js`, one global `window.TSC_KERNELS` in the browser and the same object as `globalThis.TSC_KERNELS` when the file is evaluated by Node (no ES module syntax, so it loads from `file://` as a plain script):
  - `euclidean(x: number[], y: number[]) -> number`
  - `dtwCost(x, y, w: number|null) -> Float64Array[]` (accumulated cost rows, `Infinity` outside the window)
  - `dtw(x, y, w) -> number`
  - `dtwPath(x, y, w) -> [number, number][]`
  - Invalid input throws `Error` with a message starting `invalid:` (empty or non-finite series, `w` not a non-negative integer or null, `w < |n - m|`, unequal lengths for `euclidean`). The live figure shows such a state as invalid (design 6.1). With the controls of Task 3 no invalid state is reachable: say so in the figure's contract comment.
- Produces `tests/kernels_cli.mjs`: reads a JSON list of cases `{op, x, y, w}` on stdin, evaluates `site/kernels.js`, writes a JSON list of results (`{value}` or `{error}`) on stdout.

- [ ] **Step 1: Write the parity tests** in `tests/test_kernels.py`. Expected values come from the Python reference (`code/python/tsc/distances.py`), computed in the test process, and the JavaScript values from a separate `node tests/kernels_cli.mjs` process. Tolerance `1e-9` absolute on distances, exact equality on paths.
  - `test_fixture_rows_parity`: all 66 pairs of `fixtures/demand-12.csv` at `w = 4`: `dtw` and `euclidean`.
  - `test_reachable_states_parity`: every state the live figure can reach: pairs `mon-sat` and `mon-wed`, `w` in `0..12` and `None` (28 states): `dtw` and `dtwPath`.
  - `test_window_zero_is_euclidean` (owner edge case): for `mon-sat` and `mon-wed`, JavaScript `dtw(x, y, 0)` equals Python `euclidean(x, y)` (3.71 and 4.15 rounded) and `dtwPath` is the diagonal.
  - `test_no_window` (owner edge case): `w = null` gives the Python `dtw(x, y, None)` and the same path, for both pairs (rounded 0.22 and 0.26).
  - `test_ties_hand_cases` (owner edge case), hand-computed: `x = [0, 0]`, `y = [0, 0]`, any window: path `[[0, 0], [1, 1]]` (the diagonal wins a three-way tie). `x = [0, 0, 0]`, `y = [0, 0]`, no window: path `[[0, 0], [1, 0], [2, 1]]`.
  - `test_invalid_inputs`: `[]`, `[NaN]`, `w = -1`, `w = 1.5`, `w = 0` with lengths 3 and 2: each result is `{error}` starting `invalid:`.
- [ ] **Step 2: Run** `uv run pytest tests/test_kernels.py -q`. Expected: FAIL (`site/kernels.js` missing).
- [ ] **Step 3: Implement `site/kernels.js` and `tests/kernels_cli.mjs`.** Same loops as the Python reference (plain, readable), the same tie order. Copy `kernels.js` into `assets/` in `copy_assets`.
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: all pass. Run `npm test`. Expected: `e2e ok`.
- [ ] **Step 5: Update `AGENTS.md`** (Layout: `site/kernels.js`, `tests/kernels_cli.mjs`, `tests/test_kernels.py`. Rules: the JavaScript kernels copy the reference convention and are checked against it on every reachable state). Commit.

### Task 2: Live figure data and build embedding

**Files:**
- Modify: `scripts/figures.py`, `scripts/buildlib/content.py`, `scripts/build.py`
- Create: `content/figures/dtw-explorer.svg`, `content/figures/dtw-explorer.live.json` (generated), `tests/fixtures/smoke/figures/live-a.svg`, `live-a.live.json`, `live-b.svg`, `live-b.live.json`
- Modify: `content/figures/numbers.json` (generated), `tests/fixtures/smoke/01-alpha.md`, `tests/test_build.py`, `AGENTS.md` (Content format)

**Interfaces:**
- Consumes: Task 1 kernels (not at build time, only by the page).
- Produces the data file format, `content/figures/<name>.live.json`:
  ```json
  {"component": "dtw", "unit": "half hour", "series": {"mon": [...48], "sat": [...], "wed": [...]},
   "pairs": [["mon", "sat"], ["mon", "wed"]], "w": {"min": 0, "max": 12, "initial": 4, "none": true},
   "initial": {"pair": 0}}
  ```
  Series values exactly as in `fixtures/demand-12.csv` (4 decimals). `component` names the script that draws it (only `dtw` in this checkpoint).
- Produces the rendered figure: `<figure data-live="dtw">` holding the static SVG, `<script type="application/json" class="live-data">` with the JSON (with `<` escaped as `<`, as `atlas-data` does), and the figcaption. No `id` on the data element. The page scripts are added in Task 3.
- Produces numbers in `numbers.json` (from `figures.py`, unrounded values rounded at 2 decimals as the existing keys): `euclid_mon_wed`, `dtw4_mon_wed`, `dtwnone_mon_wed`, `dtw10_mon_wed` (the smallest window that absorbs the five-hour shift, 10 samples).
- The static `dtw-explorer.svg` is the initial state (`mon-sat`, `w = 4`): top, the two series linked along the DTW path (every second link, as `lockstep-vs-dtw.svg` does), bottom, the cost grid with the band and the path (as `dtw-window.svg` does). It carries `data-pair="mon-sat"`, `data-w="4"` on the root and `data-path="i,j i,j ..."` (every path cell, space-separated) on the path element, for the e2e agreement check of Task 3. Same figure rules as every static figure.

- [ ] **Step 1: Write the build tests** in `tests/test_build.py`:
  - `test_live_figure_embeds_its_data`: smoke `01-alpha.md` holds two live figures (`live-a`, `live-b`, minimal valid data files with different series): each built `<figure data-live="dtw">` contains exactly one `script.live-data` whose JSON equals its own source file, and the page has no element id starting with `live`.
  - `test_live_data_errors`: a data file with an unknown `component`, a pair naming a missing series, `w.initial` outside `[min, max]`, series of unequal length within a pair while `w.min < |n - m|`: one diagnostic line each, naming the file and the field, exit 1.
  - `test_live_data_without_svg`: a `.live.json` with no matching `.svg` is an error (the static fallback is required).
- [ ] **Step 2: Run** `uv run pytest tests/test_build.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement.** `figures.py` writes `dtw-explorer.svg`, `dtw-explorer.live.json` and the new numbers. The build validates and embeds. Regenerate with `uv run python scripts/figures.py` and check `git diff --stat content/figures` shows only the new files and the new numbers (existing figures byte-identical).
- [ ] **Step 4: Run** `uv run pytest -q` and `npm test`. Expected: pass.
- [ ] **Step 5: Update `AGENTS.md`** (Content format: live figures, the data file and its fields, the static fallback rule). Commit.

### Task 3: The live DTW figure

**Files:**
- Create: `site/live.js`
- Modify: `site/theme.css` (live figure layout and controls, between the figure rules, no new colours), `scripts/build.py` (copy `live.js`), `site/page.html`, `tests/e2e.mjs`, `AGENTS.md`

**Interfaces:**
- Consumes: `window.TSC_KERNELS` (Task 1), `figure[data-live="dtw"]` and its `script.live-data` (Task 2), the figure classes of `site/theme.css`.
- Produces: for each `figure[data-live]`, a component found by `component` name in a small registry inside `live.js`. The `dtw` component draws into an SVG it creates (same classes, `role="img"`, a `<title>`), replaces the static SVG only after its first render succeeds, and adds the controls below it.

**Input contract (design 6.1), the `dtw` component:**
- Pair: two radio buttons, labels `mon and sat` and `mon and wed`. Initial `mon and sat`.
- Window: `<input type="range" min="0" max="12" step="1">`, value in samples, with a visible readout `w = 4 samples (2 h)` and an `aria-valuetext` with the same words. Plus a checkbox `No window`: when checked the slider is disabled and the state uses `w = null`.
- Series ends: no shift is applied to the data. Both series are the untouched fixture rows, so no end handling is needed.
- Invalid state: unreachable with these controls (equal lengths 48, integer `w >= 0`). If the kernels throw, the figure shows the static SVG again and a line `This setting cannot be computed.` in the readout.
- Reset button `Reset`: back to `mon and sat`, `w = 4`, the box unchecked.
- Text alternative: the SVG `<title>` states the pair, the window and both distances, and changes with the state. `site/page.html` loads `assets/kernels.js` and `assets/live.js` with `defer`.
- Readout under the figure, one line, `aria-live="polite"`: `mon and sat, w = 4 samples (2 h): DTW 0.22, Euclidean 3.71`, numbers at 2 decimals from the kernels. With no window: `no window`.
- Rendering budget: 48 by 48 grid, at most 2,304 cells, redrawn on every input event, no animation. Draw only the band cells (as the static figure does).
- Width: the SVG `viewBox` width equals the figure's content width at render time, recomputed on `resize` (debounced, keeping the state). Labels use the figure text classes at their CSS size, so they never scale.
- Next to the figure, the lesson text that names numbers names their state (`numbers.json` keys hold the settings in their names).

- [ ] **Step 1: Write the e2e checks** in `tests/e2e.mjs` (content build, lesson `dtw`):
  - Initial agreement: after load, the live SVG root has `data-pair="mon-sat"`, `data-w="4"`, its path element's `data-path` equals the static SVG's (read from the built HTML before the script runs, or from `content/figures/dtw-explorer.svg`), and the readout says `DTW 0.22, Euclidean 3.71`.
  - Every element inside the live SVG uses only the classes between the `figure-classes` markers (read the class list from `site/theme.css`), has no `fill`, `stroke` or `style` attribute.
  - Controls: choose `mon and wed`, set the slider to 10 with the keyboard (focus it, press ArrowRight from 4 six times): readout `DTW 0.26`. Slider to 4: readout `DTW 3.51`. Check `No window`: slider disabled, readout `no window` and `DTW 0.26`. These values are the Python ones (`numbers.json` keys of Task 2), not the page's own.
  - `Reset` restores `mon and sat`, `w = 4`, `DTW 0.22`.
  - Review Focus 1: Tab order reaches the two radios, the slider, the box and Reset, each with a visible focus outline (computed `outline-style` not `none`).
  - Review Focus 2: in a new context, abort requests for `live.js` (and separately for `kernels.js`): the static SVG is visible, `data-w="4"`, the caption is present, no readout element is added.
  - Review Focus 3: set `mon and wed`, `w = 10`, resize from 1440 to 375 px: the SVG `viewBox` width changes to the new figure content width, the state and readout are unchanged.
  - Review Focus 4: on the smoke build, the two live figures of `alpha` each show their own first pair name in their readout.
  - No-JavaScript run: the static figure is present and no control is shown.
  - The existing width, contrast (both themes) and figure-label checks cover the live figure, with the controls visible: make sure the contrast sweep runs after the live figure has rendered.
- [ ] **Step 2: Run** `npm test`. Expected: the new checks FAIL.
- [ ] **Step 3: Implement `site/live.js`** and the CSS. Plain JavaScript, no library. Controls are real `<label>`ed inputs inside a `<div class="live-ctl">` after the SVG and before the figcaption.
- [ ] **Step 4: Run** `npm test` and `uv run pytest -q`. Expected: pass. Take one screenshot of the figure at 1440 and 375 px, both themes, with `mon and wed`, `w = 10`, and look at them.
- [ ] **Step 5: Update `AGENTS.md`** (Layout: `site/live.js`. Rules: the input contract lives in the plan and in a comment at the top of the component). Commit.

### Task 4: Deep-dive blocks

**Files:**
- Modify: `scripts/buildlib/content.py`, `scripts/build.py`, `scripts/buildlib/search.py`, `site/theme.css`, `tests/fixtures/smoke/01-alpha.md`, `tests/test_build.py`, `tests/e2e.mjs`, `AGENTS.md` (Content format)

**Interfaces:**
- Produces the syntax, inside a content section only:
  ```markdown
  ::: deep Library conventions differ
  Paragraphs, lists, math and citations.
  :::
  ```
  rendered as `<details class="deep"><summary>Library conventions differ</summary> ... </details>`. Closed by default. No `id`, not listed in the contents or the jump links.
- Rules (build errors, one line each): title required, prose rules apply to it, no citation in the title, only inside a content section (not in one line, finance, measure card, code, common mistake), no nesting, no heading and no figure inside, unclosed container.
- Search: the text inside a deep-dive is indexed with its section, so a search hit lands on the section.

- [ ] **Step 1: Write the tests.** `tests/test_build.py`: `test_deep_dive_renders` (smoke alpha holds one deep-dive with a paragraph, a list and a citation: the built page has one `details.deep` with the summary text and the citation link, and the citation's source is listed at the end of the lesson). `test_deep_dive_errors` (one negative test per rule above, each asserting its message). Review Focus 5: a lesson link `#<slug of the deep-dive title>` is refused as a missing target. `tests/e2e.mjs`: the deep-dive opens with a click and with Enter on its summary, works without JavaScript, a search for a word only inside it finds its section, and the contrast sweep opens every `details.deep` before measuring.
- [ ] **Step 2: Run** the tests. Expected: FAIL.
- [ ] **Step 3: Implement** with `mdit_py_plugins.container.container_plugin` (name `deep`) and a render rule. CSS: a quiet block in the reading measure, summary in the body font with a disclosure marker, no new colours.
- [ ] **Step 4: Run** `uv run pytest -q` and `npm test`. Expected: pass.
- [ ] **Step 5: Update `AGENTS.md`** (Content format: deep-dives). Commit.

### Task 5: Lesson 5 content and sources

Done by the controller, not by an implementer subagent: it is research and writing under design 1.1 and 8, then a Codex review. Files: `content/05-dtw.md`, `content/_sources.toml`, `content/_reviews.toml` (only through `scripts/review.py`), `content/_sources-check.json`, `docs/research/` (request and review files).

- [ ] **Step 1: Restructure the text.** Remove `## Soft-DTW, a short extension`. Shorten `## Can the groups be scored?` to the silhouette on the DTW matrix (what it needs, the value {{n:silhouette_dtw4_k2}}, what it does not say). Replace `figures/dtw-window.svg` with `figures/dtw-explorer.svg` and write the paragraph that tells the reader what to try (mon and sat from `w = 0` to `w = 4`, then mon and wed past 10, with `{{n:dtw4_mon_wed}}`, `{{n:dtw10_mon_wed}}`, `{{n:dtwnone_mon_wed}}`), naming the state of every number. Move the library-conventions paragraph and the step-by-step reading of the cost grid into deep-dives. Keep `lockstep-vs-dtw.svg` and `dtw-matrix.svg` static.
- [ ] **Step 2: Sources, one claim at a time.** List every claim that is not a direct consequence of the stated definition. For each: write it, find the reference in its standard form (design 1.1), read it at the supporting point, confirm by web search (DOI, arXiv, publisher page), add it to `_sources.toml`, cite it `[@key, locator]`. Expected claims: the DTW definition and the standard form against the course convention (Sakoe and Chiba 1978 and the Paparrizos et al. 2024 survey, read at their definition), the silhouette (Rousseeuw 1987), the library conventions (`aeon` and `dtw-python` documentation, with version and access date as the locator, or Giorgino 2009 for `dtw-python`). No plain links to papers remain in the lesson.
- [ ] **Step 3: Run** `uv run python scripts/check_sources.py`. Expected: every identifier `matched`, or `manual-needed` with a dated `manual` record for author or documentation URLs.
- [ ] **Step 4: Codex review** of the rewritten lesson and every citation: request and answer files in `docs/research/`. Bring the findings to the owner with Claude's view where a finding changes meaning. Fix, re-check.
- [ ] **Step 5: Record** the lesson and every citation with `uv run python scripts/review.py record --lesson dtw` after the review. Run `npm run preview`, `uv run pytest -q`, `npm test`. Commit.

### Task 6: Checkpoint check and demo

- [ ] **Step 1:** `uv run pytest -q`, `npm test`, `npm run preview`, `npm run build` (expected exit 1 with draft map lines only), `npm run shots`. Look at the shots of lesson 5 (1440 and 390 px, both themes).
- [ ] **Step 2:** Read the lesson once with the `frontend-design` skill as the critique lens (restraint, line length, one memorable element, no generic chrome). Record proposed changes, do not apply ones that change the design without the owner.
- [ ] **Step 3:** Update `HANDOFF.md` and `LOG.md` (main agent only), commit, give the owner the demo link with what to try.
