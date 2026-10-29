# Codex request: review of the first verified citation (lesson 5)

Date: 2026-10-29. Requested by Claude (PM), checkpoint 1, Task 3.
Project rule (AGENTS.md): every factual claim is checked against a primary
source, every content change is reviewed by another model, and the
reviewer's claims are checked too. Design 1.1: a claim gets in when the
reference is found, read at the supporting point and confirmed.

## What to review

Commit `fd48aa8` on branch `redesign`: `git show fd48aa8 -- content/05-dtw.md content/_sources.toml`.

The new sentence, in `## The window is a decision` of `content/05-dtw.md`:

> The band $|i - j| \le w$ used here is the adjustment window condition of
> [@sakoe78, Sec. II-B, condition 4 (Eq. 8), p. 44], which restricts the
> warping path to a band around the diagonal.

Rendered, the citation reads "Sakoe and Chiba (1978)".

Copy read by the implementer (University of Illinois course page hosting a
scan): https://jeffe.cs.illinois.edu/teaching/compgeom/refs/Sakoe-Chiba-DTW.pdf
Passage they quote (p. 44): "Adjustment window condition:
|i(k) - j(k)| <= r, where r is an appropriate positive integer called
window length."

## Questions

1. Does the paper, at that location, support the sentence exactly? Is the
   locator correct (section, condition number, equation number, page)?
2. Is "restricts the warping path to a band around the diagonal" a fair
   reading, or does it say more than the passage?
3. The course allows w = 0 and "no window", the paper says r is a positive
   integer. Does the sentence imply anything wrong about that?
4. Metadata of `sakoe78` in `content/_sources.toml` (authors with given
   names, title, venue, volume, issue, pages, year, DOI): correct?
5. Is the hosted copy a legitimate copy to rely on (not to link: the site
   links only the DOI)?

For each: OK, or the exact change. Then a verdict line: approved as is,
approved with the listed changes, or rejected.

Do not edit any file except your answer.

## Output

Write your answer to `docs/research/2026-10-29-codex-sakoe-citation-review.md`.
When done, print only "DONE" and the path.
