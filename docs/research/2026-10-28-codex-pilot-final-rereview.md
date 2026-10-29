### Item Verdicts

Scope: `ef52f00..0575db2`, the Task 9 report and the new screenshot packet.

| Item | Verdict | Evidence |
|---|---|---|
| Important 1: stale owner packet | ADDRESSED | `tests/shots.mjs:24` rebuilds before capture. `tests/output/shots/manifest.json` identifies `0575db2`, `tree_changed: false`, and 12 full-page images, all present. The lesson 1 mobile image now shows `A: shape` and the corrected finance paragraph. |
| Important 2: finishing pass and final checks | ADDRESSED | The changes below are implemented. `task-9-report.md` records the final-tree Python, R, regeneration, browser, contrast and keyboard checks, with outputs and capture details. I distinguish those reported checks from my independent verification below. |
| Minor 1: matrix-helper assumptions | ADDRESSED | `code/python/tsc/group.py:33` explicitly states the symmetry/zero-diagonal assumptions, explains mirroring and warns that other measures need both directions and self-comparisons before validation. Runtime behaviour is unchanged. |
| Minor 2: AGENTS accuracy | ADDRESSED | `AGENTS.md:7`, line 9 and line 13 describe the implemented files. Line 44 contains the approved two-series/group-colour distinction. The controller's shared-notes update remains a closure responsibility, not an implementer omission. |
| FIX: desktop figure size | ADDRESSED | `site/theme.css:94` caps and centres panels at 520 px. The supplied desktop captures show the intended scale. |
| FIX: small mobile labels | ADDRESSED | `site/theme.css:171` uses 14 units. At the 313 px mobile SVG width this is 12.17 CSS px. Matrix labels alternate rows at `scripts/figures.py:294`, and overview headers wrap. Inspected crops remain legible. |
| FIX: light alignment links | ADDRESSED | `scripts/figures.py:182` explicitly uses `ln-muted`, meeting the requested light-theme contrast. The dark-theme consequence is considered below. |
| FIX: DTW grid axis cues | ADDRESSED | `scripts/figures.py:241` and line 246 add `mon, i ↑` and `sat, j →`. Both are visible in the mobile capture. |
| FIX: side-trace half-cell offset | ADDRESSED | `scripts/figures.py:239` uses `cy(i)` and line 244 uses `cx(j)`. Lines 247–252 place time ticks at the corresponding sample centres, ending at 23:30. |
| FIX: display-math overflow | ADDRESSED | `site/theme.css:90` supplies the display overflow rule. The report documents both scroll ends and tall-symbol inspection. The actual lesson card remains intact in the supplied mobile capture. |
| FIX: overview labels and conceptual levels | ADDRESSED | `content/figures/overview.svg:32` and line 39 use the new headers. Lines 45–47 visibly qualify the boxes as navigation and mention implicit feature maps. `<desc>` agrees. |
| FIX: SBD shift tolerance | ADDRESSED | `content/01-same-series-different-questions.md:78`, line 84 and line 96 qualify boundary effects and distinguish the fixture's recovered partition from exact invariance. The line 7 chip says “tolerated”. |
| FIX: KShape pointer | ADDRESSED | Removed from the code list at `content/01-same-series-different-questions.md:9`. |
| FIX: raw soft-DTW has no final root | ADDRESSED | Explicitly stated at `content/05-dtw.md:85`. |
| FIX: equal-length qualification at w=0 | ADDRESSED | Present at `content/05-dtw.md:54`. |
| FIX: singleton silhouette convention | ADDRESSED | Present at `content/05-dtw.md:134`. |
| FIX: mobile notes before pager | ADDRESSED | `site/page.html:27` places the pager after `aside`. `site/theme.css:108` keeps it in desktop column 1. The lesson 1 mobile capture shows notes and code pointers before Next. |
| FIX: AGENTS layout/colour drift | ADDRESSED | Same correction as Minor 2. `AGENTS.md:31` also documents the now-implemented screenshot command. |

Independent verification: in-memory regeneration matched all six generated SVGs plus `numbers.json`, and all seven previews, byte for byte. Content, SVG and math validation returned no errors. I inspected supplied full-page images and in-memory crops around the alignment figure, cost grid, measure card, corrected notes and pager. I did not rerun the full suites or a browser session. The report's 38-test, R parity, e2e, keyboard and wide-formula measurements remain implementer evidence.

The wide-formula investigation also usefully corrects the earlier diagnosis: both horizontal ends were already reachable through the outer `.math` wrapper before the new rule. A claimed failing-before/passing-after regression would therefore be misleading. The hardening and actual lesson layout are acceptable.

### New Issues in the Fix Diff

No new Critical or Important issue found.

**Minor, non-blocking:** `tests/shots.mjs:28` inherits the strict manifest regex previously deferred in e2e. Unlike e2e, the screenshot script does not compare the parsed list with home links, so valid alternative pipe spacing can silently omit lessons from a future packet. The current packet contains all three pages in all four combinations, so this does not invalidate it. When addressing that deferred parser issue, include this script: trim pipe-separated fields and verify that every published entry is captured.

### Implementer concerns

1. **Dark alignment links: more prominent, but acceptable for owner review.** In the 1280 and 375 captures, connectors remain distinguishable from the thicker series lines, and the labelled mon/sat profiles and leaning alignment are readable. This is a visual preference to show the owner, not a reason to reopen the completed light-contrast fix. If the owner wants quieter links, the smallest targeted adjustment is a dedicated alignment class using the existing muted colour in light and `--line` in dark. Leave other `ln-muted` uses alone and regenerate the figure/previews.

2. **7.54:1 on the overview tint: passes the applicable requirement.** “Comparison” is a figure label, not body prose. The binding requirement is 4.5:1 for small figure text, so the report's 10:1 target misclassifies that row. Correct its target/pass annotation, not the approved palette. No page change is needed.

3. **“Finite windows”: accurate but unnecessarily ambiguous.** I supplied that wording. Here it means finite observation records, not a DTW window parameter. Optional minimal polish at `content/01-same-series-different-questions.md:78`: “Because these series have a start and an end, zero padding and changes in overlap can still affect the distance.” The surrounding zero-padding explanation makes the current meaning recoverable, so this does not block owner review.

Equal 14-unit sizes for `.t` and `.t-sm`, and the slightly smaller grid, introduce no observed readability problem. No mandatory page fix remains from these concerns.

### Verdict

**Fix wave:** Clean

All requested fixes are addressed. The current packet is suitable for owner review. The controller should complete the shared-notes closure and retain the distinction between independently checked artifacts and implementer-reported runtime evidence.
