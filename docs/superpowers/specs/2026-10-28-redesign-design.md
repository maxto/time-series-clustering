# Time series clustering: redesign after the pilot (design)

Status: approved. Written 2026-10-28, amended 2026-10-29 with every finding of the
Codex review
([2026-10-28-codex-redesign-review.md](../../research/2026-10-28-codex-redesign-review.md))
and the owner's two answers of 2026-10-29 (draft map exception, review
checkpoints), re-checked by Codex
([2026-10-29-codex-redesign-recheck.md](../../research/2026-10-29-codex-redesign-recheck.md),
its three new points fixed), then narrowed by the owner's content
direction of 2026-10-29 (section 1.1). Approved by the owner on
2026-10-29. Amends
[2026-10-28-course-design.md](2026-10-28-course-design.md): where the two
disagree, this document wins. Decisions and their reasons, in the owner's
words where possible: `LOG.md`, entries "Pilot review: redesign direction"
and "Redesign design written and reviewed by Codex". Reference mockup
(git-ignored, throwaway, not code to reuse as is):
`.mockups/course/index.html` and `.mockups/course/logo.html`, served at
`http://127.0.0.1:60610/course/`. Its map and sector content is a draft
and partly wrong (section 5).

Decisions marked "Claude's call" came out of the builder check and were
accepted by the owner as a whole ("ok", 2026-10-28). The first draft
marked five. One of them (the full draft map in step 1) is now an owner
decision (section 5.1), so four remain marked. The builder check asked
seven questions: the record of which ones the two unmarked answers
covered was not kept, so this document does not claim seven marked calls.

## 1. Intent

The pilot (branch `pilot`, lessons 1 and 5, reviewed by Codex, all tests
green) works, but the owner judged it too thin and too close to
ai-one-token-at-a-time. That course is a short read. This one is a
learning course: people should come away able to choose a distance, a
method and a validity index for their own data, and practise doing it.

What the owner asked for, in order of weight:

1. More learning: worked examples and exercises in every lesson, more
   figures, longer lessons to scroll through.
2. The catalogue of the original README (distances, methods, validity
   indices) visible as a whole, at the start, not scattered across
   chapters: a map of the field.
3. Examples from real sectors, and the point that suitability depends on
   the sector: some measures suit finance badly and others well.
4. Sources for what the course says, attached to the paragraph that uses
   them.
5. A more modern, interactive page, without making reading heavier.

### 1.1 Content direction for the first phase (owner, 2026-10-29)

The first phase is steps 1 to 3 of section 10: shell, map and every
lesson. In it:

- **No exercises.** Exercises, transfer tasks and predict-then-reveal
  questions move to a later step (section 10, step 4). Their design
  (section 7) is kept for that step.
- **Text, figures and one or two correct references per topic.** Each
  measure, method or validity index the course treats (in a lesson or a
  map card) cites one or two references: the one that defines it in its
  standard form, and where useful a survey. Static and live figures stay
  as designed.
- **General topics, standard form.** Each measure, method or index is
  described in the form in which it is usually and historically used,
  with the reference of that form. Variants that someone published but
  that are not the common use stay out, even when they exist in the
  literature. The course's own conventions (the DTW convention of
  `AGENTS.md`) are stated as conventions where they differ from a library.
- **How a claim gets in:** written from what Claude knows, then the
  reference is found, read at the point that supports the claim, and
  confirmed by a web search (DOI, arXiv, publisher page). Then the usual
  review by another model (`AGENTS.md`).
- **Sectors in the text:** each lesson carries a worked example from one
  sector in its text (energy, on the existing fixture, unless the topic
  calls for another) and the finance block where the topic has one. This
  replaces, for the first phase, the three sectors in every lesson
  (owner decision of 2026-10-28, which returns with the exercises). The
  finance and weather fixtures move to step 4.

## 2. Goals, non-goals, anti-goals

**Goals**

- Every lesson teaches through worked examples (step by step, with
  figures and numbers the reader can follow). From step 4 it also ends
  with exercises and a **transfer task**: a decision the reader makes on
  a case the lesson did not demonstrate (section 7).
- Live figures the reader manipulates (sliders, toggles), whose numbers
  match the reference code under a stated input contract (section 6).
- A map of the field on the home page, with filters and item cards whose
  claims carry their conditions (section 5).
- From step 4, three main sectors in **every lesson** (owner decision,
  LOG 2026-10-28, deferred by section 1.1): energy, finance, weather. Per lesson, one sector carries
  the developed worked example and the other two appear at least as short
  transfer exercises (Claude's proposal, agreeing with Codex). The lead
  sector rotates where the topic allows. Examples are per lesson, not per
  section: a section without a natural sector case does not get filler.
  Finance coverage counts whether or not the lesson has a finance block.
- Sources cited at the paragraph level, linked to where the paper lives.
- Navigation and search consistent with ai-one-token-at-a-time.

**Non-goals**

- Running Python or R in the page (Pyodide, webR). Code is read and
  copied. Rejected by the owner: weight and reading come first.
- Grading, accounts, progress stored on a server. Exercises reveal their
  answer, nothing is submitted.
- Clustering or validity scores recomputed in the browser.
- A primary source for every one of the 100+ map items (owner: a couple of
  reference works plus per-paragraph sources).
- Six recurring sectors. Retail, industry and health appear in the map and
  in some exercises only.

**Anti-goals (failure even if it works)**

- A page that feels like a slide deck or an app instead of a lesson to
  read and come back to.
- Interactivity that shows numbers, paths or groups different from the
  reference code, or a grouping shown next to data it was not computed on.
- Labelling a source "free": access depends on the reader.
- A sector judgement ("good fit", "avoid") stated without its task,
  its conditions and a reason the reader can check.
- Exercises that can be answered by reading off the figure above them.
- Everything from the first design's anti-goals still holds (no universal
  winner, no trading signal, no archived package as default path).

This reverses one non-goal of the first design: "no in-browser numerical
engine or live interactive widgets" is replaced by live figures with
parity tests (section 6).

## 3. Approaches

**Page format** (owner chose A after three clickable mockups):

- **A. Explorable essay, chosen.** A reading column with live figures,
  predict-then-reveal questions, exercises.
- B. Scrollytelling (text scrolls, a sticky figure changes per step).
  Rejected: weak on phones, suits a story more than a lesson to revisit.
- C. App-like course shell (challenge first, progress ring). Rejected: an
  app more than a course to reread.

**How it is built** (owner chose 1):

- **1. Extend the pilot engine, chosen.** Keep the Python build, Markdown
  lessons, build-time KaTeX, generated SVG, `numbers.json`, the e2e tests
  and the no-CDN rule. Add the course shell, a small library of
  interactive components in plain JavaScript, data files for the map and
  the sources, and exercise blocks. Trade-off: we write the components
  ourselves, and keep full control of the look.
- 2. Observable Framework. Rejected: it would replace most of the tested
  engine, its look must be bent to ours, and it is a new dependency.
- 3. Quarto. Rejected in the first design (textbook look, theme work), and
  awkward for live figures.

## 4. What the reader sees

### 4.1 Shell (every page)

- **Top bar:** logo, course name, search box, reading progress, theme
  button, GitHub link. Logo: "TS" in Geist Mono on a blue rounded square,
  as "AI" in the other course (owner chose option A of four). The same
  mark is the favicon.
- **Contents:** fixed on the left on wide screens (290 px column, the
  mockup switches at 1180 px of width), behind a menu button below that,
  opening as a panel (full width on phones). It lists course home, map,
  examples by sector, sources, then the modules and lessons with status
  (ready, coming) and a finance tag where the lesson has a finance block.
  Under the open lesson it lists that lesson's sections and highlights the
  one being read.
- **Search:** a box in the top bar. Results replace the page while
  typing: lesson, section, a snippet with the match marked, click goes to
  the section. It searches published lessons (titles, sections, text),
  map items and planned lesson titles (shown as coming). Hidden answers
  and transfer-task solutions are not indexed. Draft map items are marked
  as draft in the results. The index is generated by the build, loaded in
  a way that works from `file://`. No external service.
- **Interaction behaviour:**
  - `/` focuses search unless the reader is typing in an input.
  - Escape closes the search results and the contents panel and returns
    focus to the control that opened them. Closing the search results
    restores the reading position.
  - The contents panel on small screens traps focus while open.
  - Map cards, citation disclosures, exercise reveals and code tabs are
    buttons or native disclosure elements with accessible names and
    states (expanded, selected).
- **No JavaScript:** the page still reads. Figures show their static SVG,
  answers and citations are reachable (native disclosure), both code
  languages are visible one after the other.
- **Reading column:** one width for everything (text, figures, finance
  block, code, exercises), on desktop, tablet and phone. 720 px with
  17 px text without the contents column, 680 px next to it. Running
  text (paragraphs, lists, the one line, the common mistake, the lede)
  stops at 34em, about 75 characters, so lines stay readable in the narrow
  Geist face. Figures, the finance and measure blocks and code keep the
  full column. No full-width bands. Phones: everything stacks, padding
  18 px, 16 px text. Amended 2026-10-29 by the owner after the checkpoint
  1 demo (text and titles looked too large): it was 800 and 760 px with
  18 px text, 56 px lesson titles and no reading measure.
- **Themes:** light and dark, the approved tokens and figure variables of
  `AGENTS.md` and `docs/design/dark-theme.md`. Every new component
  (sidebar, search results, map, cards, popovers, exercises, finance
  block, code block) has both. Same contrast rule: small text 4.5:1 on
  every fill it can sit on, body text 10:1.
- **Style:** the first design's rules hold (flat, 2D, few colours with
  constant meaning). From the frontend review in the mockups: no tracked
  all-caps labels, labels in sentence case.

### 4.2 Home

1. Hero: title, one-sentence promise, "Start with lesson 1".
2. **Map of the field** (section 5).
3. **Examples by sector:** six cards (energy, finance, weather, retail,
   industry, health), each with a small illustrative curve, the sector's
   typical questions and the measures each question starts from. A click
   filters the map on that sector and question.
4. The lesson index by module, with status and finance tags.

### 4.3 Lesson page

In this order, all in the one column:

1. Module, title, lede.
2. "It ignores" and "it keeps" (the decision lens).
3. Jump links to the sections, the finance block highlighted among them.
4. One line (the lesson in one sentence).
5. Sections. The lesson's developed **worked example** comes from its
   lead sector, step by step, with its figure and its numbers. Live
   figures sit where they explain a mechanism. From step 4,
   predict-then-reveal questions sit before the figure that answers them.
6. **Finance block**, where the lesson has one (most do, not all: the
   contents and the index tag the lessons that have it). Always in the
   same place (after the main sections, before the code), the width of
   the column, on a dark surface in both themes. Claude's call, from the
   mockup the owner approved: in the light theme it uses `--ink` as
   background, in the dark theme `--fig-bg` with a `--rule` border. It
   defines its own local foreground, link, focus and figure variables
   (the light theme's `--ink` cannot be its text colour), and its text,
   links, math, focus ring and figure labels get their own contrast check.
7. **Measure card** (kept from the pilot as a block): input assumptions,
   conventions, what the result means and what it does not.
8. **Code:** Python and R tabs with the course reference code, a copy
   button, then a line on existing library functions. A library function
   is called equivalent only when the parameters that make it match are
   stated (and, for the lessons' own numbers, checked). Otherwise it is
   listed as related. The reference code stays reproducible: same inputs,
   same numbers as the page. Existing libraries first remains the
   direction for later lessons: the format does not require a new
   implementation of every catalogue item.
9. **Exercises** and the **transfer task** (section 7), from step 4.
10. Common mistake.
11. "Sources cited in this lesson" (section 8).
12. Previous and next.

**This contract replaces the AGENTS lesson schema.** The pilot schema
(`## One line`, `## Lesson`, `## Common mistake`, optional `## In finance`,
`## Measure card`, `## Check`, figures only in `## Lesson`, enforced in
`scripts/buildlib/content.py`) maps as follows: One line and Common
mistake stay. `## Lesson` becomes the lesson's sections, and figures may
sit in any of them and in the finance block. In finance becomes the
finance block. Measure card stays as a block. Check becomes the exercises
(from step 4: in the first phase lessons have no Check block).
Front matter keeps `ignores`, `keeps`, `python`, `r`, and gains the lead
sector. The implementation updates the "Content format" section of
`AGENTS.md`, the parser and the smoke fixture `tests/fixtures/smoke/`
together. The exact Markdown syntax stays with the builder.

### 4.4 Sources page

All sources of the course in one list, filterable by topic (surveys,
compare, group, validate, finance, software), each with where it is cited.
A short paragraph states the link policy (section 8). It does not promise
that links are checked at build time.

## 5. The map of the field

- **Structure:** a root, three branches (compare: distances and
  similarities, group: clustering methods, validate: validity indices),
  families under each branch, items as chips. Families follow the first
  design's taxonomy (section 5.1 there), so items from the README move to
  the families the corrections require (for example cross-correlation and
  SBD to sliding, GAK to kernel).
- **Items:** every item of the README's "General schema", after the first
  design's corrections (KNN removed, binary distance fixed), plus the
  items the course adds (EDR, ERP, MSM, TWE, catch22, stability). Long
  families may show the main items and a "more" control.
- **Item card** (opens on click, next to the chip): what it does in one or
  two sentences, what it ignores (compare branch) or what it needs as
  input (group and validate), Python and R functions, the lesson that
  covers it, its source with a support location, and, with a sector
  question selected, the fit, its conditions and its reason.
- **Claims carry their conditions** (Codex finding 2). Each "ignores",
  "needs" and "fit" claim names the representation or preprocessing and
  the settings it holds under. The data distinguishes:
  - exact invariance (z-normalised Euclidean ignores level and scale)
    from a conditional permission (DTW permits local time alignment along
    admissible paths with `|i - j| <= w` and closed endpoints: a path
    constraint, not a guarantee of a small cost for every shift within
    `w`. Noise robustness and unequal lengths need their own conditions,
    and an admissible path must exist),
  - a distance input from a similarity input or a required conversion
    (affinity propagation takes similarities, not distances),
  - compatibility that depends on a setting (agglomerative clustering
    works from a distance matrix for single, complete and average
    linkage, Ward assumes Euclidean geometry),
  - validity requirements from the first design (section 5.2 there):
    what input an index can be computed on, what geometry it assesses.
- **Filters:**
  - "My data is": energy, finance, weather, retail, industry, health.
    Each sector lists its typical questions and the reader picks one.
    Fits are per question, not per sector: in finance, co-movement on the
    same dates and similar dynamics (ACF or model features) are different
    questions with different fits (first design, section 5.3). Good fits
    and fits to avoid are marked, the rest is dimmed.
  - "I want to ignore": level, scale, a global shift, local timing, noise,
    different lengths. Highlights the measures that are candidates under
    their stated conditions for all selected.
  - "I only have a distance matrix": highlights methods and indices that
    work from one, with their conditions (linkage, metric requirements).
  - A highlighted item means "candidate under these conditions", and the
    conditions are visible on the map (a short label or a mark on the
    chip), not only inside the card.
  - The sector filter and the other two exclude each other.
- **Data:** one data file in the repo, read by the build. Each item and
  each claim has a source and a short support location (section, page or
  table). The checks of the first design apply.
- **Phones:** the branches stack, connector lines are drawn only where
  they do not cross a box.

### 5.1 Draft map: exception and release gate

Owner decision, 2026-10-29: a narrow exception to the `AGENTS.md` rule
that an unconfirmed claim stays out. The full map, with the mockup's draft
text and sector fits, may appear in **local preview builds only**, so the
owner reviews the real size of the map in step 1 before its content is
verified in step 2. Lessons are not covered by the exception: every claim
in a rewritten lesson is verified before the owner review.

- Each map item has a `status`: `draft` or `checked`. "Checked" means
  every factual field reviewed against its source: what it does, ignores
  or needs, conditions, Python and R functions, sector fits and reasons.
  A substantive edit to a checked item sets it back to draft.
- The default build is the release build. It fails, one line per item,
  on any item whose status is draft, missing or unknown.
- The preview build needs an explicit option and writes to a separate
  output directory, never to `dist/`.
- In the preview, the draft is visible outside the cards too: a banner on
  the map, a draft mark on draft chips, on sector fit marks, on the home
  sector cards and in search results.
- The Pages workflow runs the release build and uploads only its output,
  only when it succeeded. A preview or stale output is never uploaded.
- In preview mode, draft map claims may carry pending review records and
  incomplete support locations, and are never shown as verified. Checked
  map items and every lesson claim keep the full verification
  requirements in both modes. Release mode rejects every draft map item.
- The gate is offline and deterministic (no network in the build).
- The implementation records the exception in the Rules of `AGENTS.md`.

The full map therefore cannot pass the release gate until step 2.

## 6. Live figures

- Plain JavaScript and SVG, no library, no network. One component per
  kind of figure (two linked series with a window slider, a cost grid with
  a band, groups that switch between precomputed states, and so on),
  reused across lessons. One accessible control mechanism (native range
  inputs and buttons) before any draggable inline-number variant.
- **Data:** the build embeds the fixture values a page needs. No runtime
  data fetch and no external request. Local CSS, JavaScript and fonts
  load as usual.
- **Accessibility:** native inputs, keyboard operable, visible focus,
  `prefers-reduced-motion` turns animations off, each figure keeps a text
  alternative that states what it shows and updates with its state.
  Without JavaScript the figure falls back to its static SVG.
- Figures redraw at the real width of the column, so labels keep their
  size on phones.

### 6.1 Kernels and parity

- **Scope in step 1** (Claude's call): JavaScript kernels for Euclidean,
  z-normalisation, SBD, and DTW with window (distance and path). Groupings
  and validity scores are not recomputed in the browser: Python computes
  them for each state a figure can show and the page switches between
  them.
- **Conventions copied from the reference code** (`code/python/tsc/`):
  z-normalisation with the population standard deviation and the
  reference handling of constant series, the DTW convention of
  `AGENTS.md` including unreachable cells and the reference tie order for
  the path, SBD without automatic standardisation and without circular
  wrap-around, `ValueError` cases shown as an invalid state in the page.
- **Input contract per control**, set in the plan before the widget is
  built: range, step, units, preprocessing order, how a shift treats the
  series ends, what the figure shows for an invalid state (for example a
  zero-norm series under SBD). Fixture lengths and control bounds are set
  so the live cost grid stays within a stated rendering budget.
- **Parity tests** run the JavaScript kernels against the Python reference
  on the untouched fixture rows and on inputs the controls can generate
  (every reachable state for discrete controls, a stated sample for
  continuous ones). Candidate additional edge cases, proposed to the owner
  for selection: window 0, no window, constant series, ties. Explicit
  tolerances, rounding only for display. Python and
  JavaScript agreeing is not a proof of the formula: the existing hand and
  package oracles (`code/python/tests/test_distances.py`) stay.
- **Static and live versions** (Claude's call): Python keeps generating
  the static SVG of each figure's initial state, under the existing figure
  rules. JavaScript renders the same figure from the same embedded data
  and takes over when it runs. The two share data and identifiers, not a
  renderer. The e2e tests check that the JavaScript-drawn initial state
  matches the static one in meaning (series, band, path, labels, numbers)
  and uses only the allowed figure classes, and that the static figure
  stays usable if the script fails.
- A claim a figure is built to show (for example "Euclidean grows while
  SBD stays low" under a shift) is an observation verified over the chosen
  fixture and control range, stated with those limits, not a property the
  animation is forced to display.

### 6.2 State contract

Each activity is declared as one of two kinds:

- **Precomputed-state selector:** a finite set of states (for example
  question A and question B in lesson 1). Each state binds together its
  fixture, parameters, numbers, groups, caption, text alternative and the
  answers that refer to it.
- **Live numerical experiment:** a control changes inputs and the kernels
  recompute. Only the kernels' outputs change: a grouping or score shown
  next to it is labelled with the state it was computed for, never implied
  to follow the edit.

Prose numbers come from `numbers.json` and name the settings they hold
for. Every live figure has a reset to its initial settings, and (from
step 4) baseline exercises name those settings. An answer that depends on the figure's state
follows the current state, and says which state it refers to.

**Planned figures for step 1:** lesson 1, the twelve days switching
between the two questions' groups, and a shift slider comparing Euclidean
and SBD. Lesson 5, two linked series with a window slider, the cost grid
with its band and path, all driven by one DTW state, and the too-wide
window pair (mon and wed) through the same component. Immediate state
changes come before any polish of group motion.

## 7. Worked examples and exercises

In the first phase only the worked examples in the text apply (section
1.1). The rest of this section is the design for step 4.

- **Sectors:** energy (the existing 12-day fixture), finance, weather.
  Each main sector gets an authored fixture, like the energy one, saved as
  numbers in `fixtures/`, and stated in the lessons as a demonstration,
  not evidence. Their size, length and the effects they are built to show
  are set in the plan, which the owner approves, and follow the existing
  fixture checks. Finance: synthetic returns from a factor model (first
  design, section 5.3). Weather: yearly temperature profiles of a few
  stations whose level and seasonal amplitude differ. Retail, industry and
  health: used in a few exercises where they fit, with small authored
  fixtures added with the lessons that need them.
- **Frozen** means: the numerical checks pass **and** the owner has
  approved the teaching effect (owner, 2026-10-29: a short ok on the
  finance and weather fixtures in step 4, a chart and what each is built
  to show, before they are frozen).
- **Real data:** where the licence allows, a script the reader runs on
  their own machine downloads real data, without the repo redistributing
  it. It belongs to the code labs (step 5), not to step 1. The page itself
  never fetches anything: exercises in the page work on the fixtures.
- **Worked example:** a question from the sector, the steps, the figure,
  the numbers, what the result means and what it does not.
- **Exercise:** a task stated in the page, the data it uses (a fixture,
  with its settings) and, where useful, a hint. The answer is hidden and
  revealed on click, with a short explanation. Answers are numbers from
  the reference code, a choice with its reason, or a short written
  reasoning. Nothing is graded or stored.
- **Predict-then-reveal:** a multiple-choice question before a figure, the
  answer and its reason shown after the reader picks.
- **Transfer task** (one per lesson, Codex finding 8): a case not
  demonstrated in the lesson, stated as the object, the question and the
  differences the reader may ignore. The reader proposes a compatible
  choice (a distance, and where the lesson reaches it, a method and an
  index) and rejects a plausible alternative with its reason. The reveal
  gives a worked rationale, the conditions under which the choice holds
  and the acceptable alternatives, never a single winner. It keeps the
  first design's distinction between what can be computed, what geometry
  it assumes and what answers the domain question. In lessons 1 and 5 the
  method and index may be supplied, as previews of later modules, without
  teaching the validity module early. Later lessons add cumulative tasks
  with a sensitivity check and a case where clean or stable groups answer
  the wrong question.

## 8. Sources

- **Reference works** (owner-approved): Paparrizos et al. 2024, *A
  Survey on Time-Series Distance Measures* (arXiv 2412.20574), for
  distances. Aghabozorgi, Seyed Shirkhorshidi and Ying Wah 2015,
  *Time-series clustering: a decade review* (Information Systems,
  doi 10.1016/j.is.2015.04.007), for methods. Arbelaitz et al. 2013, *An
  extensive comparative study of cluster validity indices* (Pattern
  Recognition, doi 10.1016/j.patcog.2012.07.021), for validity indices.
  A map item or a claim cites a reference work only where that work
  actually supports it, with the support location. Where it does not (a
  later method, a package API, a sector judgement), a specific source is
  added. No automatic fallback to the branch's reference work.
- **Per topic:** one or two references for each measure, method or
  index, in its standard form (section 1.1). A reference work counts as
  one of them only where it supports the claim.
- **In lessons:** a source is cited inside the paragraph that uses it. A
  click shows authors, year, title, venue and the links. The end of the
  lesson lists only the sources its paragraphs cite. Sources are found and
  checked while each lesson is written, not in advance. Non-obvious claims
  record a support location.
- **Links:** one source per claim, linked in up to four places: the
  publisher via DOI, arXiv, SSRN, the authors' page. Only legitimate
  copies of the cited work and version. No "free" label.
- **Registry:** one data file with every source (authors, year, title,
  venue, DOI, arXiv id, SSRN id, authors' URL, topics). The offline build
  fails on a citation key missing from the registry and on a claim
  without its review record (draft map claims in preview mode: section
  5.1).
- **Two kinds of check, kept apart:**
  - *Bibliographic and link check:* a separate script, run when sources
    change, checks DOIs against Crossref and ids against arXiv. Results
    are recorded as distinct outcomes: matched, metadata mismatch,
    unavailable at check time, checked by hand (SSRN refuses automated
    requests). This check does not certify that a paper supports a claim.
    The script is part of step 1.
  - *Editorial verification:* a person or reviewing model reads the
    source at the support location and confirms it supports the claim.
    Editing a claim reopens its verification even when the registry is
    unchanged.
- **Before the owner review of step 1** (Claude's call, from the project
  rule): every claim in rewritten lessons 1 and 5 has its source found,
  verified (both kinds of check) and in the registry. No placeholder
  citations.

## 9. Testing

The pilot's suite stays (reference tests with their hand and package
oracles, R parity, build validation, e2e on `file://` and under the Pages
subpath, contrast, keyboard, screenshots). Added:

- JavaScript kernel parity against Python on fixture rows and on
  control-generated inputs (section 6.1).
- Static and live figure agreement in meaning (series, band, path,
  labels, numbers), and a usable static figure when the script fails.
- e2e for the shell: contents panel open and close with focus return,
  section highlight, search results, navigation and Escape, `/` not
  stolen from inputs, answers absent from search, map filters, condition
  labels and cards, exercise reveal (from step 4), live figure controls
  and reset, no
  external request and no runtime data fetch, widths 1440, 1280, 820 and
  375 or 390 px, both themes, no-JavaScript reading.
- Build checks for the new data files (map items and their status,
  sources, citation keys, review records) and for the release gate: the
  release build fails on draft, missing or unknown status, the preview
  build never writes to `dist/`.

Edge cases for each new function are proposed to the owner, who picks
which become tests (project rule).

## 10. Delivery order

1. **Shell and format, on the two pilot lessons**, in three checkpoints
   (Codex's split):
   1. *Shell and static learning format.* The contracts of this document
      in code: new lesson template and schema, navigation, search, sources
      page and registry, release and preview builds, static fallbacks.
      One real worked example and citation. The full draft map
      with its filters (preview only). **Owner review:** look, shell, map,
      phone, dark theme.
   2. *Lesson 5 end to end.* The shared DTW state driving linked series,
      grid, band and path, the too-wide-window pair, the worked example
      in the text, source verification.
   3. *Lesson 1 and integration.* The Euclidean, z-normalisation and SBD
      experiment, the precomputed group states, both lessons complete.
      **Owner review** of the whole of step 1.
   If something must be cut, cut duplicate interaction machinery and
   animation polish first. Not cut: paragraph sources, worked
   explanations, the map's full size and the static fallbacks.
2. **Map content verified**, item by item, against the reference works and
   the sources it needs, every item to `checked`. Codex review. Only then
   can a release build pass.
3. Remaining lessons, module by module (content first, existing libraries
   first, owner's direction of 2026-10-28), under section 1.1.
4. **Exercises** (section 7), each with the owner's go-ahead to start:
   finance and weather fixtures (built, then a short owner ok on each, a
   chart and what it is built to show, before they are frozen), the
   per-lesson sector coverage table, exercises, transfer tasks and
   predict-then-reveal questions in every published lesson.
5. Code labs, real-data scripts and cross-language checks.
6. README rewrite, licence, repo rename, GitHub Pages (remote steps, each
   with the owner's go-ahead).

## 11. Left to the builder

- Data file formats (map, sources, review records, exercises), the
  Markdown syntax for citations, exercises, transfer tasks and live
  figures, the search index format and ranking.
- Component boundaries in JavaScript, file layout under `site/`.
- The exact breakpoint and widths, within the stated values.
- How to show long families and condition labels in the map.
- Whether lessons 1 and 5 keep their current section order inside the new
  structure.
- Which branch carries the work (the pilot is not merged into `master`
  yet: the plan decides, merges need the owner's go-ahead).
