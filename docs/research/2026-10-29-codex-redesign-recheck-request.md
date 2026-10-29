# Codex request: re-check of the amended redesign design

Date: 2026-10-29. Requested by Claude (PM) with the owner's go-ahead.

## Context

You reviewed `docs/superpowers/specs/2026-10-28-redesign-design.md` at
commit `0575db2`. Your review is in
`docs/research/2026-10-28-codex-redesign-review.md` (findings 1 to 10,
the "Claude's calls" table, the step 1 split). Claude has now amended the
design (uncommitted, see `git diff -- docs/superpowers/specs/`). The owner
answered two open questions on 2026-10-29:

1. Approved the narrow exception: a visibly labelled draft map in local
   preview builds only, release builds refuse draft items, lessons fully
   verified.
2. Reviews: full owner review after checkpoint 1 and after checkpoint 3,
   plus a short owner ok on the finance and weather fixtures at
   checkpoint 2 before they are frozen.

Project rules: `AGENTS.md`. Decision history: `LOG.md` (top two entries).

## What to do

A focused re-check, not a new full review:

1. For each of your findings 1 to 10 and each row of your "Claude's
   calls" table, say whether the amended text resolves it: **Resolved**,
   **Partly** (what is missing, one concrete change), or **Not resolved**.
   Cite the amended document by line.
2. List any **new** problem the amendments introduced (contradiction with
   `AGENTS.md`, `LOG.md` decisions or the first design
   `docs/superpowers/specs/2026-10-28-course-design.md`, an ambiguity a
   builder would have to guess, an over-specification that should be left
   to the builder). Severity: Critical, Important, Minor.
3. Verdict: ready for the owner's approval and the implementation plan,
   or not, in one line.

Do not edit any file except your answer. Static review only, no builds.

## Output

Write your full answer to
`docs/research/2026-10-29-codex-redesign-recheck.md`. When done, print
only "DONE" and the path in the chat.
