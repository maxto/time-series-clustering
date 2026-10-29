### Cross-task findings

Reviewed `196e416..ef52f00`. The numerical pipeline is consistent across the current Python, R, figures, numbers and lesson text. The Task 8 Important finding is **ADDRESSED** at `content/05-dtw.md:87`: the divergence statement now preserves the ground-cost qualification.

Independent verification in this pass:

- **30 Python reference tests passed**, with bytecode/cache output disabled and Numba JIT disabled. This was the reference suite, not the eight build tests.
- Ran the existing R checks with its parity-file read redirected in memory to a freshly computed Python matrix. R 4.6.1, dtw 1.23.3, **worst absolute difference 0**, including its independent package comparisons and hand cases. No parity file was rewritten.
- In-memory regeneration exactly matched all six generated SVGs, `numbers.json`, and all seven preview SVGs. Content, SVG and 53 math-token validations returned no errors.
- Freshly rendered home and both lesson pages exactly match saved `dist/`. The manifest contains 15 entries, only lessons 1 and 5 published. Static resolution of internal links and referenced page assets under `/time-series-clustering/` found no missing targets or prefix escapes.
- Lockfile source skim found PyPI plus the local editable package, and npm registry downloads. No unexpected source host.

I inspected supplied renders. I did not run a new browser session, the full build-test suite or `npm test`, which writes build and screenshot artifacts. Final-tree browser, contrast and keyboard evidence remains part of Task 9, after the fixes below.

#### Critical

None found.

#### Important

1. **The owner screenshot packet contains superseded content.** Current `content/01-same-series-different-questions.md:8` and line 115 include the accepted corrections, but `tests/output/pages/lesson1-light-375-part9.png` still omits `A: shape` and displays the rejected broad finance claims. Older lesson 5 captures likewise predate its final wording correction. This is an evidence mismatch, not a regression in current HTML. **Fix:** complete the capture script required at `docs/superpowers/plans/2026-10-28-pilot.md:298`, rebuild after the final edits, and regenerate the owner packet from that tree. Record the commit and distinguish full-page captures from viewport crops. Do not present these older images as final verification.

2. **The deferred visual and content items now affect the review target.** Small labels, faint alignment links, unqualified invariance wording and the overview taxonomy were reasonable to defer during implementation. They are visible in the pages the owner is about to judge. Apply the rows marked FIX below as one finishing pass, then perform the final checks at plan lines 296–298. This is a bounded finishing pass, not a redesign or an expansion of the fixture.

#### Minor

1. **The generic matrix helper hides properties the validity lesson says to check.** `code/python/tsc/group.py:30` computes only the upper triangle, mirrors it and supplies a zero diagonal. A direct probe with an asymmetric cost and nonzero self-cost fails `check_dissimilarity`, while the helper's output passes. Current Euclidean/SBD/DTW uses are unaffected, but extending this helper to raw soft-DTW or asymmetric measures would silently alter the input before the check at `content/05-dtw.md:134`. **Fix now:** document that `distance_matrix` assumes a symmetric measure with zero self-distance and does not verify those properties. State that other measures require evaluating both directions and self-comparisons before validation. Leave a generalized implementation to the labs.

2. **AGENTS.md did not receive all settled rulings.** `AGENTS.md:9` and line 11 still mark existing content and figures tooling as planned. Line 46 retains the old colour rule, without the approved distinction between two-series and grouping figures. **Fix:** remove the obsolete planned markers and copy the settled colour wording from `global-constraints.md`. Keep `shots.mjs` marked planned until implemented. At closure, the controller should also reconcile `HANDOFF.md:3` with the actual branch and record this review in the shared notes. This advisor has not changed them.

### Deferred list triage

FIX means include the change in the single finishing pass. LEAVE means it does not block this pilot's owner review, not that the issue has disappeared.

| Item | Verdict (FIX BEFORE OWNER REVIEW / LEAVE) | Reason |
|---|---|---|
| Desktop figure size, `site/theme.css:92` | FIX BEFORE OWNER REVIEW | Cap the figure panel around 520 px, centred and responsive. The current 700 px column enlarges compact charts excessively. Inspect the overview separately after its label edits. |
| Small labels at 375 px, `site/theme.css:168` | FIX BEFORE OWNER REVIEW | Current 12 SVG units become about 10.4 CSS px. Start with 14 units, about 12.2 CSS px at the current mobile width. Reflow long legends and overview headers rather than letting them collide. Check actual rendered size after all sizing changes. |
| Light alignment links, `scripts/figures.py:182` | FIX BEFORE OWNER REVIEW | Pass `"ln-muted"` explicitly for these links. I recomputed 2.04:1 for the current colour on white versus 4.54:1 for the muted line colour. These links carry the mechanism, unlike decorative baselines. |
| DTW grid axis cues, `scripts/figures.py:236` | FIX BEFORE OWNER REVIEW | Label the side traces `mon, i ↑` and `sat, j →`, with room reserved for the labels. Readers should not need the paragraph to discover the reversed vertical time direction. |
| DTW side-trace half-cell offset, `scripts/figures.py:234` and line 239 | FIX BEFORE OWNER REVIEW | Place mon sample i at `cy(i)` and sat sample j at `cx(j)`, matching the path and cell centres. Align the displayed time ticks with the chosen sample convention. |
| Ineffective `stroke-width="1.5"` attributes, `scripts/figures.py:235` | LEAVE | CSS deliberately wins with 2 px. Current rendering is coherent. A thin-line class or attribute cleanup can wait unless the sizing pass exposes a visual problem. |
| Display-math overflow, `site/theme.css:88` | FIX BEFORE OWNER REVIEW | Keep the readable split recurrence. Add `.katex-display { overflow: auto hidden; }` as documented by [KaTeX](https://katex.org/docs/issues#css-customization), and check a deliberately wide display at 375 px. The outer `.math` already scrolls. Verify both ends and tall symbols are reachable, not just page width. |
| Overview box labels and conceptual levels, `content/figures/overview.svg:32` and line 39 | FIX BEFORE OWNER REVIEW | Use “Sequence inputs” and “Explicit representations”, wrapping headers if needed. Add a visible sentence that these are navigation families, not mutually exclusive conceptual levels, and update `<desc>`. Kernels can imply feature mappings, as the [survey's kernel section](https://arxiv.org/html/2412.20574v1#S7) explains. |
| SBD shift-tolerance wording, `content/01-same-series-different-questions.md:78`, line 84 and line 96 | FIX BEFORE OWNER REVIEW | Replace the unconditional “changes it little” with “SBD searches over global shifts. With finite windows and zero padding, boundary and overlap changes can still affect the distance.” Say the fixture's grouping follows shape despite the shift. Qualify the chip to “global shift (tolerated)” and the prose accordingly. This follows the retained-overlap numerator and full-norm denominator in the [SBD definition, §3.1](https://www.paparrizos.org/papers/PaparrizosSIGMOD15.pdf). |
| KShape pointer, `content/01-same-series-different-questions.md:9` | FIX BEFORE OWNER REVIEW | Remove it from this lesson's code list, or explicitly label it as a related centroid method. It does not reproduce the average-linkage pipeline. [Official KShape API](https://tslearn.readthedocs.io/en/stable/gen_modules/clustering/tslearn.clustering.KShape.html). |
| Raw soft-DTW has no final root, `content/05-dtw.md:85` | FIX BEFORE OWNER REVIEW | Add “This smooths the accumulated cost, without the final square root used for our DTW distance.” This prevents readers carrying the course's rooted convention into negative raw losses. [Cuturi–Blondel, Algorithm 1](https://proceedings.mlr.press/v70/cuturi17a/cuturi17a.pdf). |
| Equal-length qualification at w=0, `content/05-dtw.md:54` | FIX BEFORE OWNER REVIEW | Begin “For equal-length series, with w=0…”. Unequal lengths instead have no admissible path under this band convention. |
| Singleton silhouette convention, `content/05-dtw.md:134` | FIX BEFORE OWNER REVIEW | Add “A singleton receives silhouette zero.” This completes design §5.2 and matches `code/python/tsc/validity.py:40`. Current groups have six members each. |
| Notes below pager on mobile, `site/page.html:24` and `site/theme.css:105` | FIX BEFORE OWNER REVIEW | Put the pager after the notes in the mobile reading order. One straightforward implementation moves it after `aside` in `.wrap`, constrains it to grid column 1 on desktop and removes any resulting excess row gap. Keep the desktop margin layout. |
| Light cards/pager white versus mockup, `site/theme.css:97` and line 106 | LEAVE | Explicitly accepted by the controller for the owner to judge. Do not undo a settled visual choice during cleanup. |
| Global-shift fixture instead of local warp, `scripts/make_fixtures.py:66` | LEAVE | The approved pilot needs this fixture and lesson 5 describes mon/sat as a global shift. Preserve the frozen CSV. |
| AGENTS layout and colour-rule drift | FIX BEFORE OWNER REVIEW | Apply the two documentation corrections in Minor 2 above. |
| DTW path tie-break test, `code/python/tests/test_distances.py:80` | LEAVE | Current tie ordering is explicit and figure regeneration is exact. I also checked the diagonal all-zero tie case. Propose additional retained cases for the later owner-selected test pass. |
| `w=True` / `np.int64` tests, `code/python/tsc/distances.py:42` | LEAVE | Focused checks confirm bool rejection and integer-scalar acceptance. No current defect or need to expand the approved test set now. |
| Tiny negative SBD roundoff, `code/python/tsc/distances.py:113` | LEAVE | No affected fixture result. Define numerical tolerance or clipping deliberately before expanding SBD validity examples, rather than silently changing the reference kernel in visual cleanup. |
| Helper type hints, including `load_demand` | LEAVE | Teaching-code polish, without a current contract or output failure. |
| Empty-file `load_demand` error, `code/python/tsc/group.py:23` | LEAVE | The frozen fixture is nonempty. Improve the error when the loader becomes a general lab interface. |
| NaN reported as “not symmetric”, `code/python/tsc/group.py:50` | LEAVE | It rejects invalid input, albeit with a poor diagnostic. Current matrices are finite. |
| Cramped test one-liners, `code/python/tests/test_validity.py` | LEAVE | No reader-facing consequence. The prose punctuation rule does not ban Python syntax. |
| Stale Python parity CSV, `code/r/check_dtw.R:67` | LEAVE | Final verification must run the documented producer immediately before the R checker. My fresh in-memory parity check avoids relying on the saved CSV. Hashing/versioning the exchange file can wait. |
| Parity diagonal assumed zero, `code/r/check_dtw.R:50` | LEAVE | Correct for this DTW kernel, whose nonnegative costs admit a zero self-path. It is not a generic-measure validation recipe. |
| R accepts `w=4.0`, `code/r/distances.R:50` | LEAVE | Ordinary R numeric literals are doubles. Preserve idiomatic acceptance of integer-valued numeric widths, rather than forcing `4L`. Clarify this language distinction when documenting lab APIs. |
| E2E manifest whitespace/CRLF, `tests/e2e.mjs:142` | LEAVE | The current manifest is parsed correctly. This causes false failures for alternative formatting, not a false success for the present navigation. |
| `numbers.json` root/type checks, `scripts/buildlib/content.py:171` | LEAVE | Current generated input is a valid object of strings. Harden malformed-root diagnostics before external content ingestion, without blocking owner review. |
| SVG viewBox numeric validation, `scripts/buildlib/svg.py:51` | LEAVE | All seven current SVGs have valid numeric dimensions. Validator completeness is later hardening. |
| SVG external marker URLs, `scripts/buildlib/svg.py:19` | LEAVE | Current marker references are local. Restrict future markers to local fragment references, but no present page depends on an external resource through this path. |
| Pages branch/content prerequisite | LEAVE | Expected deployment gate. No push, rename or Pages activation is part of this review. Keep the owner's separate approvals. |

After editing the generators, regenerate their SVGs, numbers and previews rather than hand-editing generated files. Complete the existing Task 9 final-tree checks and contrast table. The previously observed clipping warrants its focused regression check, while the LEAVE rows do not authorize an expanded test project.

### Assessment

**Branch:** Ready for owner review after the listed fixes

**Reasoning:** The pilot's numerical contracts and current generated artifacts agree, and the previous Important content findings are closed. Apply the bounded reader-facing fixes, refresh the stale owner images and complete final-tree visual/browser verification before presenting the pages.
