# HANDOFF — time-series-clustering

Closed: 2026-10-29 12:17 CET (HEAD verified before this update: 976c502)
Last operation: the two SDD workspaces deleted with the owner's go-ahead,
ledgers kept in `docs/research/`. Before that: checkpoint 1 built and
verified (LOG entry "Checkpoint 1 built (shell, format, draft map)").

## Goal

Turn the public repo `maxto/Time-Series-Clustering` into a concept-first,
English-only course on time series similarity and clustering. Now: the
owner's checkpoint 1 review of the redesign (look, shell, map, phone, dark
theme), then the plan for checkpoint 2 (lesson 5 live figures). Design:
[docs/superpowers/specs/2026-10-28-course-design.md](docs/superpowers/specs/2026-10-28-course-design.md),
amended by the approved
[docs/superpowers/specs/2026-10-28-redesign-design.md](docs/superpowers/specs/2026-10-28-redesign-design.md).
Plan executed:
[docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md](docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md).

## State

- Clone at `~/projects/personal/time-series-clustering/`. Branch `redesign`
  (from `pilot` at `6055354`), local only, commits `9fd7cdf..7f28d4f` plus
  the notes commit. `pilot` at `6055354`, `master` at `196e416` (two commits
  ahead of `origin/master`), nothing pushed.
- Verified 2026-10-29 11:06 on `7f28d4f`: pytest 113 passed, `npm test` e2e
  ok, `npm run preview` ok, `npm run build` exits 1 with draft lines only
  (by design until the map is reviewed).
- Demo: `http://127.0.0.1:60610/preview/`, served by the plain server on
  60610 through the symlink `.mockups/preview -> ../preview` (git-ignored).
  Rebuild with `npm run preview` after changes. Server verified 11:06, to
  check at resume.
- Screenshots: `tests/output/shots/` (16 PNG, manifest), git-ignored.
- SDD workspaces deleted 2026-10-29 with the owner's go-ahead. Their
  ledgers (every ruling and deferred minor finding) are tracked in
  `docs/research/2026-10-28-sdd-pilot-ledger.md` and
  `docs/research/2026-10-29-sdd-cp1-ledger.md`.
- Codex pane of this project (`term_58cbd4cb...`): chat cleared 2026-10-29
  12:20 at the owner's full-clean request (new-chat banner checked), all its
  answers saved in `docs/research/`. The bash pane was cleared too.
- The fix-wave commit `7f28d4f` carries a "Sonnet 5.5" co-author trailer
  instead of the session's line. Left as is (changing it rewrites history).

## Open items

1. **Owner review of checkpoint 1** (owner). Points to look at: static
   figures scale to the 760 px column (labels larger on desktop), one
   connector line only (root to Compare) in the 760 px column, need-tag
   label wording on map cards. Status: demo ready, waiting.
2. **Checkpoint 2 plan** (lesson 5 end to end: live DTW figures, lesson text
   to the first-phase source rule). Status: after item 1.
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

Wait for the owner's checkpoint 1 review of `http://127.0.0.1:60610/preview/`,
record the decisions, then write the checkpoint 2 plan.
