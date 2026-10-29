# Request to Codex: adversarial review of the redesign design

From Claude (PM). Review only: do not edit repo files or change git state.
Read-only commands and web lookups are fine.

## What to read

- The design under review:
  `docs/superpowers/specs/2026-10-28-redesign-design.md`
- What it amends: `docs/superpowers/specs/2026-10-28-course-design.md`
- Project rules and current engine: `AGENTS.md` (branch `pilot`, HEAD
  `0575db2`, code under `scripts/`, `site/`, `code/`, `tests/`)
- Why each decision was taken: `LOG.md`, top entry "Pilot review:
  redesign direction"
- Reference mockup (throwaway, git-ignored):
  `.mockups/course/index.html`. Its map content and sector judgements are
  a draft, not reviewed.

## Context

The owner reviewed the pilot and asked for a richer learning course:
worked examples and exercises, a map of the field from the README
catalogue, three recurring sectors (energy, finance, weather), sources per
paragraph, navigation and search like ai-one-token-at-a-time, live
figures. The owner chose the explorable-essay format and to extend the
pilot engine (no framework, no in-browser Python). A builder check already
ran: its seven questions are settled in the text as "Claude's call".

## What to do

1. **Holes and contradictions:** places where a builder must guess and a
   wrong guess is costly, contradictions with the first design or
   `AGENTS.md` that the redesign does not resolve explicitly.
2. **Risks to correctness:** the live JavaScript kernels and their parity
   with Python, the static versus live figure versions, draft map content
   and the deployable-build gate, sector judgements, the sources registry
   and checking script.
3. **Scope of step 1:** is it one reviewable step, or should it be split?
   What would you cut or defer without losing what the owner asked for?
4. **Learning design:** do worked examples, exercises with hidden answers
   and predict-then-reveal questions, as specified, serve the stated goal
   (a reader can choose a distance, method and index for their data)?
   Anything missing that a learning course on this topic needs?
5. **Claude's calls:** for each "Claude's call" in the text, agree or say
   what you would decide instead and why.

## Answer

Write to `docs/research/2026-10-28-codex-redesign-review.md`:

```
### Findings
#### Critical / Important / Minor (section, why, proposed change)
### Claude's calls
| Call | Agree / Change | Reason |
### Step 1 scope
### Verdict
**Design:** Ready for the owner after the listed changes | Needs rework
**Reasoning:** 1-2 sentences
```
