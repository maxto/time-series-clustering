# Review request: first pass of the course

You are the adversarial reviewer. Write your full answer to
`docs/research/2026-10-30-first-pass-review.md`. Do not change any other file: no edits, no commits, no
`scripts/review.py` records. The last line of the answer file must be exactly `END OF REVIEW`.

## What to review

Branch `redesign`, HEAD `e1db08f`. Read `AGENTS.md` first, above all "Draft lesson exception and iterative passes".

- The 15 lessons `content/01-*.md` to `content/15-*.md`, in the order of `content/_course.md`. Drafts of a first pass:
  we want them correct, not complete. Missing figures and missing code are known, do not report them.
- `docs/research/2026-10-30-first-pass-followups.md`: the doubts the writers left. Settle each one you can.
- Commit `32202c6`: 22 display formulas were reflowed to fit the column. The maths must be unchanged. Three were
  rewritten more deeply, check them against the versions before the commit: TWE in `06-edit-based.md` (now
  `min{D_1, D_2, D_3}`), k-Shape in `11-match-the-algorithm.md` (now through `NCC_max`), MPdist in
  `10-multivariate-subsequence.md`.
- Commit `e1db08f`: the section chooser (`lead_label`, `heading_ids` in `scripts/buildlib/content.py`, `picks_nav` in
  `scripts/buildlib/pages.py`). Look for wrong ids, broken anchors, collisions.

## What to look for, in this order

1. Wrong maths: a formula, bound, range, complexity or property that does not match its primary definition.
2. Wrong attribution: a claim the named source does not make, a wrong author, year, title or link. A lesson may only
   name whoever developed the method or ran the study.
3. `## In finance`: an entry under `Limitations in financial time series` that is our inference, or that no source read
   states, is a finding. An entry under `Empirical applications` that misreports the abstract, or does not belong to
   the instrument or question it is listed under, is a finding. Text that says what was not found is a finding.
4. Claims about the fixture that do not hold on `fixtures/demand-12.csv` with the reference code in `code/python/tsc/`.
   The DTW convention is in `AGENTS.md`. Run the code instead of reasoning about it.
5. Advice a practitioner would be harmed by following: a measure paired with a clustering algorithm that does not suit
   it, a wrong "when to use it".
6. Register and rules: popularising language, a section out of format, a semicolon or em-dash in prose, a recommended
   validity index (they are out for now).

Known and not to report: the `Elastic` family of the home map links to `dtw` while LCSS, EDR, ERP, MSM and TWE live in
`edit-based`, and the uncited entries in `_sources.toml`.

## Evidence

Check claims against primary sources: open the paper or the abstract and quote the line you rely on, with its link.
Never go around a paywall or a bot check, and never fake a user agent. If you cannot reach a source, say so and mark
the point `not verified`. A finding from memory alone must be marked as such. Do not report style preferences.

## Format of the answer

Findings first, most severe first. For each: `file:line`, severity (`wrong`, `unsupported`, `risky`, `minor`), what the
text says, what is correct, the evidence, the proposed replacement text. Replacement prose has no semicolons or
em-dashes. Then one line per doubt of the follow-ups file with its outcome. Then what you checked and found correct,
and what you could not verify. No praise, no summary of the course.
