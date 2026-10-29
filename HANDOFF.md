# HANDOFF — time-series-clustering

Closed: 2026-10-29 07:53 CET (HEAD verified before this update: 0575db2)
Last operation: redesign design written, builder check done, Codex
adversarial review received (verdict: ready after listed changes). Notes,
design and reviews committed. LOG entries "Pilot review: redesign
direction" and "Redesign design written and reviewed by Codex".

## Goal

Turn the public repo `maxto/Time-Series-Clustering` (49 stars, 7 forks,
reference tables in one README + a PDF) into a concept-first, English-only
course on time series similarity and clustering. Now: redesign of look,
navigation and lesson format after the pilot review, before writing more
lessons. Design:
[docs/superpowers/specs/2026-10-28-course-design.md](docs/superpowers/specs/2026-10-28-course-design.md),
amended by
[docs/superpowers/specs/2026-10-28-redesign-design.md](docs/superpowers/specs/2026-10-28-redesign-design.md)
(not yet approved by the owner). Codex review:
[docs/research/2026-10-28-codex-redesign-review.md](docs/research/2026-10-28-codex-redesign-review.md).

## State

- Clone at `~/projects/personal/time-series-clustering/`. Branch `pilot`
  (from master `196e416`), local only, HEAD `0575db2`. `master` at
  `196e416`, two commits ahead of `origin/master`, not pushed.
- Notes, redesign design, Codex request and review, pilot final reviews:
  committed on `pilot` 2026-10-29 (owner go-ahead). Worktree clean after
  that commit (to check at resume with `git status`).
- Pilot built and verified 2026-10-28 on `0575db2` (see LOG): reference
  code, R parity, engine, lessons 1 and 5, e2e tests.
- Redesign mockup (git-ignored, throwaway): `.mockups/course/index.html`
  (home with map of the field and sector filter, lesson 1, lesson 5,
  contents sidebar, search), `.mockups/course/logo.html` (logo options).
  Served at `http://127.0.0.1:60610/course/` by the plain server on port
  60610 (serves `.mockups/`, reload to see changes, no restart needed).
  Verified running 2026-10-28 22:32, to check at resume.
- Ports 60611 (pilot preview) and 63317 (brainstorm companion) stopped
  2026-10-28 on the owner's request. Earlier companion screens remain in
  `.superpowers/brainstorm/` (git-ignored).
- R package `dtw` 1.23.3 installed in the user R library (owner-approved).

## Open items

1. **Redesign design** (owner and Claude, in progress). Build approach
   chosen (strada 1), design written, builder check and Codex review done.
   Waiting on two owner answers: (a) narrow exception for a visibly
   labelled draft map in local preview only, release builds refuse draft
   items; (b) owner reviews after checkpoint 1 and checkpoint 3. Then
   Claude amends the design with every Codex finding (list in LOG entry
   2026-10-29), owner approves the doc, then the writing-plans skill.
2. **Map and sector content is a draft.** Every card (what a measure
   ignores, what a method or index needs, Python and R functions, sector
   fit and reasons) must be checked against primary sources before it goes
   into the course. Known: R `dist(method = "binary")` is not Hamming (README
   error), `TSclust` and `TSdist` archived on CRAN, several functions marked
   "to check". Status: to do in the content phase.
3. **Sources** (owner, 2026-10-28): a couple of reference works for the
   map (approved: Paparrizos et al. 2024, Aghabozorgi et al. 2015,
   Arbelaitz et al. 2013), and per-paragraph citations
   found and checked while each lesson is written (Crossref or arXiv,
   then Codex). Link policy in LOG. Status: approved, applies when lessons are written.
4. **Merge `pilot` into `master`** and delete the SDD workspace
   `.superpowers/sdd/2026-10-28-pilot/`: deferred until the redesign plan
   says how the pilot engine is reused. Each needs the owner's go-ahead.
5. **Parked items** (LEAVE in Codex's final triage): code hardening and
   test candidates, in `docs/research/2026-10-28-codex-pilot-final-review.md`.
   Status: parked.
6. **Content first, existing libraries first** (owner, 2026-10-28) for the
   remaining lessons and code labs. Status: applies after the redesign.
7. **Licence:** MIT code + CC BY 4.0 content proposed, owner to confirm.
   PDF rights to check. Status: to decide.
8. **Remote steps, each with its own go-ahead:** push, repo rename to
   lowercase, GitHub Pages activation. Status: not started.
9. **Codex sessions in other projects** still hold the old hooks (exit
   127) until restarted. Owner: the `~/infra/agents` session, told
   2026-10-28. Status: handed over, to check there.

## Next step

Ask the owner the two open questions of item 1 (draft map exception,
review checkpoints), then amend the redesign design per the Codex review.
