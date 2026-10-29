# Codex review request: checkpoint 2 plan

You are an adversarial reviewer. Review the implementation plan
`docs/superpowers/plans/2026-10-29-redesign-checkpoint-2.md` (lesson 5 end
to end: JavaScript DTW kernels with parity, live DTW figure, deep-dive
blocks, lesson 5 content and sources) against its spec
`docs/superpowers/specs/2026-10-28-redesign-design.md` (sections 1.1, 4.1,
4.3, 6, 6.1, 6.2, 8, 9, 10) and the repo as it is on branch `redesign`
(`AGENTS.md`, `code/python/tsc/distances.py`, `scripts/figures.py`,
`scripts/build.py`, `scripts/buildlib/content.py`, `site/course.js`,
`tests/e2e.mjs`, `tests/test_build.py`).

The owner decisions listed at the top of the plan are settled (deep-dives
yes, summary lines no, soft-DTW out of lesson 5, scoring section shortened
to the silhouette, parity edge cases window 0 / no window / ties). Do not
reopen them, but do flag anything in the plan that contradicts them.

Look for:

1. Spec requirements for checkpoint 2 with no task, or a task that
   contradicts the spec or `AGENTS.md`.
2. Steps an implementer cannot execute unambiguously (missing names,
   formats, values), or steps that hide a design decision.
3. Tests whose expected values are not independent of the code under test,
   or checks that would pass while the feature is broken.
4. The live figure contract: state, invalid states, accessibility, static
   fallback, width redraw, rendering budget. Is anything unsafe or
   untestable as written?
5. The deep-dive syntax and rules: conflicts with the existing parser
   (`markdown-it-py` commonmark, citations, prose rules, heading ids,
   search index).
6. Task 5 (content and sources): is the sourcing procedure complete and
   checkable? Are the expected sources right for the claims, in their
   standard form?
7. Ordering and dependency problems between tasks.

Write your full answer to
`docs/research/2026-10-29-codex-plan-cp2-review.md`: findings numbered,
each with severity (Critical, Important, Minor), the plan location, the
problem, and a concrete fix. End with a one-line verdict. Do not edit any
other file.
