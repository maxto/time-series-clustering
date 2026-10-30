# Pipeline course: first pass design

Owner decisions of 2026-10-30. Replaces the narrative lesson plan of the redesign for the rest of the course.
Spike approved by the owner on the home and on lesson `dtw`, which is the reference sample of the format.

## Intent

An operational, easy mini-course in the spirit of the original README list: given series of a certain kind and a
goal, which measure, which clustering algorithm, how to validate. Audience: data scientists and quantitative
practitioners. Technical and academic register, correct terminology, formulas and example figures are required.

## Passes

First pass: a base version of every lesson. Then lesson by lesson from the first to the last, raising the level.
Lessons are drafts in the preview until reviewed. Code comes last and no lesson has a `## Code` section or pointers
to reference code until then.

## Pipeline

Define, Measure, Group, Validate, Recipes. These are the modules of `content/_course.md`.

## Card format

Blocks, in order, with these titles unless the lesson needs a better one:

1. `## One line`: one paragraph, what it is and the decision it hides.
2. `## What it measures`: short, with the example figure when there is one.
3. `## When to use it`: two lists, `Use it when:` and `Avoid it when:`.
4. `## Definition`: the formula in display math, plus a `::: deep` block for what a practitioner can skip.
5. One section for the lesson's real decision (for DTW: `## The window`).
6. `## Which clustering algorithm`: which algorithms accept this measure and why, and which do not.
7. `## In finance`: see below.
8. `## Common mistake`: one paragraph.

A lesson that covers a family compares its members briefly (formula and one line each) and goes deep on the
main ones. Lessons on Group and Validate adapt the titles: the same order, but what is described is an algorithm
or an index.

Keep each lesson short: `content/05-dtw.md` without its finance block is the upper bound.

## In finance

Academic terms. Starts with what the method answers and, where it does not fit a question, names the alternatives
(several, never just one). Then two lists:

- `Empirical applications:` what was found in the literature, across financial instruments. An abstract is enough
  for these references, and each one must be coherent with the topic. Say what the study did and found, plainly.
- `Limitations in financial time series:` each limit stated by a source actually read. No inference of ours: a limit
  with no source stays out. State the scope of the source when it is not financial.

Never list what was not found.

## References

Light: `Author (year)`, with a plain Markdown link when an exact one is known (DOI, arXiv, an open copy that was
read), just the name otherwise. No `[@key, locator]` citations. For whoever developed a method or ran a study. No
survey cited for a general claim. Never get around a paywall or a bot check.

## Recommended validity indices

Out for now. Lessons say what each index needs and assumes, and do not rank or recommend.

## Claims

Every factual claim is checked against a source. A claim that cannot be confirmed stays out. Do not suppose.
