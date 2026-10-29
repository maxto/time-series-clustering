# Time series clustering: redesign after the pilot (design)

Status: draft, 2026-10-28. Builder check done (its seven questions settled
as Claude's calls, marked in the text), waiting for Codex review and the
owner's approval. Amends
[2026-10-28-course-design.md](2026-10-28-course-design.md): where the two
disagree, this document wins. Decisions and their reasons, in the owner's
words where possible: `LOG.md`, entry "Pilot review: redesign direction".
Reference mockup (git-ignored, throwaway, not code to reuse as is):
`.mockups/course/index.html` and `.mockups/course/logo.html`, served at
`http://127.0.0.1:60610/course/`.

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

## 2. Goals, non-goals, anti-goals

**Goals**

- Every lesson teaches through worked examples (step by step, with
  figures and numbers the reader can follow) and ends with exercises.
- Live figures the reader manipulates (sliders, toggles, draggable
  numbers), whose numbers match the reference code.
- A map of the field on the home page, with filters and item cards.
- Three main sectors recur through the course: energy, finance, weather.
- Sources cited at the paragraph level, linked to where the paper lives.
- Navigation and search consistent with ai-one-token-at-a-time.

**Non-goals**

- Running Python or R in the page (Pyodide, webR). Code is read and
  copied. Rejected by the owner: weight and reading come first.
- Grading, accounts, progress stored on a server. Exercises reveal their
  answer, nothing is submitted.
- A primary source for every one of the 100+ map items (owner: a couple of
  reference works plus per-paragraph sources).
- Six recurring sectors. Retail, industry and health appear in the map and
  in some exercises only.

**Anti-goals (failure even if it works)**

- A page that feels like a slide deck or an app instead of a lesson to
  read and come back to.
- Interactivity that shows numbers different from the reference code.
- Labelling a source "free": access depends on the reader.
- A sector judgement ("good fit", "avoid") stated without a reason the
  reader can check.
- Everything from the first design's anti-goals still holds (no universal
  winner, no trading signal, no archived package as default path).

This reverses one non-goal of the first design: "no in-browser numerical
engine or live interactive widgets" is replaced by live figures with
parity tests (section 6).

## 3. Approaches

**Page format** (owner chose A after three clickable mockups):

- **A. Explorable essay, chosen.** A reading column with live figures,
  draggable numbers in the text, predict-then-reveal questions.
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
- **Contents:** fixed on the left on wide screens (290 px column; the
  mockup switches at 1180 px of width), behind a menu button below that,
  opening as a panel (full width on phones). It lists course home, map,
  examples by sector, sources, then the modules and lessons with status
  (ready, coming) and a finance tag where the lesson has a finance block.
  Under the open lesson it lists that lesson's sections and highlights the
  one being read.
- **Search:** a box in the top bar, `/` focuses it. Results replace the
  page while typing: lesson, section, a snippet with the match marked,
  click goes to the section. It searches published lessons (titles,
  sections, text), map items and planned lesson titles (shown as coming).
  The index is generated by the build. No external service.
- **Reading column:** one width for everything (text, figures, finance
  block, code, exercises), on desktop, tablet and phone. 800 px with
  18 px text without the contents column, 760 px next to it. No
  full-width bands. Phones: everything stacks, padding 18 px.
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
   typical question and the measures it starts from. A click filters the
   map on that sector.
4. The lesson index by module, with status and finance tags.

### 4.3 Lesson page

In this order, all in the one column:

1. Module, title, lede.
2. "It ignores" and "it keeps" (the decision lens).
3. Jump links to the sections, the finance block highlighted among them.
4. One line (the lesson in one sentence).
5. Sections. Each teaches through at least one **worked example**: a
   concrete case from one of the three main sectors, step by step, with
   its figure and its numbers. Live figures sit where they explain a
   mechanism. Predict-then-reveal questions sit before the figure that
   answers them.
6. **Finance block**, where the lesson has one (most do, not all: the
   contents and the index tag the lessons that have it). Always in the
   same place (after the main sections, before the code), the width of
   the column, on a dark surface in both themes. Claude's call, from the
   mockup the owner approved: in the light theme it uses `--ink` as
   background, in the dark theme `--fig-bg` with a `--rule` border. Its
   text and any figure inside it get their own contrast check.
7. **Code:** Python and R tabs, a copy button, then a line naming the
   existing library functions for the same result. Read and copy only.
8. **Exercises** (section 7).
9. Common mistake.
10. "Sources cited in this lesson" (section 8).
11. Previous and next.

### 4.4 Sources page

All sources of the course in one list, filterable by topic (surveys,
compare, group, validate, finance, software), each with where it is cited.
A short paragraph states the link policy (section 8).

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
  input (group and validate: a distance matrix, vectors with a mean, the
  raw series, reference labels), Python and R functions, the lesson that
  covers it, one source, and, with a sector selected, the fit and its
  reason.
- **Filters:**
  - "My data is": energy, finance, weather, retail, industry, health. The
    sector's typical question appears, good fits are marked, fits to avoid
    are marked, the rest is dimmed. Each mark has a one-sentence reason in
    the card.
  - "I want to ignore": level, scale, a global shift, local timing, noise,
    different lengths. Highlights the measures that ignore all selected.
  - "I only have a distance matrix": highlights methods and indices that
    work from one.
  - The sector filter and the other two exclude each other.
- **Data:** one data file in the repo, read by the build. Its content in
  the mockup is a draft: every statement (what an item ignores or needs,
  functions, sector fit and reason) is checked against a source before
  release, and the file records the source used for each sector judgement.
- **Phones:** the branches stack, connector lines are drawn only where
  they do not cross a box.
- **Draft content in step 1** (Claude's call after the builder check):
  step 1 carries every item, with the mockup's draft text imported, sector
  fits included, so the owner reviews the real size of the map. Each item
  has a `status` (draft or checked). Draft items show a visible "draft"
  mark in the card. The build refuses to produce the deployable site
  (the one GitHub Pages would publish) while any item is draft: a local
  preview build allows it. This keeps the project rule that unchecked
  claims stay out of what is published.

## 6. Live figures

- Plain JavaScript and SVG, no library, no network. One component per
  kind of figure (two linked series with a window slider, groups that move
  between panels, a cost grid with a band, and so on), reused across
  lessons.
- **Numbers:** a live figure computes in the browser with the course
  conventions (the DTW convention of `AGENTS.md`, SBD, z-normalisation and
  so on). The JavaScript kernels are tested against the Python reference
  code on the fixtures: same inputs, same numbers to a stated tolerance.
  Numbers quoted in the prose still come from `numbers.json`.
- **Data:** the build embeds the fixture values a page needs. No fetch at
  runtime.
- **Accessibility:** native inputs (range, buttons), keyboard operable,
  visible focus, `prefers-reduced-motion` turns animations off, each
  figure keeps a text alternative that states what it shows. Without
  JavaScript the page still reads: the figure falls back to its static SVG.
- Figures redraw at the real width of the column, so labels keep their
  size on phones.
- **Static and live versions** (Claude's call): Python keeps generating
  the static SVG of each figure's initial state, under the existing figure
  rules. JavaScript renders the same figure from the same embedded fixture
  data and takes over when it runs. The e2e tests check that the
  JavaScript-drawn SVG uses only the allowed figure classes and that its
  initial numbers equal the static ones.
- **Scope in step 1** (Claude's call): JavaScript kernels for Euclidean,
  z-normalisation, SBD, and DTW with window (distance and path), each
  parity-tested against Python. Groupings and validity scores are not
  recomputed in the browser: Python computes them for each state a figure
  can show (for example question A and question B in lesson 1) and the
  page animates between them. Draggable numbers in the text recompute
  through the same kernels as the figure they belong to. Planned figures
  for step 1: lesson 1, the twelve days moving between groups, and a
  shift slider that shows Euclidean growing while SBD stays low. Lesson 5,
  two linked series with a window slider, the cost grid with its band and
  path, and the too-wide-window pair (mon and wed). Each of the three
  sectors appears in at least one of them or in an exercise.

## 7. Worked examples and exercises

- **Sectors:** energy (the existing 12-day fixture), finance, weather.
  Each main sector gets an authored fixture, like the energy one, saved as
  numbers in `fixtures/`, frozen once checked, and stated in the lessons
  as a demonstration, not evidence. Their size, length and the effects
  they are built to show are set in the plan, which the owner approves,
  and follow the existing fixture checks. Finance: synthetic returns from a
  factor model (first design, section 5.3). Weather: yearly temperature
  profiles of a few stations whose level and seasonal amplitude differ.
  Where the licence allows, a script the reader runs on their own
  machine downloads real data, without the repo redistributing it. It
  belongs to the code labs (step 4), not to step 1, and the page itself
  never fetches anything: exercises in the page work on the fixtures. Retail, industry and
  health: used in a few exercises where they fit, with small authored
  fixtures.
- **Worked example:** a question from the sector, the steps, the figure,
  the numbers, what the result means and what it does not.
- **Exercise:** a task stated in the page, the data it uses (a fixture)
  and, where useful, a hint. The answer is hidden and revealed on click,
  with a short explanation. Answers are numbers from the reference code,
  a choice with its reason, or a short written reasoning. Nothing is
  graded or stored.
- **Predict-then-reveal:** a multiple-choice question before a figure, the
  answer and its reason shown after the reader picks.

## 8. Sources

- **Reference works** (owner-approved): Paparrizos et al. 2024, *A
  Survey on Time-Series Distance Measures* (arXiv 2412.20574), for
  distances. Aghabozorgi, Seyed Shirkhorshidi and Ying Wah 2015,
  *Time-series clustering: a decade review* (Information Systems,
  doi 10.1016/j.is.2015.04.007), for methods. Arbelaitz et al. 2013, *An
  extensive comparative study of cluster validity indices* (Pattern
  Recognition, doi 10.1016/j.patcog.2012.07.021), for validity indices.
  Each map item cites its branch's reference work unless it has a more
  specific source.
- **In lessons:** a source is cited inside the paragraph that uses it. A
  click shows authors, year, title, venue and the links. The end of the
  lesson lists only the sources its paragraphs cite. Sources are found and
  checked while each lesson is written, not in advance.
- **Links:** one source per claim, linked in up to four places: the
  publisher via DOI, arXiv, SSRN, the authors' page. Only legitimate
  copies. No "free" label.
- **Registry:** one data file with every source (authors, year, title,
  venue, DOI, arXiv id, SSRN id, authors' URL, topics). The build fails on
  a citation key missing from the registry. A separate script, run when
  sources change, checks DOIs against Crossref and ids against arXiv
  (SSRN refuses automated checks: those links are checked by hand and
  recorded as such). The script is part of step 1.
- **Before the owner review of step 1** (Claude's call, from the project
  rule): every claim in rewritten lessons 1 and 5 has its source found,
  checked and in the registry. No placeholder citations.

## 9. Testing

The pilot's suite stays (reference tests, R parity, build validation, e2e
on `file://` and under the Pages subpath, contrast, keyboard,
screenshots). Added:

- JavaScript kernel parity against Python on the fixtures.
- e2e for the shell: contents panel open and close, section highlight,
  search results and navigation, map filters and cards, exercise reveal,
  live figure controls, no runtime request, widths 1440, 1280, 820 and
  375 or 390 px, both themes.
- Build checks for the new data files (map items, sources, citation keys).

Edge cases for each new function are proposed to the owner, who picks
which become tests (project rule).

## 10. Delivery order

1. **Shell and format, on the two pilot lessons.** Course shell, search,
   map (structure and filters, draft content clearly marked as draft until
   step 2), sources page and registry, live figure components, exercise
   blocks. Lessons 1 and 5 rewritten in the new format with worked
   examples and exercises. The finance and weather fixtures are built and
   each is used in at least one worked example or exercise in these two
   lessons. Owner review before going on.
2. **Map content verified**, item by item, against the reference works and
   the sources it needs. Codex review.
3. Remaining lessons, module by module (content first, existing libraries
   first, owner's direction of 2026-10-28).
4. Code labs and cross-language checks.
5. README rewrite, licence, repo rename, GitHub Pages (remote steps, each
   with the owner's go-ahead).

## 11. Left to the builder

- Data file formats (map, sources, exercises), the Markdown syntax for
  citations, exercises and live figures, the search index format and
  ranking.
- Component boundaries in JavaScript, file layout under `site/`.
- The exact breakpoint and widths, within the stated values.
- How to show long families in the map.
- Whether lessons 1 and 5 keep their current section order inside the new
  structure.
- Which branch carries the work (the pilot is not merged into `master`
  yet: the plan decides, merges need the owner's go-ahead).
