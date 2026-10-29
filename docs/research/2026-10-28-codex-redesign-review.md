### Findings

Static review at `0575db2`. Read the redesign, original design, project rules, decision log, mockup and relevant engine/reference/test code. Checked the specific external documentation linked below. No builds, tests or browser checks were run. The pilot's reported green suite is supplied evidence, not a fresh validation of this redesign. Existing uncommitted notes and review copies were present before this review. HANDOFF's commit matches HEAD, but its brainstorming status has been overtaken by this request.

Below, **D** means `docs/superpowers/specs/2026-10-28-redesign-design.md`, **O** means `docs/superpowers/specs/2026-10-28-course-design.md`. Proposed amendments remain recommendations until adopted.

#### Critical

None identified that requires abandoning the chosen engine or explorable-essay format.

#### Important

**1. The sector requirement has been weakened without an explicit owner decision (§§2, 6, 10).**

`LOG.md:44–50` records energy, finance and weather in **every lesson**, through worked examples and exercises. D:43 says only “through the course”; D:251–252 and D:330–332 permit each sector to occur just once across the two pilot lessons. A builder can satisfy the redesign while missing the recorded decision.

**Change:** restore per-lesson coverage, or present the reduced requirement explicitly for owner approval. Add a small lesson-by-sector coverage table to the plan. This need not mean three equally long demonstrations: one developed example and two shorter transfer exercises can preserve the intended coverage. Finance coverage need not always be a separately styled finance block. Also distinguish the owner's request for examples in every lesson from D:148's stronger requirement for an example in every section, which risks repetitive filler.

**2. The map needs conditional claims before its schema is fixed (§5).**

D:185–204 reduces “ignores” and input compatibility to categories that the filters treat as unconditional. This can encode the wrong lesson even when the card contains a caveat. The draft already demonstrates the failure: `.mockups/course/index.html:883,886,920` classifies affinity propagation and agglomerative clustering under “any distance matrix”. Precomputed affinity propagation takes similarities; agglomerative compatibility depends on linkage, with Ward restricted to Euclidean geometry. These are documented distinctions, not merely wording preferences. [AffinityPropagation documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html), [AgglomerativeClustering documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html).

Sector fit has the same problem. The finance draft mixes contemporaneous co-movement with comparisons of dynamics via ACF/AR features (`.mockups/course/index.html:929`). O:172–188 explicitly distinguishes those objectives. A sector label alone cannot choose between them.

**Change:** each highlighted claim must name its task, representation/preprocessing and relevant settings. Distinguish exact invariance from conditional tolerance, and distance input from similarity input or required conversion. “Noise” and “different lengths” should not imply that a method erases those differences. The filter should mean “candidate under these stated conditions”, with the conditions visible before opening the card. Reuse the original validity requirements in O:137–158. Store source support for those conditions, not only for the item's name. This is a modest data-contract change, not a request for a general ontology or an upfront audit of every item.

**3. The draft-map exception and release gate need an explicit contract (§5).**

D:207–214 is sensible staging, but it does not currently preserve the literal rule it claims to preserve. `AGENTS.md:52` says an unconfirmed claim stays out before it goes in, rather than only before publication. The redesign explicitly overrides the original design, not that instruction. A draft mark inside a card also leaves unsupported fit colours and home-sector recommendations looking authoritative outside it.

**Change:** ask the owner to adopt a narrow exception for visibly labelled, non-publishable local review content. Keep rewritten lesson claims fully checked. Mark the map itself and any draft recommendations/search results, not just the opened card.

Specify that the default/release build fails for draft, missing or unknown status, and that preview requires an explicit option and separate output. The Pages workflow must invoke release mode and upload only its successful output (`.github/workflows/pages.yml:37–41` currently builds and uploads `dist`). A preview or stale artifact must not substitute after failure. Define “checked” as review of all factual fields, including function mappings and sector conditions; substantive edits reopen the affected review. Keep the gate offline and deterministic. These requirements can be implemented in step 1 even though its full map cannot pass the release gate until step 2.

**4. Source identity checking is not claim verification (§8).**

D:289's automatic branch-reference fallback and D:298–306's checker leave “checked” ambiguous. Crossref exposes deposited bibliographic metadata; a valid DOI does not establish that the cited paper supports the paragraph. [Crossref REST API documentation](https://www.crossref.org/documentation/retrieve-metadata/rest-api/). Nor does a survey automatically cover every later method, package API or sector recommendation.

**Change:** separate bibliographic/link checks from editorial verification. Record a short support location, such as a section or page, for map judgments and non-obvious lesson claims. Use the approved surveys wherever they actually support the statement; add a specific source only where needed. This respects the owner's rejection of hundreds of upfront primary-source searches. Treat metadata mismatches, manual checks and temporarily unavailable checks as distinct results. Claim edits require renewed support review even when the source registry itself is unchanged. Verify that linked copies represent the cited work/version. The offline build checks keys and required review records; the separate network script does not certify scientific correctness. Do not copy the mockup's stronger “Every link is checked when the site is built” promise (`.mockups/course/index.html:395`).

**5. Live parity must cover transformations and figure meaning, not just initial scalar values (§6).**

D:222–249 specifies fixture parity but leaves the interactive input domain unspecified. Relevant conventions are already concrete: population standard deviation and constant-series handling (`code/python/tsc/distances.py:20–26`), DTW unreachable paths and tie order (`:37–48`, `:82–98`), and SBD without automatic standardisation or circular wrap-around (`:101–113`). A JS port can agree on initial distances and still show a different path, mishandle a zero-norm result, or use a different shift transformation.

**Change:** before implementing the widgets, specify each control's range, step, units, preprocessing order, shift boundary treatment and invalid-state display. Set fixture length/control bounds in the approved plan so the live grid has a deliberate rendering budget. Parity must exercise control-generated inputs as well as untouched CSV rows, use explicit tolerances and round only for display. Retain the existing hand/package oracles (`code/python/tests/test_distances.py:34–60`); Python/JS agreement is not an additional independent proof of the formula. Propose the short edge-case list to the owner as required, rather than adding it unasked.

For static/live takeover, check the initial series, band, path and labels as well as numbers and CSS classes. Adopt the Python tie rule when the same path is promised. Treat “Euclidean growing while SBD stays low” (D:249) as a verified observation over the chosen fixture and slider range, not an unconditional property to force into the animation.

**6. Live controls, precomputed groups and hidden answers need a shared state contract (§§6–7).**

D:226 freezes prose numbers while D:243–247 allows live recomputation alongside precomputed grouping states. D:272–278 does not say whether answers refer to the initial fixture or the user's edited state. A changed series beside an unchanged partition, score or answer can be internally plausible and still wrong.

**Change:** declare each activity either a finite precomputed-state selector or a live numerical experiment. For each state, bind the fixture, parameters, numbers, caption/text alternative and answer together. Do not imply that a grouping or validity score has been recomputed after a continuous edit unless it actually has. Baseline prose and baseline exercises should name their initial settings and offer reset; state-dependent answers must follow the current state. Static/live versions can share data and identifiers without sharing a renderer. This retains Python-generated SVG and avoids implementing browser clustering.

**7. The new lesson contract must explicitly replace the old one (§§4, 11).**

D:142–165 changes section order, finance placement, figures, code and exercises, but `AGENTS.md:21–22` mandates the old section schema and figures only inside `## Lesson`. The parser enforces that schema (`scripts/buildlib/content.py:20–22`). D:343 can leave syntax to the builder, but it cannot leave the fate of the old Measure card and Check implicit. The decision lens and assumptions should not disappear during a visual rewrite.

**Change:** state which old blocks are replaced, where their information goes, and that the approved implementation updates the corresponding AGENTS contract and smoke fixture. Preserve input assumptions, conventions, interpretation limits and reproducible Python/R examples. Distinguish “reference code shown here” from “equivalent package call”: naming a library beneath the tabs does not establish equivalence without matching parameters. Existing libraries first remains the direction for subsequent lessons (D:335–336); do not let the new format mandate a fresh implementation of every catalogue item.

**8. The activities need an explicit transfer outcome (§§1, 7).**

Worked examples, hidden explanations and predictions fit the stated intent. As written, however, they can all be satisfied by reading off distances or guessing the displayed grouping. That does not establish the goal at D:18–19: choosing a compatible distance, method and index for new data.

**Change:** give each lesson a decision the reader must make without copying the preceding demonstration. Include a short transfer task that states the object, objective and allowed invariances, asks for a compatible pipeline, and requires rejection of a plausible alternative. In lessons 1 and 5 this can use supplied grouping/validity choices and previews of later topics, without teaching the whole validity module early. Reveal a worked rationale, admissibility conditions and acceptable alternatives, not a purported universal winner. Preserve the original distinction between computability, geometry and domain usefulness (O:139–158). Later cumulative exercises should include sensitivity and a case where attractive or stable clusters answer the wrong question. Exclude hidden solution text from default search snippets so the course does not reveal answers before the activity.

#### Minor

**9. Define interaction behaviour beyond “keyboard operable” (§§4, 6, 9).** D:105–116 and D:229–232 leave panel focus, Escape/return focus, search dismissal and reading-position restoration unstated. Specify those outcomes and accessible names/states for cards, citation disclosures and exercises. `/` must not steal typing from an input. No-JS reading should retain access to answers, citations and both code languages, not only static figures. Clarify D:317's “no runtime request” as no external requests or runtime data fetches; normal local CSS, JS and font loading remains necessary. Preserve `file://` operation when choosing how the search index is loaded.

**10. Reconcile the call count and freeze wording.** D:3 says seven questions are settled as marked calls, but there are five explicit call sites: D:156, 207, 235, 241 and 304. Mark the other two decisions or correct the description. “Frozen once checked” for new fixtures should mean numerical checks **and** approval of the teaching effect, not merely a passing generator check (D:256–263).

### Claude's calls

| Call | Agree / Change | Reason |
| --- | --- | --- |
| Finance block dark in both themes (§4.3, D:156) | Agree | Matches the approved direction. Define local foreground/figure variables for that surface, and check links, math, focus and figure labels as well as body text. Global light-theme `ink` cannot remain the text colour on an `ink` background. |
| Full draft map in step 1, release blocked (§5, D:207) | Change | Keep the full-size local preview, but explicitly approve the draft exception, mark draft judgments outside cards too, and define the release/preview gate in finding 3. |
| Python static SVG plus JS takeover (§6, D:235) | Agree | Preserves readable initial content and the existing figure pipeline. Extend acceptance beyond initial scalar numbers to semantic figure parity and a usable fallback if enhancement fails. |
| Four JS kernels, precomputed groups/scores (§6, D:241) | Agree | A defensible boundary for two pilot lessons. Requires the input/state contracts in findings 5–6. Reuse controls and kernels; do not expand into general browser clustering. |
| All rewritten lesson claims sourced before owner review (§8, D:304) | Agree | Correct for the teaching review. “Checked” must include support for the claim, not just identifier resolution. The expressly approved draft-map exception must remain separate. |

The two other builder questions cannot be mapped reliably from the marked text. I would not invent decisions to make the count seven.

### Step 1 scope

Step 1 is an integration milestone, not one small reviewable implementation task. It combines a new content schema, shell/search, catalogue engine, source workflow, four numerical kernels, two renderers, two datasets and two lesson rewrites. Keep its owner-facing outcome, but split delivery into these review checkpoints:

1. **Shell and static learning format.** Settle the important contracts above. Implement the new template, one real worked example/exercise/citation, static fallbacks, navigation/search, sources page and draft/release separation. Include the complete draft map volume and its filters so the visual review reflects the actual catalogue. Review mobile/dark presentation before multiplying the components.
2. **Lesson 5 end to end.** Implement the shared DTW/window state driving linked series, grid, band and path, plus answers and source checks. Add and approve the finance/weather fixtures and per-lesson coverage. Review numerical and learning correctness together, not just screenshots.
3. **Lesson 1 and integration.** Add the Euclidean/z-normalisation/SBD experiment and finite precomputed grouping states. Complete both rewritten lessons, sector coverage and the retained/new checks. This is the step-1 owner review. Full map-content verification still follows in step 2 before any release.

Cut duplicate interaction machinery first: use one accessible control mechanism before adding draggable inline-number variants, and allow immediate A/B state changes before polishing group-motion animation. Reuse the DTW component for the too-wide-window pair. Keep real-data downloaders in step 4 and extra-sector exercises with the lessons that need them. Do not cut the three core sectors, paragraph sources, worked explanations, exercises, map volume or static fallbacks to make room for animation polish. Any reduction in the owner's sector frequency requires an explicit revised decision.

### Verdict

**Design:** Ready for the owner after the listed changes

**Reasoning:** The chosen engine and essay format can support the intended course without a framework change. Before implementation approval, reconcile the owner/rule conflicts and make conditional map claims, source verification and live-state correctness explicit; those are the costly guesses, while file formats and component layout can stay with the builder.

**Handoff:** Claude should incorporate or explicitly resolve the important findings, reconcile the five/seven call count, and bring the amended design and split scope to the owner. This review authorizes no implementation, merge or deployment. No other open task is known to depend on retaining this chat; the findings and continuation needs are recorded here.
