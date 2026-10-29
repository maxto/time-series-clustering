# Redesign checkpoint 2 (lesson 5 end to end) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lesson 5 complete in the new format: one live DTW figure (two linked series and the cost grid with band and path, driven by one state, with the mon and wed pair for the too-wide window), deep-dive blocks the reader opens, and every claim of the lesson sourced and reviewed, ready for the owner.

**Architecture:** JavaScript DTW kernels in `site/kernels.js`, checked against the Python reference for every state the controls can reach. `scripts/figures.py` keeps writing the static SVG of the figure's initial state and also writes the figure's data (`<name>.live.json`). The build validates that data, embeds it inside the `<figure>` and marks it with its component name. `site/live.js` redraws the figure at the real column width and takes over from the static SVG only after a successful render. A new Markdown container `::: deep <title>` renders a native `<details>` block for parts of a section the reader may skip.

**Tech Stack:** Python 3.13 (`uv`, `markdown-it-py`, `mdit-py-plugins` container plugin), plain JavaScript and SVG, Node (for the kernel parity runner), `playwright-core` with the system Chrome, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-28-redesign-design.md` (approved 2026-10-29, section 4.1 amended 2026-10-29). Checkpoint 2 is design section 10, step 1.2. Sections to read: 1.1 (content direction), 4.3 (lesson page), 6 to 6.2 (live figures, kernels and parity, state contract), 8 (sources), 9 (testing). Checkpoint 1 plan and ledger for context: `docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md`, `docs/research/2026-10-29-sdd-cp1-ledger.md`.

**Owner decisions for this checkpoint (2026-10-29):**
- "Not a brick": lessons rich but not an endless scroll. Lever 1 (34em reading measure) is done. Lever 2, deep-dives the reader opens, is approved and built here. Lever 3 (a summary line per section) was not chosen.
- Soft-DTW leaves lesson 5 (a variant, design 1.1). It stays on the map as a draft item.
- The scoring section of lesson 5 stays, shorter: the silhouette on the DTW matrix only, with its source. Caliński-Harabasz and the soft-DTW case go to the validation module.
- Parity edge cases (owner: "decidi tu"): window 0, no window, ties. Constant series moves to checkpoint 3, where z-normalisation and SBD are built.

**Revision after the Codex plan review** (`docs/research/2026-10-29-codex-plan-cp2-review.md`, owner go-ahead 2026-10-29): all 12 findings accepted, with one exception. Smoke fixture edits are recorded with `scripts/review.py` by `fixture author`, note `smoke fixture, not a real review`, as in checkpoint 1: they are engine test data, not course content, so they get no second-model review. Finding 4 was already right in the source (`<`), the review read a rendered copy, but its round-trip test is added. `dtwCost` is no longer exported (finding 5). The pair choice is a native radio group (finding 9).

## Global Constraints

- Everything in `AGENTS.md` holds: English only, no semicolons or em-dashes in prose, no CDN or external request at runtime, no runtime data fetch, approved tokens, `tsc:theme`, Geist and Geist Mono, figure classes only, `uv run` for Python, commits local, `AGENTS.md` updated in the task that changes the rule.
- DTW convention (`AGENTS.md`): local cost squared difference, closed endpoints (0, 0) and (n-1, m-1), steps (1, 0), (0, 1), (1, 1) with no weights, Sakoe-Chiba window `|i - j| <= w` in samples, result the square root of the accumulated cost, no length normalisation. Path tie order walking back: diagonal, then (i-1, j), then (i, j-1) (`code/python/tsc/distances.py:dtw_path`). Course window `w = 4`.
- Reading column (design 4.1 as amended): 680 px next to the contents, 720 px without, running text 34em, 17 px text, 16 px on phones.
- Static figures are shown at most at their drawn size (`figure svg { max-width: 360px }`). A live figure redraws at the real column width and is exempt from that cap. Every figure label stays at or below 16 px on screen (existing e2e check, keep it passing for live figures too).
- Live figures (design 6): native radio buttons, range inputs, checkboxes and buttons, keyboard operable, visible focus, a text alternative that states the current state and updates with it, `prefers-reduced-motion` respected (no animation at all), static SVG fallback without JavaScript or when the script fails. Groupings and scores are never recomputed in the browser: anything shown next to a live control names the state it was computed for.
- Tests: expected values from an independent source (Python reference values computed by a separate process, a hand computation, the spec). No test that mirrors the implementation. Negative tests check that their mutation applied, then assert the specific diagnostic.
- Headless Chrome flags `--disable-gpu --disable-software-rasterizer --use-gl=swiftshader`.
- Lesson content: every claim follows design 1.1 and 8 (written, source found and read at the supporting point, confirmed by web search, reviewed by another model). Review records only through `scripts/review.py` after the review.
- First phase: no exercises, transfer tasks or predict-then-reveal blocks.

## Review Focus

Chosen by Claude under the owner's delegation (2026-10-29). Each line names its test and the task that owns it.

1. Keyboard only, following the W3C APG radio pattern: Tab enters the pair group at the checked radio, arrows change the pair, Tab moves on to the slider (arrows change `w`), the no-window box (Space) and Reset (Enter). Focus visible in both themes. Task 3.
2. The script fails: blocked before it runs (static figure, caption and numbers complete, no controls) or throwing after the reader changed the state (the static figure comes back, the controls go, a line says which state is shown, the other figure on the page keeps working). Task 3.
3. A width change while a state is set (1440 to 375 px): the figure redraws at the new width, its rendered width equals the figure's content width, and the state and readout stay. Task 3.
4. Two live figures on one page: each reads only its own data and its own controls. Changing and resetting one leaves the other's checked inputs, path and readout unchanged. Task 3.
5. Deep-dive content: findable by search, reachable without JavaScript, measured by the contrast sweep when open, and a `#heading-id` link into a deep-dive refused (deep-dives have no headings). Task 4.

---

### Task 1: JavaScript DTW kernels and parity with Python

**Files:**
- Create: `site/kernels.js`, `tests/kernels_cli.mjs`, `tests/test_kernels.py`
- Modify: `scripts/build.py` (copy `kernels.js` into `assets/`), `AGENTS.md` (Layout, Commands)

**Interfaces:**
- Produces, in `site/kernels.js`, one global `window.TSC_KERNELS` in the browser and the same object as `globalThis.TSC_KERNELS` when the file is evaluated by Node (no ES module syntax, so it loads from `file://` as a plain script):
  - `euclidean(x: number[], y: number[]) -> number`
  - `dtw(x, y, w: number|null) -> number`
  - `dtwPath(x, y, w) -> [number, number][]`
  - Invalid input throws `Error` with a message starting `invalid:` (empty or non-finite series, `w` not a non-negative integer or null, `w < |n - m|`, unequal lengths for `euclidean`).
  - No accumulated-cost table is exported. The live figure shades local costs, `(x[i] - y[j])^2`, which it computes itself.
- Produces `tests/kernels_cli.mjs`: reads a JSON list of cases `{op, x, y, w}` on stdin (`op` one of `euclidean`, `dtw`, `dtwPath`). A number that JSON cannot carry is sent tagged, `{"special": "NaN"}` or `{"special": "Infinity"}`, and the runner turns it into the JavaScript value just before the call. It writes a JSON list with exactly one result per case, `{"value": ...}` or `{"error": "<message>"}`. A malformed request (not JSON, unknown `op`, unknown tag) is a transport failure: message on stderr, exit 2, no results.

- [ ] **Step 1: Write `tests/kernels_cli.mjs`** against the interface above, loading `site/kernels.js` with `vm.runInThisContext` on its text. With no kernels file yet it exits 2 with `kernels.js not found`.
- [ ] **Step 2: Write the parity tests** in `tests/test_kernels.py`. Expected values come from the Python reference (`code/python/tsc/distances.py`), computed in the test process, the JavaScript values from a separate `node tests/kernels_cli.mjs` process. The helper asserts exit 0 and one result per case before any comparison. Tolerance `1e-9` absolute on distances, exact equality on paths.
  - `test_fixture_rows_parity`: all 66 pairs of `fixtures/demand-12.csv` at `w = 4`: `dtw` and `euclidean`.
  - `test_reachable_states_parity`: every state the lesson's live figure can reach: pairs `mon-sat` and `mon-wed`, `w` in `0..12` and `None` (28 states): `dtw` and `dtwPath`.
  - `test_window_zero_is_euclidean` (owner edge case): for `mon-sat` and `mon-wed`, JavaScript `dtw(x, y, 0)` equals Python `euclidean(x, y)` (3.71 and 4.15 rounded) and `dtwPath` is the diagonal.
  - `test_no_window` (owner edge case): `w = null` gives the Python `dtw(x, y, None)` and the same path, for both pairs (rounded 0.22 and 0.26).
  - `test_ties_hand_cases` (owner edge case), hand-computed: `x = [0, 0]`, `y = [0, 0]`, `w = null` and `w = 0`: path `[[0, 0], [1, 1]]` (the diagonal wins a three-way tie). `x = [0, 0, 0]`, `y = [0, 0]`, `w = null`: path `[[0, 0], [1, 0], [2, 1]]`.
  - `test_invalid_inputs`: `[]`, `[{"special": "NaN"}]`, `[{"special": "Infinity"}]`, `w = -1`, `w = 1.5`, `w = 0` with lengths 3 and 2, `euclidean` with lengths 3 and 2: each result is `{error}` starting `invalid:`.
  - `test_transport_failure`: an unknown `op` gives exit 2 and no stdout.
- [ ] **Step 3: Run** `uv run pytest tests/test_kernels.py -q`. Expected: FAIL with `kernels.js not found` (the runner exists, the kernels do not).
- [ ] **Step 4: Implement `site/kernels.js`.** Same loops as the Python reference (plain, readable), the same tie order. Copy `kernels.js` into `assets/` in `copy_assets`.
- [ ] **Step 5: Run** `uv run pytest -q`. Expected: all pass. Run `npm test`. Expected: `e2e ok`.
- [ ] **Step 6: Update `AGENTS.md`** (Layout: `site/kernels.js`, `tests/kernels_cli.mjs`, `tests/test_kernels.py`. Rules: the JavaScript kernels copy the reference convention and are checked against it on every reachable state). Commit.

### Task 2: Live figure data, static fallback and build embedding

**Files:**
- Modify: `scripts/figures.py`, `scripts/buildlib/svg.py`, `scripts/buildlib/content.py`, `scripts/buildlib/pages.py`, `scripts/build.py`, `tests/test_build.py`, `tests/e2e.mjs` (smoke assertions for gamma), `AGENTS.md` (Content format)
- Create: `content/figures/dtw-explorer.svg`, `content/figures/dtw-explorer.live.json` (generated), `tests/fixtures/smoke/figures/live-a.live.json`, `live-b.live.json` (hand-written), `live-a.svg`, `live-b.svg` (generated), `tests/live_expect.py`
- Modify: `content/figures/numbers.json` (generated), `tests/fixtures/smoke/03-gamma.md`, `tests/fixtures/smoke/_reviews.toml` (only through `scripts/review.py`)

**Interfaces:**
- Produces the data file format, `<figures>/<name>.live.json`:
  ```json
  {"component": "dtw", "sample_minutes": 30,
   "series": {"mon": [48 numbers], "sat": [...], "wed": [...]},
   "pairs": [["mon", "sat"], ["mon", "wed"]],
   "w": {"min": 0, "max": 12, "initial": 4, "none": true},
   "initial": {"pair": 0}}
  ```
  Series values exactly as in `fixtures/demand-12.csv` (4 decimals). `component` names the script that draws it (only `dtw` in this checkpoint).
- Validation of a `.live.json` (build errors, one line each, naming the file and the field, all before any output is prepared): valid JSON object with exactly these keys. `component` is `dtw`. `sample_minutes` a positive integer. `series` a non-empty object, names matching `^[a-z0-9]+$`, every row a non-empty list of finite numbers, all rows of the same length, at most 48 samples (budget: 48 by 48 = 2,304 cells). `pairs` a non-empty list of two distinct series names each. `w.min` and `w.max` integers with `0 <= min <= max <= length - 1`, `w.initial` an integer in `[min, max]`, `w.none` a boolean. `initial.pair` a valid index into `pairs`. A `.live.json` with no `.svg` of the same name is an error (the static fallback is required). The component therefore never meets an invalid state: equal lengths and integer `w >= 0`.
- Produces `live_data_script(data: dict) -> str` in `scripts/buildlib/pages.py`: `<script type="application/json" class="live-data">` with the JSON serialised and then `.replace("<", "\\u003c")` (as `atlas-data`, `pages.py:233`, never HTML-escaped). The rendered figure is `<figure data-live="dtw">` holding the static SVG, that script, then the figcaption. No `id` on the data element. Any lesson figure whose name has a `.live.json` is rendered this way. The page scripts come in Task 3.
- Produces the figure markers, allowed by `svg.py` only in these forms (any other value is an error, and they are the only `data-` attributes allowed): on the root `<svg>` only, `data-pair="<a>-<b>"` (two series names) and `data-w="<integer>|none"`. On any drawn element, `data-part` with one value of `grid` (the grid frame rect), `cell` (a band cell rect), `path` (the warping path polyline in the grid), `link` (a line between the two series), `series-a`, `series-b` (the two series polylines of the top panel). Document them in `AGENTS.md` with the figure rules.
- Produces the geometry contract, shared by the static SVG of Task 2 and the live SVG of Task 3:
  - Top panel: series A (`series-a`, class `ln`) above series B (`series-b`, class `ln-accent`), one point per sample, x growing with the sample index, y decreasing affine in the value, on one shared value scale. Links (`link`, class `ln-muted`) along the DTW path of the current state, for path steps `k` with `k` even or `k` the last step, from point `i` of A to point `j` of B. Labels: the two series names.
  - Grid: rows `i` are series A from the bottom, columns `j` series B from the left. Frame `grid` at `(gx, gy)` with side `size`, `cell = size / n`. Cell `(i, j)` is the rect at `x = gx + j * cell`, `y = gy + size - (i + 1) * cell`. Only band cells are drawn (`|i - j| <= w`, every cell with no window), class `fill-muted`, opacity `0.12 + 0.78 * sqrt(c / cmax)` at 2 decimals, `c` the local cost `(a[i] - b[j])^2`, `cmax` the largest local cost among the drawn cells (0 gives opacity 0.12 everywhere). The path polyline passes through the cell centres `(gx + (j + 0.5) * cell, gy + size - (i + 0.5) * cell)`. Dashed diagonal, band label (`|i − j| ≤ w` or `no window`), traces of A along the left edge and B under the grid, labels `<a>, i ↑` and `<b>, j →`, the shading key from 0 to `cmax` labelled `local cost`. The layout follows `fig_lockstep_vs_dtw` and `fig_dtw_window` (`scripts/figures.py`).
  - `<title>` and `<desc>` state the pair, the window and both distances, and say what the band, the path and the shading mean.
- Produces `tests/live_expect.py`: `uv run python tests/live_expect.py <file.live.json> <pair-index> <w|none> [<pair-index> <w|none> ...]` prints, for each requested state, JSON with the band cells, the path (`tsc.distances.dtw_path`), the kept link steps, the opacity of every band cell and both distances at 2 decimals (`tsc.distances`). Built from the data file, the reference package and the contract above, never from a figure.
- Produces numbers in `numbers.json` (from `figures.py`, rounded at 2 decimals as the existing keys): `euclid_mon_wed`, `dtw4_mon_wed`, `dtwnone_mon_wed`, `dtw10_mon_wed` (10 samples, the smallest window that absorbs the five-hour shift).
- Smoke data, hand-written, in gamma (alpha keeps its single static figure and its checks):
  - `live-a.live.json`: `series {"aa": [0, 1, 0], "ab": [0, 0, 1]}`, `pairs [["aa", "ab"]]`, `w {"min": 0, "max": 2, "initial": 1, "none": true}`, `sample_minutes 30`, `initial {"pair": 0}`. Hand-computed initial state: Euclidean 1.41, DTW 1.00.
  - `live-b.live.json`: `series {"ba": [0, 0, 1, 1], "bb": [0, 1, 1, 1], "bc": [1, 1, 0, 0]}`, `pairs [["ba", "bb"], ["ba", "bc"]]`, `w {"min": 0, "max": 3, "initial": 1, "none": false}`, `sample_minutes 30`, `initial {"pair": 0}`. Hand-computed initial state: Euclidean 1.00, DTW 0.00.
  - `live-a.svg`, `live-b.svg`: written by `figures.py` from these files with the same drawing code (a `--smoke` option), so they follow the geometry contract.

- [ ] **Step 1: Write the build tests** in `tests/test_build.py`:
  - `test_live_figure_embeds_its_data`: the built gamma page holds two `figure[data-live="dtw"]`, each with exactly one `script.live-data` whose parsed JSON equals its own source file, and no element id starting with `live`.
  - `test_live_data_escapes_lt`: `live_data_script({"k": "</script><b>x</b>"})` contains no `</script>` before its own closing tag, and the JSON parsed back from inside the element equals the input.
  - `test_live_data_errors`: one temporary course per rule above (unknown `component`, extra key, a row with a string, a row of 49 samples, rows of unequal length, a pair naming a missing series, `w.max` above `length - 1`, `w.initial` outside `[min, max]`, `w.none` not a boolean, `initial.pair` out of range, a `.live.json` with no `.svg`): each mutation is checked applied, then the run gives exit 1 and its diagnostic names the file and the field.
  - `test_figure_markers`: a static SVG with `data-w="four"`, with `data-part="other"`, with `data-pair` on a child element, or with `data-x`: one error each.
- [ ] **Step 2: Run** `uv run pytest tests/test_build.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement.** `svg.py` markers. `figures.py` writes `dtw-explorer.svg`, `dtw-explorer.live.json`, the new numbers, and with `--smoke` the two smoke SVGs. The build validates and embeds. Add the two figures to `tests/fixtures/smoke/03-gamma.md`, then `uv run python scripts/review.py show --content tests/fixtures/smoke --lesson gamma` and `record --content tests/fixtures/smoke --lesson gamma --fingerprint '<fp>' --by 'fixture author' --note 'smoke fixture, not a real review'`. Regenerate with `uv run python scripts/figures.py` and check `git diff --stat content/figures` shows only the new files and the new numbers (existing figures byte-identical).
- [ ] **Step 4: Static geometry check.** Add to `tests/e2e.mjs`, in the smoke run, a helper `liveGeometry(p, figure, expected)` that reads the SVG of a figure through the markers and the contract (band cells from the rect positions, their opacities, path from the polyline points, links matched to series points, series rows checked affine in the data of the named pair) and compares it with `tests/live_expect.py` output for that state. Run it on the static SVGs of gamma with JavaScript disabled. Update the smoke assertions that count figures so alpha's single figure keeps its checks and gamma's two live figures are named.
- [ ] **Step 5: Run** `uv run pytest -q` and `npm test`. Expected: pass.
- [ ] **Step 6: Update `AGENTS.md`** (Content format: live figures, the data file and its rules, the markers, the static fallback rule. Layout: `tests/live_expect.py`). Commit.

### Task 3: The live DTW figure

**Files:**
- Create: `site/live.js`
- Modify: `site/theme.css` (live figure layout and controls, no new colours), `scripts/build.py` (copy `live.js`), `site/page.html`, `tests/e2e.mjs`, `AGENTS.md`

**Interfaces:**
- Consumes: `window.TSC_KERNELS` (Task 1), `figure[data-live="dtw"]`, its `script.live-data`, the markers and the geometry contract, `tests/live_expect.py` and `liveGeometry` (Task 2), the figure classes of `site/theme.css`.
- Produces: for each `figure[data-live]`, a component found by `component` name in a small registry inside `live.js`. Each figure is handled on its own inside `try`: a failure in one never touches another.

**Input contract (design 6.1), the `dtw` component, all derived from the figure's own validated data:**
- Pair: a `<fieldset>` with `<legend>Pair</legend>` and one native radio per pair, label `<a> and <b>`, group `name` unique per figure on the page (`live-<n>-pair`, `n` the figure's position). Shown only when there are two or more pairs. Initial `initial.pair`.
- Window: `<input type="range">` with `min`, `max` and `step 1` from `w`, initial `w.initial`, a visible readout of the window (`w = 4 samples (2 h)`, `w = 1 sample (30 min)`) and `aria-valuetext` with the same words. Duration: `w * sample_minutes` minutes, below 60 written `N min`, else hours written whole (`2 h`) or with one decimal (`1.5 h`).
- No window: a checkbox `No window`, shown only when `w.none` is true. Checked: the slider is disabled and the state uses `w = null`. Unchecked: the slider is enabled again and the state takes the slider's retained value.
- Reset button `Reset`: back to `initial.pair`, `w.initial`, the box unchecked.
- Readout under the figure, one line, `aria-live="polite"`: `mon and sat, w = 4 samples (2 h): DTW 0.22, Euclidean 3.71`, with no window `mon and sat, no window: DTW 0.22, Euclidean 3.71`, numbers at 2 decimals from the kernels.
- Text alternative: the live SVG's `<title>` and `<desc>` follow the geometry contract and change with the state. The live SVG carries the markers of Task 2 (`data-pair`, `data-w`, `data-part`).
- Activation is atomic: the component builds the live SVG and the controls detached, renders the initial state once, and only then swaps them in for the static SVG in one step. The static SVG node is kept, detached, as the baseline.
- Failure after activation (an exception while computing or drawing a new state): put the baseline SVG back, remove the live SVG and the controls, and set the readout to `The interactive figure stopped. Shown: the initial setting, mon and sat, w = 4 samples (2 h).` (names and window from the data). Log one `console.error` starting `live figure:`.
- Rendering: the grid holds at most 2,304 cells. Every redraw replaces the previous SVG content, so the page never holds more than one state's cells. No animation.
- Width: the live SVG has class `live`, which removes the 360 px cap (`max-width: none`). Its `viewBox` width equals the figure's content width at render time, so one unit is one CSS pixel and labels keep their CSS size. Recomputed on `resize` (debounced), keeping the state.
- `site/page.html` loads `assets/kernels.js` and `assets/live.js` with `defer`.

- [ ] **Step 1: Write the e2e checks** in `tests/e2e.mjs`, on the smoke build, gamma page (the real lesson is checked in Task 5):
  - Request guard, for every context of every run: a request of type `fetch` or `xhr` is a failure.
  - A failure context helper: like `context`, but it exempts only the one blocked URL, or only console errors starting `live figure:`, and still fails on anything else.
  - Initial agreement: after load, each live SVG passes `liveGeometry` for its initial state, and the readouts are `aa and ab, w = 1 sample (30 min): DTW 1.00, Euclidean 1.41` and `ba and bb, w = 1 sample (30 min): DTW 0.00, Euclidean 1.00`.
  - Every element inside a live SVG uses only the classes between the `figure-classes` markers (read from `site/theme.css`), and has no `fill`, `stroke` or `style` attribute.
  - Controls, keyboard only (Review Focus 1), on `live-b`: Tab into the pair group, the checked radio has focus, ArrowDown checks `ba and bc`. Tab to the slider, ArrowRight twice (`w = 3`), ArrowLeft three times (`w = 0`). After each change `liveGeometry` passes for the new state and the readout matches `tests/live_expect.py`. On `live-a`: check `No window` with Space (slider disabled, readout `no window`, geometry for `none`), uncheck (slider value back to its retained value). Reset with Enter restores the initial state.
  - Focus visible on each control, both themes: outline width at least 2 px and outline colour against the composed background at least 4.5:1, as the finance focus ring check.
  - Review Focus 4: change and reset `live-b`, and after each step the checked inputs, the path points and the readout of `live-a` are unchanged.
  - Review Focus 2, blocked: in failure contexts, block `live.js`, then separately `kernels.js`: the static SVGs are visible and pass `liveGeometry` for the initial state, captions present, no controls, no readout.
  - Review Focus 2, after activation: on `live-b` set `ba and bc`, then replace `window.TSC_KERNELS.dtwPath` with a function that throws and move the slider: `live-b` shows its baseline SVG (initial state geometry), no controls, the readout line names the initial setting, and `live-a` still responds to its slider.
  - Review Focus 3: on `live-b` set `ba and bc`, `w = 2`, resize from 1440 to 375 px: the SVG's rendered width equals the figure's content width (within 1 px), the `viewBox` width equals it too, the geometry and readout are unchanged.
  - No-JavaScript run: the static figures are present and no control is shown.
  - The existing width, contrast (both themes) and figure-label checks run on gamma after the live figures render, controls included.
- [ ] **Step 2: Run** `npm test`. Expected: the new checks FAIL.
- [ ] **Step 3: Implement `site/live.js`** and the CSS. Plain JavaScript, no library. Controls are real `<label>`ed inputs inside a `<div class="live-ctl">` after the SVG and before the figcaption, the readout below them. Put the input contract above in a comment at the top of the component.
- [ ] **Step 4: Run** `npm test` and `uv run pytest -q`. Expected: pass. Take one screenshot of gamma at 1440 and 375 px, both themes, and look at it.
- [ ] **Step 5: Update `AGENTS.md`** (Layout: `site/live.js`. Rules: the input contract lives in the comment at the top of the component). Commit.

### Task 4: Deep-dive blocks

**Files:**
- Modify: `scripts/buildlib/content.py`, `scripts/build.py`, `scripts/buildlib/search.py`, `site/theme.css`, `tests/fixtures/smoke/01-alpha.md`, `tests/fixtures/smoke/_reviews.toml` (only through `scripts/review.py`, as in Task 2), `tests/test_build.py`, `tests/e2e.mjs`, `AGENTS.md` (Content format)

**Interfaces:**
- Produces the syntax, inside a content section only:
  ```markdown
  ::: deep Library conventions differ
  Paragraphs, lists, math and citations.
  :::
  ```
  rendered as `<details class="deep"><summary>Library conventions differ</summary> ... </details>`. Closed by default. No `id`, not listed in the contents or the jump links.
- The title is plain text, HTML-escaped on output. It must be non-empty and follow the prose rules, and it may not hold a citation, math or a link.
- A source-aware validation pass runs on the lesson text before `split_blocks` and before heading ids are collected. It skips fenced code (so `::: deep` shown inside a fence is code). It reports, one line each with the line number: an opener `::: deep` without a title, a nested opener, a closer `:::` with no open block, a block still open at the next `## ` heading or at the end of the file (the plugin would close it silently), a heading (`#` at any level) inside, a figure inside, a block outside a content section (in one line, finance, measure card, code or common mistake).
- The body goes through the existing paths: inline tokens keep the citation, math, link and prose checks and count in the paragraph fingerprints.
- Search: the title and the body are indexed with their section, so a hit lands on the section.

- [ ] **Step 1: Write the tests.** `tests/test_build.py`: `test_deep_dive_renders` (smoke alpha holds one deep-dive with a paragraph, a list, inline math and a citation: the built page has one `details.deep` with the summary text, rendered KaTeX and the citation link, and the citation's source is listed at the end of the lesson). `test_deep_dive_fence_is_code` (a fenced example of the syntax renders as code, no `details`). `test_deep_dive_errors` (one negative test per rule above, plus a semicolon in the title and a semicolon in the body, each asserting its message). Review Focus 5: a lesson link `#<slug of the deep-dive title>` is refused as a missing target. `tests/e2e.mjs`: the deep-dive opens with a click and with Enter on its summary, its text is present without JavaScript, a search for a word only inside it finds its section, and the contrast sweep opens every `details.deep` before measuring.
- [ ] **Step 2: Run** the tests. Expected: FAIL.
- [ ] **Step 3: Implement** with `mdit_py_plugins.container.container_plugin` (name `deep`) and a render rule, after the validation pass. CSS: a quiet block in the reading measure, summary in the body font with a disclosure marker, no new colours. Record the alpha fingerprints with `review.py` as `fixture author`.
- [ ] **Step 4: Run** `uv run pytest -q` and `npm test`. Expected: pass.
- [ ] **Step 5: Update `AGENTS.md`** (Content format: deep-dives and their rules). Commit.

### Task 5: Lesson 5 content, sources and integration

Done by the controller, not by an implementer subagent: it is research and writing under design 1.1 and 8, then a Codex review. Files: `content/05-dtw.md`, `content/_sources.toml`, `content/_reviews.toml` (only through `scripts/review.py`), `content/_sources-check.json`, `tests/e2e.mjs` (content run), `docs/research/` (request and review files).

- [ ] **Step 1: Restructure the text.** Remove `## Soft-DTW, a short extension`. Shorten `## Can the groups be scored?` to the silhouette on the DTW matrix (what it needs, the value {{n:silhouette_dtw4_k2}}, what it does not say). Replace `figures/dtw-window.svg` with `figures/dtw-explorer.svg` and write the paragraph that tells the reader what to try (mon and sat from `w = 0` to `w = 4`, then mon and wed past 10, with `{{n:dtw4_mon_wed}}`, `{{n:dtw10_mon_wed}}`, `{{n:dtwnone_mon_wed}}`), naming the state of every number. Move the library-conventions paragraph and the step-by-step reading of the cost grid into deep-dives. Keep `lockstep-vs-dtw.svg` and `dtw-matrix.svg` static. `dtw-window.svg` stays generated but unused: propose its removal to the owner, do not delete it.
- [ ] **Step 2: Claim checklist.** List every statement of the lesson, front matter, figure titles and descriptions, captions, finance text and the scoring section included, as one of: a literature claim (needs a source), a consequence of the course's stated definition, or an observation computed from the frozen fixture (needs a `numbers.json` key). Save it in the Task 5 review request.
- [ ] **Step 3: Sources, one claim at a time.** For each literature claim: write it, find the reference in its standard form (design 1.1), read it at the supporting point, confirm by web search (DOI, arXiv, publisher page), add it to `_sources.toml`, cite it `[@key, locator]`. Expected: the DTW definition and the window (Sakoe and Chiba 1978, at their definition), the survey form against the course convention (Paparrizos et al. 2024, section 5.1, which defines the unrooted accumulated cost: the final square root is stated as the course's convention), the silhouette (Rousseeuw 1987, at its definition). Library conventions: the documentation of each library, the locator naming the function and the parameter or return value, the version and the access date (`aeon` `dtw_distance`, the Python `dtw` package `dtw.dtw` and `StepPattern`). Giorgino 2009 only for the algorithm and the step patterns, never for the Python defaults. No plain links to papers remain in the lesson.
- [ ] **Step 4: Run** `uv run python scripts/check_sources.py`. Expected: every identifier `matched`, or `manual-needed` with a dated `manual` record for author or documentation URLs.
- [ ] **Step 5: Codex review** of the rewritten lesson, the checklist and every citation: request and answer files in `docs/research/`. Bring the findings to the owner with Claude's view where a finding changes meaning. Fix, re-check.
- [ ] **Step 6: Record** after the review, with the values `show` prints for the final text:
  ```bash
  uv run python scripts/review.py show --content content --lesson dtw
  uv run python scripts/review.py record --content content --lesson dtw --fingerprint '<lesson fingerprint>' --by '<reviewer>'
  uv run python scripts/review.py record --content content --lesson dtw --cite '<key>' --locator '<locator>' --paragraph '<paragraph fingerprint>' --by '<reviewer>'
  uv run python scripts/review.py show --content content --lesson dtw
  ```
  One citation call per citation tuple `show` lists. The last `show` reports nothing missing. If a source identity edit reopened another lesson, review and record it too.
- [ ] **Step 7: Lesson e2e.** In the content run of `tests/e2e.mjs`, lesson `dtw`: the static `dtw-explorer` passes `liveGeometry` for `mon-sat, w = 4` with JavaScript disabled. With JavaScript, the live figure passes it for the initial state, then for `mon and wed` at `w = 10` (readout `DTW` equal to `numbers.json` `dtw10_mon_wed`, 0.26), at `w = 4` (`dtw4_mon_wed`, 3.51), with `No window` (`dtwnone_mon_wed`, 0.26), at `w = 0` (`euclid_mon_wed`, 4.15). Reset restores `mon and sat, w = 4 samples (2 h): DTW 0.22, Euclidean 3.71`. Run `npm run preview`, `uv run pytest -q`, `npm test`. Commit.

### Task 6: Checkpoint check and demo

- [ ] **Step 1:** `uv run pytest -q`, `npm test`, `npm run preview`, `npm run build` (expected exit 1 with draft map lines only), `npm run shots`. Look at the shots of lesson 5 (1440 and 390 px, both themes), with the live figure at `mon and wed`, `w = 10` once.
- [ ] **Step 2:** Read the lesson once with the `frontend-design` skill as the critique lens (restraint, line length, one memorable element, no generic chrome). Record proposed changes, do not apply ones that change the design without the owner.
- [ ] **Step 3:** Update `HANDOFF.md` and `LOG.md` (main agent only), commit, give the owner the demo link with what to try.
