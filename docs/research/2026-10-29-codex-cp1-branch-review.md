**Verdict: ready after the listed changes.** No Critical finding. Fix Important findings 1–7 before presenting checkpoint 1 as complete. The shell can already be shown for visual feedback, but its review and contrast guarantees need correction.

Reviewed branch `redesign`, HEAD `d9cd733`, against base `9fd7cdf`, the supplied diff, amended plan, design, ledger, current implementation and generated preview markup. Findings below are from static inspection, not executed reproductions. Several expose gaps in the approved plan itself, rather than implementation departures from it.

`HANDOFF.md` still describes the earlier `pilot`/planning state at `9a2fa1b`. I reported that mismatch before writing. The request and current checkout agree on `redesign`/`d9cd733`. Claude should reconcile the handoff when closing this work.

I attempted each permitted command once. `uv run pytest -q` exited 2 because uv could not create a temporary file in `/home/maxto/.cache/uv` on a read-only filesystem. `npm test` exited 1 at its initial uv smoke-build subprocess for the same reason, before browser checks. Neither attempt established a product failure or a passing suite. The ledger's 88 pytest passes, e2e passes, contrast results, screenshots and identifier matches remain supplied implementer evidence. I did not run the source checker, access vendors, start a server or change implementation files.

**1. Important: fingerprint normalization erases meaningful edits.**

Locations: `scripts/buildlib/cite.py:18–23`, `scripts/buildlib/content.py:296–297`, `scripts/buildlib/atlas.py:63–70`, `107–109`, `121–136`.

The shared fingerprint replaces every whitespace run with one space. A fenced Python line changing from `print("a  b")` to `print("a b")` retains the same lesson fingerprint, despite changing the copied program's output. Moving a statement into or out of an indented suite can likewise retain approval. Markdown structural whitespace is also significant. A matching hash therefore does not establish that the current lesson is the reviewed lesson.

Atlas fields are concatenated with newlines before that same collapse. Field boundaries disappear: changing `does="alpha beta", cond="gamma"` to `does="alpha", cond="beta gamma"`, with the other fields fixed and no intervening tags, produces the same input to SHA-256. This is an encoding collision, not a cryptographic attack.

**Change:** fingerprint a versioned, unambiguous payload. Preserve lesson whitespace, apart from an explicit line-ending convention, and use canonical structured serialization for atlas fields. Invalidate old records through the version change. Plan Task 2 explicitly prescribed the current normalization, so amend that contract too.

**2. Important: changing a map reference's underlying work does not reopen its approvals.**

Locations: `scripts/buildlib/atlas.py:31–32`, `63–70`, `107–109`, `382–393`; `scripts/buildlib/cite.py:74–75`; `scripts/review.py:110–118`.

Item and fit fingerprints contain a source key, locator, support field and candidate flag, but never the resolved source identity. Replacing a referenced registry entry's DOI/title/year while keeping its key leaves every associated item/fit record valid. The displayed source changes and the old support location may now name an unrelated work. Lesson citations correctly include source identity, so the two consumers have different guarantees.

Additionally, `Source.identity` omits authors and venue even though both are public bibliography, and authors determine citation labels. Those edits retain lesson and citation approval too.

The citation recorder also accepts only key/locator/paragraph as the expected citation state and stamps the source identity current at recording time. If the registry changes after review but before recording, the old command silently approves the new identity. A separately recorded current lesson is still required, but the citation's support approval is no longer tied to the work the reviewer read.

**Change:** bind source identity end to end: include authors/venue, include the resolved identity in atlas references, and require the citation recorder to compare an expected identity shown to the reviewer. Reopen only dependent records. The author/venue omission also originates in the plan.

**3. Important: map classification and recommendation context are outside the review dependency graph.**

Locations: `scripts/buildlib/atlas.py:63–70`, `107–122`, `262–286`, `382–393`.

Moving an item between families, changing its family name or changing the family lesson leaves the item approved. Branch labels/subtitles have no review record either. These fields are rendered as part of the field's taxonomy and lesson recommendation.

A fit records its question ID, but not the question text. Changing a question while retaining its ID reopens the question alone. Recording the new question then makes the old fit approval usable under a different question, without another fit review. The gate catches a changed row, but misses the recommendation's changed meaning.

**Change:** define explicit review dependencies: include the item's classification/lesson context in its approval payload, gate displayed branch/family descriptions, and bind each fit to the question text it answers. Resolve these payloads before computing approval state. This does not require a review of the draft map's scientific content now.

**4. Important: the promised per-field support gate cannot require support for an item's condition.**

Locations: `scripts/buildlib/atlas.py:21`, `72–76`, `250–258`, `301–304`, `384`; plan Task 4's “for each factual field” rule.

`Item.cond` is fingerprinted but absent from both required support fields and accepted support names. A reviewed item can therefore acquire a factual condition without any reference explicitly covering that condition. This promotes part of the ledger's deferred Minor finding.

Tag conditions need a more precise ruling: a reference supporting `ignores:warp` can legitimately support the entire conditional claim. A separate reference for each subfield is unnecessary if the review explicitly covers both the property and its condition. The same principle applies to a fit's reason and condition.

**Change:** add support coverage for non-empty item conditions and document that a tag/fit support decision covers the full conditional claim. Require that coverage before deriving `reviewed`. Do not manufacture source records merely to make the present draft releaseable.

**5. Important: valid links to fixed lesson blocks are rejected.**

Locations: `scripts/buildlib/content.py:298–302`, `332–355`; `scripts/buildlib/pages.py:165–180`.

The renderer emits `#one-line`, `#in-finance`, `#measure-card`, `#code` and `#common-mistake`, and generates navigation to them. The fragment validator's ID set contains only ordinary section/subheading IDs. Thus an authored link such as `[the measure card](#measure-card)` fails even when that block is present. Task 1 validation and Task 5 rendering disagree.

**Change:** validate against the actual rendered target set, including present fixed blocks. Only include `code` when a code section will render. Keep collision checks against reserved IDs.

**6. Important: preview isolation misses a symlinked release directory.**

Locations: `scripts/build.py:94–102`, `132–137`.

The output path is resolved, but the forbidden `ROOT / "dist"` is not. If `dist` points to another directory holding an existing marked release output, `--preview --dist dist` resolves outside the lexical `ROOT/dist` tree and passes the guard. `prepare_dist` then replaces the release target with a preview. The same issue applies when selecting that target through another alias.

This is a conditional path-handling defect, not a leak observed here: current `dist/` and `preview/` are ordinary directories. The normal workflow does not upload `preview/`.

**Change:** compare the output against both the reserved lexical release path and its resolved target, including descendants, before any output mutation. This closes the stated “never into the release tree” guarantee without changing the default directories.

**7. Important: the contrast test still excludes normal finance and measure-card prose from 10:1.**

Location: `tests/e2e.mjs:717–732`; amended plan lines 18 and 609.

The corrected inline-colour rule only applies inside `section.content`, `.oneline` and `.mistake`. Normal paragraphs/list items inside `.finance` and `.measure` are measured as generic text at 4.5:1. Yet the plan explicitly includes reading-column body prose and finance body text. A regression to 7:1 there would pass the new matrix. This is a coverage defect, not an assertion that current finance colours fail.

**Change:** classify normal reading-column prose by the declared role, including finance, measure-card and code-introduction prose, while retaining the explicit link/accent/popover exceptions. Check that each required role contributes rows at its intended threshold. Include threshold/role in the deduplication key at line 760 so a weaker measurement cannot suppress a stronger one.

**Additional Minor findings.**

- **Caption support text disappears from the review command.** `scripts/review.py:60–79` searches only surviving inline tokens. `scripts/buildlib/content.py:453–454, 483–497` has already replaced a figure paragraph with `tsc_figure`. The citation survives, but `review.py show` prints an empty paragraph for it. Preserve the original citation-bearing text when collecting citations, then display that text. Fix before relying on this command to review new caption citations.
- **Fit provenance does not reach the reader.** `scripts/buildlib/pages.py:229–231` drops fit references from the serialized data, while `site/map.js:51–64` renders fit reasons and conditions. Item-card references at `pages.py:266` cover only item/tag claims. A fit-specific source can appear on the Sources page without a located link from its recommendation. Serialize and display fit references alongside the selected fit. This can wait until source-backed map content is authored, but should precede its release.
- **The phone scrim assertion has the wrong target.** `tests/e2e.mjs:360–364` clicks `(width - 5, 700)` at both 820 and 375 px. At 375 px, `site/theme.css:375` makes the drawer full width, so this is not an outside point. Test outside-click closure only where an exposed scrim exists, assert its hit target, and use the close button/Escape for the full-width phone drawer. Resolve this before citing this assertion as phone scrim evidence. I did not execute a browser reproduction.

**Integration, scope and release assessment.**

The ordinary path is coherent: schema produces structured blocks, citations are checked in both modes, atlas state is derived from records, search is generated locally, and the home and Sources page consume the same source registry. Static HTML retains lesson content without JavaScript. UI scripts implement navigation/filtering/search rather than new numerical live figures. I found no implementation of the deferred exercises, transfer tasks or new finance/weather fixtures. Retaining the pilot prose as the explicitly approved baseline is appropriate here. That approval is not a new scientific audit of every pilot claim.

Missing lesson/citation records are checked before output preparation in both modes (`build.py:155–156`). Missing item/fit/question/sector records block a release (`158–162`). The question/sector ruling was implemented. The defects above concern what a matching record actually covers, rather than a missing top-level call to the gate.

The Pages workflow builds in release mode and uploads `dist` only following a successful build. I found no ordinary preview-upload path. Nevertheless, output preservation must be described accurately: gate failure returns before `prepare_dist`, so an existing output remains. The ledger's “failed release leaves no output” is not true for a pre-existing output. The correct invariant is **failure leaves the old output untouched and prevents upload**. Also, the inherited default “no `_course.md`” path returns success without building (`build.py:140–145`). Do not use that success as evidence of a fresh artifact in a wrapper that reuses output directories.

**Disposition of the ledger's deferred findings.**

| Ledger group | Disposition and concrete next action |
| --- | --- |
| T1 title rendering/slug and code paragraphs carried to T5 | Title rendering now uses inline tokens/plain labels. Code prose is rendered with a real code block. Do not reopen the old blanket finding. Decide separately whether a prose-only `Code` block should be rejected rather than silently omitted. |
| T1 duplicate fences/non-paragraph code tests, lowercase legacy headings, weak Julia assertion | Minor, can wait. Keep the code-schema edge cases on the owner's list. Strengthen Julia's expected diagnostic when touching that test. |
| T2 H2 citation and unused `cited_sources` | Resolved: H2 citation is explicitly rejected at `content.py:328–329`, and the source index is consumed. |
| T2 malformed citation spelling, generic identity-test assertion, absent stale-recorder tests | Minor, can wait as separate edge cases. Before broader source authoring, reject citation-like malformed syntax. Split lesson/citation identity assertions when fixing finding 2. |
| T3 stale `_sources-check.json`, shared manual note, unchecked checker paths | Minor for this checkpoint, must not become release evidence later. Bind results/manual attestations to the identifiers checked. “No independent value” is not a reason the checker cannot be tested: saved API response fixtures or literal protocol cases provide independent expectations. Propose those tests to the owner. |
| T3 arXiv no-entry/empty-title classification | Minor, can wait. Document provider-specific absence semantics and treat unreadable metadata separately from a positively conflicting identity. |
| T4 condition support | Promote to Important finding 4. |
| T4 stale item/fit recorder tests and failed-release-output test | Stale fingerprints are explicitly rejected at `review.py:145–147`; missing tests alone do not prove a bypass. Propose tests, including the corrected output-preservation invariant above. |
| T4 preview banner and run-on comment | Banner is now unconditional for a preview map at `pages.py:273`. Comment cleanup can wait. |
| T5 phone identity/GitHub visibility, heading outline, duplicated math labels, unused imports | Minor, can wait. Bring phone visibility and math-label readability to the owner. A navigation H2 before the page H1 alone is not a demonstrated functional defect. |
| T5 tab associations | Resolved by `course.js` adding panel roles, IDs and `aria-controls`/`aria-labelledby`. |
| T5 scaled figure labels; T7 one root connector | Owner visual decisions, not gate blockers. Show the existing screenshots/preview with those deviations named. |
| T6 reused `.ln`, CSS after figure markers, absent “free” assertion | No demonstrated collision or runtime defect. SVG classes are scoped, ordinary CSS may follow the markers. Missing negative assertion can wait. |
| T6 dark draft marks | Later preview-search and contrast checks cover both themes; do not describe this as wholly untested. Their execution here remains unverified. |
| T7 Home/End tabs, copy fallback focus, malformed URL decoding, language memory, popover hover colour | Minor, can wait. Restore focus in the copy fallback when touched. Do not turn optional language persistence into a new requirement. Keep hover contrast on the remaining state checklist. |
| T7 phone scrim click | Correct the assertion as described above before using it as evidence. |
| T8 draft spacing, planned target, form assumption, Unicode highlighting | Minor, can wait. The planned target exists at `pages.py:342`; the form is supplied by the shared template. Add a target-existence assertion when touching search tests. Visually inspect draft spacing and keep Unicode offsets as a separate hardening case. |
| T9 viewport/state coverage and SVG bounding-box backgrounds | Keep as explicit coverage limits. The SVG heuristic is not a general geometric contrast proof. Extend it when introducing new figure geometry, rather than claiming all possible fills are already verified. Finding 7 is a separate present coverage defect. |

**Test-oracle assessment and continuation.**

I did not find grounds to discard the suite as implementation-mirroring. Literal fingerprint and contrast values are independent oracles. Design-derived diagnostics and navigation targets are valid expectations. Calling the recorder to prepare an approved fixture is setup, not inherently a circular assertion.

There are weaker claims to correct. `tests/test_build.py:490` replaces a tag with a dictionary that also removes its sources, so the “tag cond” mutation does not isolate a condition-only edit. Preserve its references and edit only the condition. The generic `"has no review"` assertion at line 292 does not establish that both the lesson and citation approvals reopened. The contrast-role and scrim findings are concrete cases where the oracle differs from the contract. Search assertions derived from the emitted index can test presentation consistency, but do not independently prove the index contains every required content entry.

Suggested additional owner-approved regression cases are the literal whitespace/field-boundary examples, a map source-identity edit, question/classification dependency edits, a fixed-block fragment, and a symlinked release target. Existing role, condition and drawer assertions should be corrected as part of their respective fixes. No tests were added in this review.

Claude can continue from this file: amend the fingerprint/dependency contracts, make the listed fixes, run the checks in a writable environment, and bring the visual choices to the owner. Map source verification, live figures and subsequent checkpoints remain open under their existing scopes. No other open task requires retaining this chat: the remaining findings and continuation requirements are recorded here.
