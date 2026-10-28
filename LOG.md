# LOG — time-series-clustering

## 2026-10-28 · Project set up, course designed, look drafts

Session run from `~/projects/personal/maxto-brain` (the owner's personal
brain), then moved here. No commits yet. HEAD `be77989`.

**Done**

- Cloned `maxto/Time-Series-Clustering` to
  `~/projects/personal/time-series-clustering/` (branch `master`).
- Codex taxonomy review (copied to
  `docs/research/2026-10-28-codex-taxonomy-review.md`) and Codex design
  review (`docs/research/2026-10-28-codex-design-review.md`).
- Design written: `docs/superpowers/specs/2026-10-28-course-design.md`,
  with the design review folded in.
- Three look drafts in `.mockups/` (git-ignored), generator
  `.mockups/gen.py`, preview server on port 60610.
- `.gitignore` added (`.mockups/`, `.superpowers/`).

**Verified**

- `TSclust` and `TSdist` archived on CRAN 2026-01-16 (CRAN pages).
- GitHub repo names are case-insensitive: lowercase web and raw URLs
  resolve to the repo (curl, `gh api`).
- `gh search prs --owner=@me --state=open`: no open PRs.
- Drafts 1 and 2 rendered correctly in headless Chrome at 1280 px after a
  font-fallback fix. Draft 3 not screenshot-checked (timeout).

**Decisions (all approved by the owner unless marked)**

- Mini-course, English only. Rejects the bilingual schema of
  ai-one-token-at-a-time: readers of this topic read English.
- Concepts first, code second. Core = distance measures and validity
  indices. Algorithms get one shorter lesson on which algorithm fits which
  geometry.
- Validity indices are a full module organised by the geometry they
  assume, not an inventory (rejects Codex's proposal to shrink them to a
  note).
- Build approach A: reuse the ai-one-token-at-a-time engine, adapted.
  Rejected: Quarto (textbook look, theme work), plain Markdown without a
  site (no navigation, weak first impression). Data figures generated from
  the same fixtures as the code, concept figures hand-made SVG.
- Two running examples: synthetic electricity-demand profiles (main),
  finance co-movement via return correlation on a shared window
  (Mantegna, López de Prado), synthetic factor-model fixture plus optional
  real-data download script, limits stated.
- Code scope: seven from-scratch representatives with Python/R parity,
  package examples only where both languages have the method, missing
  counterparts marked as gaps.
- Rename the repo to lowercase `time-series-clustering` before enabling
  Pages (remote action, needs its own go-ahead).
- Visual style: minimal, flat, 2D, low density, not identical to the other
  course. Direction still open (three drafts).
- Proposed, not decided: licence MIT code + CC BY 4.0 content, the pilot
  scope in design section 9.
