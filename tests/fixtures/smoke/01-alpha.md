---
id: alpha
module: A
title: Alpha lesson
kicker: Engine check
sector: energy
lede: A fixture lesson that uses every feature the build supports, so the end-to-end test can find each one.
ignores: local timing, small shifts
keeps: level, scale
python: tsc.distances
r: distances.R
---

## One line

The build finds *sections* in parsed tokens, so a heading inside a code block stays code.

## Engine features

Inline math such as $d(x, y) = \sqrt{\sum_t (x_t - y_t)^2}$ sits inside a sentence.

$$
D(i, j) = c(a_i, b_j) + \min\{D(i-1, j),\ D(i, j-1),\ D(i-1, j-1)\}
$$

A fenced code block with a line that looks like a heading:

```text
## not a section
x = 1; y = 2
```

The next published lesson is [Gamma](lesson:gamma). The math is rendered by [KaTeX](https://katex.org/) at build time.

Jump down to [the subheading](#a-subheading).

The band of [@sakoe78, sec. II] limited the path to a strip around the diagonal.

![A small hand-made figure: series A in ink, series B in accent](figures/overview.svg)

### A subheading

More text with `inline code; with a semicolon` that the prose check skips.

## A second section

A second content section, so the order of sections is visible.

::: deep Library conventions differ
Packages disagree on the wavefront order of the recursion, so a result can shift by one cell, and the squared cost $c(a, b) = (a - b)^2$ is the one this course uses [@sakoe78, p. 44].

- the first convention keeps the root outside
- the other convention keeps the root inside
:::

## In finance

A finance note sits in the margin, next to the reading column. It cites a source too [@sakoe78, sec. II].

## Measure card

$$
\mathrm{ED}(x, y) = \sqrt{\sum_{t=1}^{n} (x_t - y_t)^2}
$$

The formula above is the distance this card names.

## Code

The two blocks below print the same value.

```python
print(1)
```

```r
cat(1)
```

## Common mistake

Reading a heading inside a code block as the start of a new section.
