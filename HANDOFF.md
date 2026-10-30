# HANDOFF — time-series-clustering

Closed: 2026-10-30 14:47 CET (HEAD verified before this update: a7a5e7a)
Last operation: version 1 online at https://maxto.github.io/time-series-clustering/. Repo renamed
`maxto/time-series-clustering`, Pages active from the workflow, push on `master`.

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

- Clone at `~/projects/personal/time-series-clustering/`. Working branch now `master`, same as
  `redesign` plus the notes commit. Every push to `master` republishes the site. `pilot` local only.
- Verified 2026-10-30 14:47 CET: the live site answers 200 on home, lessons, sources, card and assets. In a browser:
  15 lessons, no draft banner, no sector section, the map filter reacts, no display formula overflows
  at 375 px, the live DTW figure is there, no console or request errors. Workflow run 41065978711
  success. pytest 164 passed, `npm test` e2e ok. The old repo URL still answers.
- `npm run build` (release) still fails by design, the site uses `--publish`.
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

1. **Owner reads the live course** and says what to change. No second-model review was done,
   Claude has not read all lessons end to end, DISSIM's definition was not checked on the paper.
   Status: waiting.
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
13. **Branches:** `redesign` merged into `master` by fast-forward. Status: done.
14. **Parked items** of the pilot: `docs/research/2026-10-28-codex-pilot-final-review.md`.
    Status: parked.
15. **Licence:** done, MIT and CC BY 4.0 (LOG 2026-10-30). PDF rights still to check.
16. **Remote steps:** done 2026-10-30, no tag (owner: the other course has none). A later push needs
    its own go-ahead. The notes commit after the publication is local only.
17. **Codex sessions in other projects** still hold the old hooks (exit 127) until
    restarted. Owner: the `~/infra/agents` session, told 2026-10-28. Status: handed over,
    to check there.

## Next step

Take the owner's corrections on the live course, version after version, lesson by lesson.
