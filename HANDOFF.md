# HANDOFF — time-series-clustering

Closed: 2026-10-29 08:50 CET (HEAD verified before this update: 9a2fa1b)
Last operation: redesign design amended with every Codex finding, Codex
re-check done and its three new points fixed, owner's content direction
applied, design approved by the owner. LOG entry "Redesign design
amended, re-checked and approved".

## Goal

Turn the public repo `maxto/Time-Series-Clustering` (49 stars, 7 forks,
reference tables in one README + a PDF) into a concept-first, English-only
course on time series similarity and clustering. Now: implementation plan
for the approved redesign, then step 1 (shell and format on lessons 1
and 5). Design:
[docs/superpowers/specs/2026-10-28-course-design.md](docs/superpowers/specs/2026-10-28-course-design.md),
amended by the approved
[docs/superpowers/specs/2026-10-28-redesign-design.md](docs/superpowers/specs/2026-10-28-redesign-design.md)
(section 1.1: content direction for the first phase, section 10:
delivery order). Codex reviews:
[review](docs/research/2026-10-28-codex-redesign-review.md),
[re-check](docs/research/2026-10-29-codex-redesign-recheck.md).

## State

- Clone at `~/projects/personal/time-series-clustering/`. Branch `pilot`
  (from master `196e416`), local only. `master` at `196e416`, two commits
  ahead of `origin/master`, not pushed.
- Design amendment and Codex re-check: committed on `pilot` 2026-10-29
  with these notes (owner go-ahead "Ok, procedi"). To check at resume
  with `git status`.
- Pilot built and verified 2026-10-28 on `0575db2` (see LOG): reference
  code, R parity, engine, lessons 1 and 5, e2e tests.
- Redesign mockup (git-ignored, throwaway): `.mockups/course/index.html`
  (home with map, lesson 1, lesson 5 with the 2026-10-29 demo additions:
  measure card, state line with reset, draft banner, condition labels,
  exercises removed), `.mockups/course/logo.html`. Served at
  `http://127.0.0.1:60610/course/` by the plain server on port 60610.
  Verified running 2026-10-29 08:45, to check at resume.
- Headless Chrome screenshots timed out 2026-10-29 ~08:40, even on a blank
  page (page JS responsive). Not investigated. To check before e2e runs.
- R package `dtw` 1.23.3 installed in the user R library (owner-approved).
- Codex pane of this project: re-check task done, answer saved in
  `docs/research/`. Its chat can be cleared when idle.

## Open items

1. **Implementation plan** for the redesign (Claude, writing-plans skill),
   then step 1 in three checkpoints. Owner reviews after checkpoint 1 and
   checkpoint 3. Status: to do, next.
2. **Map and sector content is a draft.** Every card must be checked
   against sources before release (design section 5.1: release build
   refuses draft items). Known: R `dist(method = "binary")` is not Hamming
   (README error), `TSclust` and `TSdist` archived on CRAN, several
   functions marked "to check", affinity propagation takes similarities,
   Ward needs Euclidean. Status: step 2 of the design.
3. **Sources** (owner): reference works approved (Paparrizos et al. 2024,
   Aghabozorgi et al. 2015, Arbelaitz et al. 2013). One or two references
   per topic in standard form, found, read and confirmed by web search
   while each lesson is written (design section 1.1). Status: applies
   from step 1.
4. **Exercises, transfer tasks, finance and weather fixtures:** step 4 of
   the design, each with the owner's go-ahead to start. Status: deferred.
5. **Merge `pilot` into `master`** and delete the SDD workspace
   `.superpowers/sdd/2026-10-28-pilot/`: the plan decides the branch, each
   needs the owner's go-ahead. Status: to decide in the plan.
6. **Parked items** (LEAVE in Codex's final triage): code hardening and
   test candidates, in `docs/research/2026-10-28-codex-pilot-final-review.md`.
   Status: parked.
7. **Content first, existing libraries first** (owner, 2026-10-28) for the
   remaining lessons and code labs. Status: applies from step 3.
8. **Licence:** MIT code + CC BY 4.0 content proposed, owner to confirm.
   PDF rights to check. Status: to decide.
9. **Remote steps, each with its own go-ahead:** push, repo rename to
   lowercase, GitHub Pages activation. Status: not started.
10. **Codex sessions in other projects** still hold the old hooks (exit
    127) until restarted. Owner: the `~/infra/agents` session, told
    2026-10-28. Status: handed over, to check there.

## Next step

Invoke the writing-plans skill on the approved redesign design and write
the plan for step 1 (checkpoint 1 first), then pass it to Codex for review.
