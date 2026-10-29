# HANDOFF — time-series-clustering

Closed: 2026-10-29 18:50 CET (HEAD verified before this update: a55b239)
Last operation: checkpoint 2 Tasks 1 to 4 built and reviewed (kernels,
live figure data, live figure, deep-dives). Next: Task 5, lesson 5 text and
sources, by the main agent with a Codex review.

## Goal

Turn the public repo `maxto/Time-Series-Clustering` into a concept-first,
English-only course on time series similarity and clustering. Now: the
checkpoint 2 of the redesign, lesson 5 end to end (live DTW figure,
deep-dives, sources). Design:
[docs/superpowers/specs/2026-10-28-course-design.md](docs/superpowers/specs/2026-10-28-course-design.md),
amended by the approved
[docs/superpowers/specs/2026-10-28-redesign-design.md](docs/superpowers/specs/2026-10-28-redesign-design.md).
Plan in execution:
[docs/superpowers/plans/2026-10-29-redesign-checkpoint-2.md](docs/superpowers/plans/2026-10-29-redesign-checkpoint-2.md)
(Tasks 1 to 4 done, 5 and 6 to do). Ledger with every ruling and deferred
minor finding: `.superpowers/sdd/2026-10-29-redesign-checkpoint-2/progress.md`
(git-ignored, keep it until the final review).

## State

- Clone at `~/projects/personal/time-series-clustering/`. Branch `redesign`
  (from `pilot` at `6055354`), local only, commits `9fd7cdf..7f28d4f` plus
  the notes commit. `pilot` at `6055354`, `master` at `196e416` (two commits
  ahead of `origin/master`), nothing pushed.
- Checkpoint 2 commits `b1263e8..a55b239` (plan revision, Tasks 1 to 4).
- Verified 2026-10-29 18:45 on `a55b239`: pytest 163 passed, `npm test` e2e
  ok. `npm run build` exits 1 with draft lines only (by design until the
  map is reviewed).
- Demo: `http://127.0.0.1:60610/preview/`, served by the plain server on
  60610 through the symlink `.mockups/preview -> ../preview` (git-ignored).
  Rebuild with `npm run preview` after changes. Smoke course (live figures
  in gamma, deep-dive in alpha): `http://127.0.0.1:60610/smoke/`, symlink
  `.mockups/smoke -> ../tests/output/smoke-dist`, rebuilt by `npm test`.
  Server verified 18:45.
- Screenshots: `tests/output/shots/` (16 PNG, manifest), git-ignored.
- SDD workspaces deleted 2026-10-29 with the owner's go-ahead. Their
  ledgers (every ruling and deferred minor finding) are tracked in
  `docs/research/2026-10-28-sdd-pilot-ledger.md` and
  `docs/research/2026-10-29-sdd-cp1-ledger.md`.
- Codex pane of this project (`term_58cbd4cb...`): chat cleared 2026-10-29
  after the checkpoint 2 plan review (answer saved in `docs/research/`).
- The fix-wave commit `7f28d4f` carries a "Sonnet 5.5" co-author trailer
  instead of the session's line. Left as is (changing it rewrites history).

## Open items

1. **Owner review of checkpoint 1** (owner). Static figures were shown
   2x enlarged: fixed 2026-10-29 (shown at their drawn 360 px, LOG entry
   "Static figures no longer enlarged"), owner confirmed. Type made
   smaller (LOG "Smaller type, reading measure, frontend-design skill"). Other points:
   one connector line only (root to Compare) in the 760 px column, need-tag
   label wording on map cards. Status: demo ready, waiting.
2. **Checkpoint 2** (owner asked: after each task send the demo link, clean
   up, go on). Tasks 1 to 4 done (LOG "Checkpoint 2 plan, Codex review,
   Tasks 1 to 4 built"). Task 5 (lesson 5 text, sources, Codex review,
   records, lesson e2e) and Task 6 (checks, `frontend-design` critique,
   demo), then the final whole-branch review with the deferred minor list
   of the ledger. To propose to the owner: remove the unused
   `dtw-window.svg` after Task 5. Status: in progress.
3. **Map and sector content is a draft** (design step 2). Release build
   refuses it. Known: R `dist(method = "binary")` is not Hamming,
   `TSclust` and `TSdist` archived on CRAN, affinity propagation takes
   similarities, Ward needs Euclidean, several functions "to check".
   Status: to do in step 2.
4. **Sources** (owner): one or two references per topic in standard form,
   read at the supporting point, confirmed by web search, reviewed by another
   model (design 1.1). Reference works approved. Status: applies from
   checkpoint 2.
5. **Deferred edge cases and minor findings** of checkpoint 1, listed in the
   ledger (`docs/research/2026-10-29-sdd-cp1-ledger.md`) and in the Codex
   branch review's disposition table: to propose to the owner as a short list. Status: to do with
   checkpoint 2 planning.
6. **Branches:** `redesign` builds on `pilot`. Merging into `master` needs
   the owner's go-ahead. Status: after the redesign checkpoints.
7. **Exercises, transfer tasks, finance and weather fixtures:** design step
   4, each with the owner's go-ahead. Status: deferred.
8. **Parked items** of the pilot (Codex final triage):
   `docs/research/2026-10-28-codex-pilot-final-review.md`. Status: parked.
9. **Content first, existing libraries first** (owner, 2026-10-28) for the
   remaining lessons and code labs. Status: applies from step 3.
10. **Licence:** MIT code + CC BY 4.0 content proposed, owner to confirm.
    PDF rights to check. Status: to decide.
11. **Remote steps, each with its own go-ahead:** push, repo rename,
    GitHub Pages activation. Status: not started.
12. **Codex sessions in other projects** still hold the old hooks (exit
    127) until restarted. Owner: the `~/infra/agents` session, told
    2026-10-28. Status: handed over, to check there.

## Next step

Task 5 Step 1: restructure `content/05-dtw.md` (soft-DTW out, scoring to
the silhouette, `dtw-explorer.svg` in, deep-dives), then the claim
checklist and sources one at a time.
