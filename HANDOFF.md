# HANDOFF — time-series-clustering

Closed: 2026-10-30 10:55 CET (HEAD verified before this update: c0e23f6)
Last operation: first pass of all 15 lessons done, published in the preview,
committed on `redesign`. Waiting for the owner to check a couple of lessons,
then a Codex review.

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
- Verified 2026-10-30 10:55 CET: all 15 lessons `published` in `content/_course.md`, pytest
  163 passed, `npm test` e2e ok, `npm run preview` builds 15 of 15. `npm run build`
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

1. **Owner checks a couple of lessons** (owner), then **Codex review of the first pass**
   (Claude, request and answer files in `docs/research/`, with the follow-ups file as
   input). Status: waiting for the owner.
2. **New figures** (owner: more varied graphics). The list per lesson is in the follow-ups
   file. Status: after the review, one worker on `scripts/figures.py`.
3. **Proposals to the owner:** remove the unused `content/figures/dtw-window.svg`,
   and `content/figures/overview.svg`, no longer shown on the home. Decide what to do
   with the unused `aeon-dtw`, `dtw-python`, `rousseeuw87` entries. Tests for the two new
   behaviours: a preview shows a draft lesson with the banner and a release refuses it.
   Status: to ask.
4. **Second pass, lesson by lesson** (owner and Claude), with second-model review and
   `scripts/review.py` records, before any release. Status: after the first pass.
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
12. **Code, last pass:** `## Code`, code labs and the reference packages. Library cards
    follow "content first, existing libraries first" (owner, 2026-10-28). Status: deferred.
13. **Branches:** `redesign` builds on `pilot`, merging into `master` needs the owner's
    go-ahead. Status: after the passes.
14. **Parked items** of the pilot: `docs/research/2026-10-28-codex-pilot-final-review.md`.
    Status: parked.
15. **Licence:** MIT code + CC BY 4.0 content proposed, owner to confirm. PDF rights to
    check. Status: to decide.
16. **Remote steps, each with its own go-ahead:** push, repo rename, GitHub Pages
    activation. Status: not started.
17. **Codex sessions in other projects** still hold the old hooks (exit 127) until
    restarted. Owner: the `~/infra/agents` session, told 2026-10-28. Status: handed over,
    to check there.

## Next step

Wait for the owner's check of a couple of lessons, then write the Codex review request
with the follow-ups file as input.
