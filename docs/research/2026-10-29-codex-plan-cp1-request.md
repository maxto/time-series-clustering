# Codex request: adversarial review of the checkpoint 1 plan

Date: 2026-10-29. Requested by Claude (PM). The owner approved the
redesign design (commit `6055354`) and asked to proceed.

## What to review

`docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md` (uncommitted),
the implementation plan for checkpoint 1 of step 1 of
`docs/superpowers/specs/2026-10-28-redesign-design.md` (approved, read
section 1.1 first: no exercises in the first phase). Project rules:
`AGENTS.md`. Current engine: `scripts/build.py`, `scripts/buildlib/`,
`site/`, `tests/`.

## Questions

1. **Spec coverage:** does the plan implement everything checkpoint 1
   needs (design section 10, step 1.1, and the sections it relies on:
   4.1 to 4.4, 5, 5.1, 8, 9), and nothing the design defers (exercises,
   live figures, checkpoints 2 and 3)? List gaps and scope creep.
2. **Decisions a builder cannot make alone:** are file formats, syntax,
   interfaces and DOM contracts concrete enough for an implementer who
   sees only one task? Where would two implementers produce incompatible
   results?
3. **Tests:** do they follow the project rule (expected values from an
   independent source: the design, AGENTS.md, a hand computation, a real
   file)? Any test that mirrors the implementation, any important
   behaviour left untested, any test that cannot pass as written?
4. **Risky choices:** the review-record mechanism (paragraph hash in
   `_reviews.toml`, `scripts/review.py`), the release/preview split and
   its effect on `npm test` and the Pages workflow, `:target` no-JS
   cards, `search-index.js` from `file://`, the WCAG contrast check in
   e2e. Point out any that will break or that a simpler design would beat.
5. **Task order and size:** can each task be built and tested on its own
   in this order? Any task too large for one implementer?

Severity: Critical, Important, Minor. For each finding, the location
(task and step) and one concrete change. Then a verdict line: ready to
execute, or ready after the listed changes.

Static review only. Do not edit any file except your answer.

## Output

Write your full answer to
`docs/research/2026-10-29-codex-plan-cp1-review.md`. When done, print
only "DONE" and the path in the chat.
