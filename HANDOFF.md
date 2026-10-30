# HANDOFF — time-series-clustering

Closed: 2026-10-30 14:23 CET (HEAD verified before this update: ddda879)
Last operation: version 1 ready locally on `redesign`. Nothing pushed. Waiting for the owner's
go-ahead on the remote steps (open item 1).

## Goal

Turn the public repo `maxto/Time-Series-Clustering` into an operational,
technical, English-only mini-course on time series similarity and clustering,
in the spirit of the original README list. Now: review of the first pass, then
lesson by lesson from the first to the last. Design:
[docs/superpowers/specs/2026-10-30-pipeline-course-design.md](docs/superpowers/specs/2026-10-30-pipeline-course-design.md),
which replaces the narrative plan of the redesign for the rest of the course.
The plan `docs/superpowers/plans/2026-10-29-redesign-checkpoint-2.md` is
superseded from Task 5 on (LOG 2026-10-30).

## State

- Clone at `~/projects/personal/time-series-clustering/`. Branch `redesign`,
  local only. `pilot` at `6055354`, `master` at `196e416`, nothing pushed.
- Verified 2026-10-30 13:49 CET: all 15 lessons `published` in `content/_course.md`, pytest
  163 passed, `npm test` e2e ok, `npm run preview` builds 15 of 15 with 22 figures. `npm run build`
  fails by design (draft lessons and map).
- Follow-ups per lesson, figures asked for and doubts:
  `docs/research/2026-10-30-first-pass-followups.md`. Finance research:
  `docs/research/2026-10-30-dtw-finance-report.md` (in Italian) and
  `docs/research/2026-10-30-dtw-finance-notes/`.
- Demo: `http://127.0.0.1:60610/preview/`, plain server on 60610 through the
  symlink `.mockups/preview -> ../preview` (git-ignored). Rebuild with
  `npm run preview`.
- Ledgers: `docs/research/2026-10-28-sdd-pilot-ledger.md`,
  `docs/research/2026-10-29-sdd-cp1-ledger.md`, and the git-ignored
  `.superpowers/sdd/2026-10-29-redesign-checkpoint-2/progress.md`.
- The fix-wave commit `7f28d4f` carries a "Sonnet 5.5" co-author trailer instead of
  the session's line. Left as is.

## Open items

1. **Remote steps of version 1, need the owner's explicit go-ahead:** fast-forward `master` to
   `redesign`, push `master` and tag `v1`, rename the repo to `time-series-clustering` and update
   `origin`, enable Pages from the workflow, set description and homepage. The owner stated the goal
   (first publication now, like ai-one-token-at-a-time), the go-ahead on these steps is pending.
   Then check the live site. Status: waiting for the owner.
2. **Remaining figures** of the follow-ups file (second panels, Ward, DTW_D against DTW_I, the
   Keogh and Lin test). Status: after the owner's look.
3. **Proposals to the owner:** remove the unused `content/figures/dtw-window.svg`,
   and `content/figures/overview.svg`, no longer shown on the home. Decide what to do
   with the unused `aeon-dtw`, `dtw-python`, `rousseeuw87` entries. Tests for the two new
   behaviours: a preview shows a draft lesson with the banner and a release refuses it.
   Status: to ask.
4. **Next versions, lesson by lesson** (owner and Claude). A second-model review is welcome but
   no longer holds back a publication (owner, 2026-10-30). Status: after version 1.
5. **Facts to confirm in the second pass:** the year of Ratanamahatana and Keogh
   (2004 from memory, the copy read has no date), the "When to use it" and
   "Which clustering algorithm" text of lesson `dtw`, written from standard knowledge.
   Status: to check.
6. **Recommended validity indices:** out for now, the owner will decide later.
   Status: parked.
7. **Finance figure and fixture:** the design's step 4 needs the owner's go-ahead for
   finance and weather fixtures. Status: deferred.
8. **Map and sector content is a draft.** The release build refuses it. Known: R
   `dist(method = "binary")` is not Hamming, `TSclust` and `TSdist` archived on CRAN,
   affinity propagation takes similarities, Ward needs Euclidean. The item cards still
   show library functions. Status: to do in a later pass.
9. **Sources page** still shows source links, unchanged. Status: to decide in a later pass.
10. **Owner review of checkpoint 1 points:** need-tag label wording on map cards.
    The connector line point is closed, the lines are gone. Status: waiting.
11. **Deferred minor findings** of checkpoint 1 and 2, in the ledgers above. One is flagged
    as worth fixing: the deep-dive validation accepts `:::` as closer of a `::::` opener.
    Status: to propose as a short list.
12. **Code, last pass, not in version 1 (owner, 2026-10-30):** `## Code`, code labs and the reference packages. `code/` stays in the repo only because `scripts/figures.py` draws the figures with it. Library cards
    follow "content first, existing libraries first" (owner, 2026-10-28). Status: deferred.
13. **Branches:** `redesign` builds on `pilot`, merging into `master` needs the owner's
    go-ahead. Status: after the passes.
14. **Parked items** of the pilot: `docs/research/2026-10-28-codex-pilot-final-review.md`.
    Status: parked.
15. **Licence:** done, MIT and CC BY 4.0 (LOG 2026-10-30). PDF rights still to check.
16. **Remote steps:** see item 1.
17. **Codex sessions in other projects** still hold the old hooks (exit 127) until
    restarted. Owner: the `~/infra/agents` session, told 2026-10-28. Status: handed over,
    to check there.

## Next step

Get the go-ahead on item 1, run the steps, check the live site. Then version after version,
lesson by lesson.
