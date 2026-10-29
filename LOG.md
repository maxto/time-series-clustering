# LOG — time-series-clustering

## 2026-10-29 · Smaller type, reading measure, frontend-design skill

Owner, after the figure fix: text and titles still looked too large "from
the title on". Decision (approved by the owner, done): body text 17 px
instead of 18 (as the pilot and ai-one-token-at-a-time), lesson title 44 px
instead of 56, home title 50 instead of 64, lede 19.5 instead of 22,
section titles 25 instead of 30, the one line 19 instead of 21, the common
mistake 17.5 instead of 19, finance and measure text one step smaller,
phones 16 px text. Column 720 px without the contents and 680 px next to
it, instead of 800 and 760. Replaces the "800 px with 18 px text, 760 px
next to it" rule of design 4.1 (amended there).

Owner's go-ahead to install a UI/UX skill ("installa la skill, vedi te"):
Anthropic's `frontend-design` (Apache-2.0) copied from
`~/resources/anthropic-skills/skills/frontend-design/` into
`.claude/skills/frontend-design/`, and the project recorded in the
catalog's "Used by" column (`~/resources/README.md`, left uncommitted in
that repo, which another session also has open). `ui-ux-pro-max` was not
installed: the catalog verdict is reference only and its palettes would
fight the approved tokens. Colours stay as chosen (owner: "per i colori va
bene questo, come l'altro corso").

Applying the skill's line-length rule (both skills say under 80, 65 to 75
ideal): measured 87 to 89 characters per line at 680 px, because Geist is
narrow. Decision (done, under the owner's "vedi te"): running text
(paragraphs, lists, the one line, the common mistake, the lede) stops at
34em, 578 px, measured 73 to 78 characters, while figures, finance,
measure and code keep the full column. This is the first of the three
"not a brick" levers. The other two (collapsible deep-dive sections, a
summary line per section) are proposed, not decided, and go to the
checkpoint 2 planning together with the live figures.

Verified: `npm test` e2e ok (assertions updated to 17 px, 680 and 720 px,
new check: reading measure 578 px at 1280), `npm run preview` ok,
screenshots of lesson 5 at 1440 and 375 px and of the home map looked at.

## 2026-10-29 · Static figures no longer enlarged

Owner report: figures and the home image looked giant and zoomed. Root
cause (measured at 1440 px): the static SVGs are drawn 360 units wide with
14-unit labels, and checkpoint 1 stretched them to the full 760 px column
(Task 5 ruling "figures full column, as the design asks"), so everything
was drawn at 2.01x: labels about 28 px, the home overview 722 by 947 px.
The mockup drew its figures in JavaScript at the real width, with 12.5 to
13 px labels, which is what design 6 means for live figures. Fix (done):
`figure svg` gets `max-width: 360px` and is centred on the full-width panel,
so a static figure is shown at most at its drawn size and never enlarged.
The Task 5 ruling is replaced by this one for static figures. Regression
test in the e2e width checks: no figure label renders above 16 px at 1440,
1280, 820 or 375 px (failed before the fix with 28.1 px, passes after).
Text sizes (18 px body, 56 px title, 800/760 px column) match the approved
mockup and were left unchanged. Verified: `npm test` e2e ok, pytest 113
passed, `npm run preview` ok, figures measured at 360 px wide, scale 1.00.

## 2026-10-29 · SDD workspaces deleted, ledgers kept in docs/research

Owner's go-ahead ("ok", 2026-10-29) to delete the two git-ignored SDD
workspaces. Done: both ledgers copied first, byte-identical (`cmp`), to
`docs/research/2026-10-28-sdd-pilot-ledger.md` and
`docs/research/2026-10-29-sdd-cp1-ledger.md`, then
`.superpowers/sdd/2026-10-28-pilot/` and
`.superpowers/sdd/2026-10-29-redesign-checkpoint-1/` deleted (briefs,
reports, review diffs, pilot task-level Codex reviews). The ledger paths
named in the entries below and in
`docs/research/2026-10-29-codex-cp1-branch-review-request.md` now live at
these two files. Decision (done): keep the ledgers tracked because they hold
every ruling and the deferred minor findings that HANDOFF item 5 still
needs. The diffs are reproducible from git and were not kept.

## 2026-10-29 · Checkpoint 1 built (shell, format, draft map)

Plan `docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md` (9 tasks)
written with the writing-plans skill, reviewed by Codex
(`docs/research/2026-10-29-codex-plan-cp1-review.md`, all findings adopted),
then executed subagent-driven on the new local branch `redesign` (from
`pilot`): Sonnet implementers and task reviewers, Codex for the citation
review and the whole-branch review
(`docs/research/2026-10-29-codex-cp1-branch-review.md`), one fix wave.
Commits `9fd7cdf..7f28d4f` (21 commits). Ledger with every ruling and
deferred minor: `.superpowers/sdd/2026-10-29-redesign-checkpoint-1/progress.md`
(git-ignored).

Built: lesson schema v2 (content sections, sector, code tabs, Check dropped
for the first phase), citations `[@key, locator]` with a source registry and
review records bound to versioned fingerprints (an edit reopens the review),
`scripts/review.py`, `scripts/check_sources.py`, map and sector data imported
from the mockup as draft with derived review state, release build refusing
any unreviewed map item, fit, question, sector or branch, `--preview` into
`preview/`, the course shell (top bar, contents, search), home with map,
filters and sector cards, sources page, behaviour scripts, search index that
works from `file://`, contrast and width checks.

First verified citation: Sakoe and Chiba (1978), adjustment window condition,
Sec. II-B condition 4 (Eq. 8), p. 44, in lesson 5. Passage read on a scan
hosted on a University of Illinois course page, metadata matched on Crossref,
sentence approved by Codex as is
(`docs/research/2026-10-29-codex-sakoe-citation-review.md`). The site links
only the DOI.

**Verified (Claude, 11:06 CET on `7f28d4f`):** `uv run pytest -q` 113 passed.
`npm test` e2e ok (smoke release and content preview, `file://` and HTTP,
no-JS context, contrast matrix with body rows at 10:1 in content, one line,
mistake, finance and measure areas). `npm run preview` ok. `npm run build`
exits 1 with 110 lines, all "draft" (the gate working, map content is design
step 2). Earlier, per task: 16 screenshots in `tests/output/shots/`, the four
source identifiers `matched` by `check_sources.py`. Demo served at
`http://127.0.0.1:60610/preview/` through a symlink `.mockups/preview ->
../preview` (git-ignored) on the existing server.

**Decisions**

- Approved (owner): execution subagent-driven with a review per task.
- Approved (owner, delegated): the four groups of edge-case tests in the
  plan's Review Focus (citations and reviews, map, navigation and search,
  schema and layout), on Claude's recommendation.
- Approved (owner): Codex's plan findings, with Claude's simplification:
  review state is derived from records matching the current fingerprint,
  never a hand-typed status (replaces the design's `status` field in
  practice: an edited item turns draft by itself).
- Done (Claude rulings, full list in the ledger): question text, starts,
  sector about and curve, and branch labels are gated like items (they are
  recommendations shown on the home). Planned lessons are not linked from
  the contents. Figures take the column width (design 4.1). Connector lines
  with a root box (owner-approved mockup). Need-tag labels are UI vocabulary.
  "None of the listed properties" dropped as an unsupported claim. Dimmed
  chips keep 4.5:1 text. Contrast rule made concrete: body prose 10:1 by
  colour, every other text 4.5:1. Fingerprint v2 (no whitespace collapse,
  canonical JSON for map data, source identity with authors and venue)
  after Codex's final review, with the two lesson records and the citation
  record re-recorded on unchanged text.
- Proposed, for the owner's checkpoint 1 review: static figures now scale to
  the 760 px column, so their labels grow on desktop. Only one connector
  line (root to Compare) in the 760 px column. Need-tag label wording.

**HANDOFF reconciliation:** item 1 (plan, then step 1) moved on: checkpoint 1
built, owner review pending. Added: delete the SDD workspace of this plan
(owner go-ahead), the `.mockups/preview` symlink, edge cases deferred in the
ledger. Other items unchanged.

## 2026-10-29 · Redesign design amended, re-checked and approved

Continues HANDOFF item 1. Asked the owner the two open questions, amended
`docs/superpowers/specs/2026-10-28-redesign-design.md` with every finding
of the Codex review, ran a focused Codex re-check (request
`docs/research/2026-10-29-codex-redesign-recheck-request.md`, answer
`docs/research/2026-10-29-codex-redesign-recheck.md`), fixed its three
new points, then applied the owner's content direction. Owner approved
the design ("Ok, procedi"). Throwaway demo in `.mockups/course/` (lesson 5
measure card, state line with reset, map draft banner and condition
labels). No code changed.

**Verified:** Codex re-check read in full. Its N1 counterexample checked
by hand (x = (0, 0), y = (0, 1), w = 1 gives DTW 1, equal to Euclidean).
Demo numbers from the reference code on the fixture: mon and wed, DTW
3.51 at w = 4, 0.26 at w = 10, Euclidean 4.15. Demo checked in headless
Chrome (slider, state line, reset, no page errors) and by screenshot at
1280 and 390 px before the last small edits. After that, headless Chrome
screenshots timed out even on a blank page (environment issue, not
investigated), so the last demo version was not screenshotted.

**Decisions**

- Approved (owner): narrow exception to the AGENTS.md rule that an
  unconfirmed claim stays out. The full draft map may appear in local
  preview builds only, visibly marked as draft (banner, chips, fit marks,
  sector cards, search). The default build is the release build and fails
  on draft, missing or unknown status. Preview writes to a separate
  directory, never `dist/`. Lessons are not covered. To be recorded in
  AGENTS.md Rules by the implementation (design section 5.1).
- Approved (owner): owner reviews after checkpoint 1 (look) and after
  checkpoint 3 (all of step 1). A short owner ok on the finance and
  weather fixtures before they are frozen, now in step 4. Rejects a full
  review at every checkpoint and a single review at the end.
- Approved (owner, content direction for the first phase = steps 1 to 3):
  no exercises, transfer tasks or predict-then-reveal questions. Text,
  static and live figures, and one or two correct references per topic
  (each measure, method or index: the reference that defines it in its
  standard form, plus a survey where useful). General topics in their
  usual, historical form: niche published variants stay out. A claim gets
  in by: written from Claude's knowledge, reference found, read at the
  supporting point, confirmed by web search, then reviewed by another
  model. Each lesson has one sector worked example in its text (energy on
  the existing fixture unless the topic needs another) and the finance
  block where relevant. Replaces, for the first phase, "three main
  sectors in every lesson" (2026-10-28), which returns with the exercises
  in step 4, together with the finance and weather fixtures. "First
  phase = steps 1 to 3" is Claude's reading, stated to the owner, not
  objected to.
- Done: Codex findings resolved in the design. Sector coverage, map
  claims with conditions (exact invariance versus conditional permission,
  distance versus similarity input, linkage-dependent compatibility),
  bibliographic check kept apart from editorial verification with a
  support location, live-figure input contract and parity on
  control-generated inputs, state contract with reset, lesson contract
  replacing the AGENTS schema (Check becomes exercises, Measure card
  kept), interaction behaviour. Re-check new points fixed: N1 (DTW window
  is a path constraint, not a guarantee of small cost or noise
  reduction), N2 (preview may hold pending review records for draft map
  claims only), N3 (edge cases are candidates for the owner, not
  mandatory tests).
- Done: Claude's-call count corrected to four marked calls. The builder
  check's seven questions cannot be mapped to the text, none invented.
- Delivery order now: 1 shell and format on lessons 1 and 5 (three
  checkpoints), 2 map content verified, 3 remaining lessons, 4 exercises,
  5 code labs and real-data scripts, 6 README, licence, remote steps.

**HANDOFF reconciliation:** item 1 (redesign design) done, design
approved. New item 1: implementation plan (writing-plans), then step 1.
Other items unchanged.

## 2026-10-29 · Redesign design written and reviewed by Codex

Continues the redesign brainstorm (HANDOFF item 1). Wrote
`docs/superpowers/specs/2026-10-28-redesign-design.md` (amends
`2026-10-28-course-design.md`), ran a builder check (Sonnet subagent),
then a Codex adversarial review: request
`docs/research/2026-10-28-codex-redesign-request.md`, answer
`docs/research/2026-10-28-codex-redesign-review.md`. Committed with the
pilot closure notes and the two pilot final reviews (HANDOFF item 4,
done). No code changed.

**Verified:** the review file exists and was read in full. Nothing else
run in this step.

**Decisions**

- Approved (owner, "strada 1"): extend the pilot engine (Python build,
  plain JS and SVG for live figures). Rejects Observable Framework and
  Quarto (a new toolchain for the same result).
- Approved (owner, "ok"): the builder check's seven questions settled as
  Claude's calls, marked "Claude's call" in the design (six marked in the
  text, Codex counted five call sites: to reconcile when the doc is
  amended).
- Codex verdict: "Ready for the owner after the listed changes", no
  Critical findings. Eight Important findings: sector coverage per lesson
  weakened, map claims need their conditions (affinity propagation takes
  similarities, Ward needs Euclidean geometry, co-movement versus similar
  dynamics in finance), the draft map conflicts with the AGENTS.md rule,
  a DOI check is not a claim check (record a support location), live
  parity must cover every reader-reachable state (constant series, ties),
  a state contract between figures and answers (with reset), the new
  lesson contract must replace the AGENTS schema explicitly, a transfer
  task per lesson. Minor: keyboard and drawer behaviour, the call count,
  the meaning of "frozen". Step 1 split into three checkpoints.
- Proposed (Claude, agreeing with Codex on every finding): per lesson one
  developed sector example plus two short transfer exercises for the
  other main sectors, not an example in every section. Map items carry
  visible conditions. Support location recorded per non-obvious claim.
  Measure card kept as a block, Check becomes an exercise.
- Open (owner): (1) a narrow exception for a visibly labelled draft map
  in the local preview only, with release builds refusing draft items,
  lessons still fully verified. (2) Owner reviews after checkpoint 1
  (look: shell, map, phone, dark theme) and after checkpoint 3 (all).

**HANDOFF reconciliation:** item 1 now "amend the design doc after the
owner's two answers". Item 4 (commit of the closure notes) done, this
commit. Other items unchanged.

## 2026-10-28 · Pilot review: redesign direction

Owner reviewed the pilot (item 1 of the previous HANDOFF, done): the look
is too thin and too close to ai-one-token-at-a-time. This course is a
learning course, the other one a short read. Brainstorm with clickable
mockups (companion screens in `.superpowers/brainstorm/`, then
`.mockups/course/`). No code or content changed, no commits.

**Verified:** each mockup screen in headless Chrome at 1440, 1280, 820
and 390 px with no page errors. In-browser DTW gives the course numbers
(Euclidean 3.71, DTW w=4 0.22 on mon and sat) under the course convention.
Search, map filters, sector filter, popover cards and contents drawer
clicked through.

**Decisions**

- Approved (owner): explorable-essay format ("A"). Rejects scrollytelling
  ("B": weak on phones, a story rather than a lesson to revisit) and an
  app-like course shell ("C").
- Approved (owner): one reading column, every block (text, figures,
  finance, code) the same width, on desktop, tablet and phone. Rejects
  full-width bands. Width proposed by Claude and accepted: 800 px with
  18 px text, 760 px next to the contents.
- Approved (owner): navigation as in ai-one-token-at-a-time: contents fixed
  on the left from 1180 px, behind a menu button below that, with the open
  lesson's sections listed under it. Search box in the top bar ("metti
  anche la ricerca"). Replaces the pilot's single top bar.
- Approved (owner): code is read and copied only (Python and R tabs,
  libraries listed under it). Rejects running code in the page (Pyodide,
  webR): weight and reading come first.
- Approved (owner): more operative course: worked examples and exercises
  in every lesson, more figures, longer lessons. Replaces "lean lessons".
- Approved (owner): a map of the field at the start of the course, built
  from the README tables and the course taxonomy (compare, group,
  validate), with item cards and filters (what to ignore, distance matrix
  only, sector). Why: the README catalogue was lost in the pilot. Card
  content is a draft to verify.
- Approved (owner): examples from main sectors (energy, finance, weather,
  retail, industry, health), and suitability depends on the sector: the
  map marks good fits and fits to avoid per sector. Open: how many sectors
  recur as main examples.
- Approved (owner): three main sectors recur in every lesson with worked
  examples and exercises: energy (the existing fixture), finance, weather.
  Retail, industry and health stay in the map's sector filter and appear
  in some exercises. Each main sector gets an authored dataset like the
  energy one, plus, where the licence allows, a script that downloads real
  data for the exercises. Rejects six recurring sectors (six datasets to
  build and check).
- Proposed by Claude, shown in the mockups, not objected to:
  predict-then-reveal questions in lessons, finance block always before
  the code, live figures in JavaScript under the course DTW convention.
- Approved (owner): logo "TS" in a blue square, as "AI" in the other
  course. Rejects TSC, TS with a wave, letterless mark.
- Approved (owner): sources for everything. Every definition (each
  measure, method, validity index) cites its primary source. The owner
  supplied only the README's few references, Claude finds the rest.
  Link policy (owner, refined in conversation): one reference source per
  item, the one that defines it, linked in up to four places (publisher
  via DOI, arXiv, SSRN, authors' page) so the reader picks one. No "free
  to read" label anywhere: access depends on the reader, and a free label
  can be wrong. Rejects Claude's first version with free labels. A Sources
  page, a sources list per lesson, one source in each map card.
  Then narrowed (owner): not hundreds of sources. A couple of reference
  works cover the map (proposed: Paparrizos et al. 2024 for distances,
  Aghabozorgi et al. 2015 for methods, Arbelaitz et al. 2013 for validity
  indices, all checked on Crossref or arXiv), and each lesson cites only
  what its paragraphs use, in the paragraph itself (a click shows the
  source and its links) and in a short list at the end. Rejects an upfront
  search for the original paper of every one of the 100+ items: sources
  are found while each lesson is written. The three reference works were
  approved by the owner. Mockup references
  checked on Crossref (14 DOIs) and the arXiv API (4 ids). The SSRN page
  refuses automated requests (HTTP 403), so SSRN links need a manual check.
- Done (owner request): one plain preview server, port 60610, no key.
  Stopped 60611 and the companion server on 63317.
- Found: R `dist(method = "binary")` is a Jaccard-type distance, not
  Hamming as the README says.

**HANDOFF reconciliation:** "owner review of the pilot" done (this entry).
"Merge pilot" kept, now deferred until the redesign plan. "Preview server
60610" kept as the one server. Added: redesign brainstorm, map content to
verify, commit of the closure notes still waiting.

## 2026-10-28 · Pilot built and reviewed (branch `pilot`)

Subagent-driven execution of `docs/superpowers/plans/2026-10-28-pilot.md`.
Claude as PM, implementers on Sonnet (Tasks 1 to 4) and Opus (Tasks 5 to 9),
reviewers: Sonnet for Tasks 1 to 4, Codex (GPT-6 Astra) from Task 5 on and
for the whole branch. Run ledger: `.superpowers/sdd/2026-10-28-pilot/progress.md`
(git-ignored, to be deleted after the owner's ok).

**Commits on `pilot`** (from master `196e416`): `6a8bc72` setup and fixture,
`5b0dea3` Python distances, `816e04e` dark theme rules, `3197dda` grouping
and validity, `a99b2bc` R DTW and parity, `df22549` + `e5c6986` engine,
`f147268` + `ef3e721` figures, `5295eff` group-colour rule, `d5c44b6` +
`4665ec4` overview and lesson 1, `364d5e1` + `ef52f00` lesson 5,
`e828b35` `59434d0` `1d5f42d` `6925633` `0575db2` final fix wave.

**Verified** (on `0575db2`): 38 pytest (30 reference tests with expected
values from hand computation, dtw-python, aeon, scikit-learn and the
fixture's declared groups), R vs Python and R vs R `dtw` worst difference
0, figures and numbers regenerate byte-identical, `npm test` (e2e on
file:// and under `/time-series-clustering/`: no external request, no
failed asset, exact prev/next for every lesson, theme persistence, system
dark fallback, 375 px), contrast table in both themes, keyboard focus, 12
full-page screenshots. Codex independently re-checked the numbers, the R
parity, the regeneration and the page links (`docs/research/2026-10-28-codex-pilot-final-review.md`,
`...-final-rereview.md`).

**Bugs caught by review and fixed:** small-text contrast under 4.5:1 in
light; fragment links with no heading ids; e2e navigation assertions that
could pass with missing pager links; figure shading descriptions false in
dark; lesson 1 implying Euclidean ignores shape; a finance note claiming
more than its source; lesson 5 stating the soft-DTW divergence guarantee
without the source's conditions; stale screenshots.

**Decisions**

- Done (owner, mid-run): dark theme = the palette and rules approved for
  ai-one-token-at-a-time (`docs/design/dark-theme.md`). Replaces the
  provisional dark tokens. Closes the HANDOFF item "dark palette".
- Approved (owner): "content first, code later, starting from existing
  libraries". The owner meant this for the course order. The pilot already
  had its code and was finished as planned. Applies from design step 2 on.
- Approved (owner): Codex is the adversarial reviewer, "as usual". Done:
  task reviews from Task 5 on and the whole-branch review by Codex, instead
  of Sonnet reviewers.
- Done (Claude rulings, each in the run ledger with its cost if wrong):
  branch in the same checkout instead of a worktree; smoke content kept as
  a permanent test fixture (`tests/fixtures/smoke/`) instead of deleted;
  build exits 0 with a note when no `content/_course.md`; F-group edge
  checks automated; contrast fixed by switching small text to `--ink-2`
  without changing brand tokens; grouping figures colour by group while
  two-series figures keep A ink / B accent (plan amended, `5295eff`);
  lesson 5 stays `planned` until written; a verbatim one-line fix accepted
  without a separate re-review; Codex's LEAVE items parked.
- Proposed, owner to judge in review: light cards and pager on white,
  more prominent dark alignment links.

**HANDOFF reconciliation:** "Pilot execution" done (this entry). "Dark
palette" done (dark-theme rules adopted). Added: owner review, merge and
workspace deletion, parked items (moved to the copied Codex final review),
next-phase direction.

## 2026-10-28 · Pilot plan reviewed and approved, Codex hooks fixed

**Done**

- Codex adversarial review of the pilot plan:
  `docs/research/2026-10-28-codex-pilot-plan-review.md` (12 points,
  verdict "keep the approach, correct the contracts"). All 12 folded into
  `docs/superpowers/plans/2026-10-28-pilot.md`, none rejected. Real errors
  it caught: wrong no-window call to the DTW reference packages, an SBD
  delayed-series test that would fail (0.0646 > 0.05), `fcluster`
  `maxclust` giving at most k groups with 1-based labels, bare `python3`
  instead of `uv run`, a Pages workflow that would not install the new
  dependencies.
- Codex hooks failing with exit 127: Codex sessions started before the
  16:49 cleanup of `~/.codex/hooks.json` still held hooks calling
  `/home/maxto/opt/ai-memory-2.6.0/ai-memory`, which was removed. Fix:
  restart. This project's Codex was restarted (`/exit`, `codex`) on the
  owner's ok. The other projects' sessions were reported to the Claude
  session in `~/infra/agents`, which owns the Codex config (message sent
  in its pane, received).

**Verified**

- Codex silhouette hand case recomputed by hand: point scores 1/2, 2/3, 0,
  mean 7/18.
- After the restart a one-word prompt to Codex ran with no hook error.

**Decisions (approved by the owner, 2026-10-28, "procedi con tutto")**

- New libraries: markdown-it-py + mdit-py-plugins, KaTeX, Geist,
  dtw-python and R `dtw` (test references only), scikit-learn, aeon, numpy,
  scipy. None was in the resources catalog except markdown-it-py.
- Quizzes dropped from the pilot (revisit after the owner's review).
  Replaces the old engine's three-question quiz per module.
- One static page per lesson. Replaces the single-page app of the other
  engine. Why: longer lessons, shareable URLs, margin notes.
- All proposed edge-case test groups A to F kept (DTW inputs, DTW path
  structure, SBD zero norm and delayed pulse, silhouette edge matrices,
  too few clusters, build parsing and TeX errors).
- Numbers quoted in lessons are generated (`numbers.json`) and substituted
  by the build. Rejects copying numbers by hand (Codex point 11).
- Execution: subagent-driven (proposed by Claude as PM, per the global
  rule that Claude splits work across subagent workers).

## 2026-10-28 · Look chosen, design approved, pilot plan

Session in this project (Orca tab with Codex and a bash pane). HEAD
`043259a` at start, no new commits yet.

**Done**

- Full Orca setup opened: Codex on the right, bash below it.
- Three colour variants of the Notebook draft, then the chosen one with the
  exact brand tokens, light and dark, theme toggle:
  `.mockups/gen_palettes.py` -> `notebook-a-white-blue.html`,
  `notebook-b-cool-grey.html`, `notebook-c-white-sage.html`,
  `notebook-brand.html`, `palettes.html` (all git-ignored).
- Design section 6 and status updated. Plan written:
  `docs/superpowers/plans/2026-10-28-pilot.md` (9 tasks, pilot only).
- Plan sent to Codex for an adversarial review
  (`docs/research/2026-10-28-codex-pilot-plan-request.md`).

**Verified**

- Original drafts and `.mockups/index.html` unchanged after the new
  generator ran (md5 checksums).
- Headless Chrome screenshots at 1280 px: the three variants, the brand
  page light and dark. A dark-theme bug (legend colours fixed to light)
  was found and fixed, the fix checked in the generated HTML.
- Headless screenshots hang intermittently while Google Fonts load. Not a
  course issue: the plan self-hosts fonts.
- The earlier `LOG` entry says "No commits yet": it was written just before
  commit `043259a`. Harmless, noted here as the correction.

**Decisions**

- Approved (owner): Notebook layout (single reading column, margin notes).
  Rejects Atlas (dark, map-first home, close to maxto.io) and Field guide
  (catalogue of cards). Why: lessons here are longer than in
  ai-one-token-at-a-time, a reading column with margin notes keeps them
  light.
- Approved (owner): white and blue brand palette, the same tokens as
  ai-one-token-at-a-time. Rejects the cool-grey and sage variants. Why:
  the owner's courses share one palette. Replaces "not identical to the
  other course" for colour: layout and type still differ.
- Proposed: Geist + Geist Mono, self-hosted (different type from the other
  course, no runtime CDN).
- Approved (owner): dark tokens are provisional, the owner is reworking the
  brand's dark palette. Swap later in one place.
- Approved (owner): site on GitHub Pages,
  `https://maxto.github.io/time-series-clustering/`, a custom domain may
  come later. The address lives in one constant in the build.
- Approved (owner): design approved with the go-ahead to start production.
- Proposed, waiting on the owner (plan header): new libraries, quizzes
  dropped, one page per lesson instead of a single-page app.

**HANDOFF reconciliation:** "owner picks the look", "owner approves the
design" and "implementation plan" are done (this entry). "Push of the
first commit" is merged into the remote-steps item. "Project rules file"
moved into Task 1 of the pilot plan.

## 2026-10-28 · Project set up, course designed, look drafts

Session run from `~/projects/personal/maxto-brain` (the owner's personal
brain), then moved here. No commits yet. HEAD `be77989`.

**Done**

- Cloned `maxto/Time-Series-Clustering` to
  `~/projects/personal/time-series-clustering/` (branch `master`).
- Codex taxonomy review (copied to
  `docs/research/2026-10-28-codex-taxonomy-review.md`) and Codex design
  review (`docs/research/2026-10-28-codex-design-review.md`).
- Design written: `docs/superpowers/specs/2026-10-28-course-design.md`,
  with the design review folded in.
- Three look drafts in `.mockups/` (git-ignored), generator
  `.mockups/gen.py`, preview server on port 60610.
- `.gitignore` added (`.mockups/`, `.superpowers/`).

**Verified**

- `TSclust` and `TSdist` archived on CRAN 2026-01-16 (CRAN pages).
- GitHub repo names are case-insensitive: lowercase web and raw URLs
  resolve to the repo (curl, `gh api`).
- `gh search prs --owner=@me --state=open`: no open PRs.
- Drafts 1 and 2 rendered correctly in headless Chrome at 1280 px after a
  font-fallback fix. Draft 3 not screenshot-checked (timeout).

**Decisions (all approved by the owner unless marked)**

- Mini-course, English only. Rejects the bilingual schema of
  ai-one-token-at-a-time: readers of this topic read English.
- Concepts first, code second. Core = distance measures and validity
  indices. Algorithms get one shorter lesson on which algorithm fits which
  geometry.
- Validity indices are a full module organised by the geometry they
  assume, not an inventory (rejects Codex's proposal to shrink them to a
  note).
- Build approach A: reuse the ai-one-token-at-a-time engine, adapted.
  Rejected: Quarto (textbook look, theme work), plain Markdown without a
  site (no navigation, weak first impression). Data figures generated from
  the same fixtures as the code, concept figures hand-made SVG.
- Two running examples: synthetic electricity-demand profiles (main),
  finance co-movement via return correlation on a shared window
  (Mantegna, López de Prado), synthetic factor-model fixture plus optional
  real-data download script, limits stated.
- Code scope: seven from-scratch representatives with Python/R parity,
  package examples only where both languages have the method, missing
  counterparts marked as gaps.
- Rename the repo to lowercase `time-series-clustering` before enabling
  Pages (remote action, needs its own go-ahead).
- Visual style: minimal, flat, 2D, low density, not identical to the other
  course. Direction still open (three drafts).
- Proposed, not decided: licence MIT code + CC BY 4.0 content, the pilot
  scope in design section 9.
