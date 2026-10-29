# Codex request: whole-branch review of checkpoint 1

Date: 2026-10-29. Requested by Claude (PM). All 9 tasks of
`docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md` are done on
branch `redesign` (base `9fd7cdf`, head `d9cd733`, 19 commits), each with a
task review (Sonnet) and fix rounds. This is the final review before the
owner's checkpoint 1 review.

## Inputs

- Plan: `docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md`.
- Design: `docs/superpowers/specs/2026-10-28-redesign-design.md` (sections
  1.1, 4, 5, 5.1, 8, 9).
- Rules: `AGENTS.md`.
- Whole diff in one file:
  `.superpowers/sdd/2026-10-29-redesign-checkpoint-1/review-9fd7cdf..d9cd733.diff`
  (git-ignored workspace, read it from disk).
- Ledger with rulings and deferred minor findings:
  `.superpowers/sdd/2026-10-29-redesign-checkpoint-1/progress.md`.
- Built preview: `preview/` (from `npm run preview`).

## Questions

1. Cross-task integration: do the pieces fit (schema, citations and review
   records, atlas and its derived review state, release and preview builds,
   shell, home, sources page, behaviour, search, checks)? Anything a task
   review could not see because it spans tasks?
2. The review gate: can any lesson text, citation, map item, fit, question
   or sector reach a release build without a matching review record? Can a
   preview ever be written into or uploaded as the release?
3. Design conformance for checkpoint 1, and anything built that the design
   defers (exercises, live figures).
4. Triage of the ledger's deferred minor findings: which must be fixed
   before the owner review, which can wait.
5. Tests: any test that mirrors the implementation or asserts nothing,
   against the project rule.

Severity: Critical, Important, Minor, each with location and one concrete
change. Then a verdict: ready for the owner's checkpoint 1 review, or
ready after the listed changes.

Static review. You may run `uv run pytest -q` and `npm test` once if
useful. Do not edit any file except your answer.

## Output

Write your full answer to
`docs/research/2026-10-29-codex-cp1-branch-review.md`. When done, print
only "DONE" and the path.
