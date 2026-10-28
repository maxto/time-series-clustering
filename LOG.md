# LOG — time-series-clustering

## 2026-10-28 · Pilot plan reviewed and approved, Codex hooks fixed

**Done**

- Codex adversarial review of the pilot plan:
  `docs/research/2026-10-28-codex-pilot-plan-review.md` (12 points,
  verdict "keep the approach, correct the contracts"). All 12 folded into
  `docs/superpowers/plans/2026-10-28-pilot.md`, none rejected. Real errors
  it caught: wrong no-window call to the DTW reference packages, an SBD
  delayed-series test that would fail (0.0646 > 0.05), `fcluster`
  `maxclust` giving at most k groups with 1-based labels, bare `python3`
  instead of `uv run`, a Pages workflow that would not install the new
  dependencies.
- Codex hooks failing with exit 127: Codex sessions started before the
  16:49 cleanup of `~/.codex/hooks.json` still held hooks calling
  `/home/maxto/opt/ai-memory-2.6.0/ai-memory`, which was removed. Fix:
  restart. This project's Codex was restarted (`/exit`, `codex`) on the
  owner's ok. The other projects' sessions were reported to the Claude
  session in `~/infra/agents`, which owns the Codex config (message sent
  in its pane, received).

**Verified**

- Codex silhouette hand case recomputed by hand: point scores 1/2, 2/3, 0,
  mean 7/18.
- After the restart a one-word prompt to Codex ran with no hook error.

**Decisions (approved by the owner, 2026-10-28, "procedi con tutto")**

- New libraries: markdown-it-py + mdit-py-plugins, KaTeX, Geist,
  dtw-python and R `dtw` (test references only), scikit-learn, aeon, numpy,
  scipy. None was in the resources catalog except markdown-it-py.
- Quizzes dropped from the pilot (revisit after the owner's review).
  Replaces the old engine's three-question quiz per module.
- One static page per lesson. Replaces the single-page app of the other
  engine. Why: longer lessons, shareable URLs, margin notes.
- All proposed edge-case test groups A to F kept (DTW inputs, DTW path
  structure, SBD zero norm and delayed pulse, silhouette edge matrices,
  too few clusters, build parsing and TeX errors).
- Numbers quoted in lessons are generated (`numbers.json`) and substituted
  by the build. Rejects copying numbers by hand (Codex point 11).
- Execution: subagent-driven (proposed by Claude as PM, per the global
  rule that Claude splits work across subagent workers).

## 2026-10-28 · Look chosen, design approved, pilot plan

Session in this project (Orca tab with Codex and a bash pane). HEAD
`043259a` at start, no new commits yet.

**Done**

- Full Orca setup opened: Codex on the right, bash below it.
- Three colour variants of the Notebook draft, then the chosen one with the
  exact brand tokens, light and dark, theme toggle:
  `.mockups/gen_palettes.py` -> `notebook-a-white-blue.html`,
  `notebook-b-cool-grey.html`, `notebook-c-white-sage.html`,
  `notebook-brand.html`, `palettes.html` (all git-ignored).
- Design section 6 and status updated. Plan written:
  `docs/superpowers/plans/2026-10-28-pilot.md` (9 tasks, pilot only).
- Plan sent to Codex for an adversarial review
  (`docs/research/2026-10-28-codex-pilot-plan-request.md`).

**Verified**

- Original drafts and `.mockups/index.html` unchanged after the new
  generator ran (md5 checksums).
- Headless Chrome screenshots at 1280 px: the three variants, the brand
  page light and dark. A dark-theme bug (legend colours fixed to light)
  was found and fixed, the fix checked in the generated HTML.
- Headless screenshots hang intermittently while Google Fonts load. Not a
  course issue: the plan self-hosts fonts.
- The earlier `LOG` entry says "No commits yet": it was written just before
  commit `043259a`. Harmless, noted here as the correction.

**Decisions**

- Approved (owner): Notebook layout (single reading column, margin notes).
  Rejects Atlas (dark, map-first home, close to maxto.io) and Field guide
  (catalogue of cards). Why: lessons here are longer than in
  ai-one-token-at-a-time, a reading column with margin notes keeps them
  light.
- Approved (owner): white and blue brand palette, the same tokens as
  ai-one-token-at-a-time. Rejects the cool-grey and sage variants. Why:
  the owner's courses share one palette. Replaces "not identical to the
  other course" for colour: layout and type still differ.
- Proposed: Geist + Geist Mono, self-hosted (different type from the other
  course, no runtime CDN).
- Approved (owner): dark tokens are provisional, the owner is reworking the
  brand's dark palette. Swap later in one place.
- Approved (owner): site on GitHub Pages,
  `https://maxto.github.io/time-series-clustering/`, a custom domain may
  come later. The address lives in one constant in the build.
- Approved (owner): design approved with the go-ahead to start production.
- Proposed, waiting on the owner (plan header): new libraries, quizzes
  dropped, one page per lesson instead of a single-page app.

**HANDOFF reconciliation:** "owner picks the look", "owner approves the
design" and "implementation plan" are done (this entry). "Push of the
first commit" is merged into the remote-steps item. "Project rules file"
moved into Task 1 of the pilot plan.

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
