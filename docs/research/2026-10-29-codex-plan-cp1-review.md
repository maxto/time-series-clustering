# Checkpoint 1 plan: adversarial review

Static review at `6055354` on `pilot`, 2026-10-29. Read the approved design, especially section 1.1, the uncommitted plan, project rules, current build/parser/templates, test runners and smoke/lesson inputs. Opened the official HTML and WCAG sources linked below. No builds, tests, browser sessions or source-check scripts ran. Only this answer file was written.

The handoff's pre-closure HEAD is `9a2fa1b`; the expected approval commit `6055354` has since landed. The plan and request were already untracked. No unexpected state mismatch blocks this review. The later approved direction governs: exercises, transfer tasks and finance/weather fixtures stay deferred.

**P** = `docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md`. **D** = `docs/superpowers/specs/2026-10-28-redesign-design.md`. Locations below use their current line numbers.

## Critical

None identified. The engine choice and overall checkpoint boundary remain viable.

## Important

### 1. Task 1's migration cannot satisfy its own schema

**Location:** Task 1, steps 4–6 and 8, P:106–131.

The new schema puts Common mistake last, but the migration never moves it after finance/measure/code in smoke alpha or either real lesson. Their current files put it before those blocks. Lesson 1 also receives an introductory `## Twelve days of demand` immediately before its existing heading of exactly that name (`content/01-same-series-different-questions.md:19–23`), conflicting with the new duplicate-id rule. The retained e2e test still requires gamma's `.card.check` (`tests/e2e.mjs:129`), although the plan removes that block and permits only `.lesson-body` selector changes at this step.

**Change:** give Task 1 a complete migration list: move Common mistake to the end in every affected file, name the new introduction `The comparison question` or another unique title, and replace gamma's Check assertion with an assertion on its migrated validity section. Update the corresponding AGENTS schema in this same task, as D:255–257 requires, rather than waiting until Task 7.

### 2. Tasks 2–6 depend on rendering and runner changes scheduled later

**Location:** Task 2, steps 1/3/6, P:170–174, 207–237; Task 3, steps 1/6, P:286–290, 339–341; Tasks 4–6 PASS commands; Task 7, P:499.

Task 2 asserts a rendered `#src-sakoe78` entry, but that renderer is assigned to Task 4. Task 3 asserts `.draft-banner`, also assigned to Task 4. More seriously, `package.json:7` still executes the real release build before e2e. Once Task 3 imports drafts, every later `npm test` stops there. Adapting only `e2e.mjs` in Task 7 does not remove that package-script precondition. Task 4's intended red run would fail at the release gate, not its new DOM assertions.

**Change:** make Task 2 render its minimal cited-source list, and Task 3 render the preview banner and adapt both `package.json` and the e2e entry point immediately. For example, let `npm test` invoke the runner, which freshly builds smoke in release mode and real content in preview mode before checking each output. Keep `npm run build` as release. Do not read an old `dist/` as the real test target. Task 7 should broaden coverage, not repair the basic runner.

### 3. Citation matching is not a complete review gate, and the recorder renews too much

**Location:** Task 2, interfaces and step 3, P:161–162, 210–224.

Only citation occurrences require a record. Remove the citation from a changed paragraph and there is nothing to match, so the stated gate no longer catches that change. Newly added uncited claims have the same gap. Meanwhile `review.py --lesson … --key …` stamps every occurrence of that source, including other changed paragraphs the reviewer may not have read. Printing them while writing records is not review. These are ordinary editing failures, not malicious-input scenarios.

**Change:** add one reviewed lesson-content fingerprint covering the lesson text and its citation inventory, alongside the located citation records. A changed or removed citation then invalidates the lesson review. Make recording target the exact approved fingerprint/occurrence rather than bulk-renewing all uses of a source. Editorial review still decides which statements need support. Explicitly require the second-model review before recording completion. This need not attempt automatic scientific claim detection.

Checkpoint 1 may retain unchanged pilot prose while source completion continues in checkpoints 2/3, but say so explicitly and identify that retained baseline. Do not describe one new citation in lesson 5 as verification of both migrated lessons. All newly written claims and the checkpoint's worked example must follow D:68–71 and 328–329.

### 4. Checked map content has no review identity or invalidation mechanism

**Location:** Task 3, interfaces and steps 3–4, P:261–264, 320–332.

An item is accepted as checked if its fields are non-empty and one source has a locator. Its Python/R mappings, individual conditions and sector recommendations need no associated support record. Editing those fields leaves `status = "checked"` untouched. That implements a completeness flag, not D:331–347's reviewed factual fields and substantive-edit invalidation. `Tag` has no way to identify which source supports a condition. Separately, assigning every item its branch survey restores the automatic fallback explicitly rejected at D:489–492. An empty locator marks pending verification, but should not present an unconfirmed work as supporting the claim.

**Change:** extend the review-record contract to map items/fits with a fingerprint covering their factual fields, named support locations for those fields and reviewed status. A changed fingerprint makes the item draft. Permit explicit pending/candidate sources in preview, displayed as such, and no claimed supporting source where none has been identified. Use these records for checked smoke data too. Keep full map research in design step 2.

### 5. Citation extraction and hashing are not specified enough for matching records

**Location:** Review Focus 2; Task 2, P:161, 188–195, 209–224.

“Whitespace-normalised source text of the block” leaves the boundary unresolved: a list item's entire contents or its paragraph, a caption or its image syntax, raw `{{n:key}}` or its substituted value. The current parser substitutes numbers before parsing (`scripts/buildlib/content.py:246–247`) and moves caption tokens into `tsc_figure.meta` (`:361–375`). A recorder and validator implemented separately can hash different text, or miss changed displayed numbers. Table-cell coverage is promised, but the parser uses the CommonMark preset with no table enablement (`:45–48`). The proposed tests cover a list only.

**Change:** specify one canonical extraction function shared by build and recorder, including container precedence, caption traversal, number-substitution stage and how referenced source identity changes invalidate approval. Keep fixed literal text/digest fixtures in tests, computed independently of this function. Either explicitly enable and document tables or remove the unsupported table-cell promise from this checkpoint. Add the caption/list cases to the owner's proposed test list.

The recorder-then-build test is useful integration coverage, but both sides using the same wrong extraction cannot serve as the independent oracle for the fingerprint contract.

### 6. The map-card fallback nests interactive controls and conflicts with the DOM contract

**Location:** Task 4, DOM contract and step 3, P:365, 371, 384; Task 5, P:413, 423.

The card contract specifies `button.chip`, then asks for an anchor inside that button for no-JS navigation. HTML buttons cannot contain interactive descendants. The [HTML button content model](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) explicitly disallows this. `hidden`, `:target` and JavaScript-expanded state also become competing ways to control visibility. CSS can override hidden display, so the specific problem is conflicting state ownership, not a claim that `:target` can never work.

**Change:** use a native `details`/`summary` card and style the summary as the chip. Give the details a stable target id for search and enhance its existing open state. This meets the design's native-disclosure direction, works without JavaScript and avoids separate anchor/button fallbacks. Update Tasks 4–6 selectors together.

### 7. Map behaviour has no concrete data or filter-control handoff

**Location:** Task 3 interfaces, P:261–264; Task 4 DOM, P:365; Task 5, P:423–434.

The Python atlas contains tags, conditions, questions and fits, but the HTML contract exposes only `data-item` and `data-sector`. No embedded data format or filter controls are assigned. Task 5 cannot derive the full filtering rules from the declared DOM without parsing prose or inventing its own serialization. A finance sector card contains two questions but has no question-specific action, although D:205–208 requires sector-and-question selection. The single-tag test also leaves the required all-selected-tags matching rule unspecified in the implementation steps.

**Change:** define one serialized atlas payload or explicit data attributes in Task 4, with stable item/question ids and condition text, and specify the matching controls there. Require one action per sector question, AND semantics for multiple ignore tags, and mutual exclusion between sector mode and the other filters. Task 5 should consume that interface directly. Keep source formats and public ids consistent in a small checked-in specimen shared by the tasks.

### 8. Navigation targets and search-layer ownership remain contradictory

**Location:** Task 4, P:363; Task 5, P:419, 434; Task 6, P:459, 464, 473.

Literal `#map` and `#sectors` links in every page's contents point nowhere from a lesson or sources page. Planned lesson results have no defined destination. Map search also needs a defined open-card target. Finally, search input `#q` is outside `nav#contents`, while the drawer traps focus inside that nav. The required “open search while drawer remains open” test needs an explicit transition that suspends the drawer trap and permits focus in search. Escape ordering alone does not establish that.

**Change:** define root-relative home anchors (`<root>index.html#map`, `#sectors`), stable home-index anchors for planned entries, and map-card search targets that open the target disclosure. Give `course.js` one small shared layer controller: entering search suspends the drawer trap, closing search restores its prior state/focus, and the next Escape closes the drawer. Define script order so `TSC_SEARCH` is available before initialization. Keep the plain generated script approach for `file://`; no fetch or module loader is needed.

### 9. The contrast algorithm can pass unreadable text

**Location:** Task 7, step 1, P:497; Task 4 finance styling, P:381.

WCAG's large-text thresholds are 18 **points** regular and 14 **points** bold, approximately 24 and 18.67 CSS px, not 18/14 px. The plan also gives no minimum for text outside its small/body categories. The [W3C contrast explanation](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) specifies those point thresholds and the separate large-text minimum.

“First opaque background” is insufficient for SVG text over sibling rectangles, semi-transparent layers or text whose painted colour is SVG `fill`, not CSS `color`. Scanning only visible initial text also omits closed cards, popovers and results unless the test explicitly opens them. Testing a parent paragraph's colour misses differently coloured descendant links.

**Change:** use a bounded role/state contrast matrix based on the design: body text and its inline children at 10:1, small text at 4.5:1, and an explicit threshold for other text. Verify actual SVG fill/background pairs separately, compose supported alpha layers, and explicitly open the named interactive states. Back the luminance helper with published/hand-computed values rather than its own output. Do not claim a generic DOM scan proves every painted combination.

Also give the finance surface a dedicated `--fin-bg`: applying `background: var(--ink)` and then rebinding local `--ink` to the light foreground can make the background resolve to that foreground too. Keep the background independent of the figure/text overrides.

### 10. Required static controls are missing from the task contracts

**Location:** Task 4 DOM, P:362–364; Task 5 behaviour, P:415–434.

The design requires code copying (D:234–235), but the plan defines neither a copy button nor its behaviour/check. Reading progress has an element but no update semantics or implementation step. The code schema permits zero or one language, while the renderer always promises two tabs and two blocks. Sources-page entries use `Source.label`, which deliberately abbreviates authors, but the design asks for source authors and full bibliographic details.

**Change:** add a small shared component contract: copy the active language's exact code, show only tabs for languages present, define scroll-based reading progress, and show the full author list in source details while keeping abbreviated inline labels. Include these in Task 5's acceptance criteria and the owner's proposed test list. These are checkpoint-1 features, not live numerical work.

## Minor

### 11. New policy choices are presented as already mandated

**Location:** Global Constraints, P:15, 25; Task 1 step 4, P:110; Task 2 step 3, P:211.

Rejecting repeated heading slugs changes the existing suffix policy in `AGENTS.md:22` and `content.py:264–278`. Reserving structural ids is sensible, but ordinary repeated headings need not become errors. Applying prose punctuation bans to exact bibliographic titles/venues can require corrupting a real title or refusing a valid source. “Edge cases beyond the ones listed here” also treats this plan's selected cases as approved before owner selection.

**Change:** preserve suffixing for ordinary headings while protecting structural ids, exempt verbatim bibliographic metadata from prose style checks, and label the listed new edge cases as the batch proposed for owner approval. Do not restore the deferred exercises or introduce extra scientific variants.

### 12. Source-check outcomes need an honest completion state

**Location:** Task 2 step 4, P:228; steps 5–6, P:232–237.

An SSRN/author URL is marked `manual` merely because the script cannot check it. That is “manual check needed”, not D:513's “checked by hand”. Exit 0 also permits every identifier to be unavailable, while later steps claim everything matched. Metadata comparison may legitimately encounter distinct preprint/publication years, so a mismatch needs inspection rather than title/year editing to force green output.

**Change:** separate `manual-needed` from an actual dated manual verification record, and make the completion packet enumerate unresolved/unavailable checks. Only report a source verified after identity and editorial support have both been checked. Keep network results outside the offline build's automatic scientific-verification claims.

### 13. Preview output exclusion should cover the release tree, not one exact path

**Location:** Task 3 step 3, P:320.

An equality check rejects `--dist <repo>/dist` but accepts `--dist <repo>/dist/preview`, placing preview content inside the directory Pages packages. The current builder already resolves paths (`scripts/build.py:171–172`), which should be retained.

**Change:** after resolution, reject preview output equal to or below the release directory before any output preparation. The existing workflow's sequential release-build/upload structure is otherwise appropriate. No workflow activation or deployment is needed for this checkpoint.

## Coverage, tests and execution order

**Coverage:** the plan broadly covers the requested shell, new lesson format, source registry, full-size draft map, sector cards, search and preview/release distinction. It correctly excludes numerical live figures, exercises and new finance/weather fixtures. The concrete omissions and contract conflicts are findings 3–10. Reusing the existing energy example is appropriate. Full map content verification stays in design step 2.

**Tests:** most proposed outcomes have valid independent authorities: the approved design, source fixture data, documented browser contracts and frozen lesson numbers. The major problems are timing and isolation, not a requirement for a much larger suite. Task 1's red phase searches for new headings and sector metadata before migration, and changes `add_to_lesson` before the old fixture has that heading. Helpers can fail or silently do nothing before the parser is exercised. Several negative tests merely assert exit 1, which can pass because the fixture is globally broken. Task 3's located-source test uses `paparrizos24`, whereas Task 2 only requires `sakoe78` in smoke, so it can pass for an unknown key rather than an empty locator.

Make valid v2 smoke input available to the new tests, retain a separate old-schema rejection specimen, and verify each mutated input was valid beforehand. Require the intended diagnostic, not just nonzero exit. Use an existing known source for the empty-locator case. Add the exact hash fixture described in finding 5. Present these corrections and the small additional coverage list to the owner before adding unapproved edge tests.

**Order and size:** retain the seven broad milestones, but split Task 2 into citation/review core and source-check/content verification, and Task 4 into shell/lesson rendering and atlas/sources rendering. Each currently crosses enough independent contracts to merit separate reviewable units. Move the minimal rendering and runner work earlier as in finding 2. Update AGENTS incrementally when schema and preview rules land. Tasks 5 and 6 can then build on explicit DOM/data/layer contracts. Task 7 should be verification and the owner packet, with fixes committed alongside every file changed rather than staging only `tests AGENTS.md` after CSS/JS fixes.

The screenshot timeout remains uninvestigated in HANDOFF/LOG. Existing launch flags are not fresh proof that screenshots now work. Treat browser/screenshot availability as a prerequisite to the relevant execution checks and report any failure separately from product correctness.

## Verdict

**Ready after the listed changes.**

**Handoff:** Claude should amend the task dependencies, review gate and DOM/data contracts before dispatching implementers, then obtain the owner's selection of proposed edge tests. No other open task is known to require retaining this chat. This review does not authorize merge, push, deployment or edits outside the requested implementation scope.
