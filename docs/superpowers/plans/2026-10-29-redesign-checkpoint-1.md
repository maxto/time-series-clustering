# Redesign checkpoint 1 (shell, format, draft map) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the pilot engine into the redesigned course shell (top bar, contents, search, home with the map of the field and sector cards, sources page, new lesson format) with release and preview builds, on the two pilot lessons, ready for the owner's checkpoint 1 review.

**Architecture:** Extend the pilot's Python build. New content data files (`_sources.toml`, `_reviews.toml`, `_map.toml`, `_sectors.toml`) are read and validated by new `buildlib` modules. Review state is derived, never typed by hand: a lesson or map item counts as reviewed only when a record in `_reviews.toml` matches the fingerprint of its current text. Pages are static HTML that reads without JavaScript. Two plain scripts (`course.js`, `map.js`) add behaviour, a generated `search-index.js` works from `file://`. The default build is the release build and refuses draft map content. `--preview` writes a marked preview to `preview/`.

**Tech Stack:** Python 3.13 (`uv`, `markdown-it-py`, `mdit-py-plugins`, `tomllib`, `hashlib`), KaTeX via Node at build time, plain JavaScript and SVG, `playwright-core` with the system Chrome for e2e, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-28-redesign-design.md` (approved 2026-10-29), amending `docs/superpowers/specs/2026-10-28-course-design.md`. Checkpoint 1 is design section 10, step 1.1. Read design section 1.1 first: no exercises in the first phase. Checkpoints 2 (lesson 5 live figures) and 3 (lesson 1 and integration) get their own plans after the owner's checkpoint 1 review. Codex review of this plan: `docs/research/2026-10-29-codex-plan-cp1-review.md` (all findings adopted, owner 2026-10-29).

## Global Constraints

- English only. Prose (lesson text, captions, map and sector text) has no semicolons and no em-dashes, outside code and math. The build rejects them (`AGENTS.md`). Verbatim bibliographic metadata (source titles and venues) is exempt.
- No CDN or external request at runtime. Fonts and KaTeX CSS and fonts are copied into the output `assets/`. No runtime data fetch: data reaches the page as inline JSON or a plain `<script>` file.
- Light and dark themes with the approved tokens of `AGENTS.md` and `docs/design/dark-theme.md`. Preference stored in `localStorage` under `tsc:theme` (never `aicourse:`). With no stored preference, follow `prefers-color-scheme`.
- Contrast (design 4.1, made concrete here): normal-colour body text of the reading column (paragraphs, list items, not links) 10:1 against its background. Every other text, links included, 4.5:1. Both themes. Figure text: its SVG `fill` against the figure panel or box it sits on, same 4.5:1.
- Type: Geist (text), Geist Mono (labels, code). No tracked all-caps labels, labels in sentence case (design 4.1).
- Reading column: one width for everything. 800 px with 18 px text without the contents column, 760 px next to it. Contents column 290 px, fixed from 1180 px of viewport width, a drawer below that (full width on phones). Phones: padding 18 px (design 4.1).
- Figures: SVG styled only through the classes between the `figure-classes` markers of `site/theme.css`, `role="img"` and `<title>`, no colour attributes, no inline style, no root `width`/`height` (`AGENTS.md`).
- Links in lessons: `lesson:<id>`, `#<heading-id>`, `https://`, `mailto:`. No `http://`.
- Site address `https://maxto.github.io/time-series-clustering/` in `SITE_URL`. Add `REPO_URL = "https://github.com/maxto/Time-Series-Clustering"` next to it in `scripts/build.py` (the repo is not renamed yet).
- Every Python command runs through `uv run`. Commits stay local: no push. Each task commits every file it changed.
- Tests: expected values from an independent source (the design, `AGENTS.md`, a hand computation, a literal value computed outside the code under test). No test that mirrors the implementation. Each negative test first checks that its mutation applied (the helper asserts the replaced text existed) and then asserts the specific diagnostic, not only a non-zero exit. The edge cases in the Review Focus were chosen with the owner on 2026-10-29. Any further edge case is proposed to the owner, not added.
- Headless Chrome: launch with `--disable-gpu --disable-software-rasterizer --use-gl=swiftshader`, as `tests/e2e.mjs` does. On 2026-10-29 screenshots timed out without these flags and the cause was not investigated: before any screenshot step, take one screenshot of a blank page and, if it fails, report it as an environment problem, separately from product results.
- First-phase content direction (design 1.1): no exercises, transfer tasks or predict-then-reveal blocks. Do not build them.
- `AGENTS.md` is updated in the task that changes the rule it describes, not at the end.

## Review Focus

Chosen with the owner on 2026-10-29 (all four proposed groups). Each line names its test and the task that owns it.

1. Citations and reviews: a citation in a list item and in a figure caption, a citation removed from a paragraph, the fingerprint of a fixed literal text. Task 2.
2. Map: the same item name in two families, a fit on an item that does not exist, a reviewed item edited afterwards turns draft, preview output inside `dist/` refused. Task 4.
3. Navigation and search: Escape with the drawer and the search open together, focus returns to the control that opened each layer, the reading position is restored, search works from `file://`. Tasks 7 and 8.
4. Schema and layout: a section titled like a reserved block in another case (`## code`), a heading whose slug equals a block id, long chips with conditions and the six sector cards at 375 px without overflow or clipped text. Tasks 1 and 9.

---

### Task 1: Branch, lesson schema v2, migrated lessons, test runner

**Files:**
- Modify: `scripts/buildlib/content.py`, `scripts/build.py` (minimal rendering of the new blocks in the existing template, replaced in Task 5)
- Modify: `content/01-same-series-different-questions.md`, `content/05-dtw.md`
- Modify: `tests/fixtures/smoke/01-alpha.md`, `tests/fixtures/smoke/03-gamma.md`
- Modify: `tests/test_build.py`, `tests/e2e.mjs`, `package.json`, `AGENTS.md` (Content format)

**Interfaces:**
- Produces: `Lesson.blocks: list[Block]`, `Block(kind: str, title: str, id: str, tokens: list)`, `kind` in `oneline | section | finance | measure | code | mistake`. Block ids: `one-line`, `in-finance`, `measure-card`, `code`, `common-mistake` for the fixed blocks, the heading slug for `section`. `Lesson.meta["sector"]: str`. `SECTORS = ("energy", "finance", "weather", "retail", "industry", "health")` in `content.py`. `Lesson.code: dict[str, str]` (language `python` or `r` to code text, only those present).

- [ ] **Step 1: Create the branch**

Run: `git switch -c redesign pilot`
Expected: `Switched to a new branch 'redesign'`

- [ ] **Step 2: Migrate the smoke fixture to the v2 format first**

So the new tests start from valid input:
- `01-alpha.md`: add `sector: energy`. `## Lesson` becomes `## Engine features`. Add `## A second section` with one paragraph after it. Move `## Common mistake` to the end. Add `## Code` before it, with one `python` fence and one `r` fence (one line each).
- `03-gamma.md`: add `sector: finance`. `## Lesson` becomes `## Back to alpha`. `## Check` becomes the content section `## Validity example`, before `## In finance` if present, its sentence unchanged. Move `## Common mistake` to the end.

- [ ] **Step 3: Write the failing tests in `tests/test_build.py`**

Expected values from design 4.3 and 1.1. `mutate(path, old, new)` asserts `old` is in the file before replacing.

```python
def test_v2_smoke_builds(content): ...  # returncode 0

def test_old_lesson_section_is_rejected(content):
    mutate(content / "01-alpha.md", "## Engine features", "## Lesson")
    assert "'## Lesson' was replaced by content sections" in build(content).stdout

def test_check_section_is_rejected(content):
    mutate(content / "03-gamma.md", "## Validity example", "## Check")
    assert "'## Check' is not used in the first phase" in build(content).stdout

def test_reserved_name_in_other_case_is_rejected(content):  # Review Focus 4
    mutate(content / "01-alpha.md", "## A second section", "## code")
    assert "reserved block name" in build(content).stdout

def test_block_order_is_enforced(content):
    move_block_before(content / "01-alpha.md", "Common mistake", "Code")
    assert "out of order" in build(content).stdout

def test_lesson_needs_a_content_section(content):
    remove_block(content / "03-gamma.md", "Back to alpha"); remove_block(content / "03-gamma.md", "Validity example")
    assert "at least one content section" in build(content).stdout

def test_unknown_sector_is_rejected(content):
    mutate(content / "01-alpha.md", "sector: energy", "sector: banking")
    assert "sector 'banking'" in build(content).stdout

def test_figure_in_finance_block_builds(content):
    append_to_block(content / "01-alpha.md", "In finance", "![Caption](figures/overview.svg)")
    assert build(content).returncode == 0

def test_heading_slug_equal_to_block_id_is_rejected(content):  # Review Focus 4
    add_section(content / "01-alpha.md", "Measure card!")  # slug "measure-card"
    assert "measure-card" in build(content).stdout and "block id" in build(content).stdout

def test_repeated_heading_gets_suffix(content):  # AGENTS.md: -2, -3 on repeats, unchanged
    add_subheading(content / "01-alpha.md", "A subheading")
    assert build(content).returncode == 0 and 'id="a-subheading-2"' in page(content, "alpha")

def test_unknown_code_language_is_rejected(content):
    mutate(content / "01-alpha.md", "```r", "```julia")
    assert "julia" in build(content).stdout
```

`add_to_lesson` inserts after `## Engine features`.

- [ ] **Step 4: Run them to see them fail**

Run: `uv run pytest tests/test_build.py -q`
Expected: the new tests FAIL with "unknown section" errors (the parser still has the pilot schema).

- [ ] **Step 5: Implement schema v2 in `content.py`**

- Front matter: the pilot's nine keys plus `sector` (required, one of `SECTORS`).
- Blocks in this order: `## One line` (required, exactly one paragraph), one or more content sections `## <title>`, `## In finance` (optional), `## Measure card` (optional), `## Code` (optional), `## Common mistake` (required, exactly one paragraph, last).
- Reserved names `One line`, `In finance`, `Measure card`, `Code`, `Common mistake`, compared case-insensitively: a content section with one of them in another case is "reserved block name". `## Lesson` and `## Check` get the two messages of Step 3, with "(design 4.3)" and "(design 1.1)".
- `## Code`: at most one fence with info `python`, at most one with info `r`, optional paragraphs. Other fence info: error naming it.
- Figures: alone in a paragraph inside a content section or `## In finance`.
- Heading ids: keep the pilot rule (slug, then `-2`, `-3` on repeats). A slug equal to one of the five block ids is an error naming the slug and "block id".

- [ ] **Step 6: Keep the build running**

In `scripts/build.py`, render content sections in order into the existing `{{body}}` as `<section id="…"><h2>title</h2>…</section>`, the measure card into `{{specimens}}`, each code language as a plain `<pre>`. Task 5 replaces the templates.

- [ ] **Step 7: Migrate the two lessons (structure only, no wording change)**

- `01-same-series-different-questions.md`: `sector: energy`. The two paragraphs before `### Twelve days of demand` become `## What counts as close`. Every `###` becomes `##`. Move `## Common mistake` to the end.
- `05-dtw.md`: `sector: energy`. The paragraphs before `### Two days, one shift` become `## When timing shifts`. Every `###` becomes `##`. `## Check` becomes `## Can the groups be scored?`, after the other content sections. Add `## Code` after `## Measure card`: Python with `tsc.distances.dtw` and `euclidean` on the mon and sat fixture rows at `w = 4`, R with `dtw_distance` from `code/r/distances.R`. Move `## Common mistake` to the end.

- [ ] **Step 8: Check the code block numbers by running them**

Run the Python snippet with `uv run python` and the R snippet with `Rscript` from the repo root.
Expected: Euclidean `3.71` and DTW `0.22` at 2 decimals, the numbers the lesson already states (computed on 2026-10-29 from the reference code: mon and sat, Euclidean 3.71, DTW w=4 0.22).

- [ ] **Step 9: Test runner**

`package.json`: `"test": "node tests/e2e.mjs"`. `tests/e2e.mjs` builds the smoke fixture and the real content itself, fresh, into `tests/output/` (never reading an old `dist/`), then checks both. Replace the smoke assertion on gamma's `.card.check` with one on its `section#validity-example`, and the `.lesson-body` selectors with `main section`.

- [ ] **Step 10: `AGENTS.md` Content format**

Replace the lesson section rules with the contract of Step 5 (`sector`, block order, reserved names, `## Code`, figures in content sections and `## In finance`).

- [ ] **Step 11: Run all tests and commit**

Run: `uv run pytest -q && npm test`
Expected: all pass.

```bash
git add scripts content tests package.json AGENTS.md
git commit -m "Lesson schema v2: content sections, sector, code block"
```

---

### Task 2: Citations, fingerprints and review records

**Files:**
- Create: `scripts/buildlib/cite.py`, `scripts/review.py`
- Create: `tests/fixtures/smoke/_sources.toml`, `tests/fixtures/smoke/_reviews.toml`
- Modify: `scripts/buildlib/content.py` (inline rule), `scripts/build.py` (checks, minimal "Sources cited in this lesson" list), `tests/fixtures/smoke/01-alpha.md`, `AGENTS.md`
- Test: `tests/test_build.py`

**Interfaces:**
- Consumes: `Lesson.blocks`, the number substitution of `content.py`.
- Produces:
  - `load_sources(content, errors) -> dict[str, Source]`, `Source(key, authors: list[str], year: int, title: str, venue: str, doi, arxiv, ssrn, url, topics: list[str])`. `authors` entries are `"Family, Given"`. `Source.label` ("Sakoe and Chiba (1978)", three or more authors "Paparrizos et al. (2024)", family name = text before the comma). `Source.full_authors` ("Hiroaki Sakoe and Seibi Chiba"). `Source.links -> list[tuple[str, str]]`: `("Publisher", "https://doi.org/<doi>")`, `("arXiv", "https://arxiv.org/abs/<id>")`, `("SSRN", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=<id>")`, `("Authors' page", url)`, in that order, only those present. `Source.identity` = `fingerprint` of `doi|arxiv|ssrn|url|title|year`.
  - `TOPICS = ("survey", "compare", "group", "validate", "finance", "software")`.
  - `normalise(text: str) -> str` (runs of whitespace to one space, stripped) and `fingerprint(text: str) -> str` = first 16 hex chars of SHA-256 of `normalise(text)` in UTF-8. One function, used by the build and by `review.py`.
  - Citation syntax `[@key, locator]`, token `tsc_cite`, rendered `<a class="cite" href="#src-<key>" data-ref="<key>">Label</a>`.
  - `Lesson.citations: list[Citation]`, `Citation(key, locator, paragraph: str)`. `paragraph` = `fingerprint` of the `content` of the inline token of the paragraph that holds the citation, after `{{n:}}` substitution. A tight list item and a figure caption are paragraphs too (markdown-it gives each list item a paragraph, the caption is the alt text inside the figure's paragraph).
  - `Lesson.fingerprint` = `fingerprint` of the whole lesson file text after `{{n:}}` substitution, plus the `identity` of every cited source, joined by newlines.
  - `load_reviews(content, errors) -> Reviews` with `lessons: dict[id, set[fingerprint]]`, `citations: set[(lesson, key, locator, paragraph, identity)]`, `items: dict[name, set[fingerprint]]`, `fits: dict[(question, item), set[fingerprint]]` (the last two used by Task 4).
- `_reviews.toml` format:

```toml
[[lesson]]
id = "dtw"
fingerprint = "…"            # Lesson.fingerprint at review time
by = "Claude (sources read), Codex (review)"
date = 2026-10-29
note = "pilot text reviewed 2026-10-28, structure migrated, Sakoe and Chiba sentence added and reviewed"

[[citation]]
lesson = "dtw"
key = "sakoe78"
locator = "sec. II"
paragraph = "…"
identity = "…"
by = "…"
date = 2026-10-29
```

- [ ] **Step 1: Write the failing tests**

Expected values: design 8 and Review Focus 1. The smoke alpha gets the sentence "The band of [@sakoe78, sec. II] limited the path to a strip around the diagonal." in `## Engine features`, a smoke `_sources.toml` with `sakoe78` (the real metadata, see Task 3), and `_reviews.toml` records made with `review.py` for the final fixture.

```python
def test_fingerprint_of_a_literal_text():  # value computed outside the code:
    # printf 'a b c' | sha256sum | cut -c1-16  -> paste the result here at implementation time
    assert fingerprint("  a \n b\tc ") == "<16 hex chars from sha256sum of 'a b c'>"

def test_citation_renders_label_and_source_entry(content):
    page = built_page(content, "alpha")
    assert '<a class="cite" href="#src-sakoe78" data-ref="sakoe78">Sakoe and Chiba (1978)</a>' in page
    assert 'id="src-sakoe78"' in page and "Hiroaki Sakoe and Seibi Chiba" in page

def test_unknown_citation_key_fails(content):
    add_to_lesson(content, "As shown by [@nobody99, p. 1].")
    assert "unknown source 'nobody99'" in build(content).stdout

def test_citation_without_locator_fails(content):
    add_to_lesson(content, "As shown by [@sakoe78].")
    assert "needs a locator" in build(content).stdout

def test_any_edit_reopens_the_lesson_review(content):
    mutate(content / "01-alpha.md", "A fixture lesson", "A fixture lesson,")  # front matter lede
    assert "lesson 'alpha' has no review for its current text" in build(content).stdout

def test_removed_citation_reopens_the_lesson_review(content):  # Review Focus 1
    mutate(content / "01-alpha.md", "The band of [@sakoe78, sec. II] limited", "The band limited")
    assert "lesson 'alpha' has no review" in build(content).stdout

def test_citation_in_list_item_needs_its_record(content):  # Review Focus 1
    add_to_lesson(content, "- a list item citing [@sakoe78, sec. II]")
    record_lesson(content, "alpha")  # lesson record only
    assert "citation [@sakoe78, sec. II] has no review record" in build(content).stdout

def test_citation_in_caption_needs_its_record(content):  # Review Focus 1
    add_to_lesson(content, "![Band of [@sakoe78, sec. II]](figures/overview.svg)")
    record_lesson(content, "alpha")
    assert "has no review record" in build(content).stdout

def test_changed_source_identity_reopens(content):
    edit_source(content, "sakoe78", year=1979)
    assert "has no review" in build(content).stdout

def test_registry_rules(content):
    edit_source(content, "sakoe78", topics=["speech"])
    assert "unknown topic 'speech'" in build(content).stdout
    edit_source(content, "sakoe78", topics=["compare"], doi=None, arxiv=None, ssrn=None, url=None)
    assert "no link" in build(content).stdout
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_build.py -q -k "fingerprint or citation or review or registry"`
Expected: FAIL.

- [ ] **Step 3: Implement `cite.py`, the inline rule and the checks**

- Inline rule regex `\[@([a-z0-9-]+)(?:,\s*([^\]]+))?\]`, registered before the link rule. Inline rules do not run in code spans or fences.
- Checks, in every build mode (lessons are never covered by the draft exception, design 5.1): known key, non-empty locator, a citation record matching `(lesson, key, locator, paragraph, identity)`, a lesson record matching `Lesson.fingerprint`.
- Registry: required `authors`, `year`, `title`, `venue`, `topics` (in `TOPICS`), at least one link field, `url` only `https://`. No prose punctuation rule on `title` and `venue` (verbatim metadata).
- Render the minimal "Sources cited in this lesson" list (`section.lsrc`, one `li#src-<key>` with full authors, year, title, venue, links) at the end of the lesson. Task 5 styles it.

- [ ] **Step 4: Implement `scripts/review.py`**

- `review.py show --content DIR --lesson ID`: prints the lesson fingerprint, then each citation with its locator, its paragraph text and its paragraph fingerprint, and which ones already have a matching record.
- `review.py record --content DIR --lesson ID --fingerprint F --by TEXT [--note TEXT]`: writes the lesson record only if `F` equals the current fingerprint (so the reviewer approves exactly what they read). Same for one citation: `--cite KEY --locator L --paragraph P`.
- `review.py` records a review done by a person or a model. It verifies nothing. A record needs the second-model review done before it is written (`AGENTS.md` Rules).

- [ ] **Step 5: Baseline records for the real lessons**

From here the real content needs lesson records to build. Create `content/_sources.toml` (empty table is valid) and `content/_reviews.toml` with one `[[lesson]]` record per lesson, written with `review.py record`, `by = "Codex, pilot final review"`, `note = "pilot baseline reviewed 2026-10-28 (docs/research/2026-10-28-codex-pilot-final-review.md and re-review), structure migrated 2026-10-29 without wording change"`. This is the retained baseline: checkpoint 1 does not claim the pilot prose meets the first-phase source rule (one or two references per topic). Rewriting it to that rule is checkpoints 2 and 3. Before recording, confirm with `git diff pilot -- content/*.md` that the migration changed only headings, front matter `sector` and block order (plus lesson 5's `## Code`, whose numbers Task 1 Step 8 checked).

- [ ] **Step 6: Run tests, update `AGENTS.md`, commit**

`AGENTS.md`: citation syntax, `_sources.toml` and `_reviews.toml`, `review.py`, the rule that a lesson edit reopens its review.

Run: `uv run pytest -q && npm test`
Expected: PASS.

```bash
git add scripts tests content AGENTS.md
git commit -m "Citations with locators, lesson and citation review records"
```

---

### Task 3: Source check script and the real sources

**Files:**
- Create: `scripts/check_sources.py`
- Modify: `content/_sources.toml`, `content/_reviews.toml`
- Modify: `content/05-dtw.md` (one citation), `content/01-same-series-different-questions.md` (no text change, review record only), `AGENTS.md` (Commands)

**Interfaces:**
- Consumes: `load_sources`, `fingerprint`, `review.py` (Task 2).
- Produces: `content/_sources-check.json`: `{"run": "<date>", "sources": {key: {"doi": outcome, "arxiv": outcome, "ssrn": outcome, "url": outcome, "remote": {...}}}}`, `outcome` in `matched | mismatch | unavailable | manual-needed`. A dated hand check is a field of the source in `_sources.toml`: `manual = { date = 2026-10-29, by = "…", what = "SSRN page opened, title and year match" }`.

- [ ] **Step 1: Implement `check_sources.py`**

Network script, never called by the build. DOI via `https://api.crossref.org/works/<doi>`, arXiv via `https://export.arxiv.org/api/query?id_list=<id>`. Compare the normalised title and the year. A year difference between a preprint and its publication is reported as `mismatch` with both values for a person to judge, never "fixed" by editing the registry to match. SSRN ids and author URLs are `manual-needed` unless the source has a `manual` record. Prints one line per source and a final list of everything not `matched` or manually checked. Exit 1 on any `mismatch`.

- [ ] **Step 2: Add the sources**

`content/_sources.toml`: `sakoe78` (Sakoe and Chiba, *Dynamic programming algorithm optimization for spoken word recognition*, IEEE Transactions on Acoustics, Speech, and Signal Processing, 1978), and the approved reference works `paparrizos24` (arXiv `2412.20574`), `aghabozorgi15` (doi `10.1016/j.is.2015.04.007`), `arbelaitz13` (doi `10.1016/j.patcog.2012.07.021`). Metadata confirmed by web search and by the script, never from memory alone.

Run: `uv run python scripts/check_sources.py`
Expected: every DOI and arXiv id `matched`. Anything else is reported to the controller, not worked around.

- [ ] **Step 3: The one real citation (design 1.1 process)**

In `05-dtw.md`, section `## The window is a decision`, one sentence citing Sakoe and Chiba for the band `|i - j| <= w` (the paper's adjustment window condition). Steps: open the paper, find the passage that states the window condition, record its section or page as the locator, write the sentence so it says only what the passage says, confirm the bibliographic data by web search. Then the controller has the sentence reviewed by another model (Codex) before any record is written.

- [ ] **Step 4: Records for lesson 5**

After Step 3's review: the citation record for `sakoe78` and a new lesson record for lesson 5 (its fingerprint changed with the new sentence), `note` naming the baseline and the reviewed sentence. Lesson 1 keeps its Task 2 record.

- [ ] **Step 5: Run, update `AGENTS.md`, commit**

Run: `uv run pytest -q && npm test && uv run python scripts/check_sources.py`
Expected: PASS, every identifier `matched`.

```bash
git add scripts content AGENTS.md
git commit -m "Source check script, reference works and the first verified citation"
```

---

### Task 4: Map and sector data with derived review state, release and preview builds

**Files:**
- Create: `scripts/buildlib/atlas.py`, `content/_map.toml`, `content/_sectors.toml`, `tests/fixtures/smoke/_map.toml`, `tests/fixtures/smoke/_sectors.toml`
- Modify: `scripts/build.py` (`--preview`, output rules, `data-build` attribute, minimal draft banner), `scripts/review.py` (map records), `tests/fixtures/smoke/_reviews.toml`, `package.json` (`"preview"`), `.gitignore` (`preview/`), `.github/workflows/pages.yml` (comment), `tests/e2e.mjs` (real content built in preview mode), `AGENTS.md` (Rules: the exception, Commands)
- Test: `tests/test_build.py`

**Interfaces:**
- Consumes: `load_sources`, `fingerprint`, `Reviews` (Task 2), `SECTORS` (Task 1), `Course.entries`.
- Produces:
  - `load_atlas(content, sources, reviews, course, errors) -> Atlas | None` (None when `_map.toml` is absent: no map on the home).
  - `Branch(id, name, sub, families)`, `Family(name, lesson: str | None, items)`, `Item(id, name, does, ignores: list[Tag], needs: list[Tag], cond, python, r, sources: list[Ref], reviewed: bool)`. `Tag(tag, cond, sources: list[Ref])`. `Ref(key, locator, supports, candidate: bool)`, `supports` in `does | python | r | ignores:<tag> | needs:<tag>`. `Item.id` = slug of the name. `Item.fingerprint` = `fingerprint` of its factual fields (name, does, every tag with cond, cond, python, r, every ref) serialised in that order, one per line.
  - `Sector(id, name, curve: list[float], questions)`, `Question(id, text, starts: list[str], fits)`, `Fit(item, mark, reason, cond, sources: list[Ref], reviewed: bool)`, `Fit.fingerprint` over question id, item, mark, reason, cond, refs. Public question id `<sector>/<question>`.
  - `Atlas.drafts() -> list[str]`: one line per item or fit that is not reviewed, naming it.
  - Vocabularies: `IGNORE_TAGS = ("level", "scale", "shift", "warp", "noise", "length")`, `NEED_TAGS = ("matrix", "similarity", "vectors", "series", "labels")`, `MARKS = ("good", "avoid")`.
  - Build modes: release (default, `--dist` default `dist/`) and preview (`--preview`, `--dist` default `preview/`). `<html data-build="release|preview" data-root="…">` on every page.
  - `_reviews.toml` gains `[[item]] name, fingerprint, by, date` and `[[fit]] question, item, fingerprint, by, date`. `review.py show-map` lists every item and fit with its fingerprint and whether it is reviewed. `review.py record-item --name N --fingerprint F --by B` and `record-fit --question Q --item I --fingerprint F --by B`, refusing a fingerprint that is not current.

Review state is derived (design 5.1, owner 2026-10-29): there is no `status` field. An item or fit is reviewed when a record matches its current fingerprint, else it is draft. Editing a reviewed item makes it draft by itself. A reviewed item also needs, for each factual field, at least one non-candidate ref with that `supports` value and a non-empty locator. A draft may have `candidate = true` refs, shown as "candidate source, not yet confirmed", or none, shown as "source pending". No item gets its branch's reference work by default (design 8).

- [ ] **Step 1: Write the smoke data and the failing tests**

Smoke `_map.toml`: two branches (compare, group), three families, five items, one with `cond`, one with `needs = [{tag = "matrix", cond = "single, complete, average linkage"}]`. Smoke `_sectors.toml`: energy and finance, one question each, one `good` and one `avoid` fit. Every item and fit has refs to `sakoe78` with locators and a review record.

```python
def test_release_refuses_an_unreviewed_item(content):
    remove_item_record(content, "Euclidean")
    out = build(content).stdout; assert "Euclidean" in out and "draft" in out

def test_editing_a_reviewed_item_makes_it_draft(content):  # Review Focus 2
    edit_item(content, "Euclidean", does="Compares the same time steps, now edited.")
    assert "Euclidean" in build(content).stdout and build(content, preview=True).returncode == 0

def test_release_refuses_an_unreviewed_fit(content):
    remove_fit_record(content, "finance/same-dates")
    assert "finance/same-dates" in build(content).stdout

def test_preview_allows_drafts_and_marks_them(content):
    remove_item_record(content, "Euclidean")
    assert build(content, preview=True).returncode == 0
    home = (content.parent / "preview" / "index.html").read_text()
    assert 'class="draft-banner"' in home and 'data-build="preview"' in home
    assert not (content.parent / "dist").exists()

def test_preview_never_writes_into_the_release_tree(content):  # Review Focus 2
    for target in (ROOT / "dist", ROOT / "dist" / "preview"):
        assert "a preview never writes into dist/" in build(content, preview=True, dist=target).stdout

def test_duplicate_item_name_fails(content):  # Review Focus 2
    duplicate_item(content, "Euclidean")
    assert "item 'Euclidean' appears twice" in build(content, preview=True).stdout

def test_fit_on_unknown_item_fails(content):  # Review Focus 2
    edit_fit(content, "finance/same-dates", item="Nonexistent")
    assert "unknown item 'Nonexistent'" in build(content, preview=True).stdout

def test_reviewed_item_needs_located_support_for_each_field(content):
    edit_ref(content, "Euclidean", supports="python", locator="")
    rerecord_item(content, "Euclidean")
    assert "Euclidean" in build(content).stdout and "python" in build(content).stdout

def test_tag_vocabulary(content):
    edit_item(content, "Euclidean", ignores=[{"tag": "amplitude", "cond": ""}])
    assert "unknown tag 'amplitude'" in build(content, preview=True).stdout

def test_semicolon_in_map_text_fails(content):
    edit_item(content, "Euclidean", does="One; two")
    assert "semicolon" in build(content, preview=True).stdout
```

`build(content, preview=False, dist=None)` gains the two options. Before writing the edit helpers, check that `sakoe78` exists in the smoke registry (from Task 2).

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_build.py -q -k "item or fit or preview or tag or map"`
Expected: FAIL.

- [ ] **Step 3: Implement `atlas.py`, the modes and the minimal draft rendering**

Both modes: schema and vocabularies, unique item names, `Family.lesson` listed in `_course.md`, fits and `starts` naming existing items, ref keys in the registry, `ignores` only in the compare branch and `needs` only in group and validate, prose rules on every text field. Release mode: one error per `Atlas.drafts()` line. Preview: after resolving paths, a `--dist` equal to or inside `ROOT / "dist"` is "a preview never writes into dist/", checked before anything is written. The home in preview carries a minimal `div.draft-banner` (Task 6 styles it). `pages.yml`: add a comment that it runs the release build, uploads `dist` only when that step succeeds, and fails until the map is reviewed (design step 2) by design.

- [ ] **Step 4: Import the draft map and sectors from the mockup**

One-off scratch script, not committed: read the `MAP` and `FIT` arrays of `.mockups/course/index.html`, write `content/_map.toml` and `content/_sectors.toml` with no refs and no records (everything draft). Then apply by hand the known corrections (design 5, HANDOFF item 2):
- Affinity propagation: `needs = [{tag = "similarity", cond = "precomputed similarities, not distances"}]`, `cond = "similarities"`.
- Agglomerative: `needs = [{tag = "matrix", cond = "single, complete, average linkage"}, {tag = "vectors", cond = "Ward: Euclidean geometry"}]`, `cond = "Ward: Euclidean"`.
- Calinski-Harabasz and Davies-Bouldin: `needs = [{tag = "vectors", cond = "Euclidean centroids"}]`, `cond = "Euclidean"`.
- Silhouette: `needs = [{tag = "matrix", cond = "dissimilarities"}]`.
- DTW: `ignores = [{tag = "warp", cond = "alignment within w permitted, not a guarantee of small cost"}]`, `cond = "within w"`.
- Finance: questions `same-dates` ("Which assets move together on the same dates?") and `dynamics` ("Which assets have similar dynamics?"), the mockup's fits split between them.
- Fields marked "to check" in the mockup become empty strings.
No claim is added that is not in the mockup: reviewing them is design step 2.

- [ ] **Step 5: e2e on the preview, `AGENTS.md`, run, commit**

`tests/e2e.mjs` builds the real content with `--preview` into `tests/output/content-preview/`. `AGENTS.md` Rules: the draft map exception in one paragraph (design 5.1, owner 2026-10-29). Commands: `npm run build` is the release build and fails on draft map content, `npm run preview`.

Run: `uv run pytest -q && npm test && npm run build; echo "release exit $?"`
Expected: tests pass. The release build exits 1, every error line names a draft item or fit.

```bash
git add scripts content tests package.json .gitignore .github AGENTS.md
git commit -m "Map and sector data with derived review state, release and preview builds"
```

---

### Task 5: Shell and lesson page

**Files:**
- Create: `scripts/buildlib/pages.py` (page assembly moves here from `build.py`)
- Modify: `site/page.html`, `site/theme.css`, `site/favicon.svg`, `scripts/build.py`
- Test: `tests/e2e.mjs`

**Interfaces:**
- Consumes: `Lesson.blocks`, `Lesson.code`, `Lesson.citations`, `Source` (Tasks 1 to 3).
- Produces (DOM contract for Tasks 6 to 9):
  - `<html data-build data-root>`: `data-root` is `""` on the home, `"../"` on lessons and the sources page.
  - Top bar `header.top`: `a.logo` ("TS" mark, links `<root>index.html`), course name, `form.search` with `input#q` (type `search`, `aria-label="Search the course"`), `div.progress > i` on lesson pages, `button.theme`, `a.gh` (`REPO_URL`, `aria-label="GitHub repository"`), `button.menu` (`aria-controls="contents"`, `aria-expanded="false"`).
  - `nav#contents`: links `<root>index.html`, `<root>index.html#map`, `<root>index.html#sectors`, `<root>sources/index.html`, then per module an `ol` of lessons: published as links, planned as `li.coming` with an id `<root>index.html#lesson-<id>` target on the home, `span.fin` "Finance" where the lesson has `## In finance`. Under the current lesson, `ol.toc` with one `a[href="#<block id>"]` per content section and per fixed block present.
  - `main#main` of a lesson: `.hero` (module, `h1`, `.lede`), `.trade` (two boxes "It ignores", "It keeps", from front matter), `nav.jump`, `.oneline`, `section.content#<id>` per content section, `section.finance#in-finance`, `section.measure#measure-card`, `section.code#code` with `div[role=tablist]` holding one `button[role=tab][data-lang]` per language present (none when only one), one `pre[data-lang]` per language, all present in the HTML, `button.copy`, `p.libs` ("Related library functions: …" from front matter `python` and `r`), `.mistake`, `section.lsrc`, `nav.pager`.
- Finance block styles: `--fin-bg` (light: the light `--ink` value, dark: `--fig-bg`, with a `--rule` border) set independently, then local `--fin-text`, `--fin-muted`, `--fin-link`, `--fin-focus` and the figure variables re-pointed inside `.finance`, so the background never follows the re-pointed text colour.

- [ ] **Step 1: Write the failing e2e checks**

In `smokeChecks`: the top bar elements, contents lists the 3 smoke lessons with beta as coming and alpha's blocks under it, contents links to `#map` resolve to the home's map from a lesson page (href ends `index.html#map`), every `nav.jump` and `ol.toc` link resolves to an element id on the page, finance block on alpha and absent on gamma, both code languages in the HTML, `#src-sakoe78` in `section.lsrc`. A second context with `javaScriptEnabled: false`: both `pre` visible, `a.cite` goes to `#src-sakoe78`.

- [ ] **Step 2: Run to see them fail**

Run: `npm test`
Expected: FAIL on the new checks.

- [ ] **Step 3: Implement templates, `pages.py`, CSS**

Layout values from Global Constraints. Logo "TS" in Geist Mono on an `--accent` rounded square, the same mark in `favicon.svg`. Light and dark for every component. The pilot's uppercase tracked labels (`.kicker`, `.lbl`, `.pager span`, `.coming`) become sentence case. The pilot's margin `aside` is removed: everything is in the one column.

- [ ] **Step 4: Run tests, check the blank-page screenshot, look at it**

Run: `uv run pytest -q && npm test`
Expected: PASS. Then the screenshot check of Global Constraints, then screenshots of lesson 5 at 1440 and 390 px, both themes, compared with `.mockups/course/index.html`. Fix visible breakage only.

- [ ] **Step 5: Commit**

```bash
git add scripts site tests
git commit -m "Course shell and lesson page"
```

---

### Task 6: Home and sources page

**Files:**
- Create: `site/sources.html`
- Modify: `site/home.html`, `site/theme.css`, `scripts/buildlib/pages.py`, `scripts/build.py`
- Test: `tests/e2e.mjs`

**Interfaces:**
- Consumes: `Atlas` (Task 4), `Source` and `cited_sources` (Task 2), the shell (Task 5).
- Produces (DOM and data contract for Tasks 7 and 8):
  - Home `main`: `.hero` with "Start with lesson 1" (link to the first published lesson), `section#map`, `section#sectors`, `section#lessons` (module index, `li#lesson-<id>` for every lesson, status and finance tags).
  - Map: `div.draft-banner` (preview only, text: "Draft map. Local preview only. What each item ignores or needs, its functions and its sector fits are not yet checked against sources. A release build refuses this map until every item is checked."). Filter controls: `div#f-ignore` with one `button[data-tag][aria-pressed]` per `IGNORE_TAGS` (labels: level, scale, a global shift, local timing, noise, different lengths), `button#f-matrix[aria-pressed]` ("I only have a distance matrix"), `div#f-question` with one `button[data-question="<sector>/<question>"][aria-pressed]` per question, grouped under its sector name, `p#f-status` (`aria-live="polite"`). Then `div.branch[data-branch]` > `div.family` > `ul` > `li.item[data-item="<item id>"]` > `details#item-<item id>` with `summary.chip` (name, `span.cond` when `cond`, `span.draft` "draft" when draft) and the card body (does, ignores or needs with conditions, Python, R, lesson link, refs with locator or "candidate source, not yet confirmed" or "source pending").
  - `<script type="application/json" id="atlas-data">` with `{"items": {"<id>": {"name", "branch", "ignores": [{"tag", "cond"}], "needs": [...], "draft": bool}}, "questions": {"<sector>/<question>": {"text", "fits": [{"item": "<id>", "mark", "reason", "cond", "draft"}]}}}`. `map.js` reads only this and the DOM above.
  - Sector cards: `section#sectors` > `div.sector[data-sector]` with an SVG sparkline (`polyline.ln`, `role="img"`, `<title>` "<Sector> example curve", `viewBox` only), the name, and one `a.q[href="#map"][data-question]` per question with the items it starts from. In preview, `span.draft` on cards whose fits are draft.
  - Sources page `sources/index.html`: link policy paragraph (design 8, no promise that links are checked at build time), `div#f-topic` with `button[data-topic]` per topic and "All", one `li#src-<key>[data-topics]` per source with full authors, year, title, venue, links, and "Cited in" lesson links.

- [ ] **Step 1: Write the failing e2e checks**

Smoke home: 5 `li.item`, each `details` opens on click of its `summary` (native, so it also works with JavaScript off), the matrix item's card shows "single, complete, average linkage", 2 sector cards with 1 `a.q` each, `#atlas-data` parses as JSON with 5 items, `li#lesson-beta` present. Smoke release pages have no `.draft-banner`, no `span.draft`. Sources page lists `sakoe78` with "Cited in" alpha and the full author names.

- [ ] **Step 2: Run to see them fail**

Run: `npm test`
Expected: FAIL.

- [ ] **Step 3: Implement**

The map and sector text appear exactly as in the data files. Draft styling: dashed outline and a "draft" label, readable in both themes.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest -q && npm test`
Expected: PASS.

```bash
git add scripts site tests
git commit -m "Home with map and sector cards, sources page"
```

---

### Task 7: Behaviour

**Files:**
- Create: `site/course.js`, `site/map.js`
- Modify: `scripts/build.py` (copy both into `assets/`), templates (`<script defer>`, order: `search-index.js` from Task 8 first, then `course.js`, then `map.js` on the home)
- Test: `tests/e2e.mjs`

**Interfaces:**
- Consumes: the DOM and data contracts of Tasks 5 and 6.
- Produces: `window.TSC.layers` in `course.js`, a stack with `open(name, element, opener, {trap: bool})` and `close(name)`. Escape closes only the top layer and returns focus to its opener. Opening a layer above a trapping one suspends that trap. Closing restores it. Task 8 uses it for the search results.

- [ ] **Step 1: Write the failing e2e checks**

From design 4.1 and 5:
- At 820 and 375 px, `button.menu` opens `#contents` (`aria-expanded="true"`). Tab stays inside it. Escape closes it and focus returns to `button.menu`. At 1440 px the contents is visible without the button.
- Scroll-spy: scrolling lesson 5 to `#measure-card` sets `aria-current="true"` on its `ol.toc` link.
- Reading progress: at the top of a lesson `div.progress > i` has width 0%, at the bottom 100% (scroll fraction of `main`).
- Code: clicking the R tab shows only the R `pre`, `aria-selected` follows. `button.copy` copies the visible language's exact text (read back with the clipboard permission granted in the test context).
- Citation: clicking `a.cite` opens a `role="dialog"` popover labelled by the source label, with full authors, year, title, venue and links. Escape closes it and focus returns to the link.
- Map: one ignore tag highlights the items with that tag and shows the tag's condition next to each chip. Two tags highlight only items having both (AND). The matrix button highlights items with `needs` matrix and shows the condition. A question button shows its text, marks `good` and `avoid` fits with their reason, dims the rest, and resets the ignore and matrix buttons (they exclude each other). `p#f-status` states what is shown.
- Sector card: clicking a question link scrolls to `#map` with that question pressed.
- Sources page: a topic button shows only sources with that topic, "All" shows every source.

- [ ] **Step 2: Run to see them fail**

Run: `npm test`
Expected: FAIL.

- [ ] **Step 3: Implement**

`prefers-reduced-motion` disables smooth scrolling and transitions. Map connector lines are decoration (`aria-hidden`), drawn only where they do not cross a box, none when the branches stack. Clipboard: `navigator.clipboard.writeText`, with a select-and-`execCommand` fallback where it is unavailable on `file://`.

- [ ] **Step 4: Run tests and commit**

Run: `npm test`
Expected: PASS.

```bash
git add site scripts tests
git commit -m "Shell, code, citation and map behaviour"
```

---

### Task 8: Search

**Files:**
- Create: `scripts/buildlib/search.py`
- Modify: `site/course.js`, `scripts/build.py`, templates
- Test: `tests/test_build.py`, `tests/e2e.mjs`

**Interfaces:**
- Consumes: `Lesson.blocks`, `Course.entries`, `Atlas`, `TSC.layers` (Task 7).
- Produces: `assets/search-index.js` setting `window.TSC_SEARCH = [{kind, title, section, href, text, draft}]`, `kind` in `lesson | map | planned`, `href` relative to the site root: lesson section `"<id>/index.html#<block id>"`, map item `"index.html#item-<item id>"`, planned lesson `"index.html#lesson-<id>"`. Loaded with a plain `<script defer>` before `course.js`.

- [ ] **Step 1: Write the failing tests**

- `test_build.py`: the smoke `search-index.js`, parsed after stripping the assignment, contains alpha's "A second section", beta as `planned`, every smoke item as `map`, and no text from inside `pre` code blocks (the fence line `x = 1; y = 2` of alpha is absent).
- e2e, in the `file://` and the http run (Review Focus 3): `/` focuses `#q`, `/` typed inside `#q` stays as text. Typing "second" lists alpha's "A second section" with `mark`. Enter on the first result goes to `alpha/index.html#a-second-section`. A map result opens `details#item-<id>`. Escape clears the results, shows the page at the previous scroll position, focus on `#q`. With the drawer open at 375 px, focus moves to `#q`, results open, Escape closes the results only, a second Escape closes the drawer, focus returns to `button.menu`. In the real preview, a map result carries a "draft" label.

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q -k search && npm test`
Expected: FAIL.

- [ ] **Step 3: Implement**

Indexed text: rendered text of each block without code, math source or figure markup. Case-insensitive substring match on title, section and text. Ranking: title, then section, then text, then course order. Results replace the page (`main` hidden, a results region shown with an `aria-live="polite"` count), opened as a `TSC.layers` layer. A map result navigates to the home and opens its `details`.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest -q && npm test`
Expected: PASS.

```bash
git add scripts site tests
git commit -m "Search over lessons, map items and planned lessons"
```

---

### Task 9: Contrast, widths, screenshots, owner review packet

**Files:**
- Modify: `tests/e2e.mjs`, `tests/shots.mjs`, `AGENTS.md` (Layout, final check), any CSS or JS file a failing check points to
- Test: `tests/e2e.mjs`

- [ ] **Step 1: Write the contrast check**

- A luminance and ratio helper, checked first against published values: black on white 21:1, `#767676` on white 4.54:1, `#777777` on white 4.48:1 (WCAG 2.2 Understanding 1.4.3 and its common worked examples).
- A role and state matrix, both themes, on the real preview: body paragraphs and list items of `main` (their own colour, not links) at 10:1, every other text at 4.5:1. States opened explicitly before measuring: a map card, the citation popover, the search results, the drawer, the R tab, a question filter. Backgrounds: compose the element's ancestors' backgrounds with their alpha down to an opaque colour. Figure text: each `text` element's computed `fill` against the fill of the figure box under it (`.box`, `.box-accent`) or the figure panel. Include the finance block (body text, links, math, focus ring, figure labels), the condition labels, the draft banner and draft labels.
- The failure line names the page, theme, selector, the two colours and the ratio.

- [ ] **Step 2: Widths (Review Focus 4)**

Widths 1440, 1280, 820 and 375 px, both themes, every page of both builds: `documentElement.scrollWidth <= viewport width`, and on every `summary.chip`, `.sector` card and `a.q`: `scrollWidth <= clientWidth`.

- [ ] **Step 3: Run, fix, run again**

Run: `npm test`
Expected: PASS after fixes. Contrast fixes use the existing tokens, a local variable only where no token passes (as in the finance block).

- [ ] **Step 4: Screenshots**

Blank-page screenshot check first (Global Constraints). `tests/shots.mjs`: build the preview, then home, lesson 1, lesson 5 and the sources page, light and dark, 1440 and 390 px, into `tests/output/shots/` with `manifest.json` (commit, build mode).
Run: `npm run shots`
Expected: 16 PNG files and the manifest.

- [ ] **Step 5: `AGENTS.md` final pass**

Layout section: new `buildlib` modules, `course.js`, `map.js`, `review.py`, `check_sources.py`, `preview/`, the data files. Check that the content format, rules and commands written in Tasks 1 to 4 match the final code. Same prose style as the file.

- [ ] **Step 6: Full verification and commit**

Run: `uv run pytest -q && npm test && npm run shots && uv run python scripts/check_sources.py && npm run build; echo "release exit $?"`
Expected: tests pass, 16 screenshots, every identifier `matched`, release exits 1 with "draft" lines only.

```bash
git add -A tests site scripts AGENTS.md
git commit -m "Contrast and width checks, screenshots, AGENTS.md for the redesign"
```

- [ ] **Step 7: Owner review packet (controller)**

Report to the owner: what checkpoint 1 contains and what it does not (lesson prose is the pilot baseline, map content is a draft, live figures come in checkpoint 2), the screenshots, how to open the preview (serve `preview/` locally: ask which port, since 60610 serves `.mockups/`), any edge case seen and not covered, to propose for selection, and the source check results with anything still `manual-needed`.
