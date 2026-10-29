# Redesign design: focused re-check

Static review of the uncommitted amendment on `pilot`, HEAD `9a2fa1b`, 2026-10-29. Compared the previous review, amended design, original design, project rules and the top two LOG entries. Inspected the reference DTW implementation and the official documentation linked below. No builds, tests or browser checks ran. Only this answer file was written.

The handoff records `0575db2` and a clean worktree. HEAD has since advanced by the notes/design commit `9a2fa1b`, and the design amendment and re-check request were already uncommitted. LOG still lists the two owner questions as open. The current request explicitly supplies their approved answers, which govern this review. These are stale notes, not blockers. Claude remains responsible for updating them.

**D** = `docs/superpowers/specs/2026-10-28-redesign-design.md`. All D line references below refer to the amended working copy.

## Findings 1–10

| Previous finding | Status | Amended evidence and remaining change |
| --- | --- | --- |
| **1. Sector coverage** | **Resolved** | D:57–63 restores all three sectors in every lesson, distinguishes lesson coverage from section filler, and correctly labels the one-developed-plus-two-transfer approach as a proposal. D:512–519 requires the coverage table and preserves coverage through integration. |
| **2. Conditional map claims** | **Partly** | D:249–281 now requires task, representation, settings, visible conditions and claim-level support, including similarity versus distance and linkage restrictions. However, the newly inserted DTW example at D:252–255 overstates the guarantee. Replace that example with the wording in N1 below. |
| **3. Draft exception and release gate** | **Partly** | D:287–310 incorporates the explicit owner exception, draft marks outside cards, checked-field scope, edit invalidation, default release failure, separate preview output and successful-release-only upload. The remaining integration ambiguity is the unconditional claim-review validator at D:456–459. Add the explicit preview handling in N2. |
| **4. Source identity versus support** | **Partly** | D:437–474 separates metadata checks from editorial support, removes automatic survey fallback, records support locations, distinguishes check outcomes and reopens verification after claim edits. D:229–230 removes the build-time link-check promise. Clarify only how this validator handles permitted draft map claims, as in N2. |
| **5. Live parity and input domain** | **Partly** | D:336–365 covers conventions, transformation order, bounds, rendering budget, generated inputs, tolerances, independent oracles, semantic SVG parity and fixture-limited observations. Input values appropriately remain for the approved plan. D:347–351 nevertheless mandates named edge cases while D:497–498 reserves their selection to the owner. Make that list proposed, as in N3. |
| **6. Shared activity state** | **Resolved** | D:369–383 distinguishes finite precomputed states from live experiments, binds state to data, groups, captions and answers, labels fixed outputs, specifies baseline settings and reset, and requires state-dependent answers to follow the state. D:323–324 also updates the text alternative. |
| **7. Replacement lesson contract** | **Resolved** | D:198–223 retains assumptions, conventions, interpretation limits and reproducible examples, distinguishes equivalent package calls from related functions, maps the old blocks and requires coordinated AGENTS/parser/smoke-fixture changes. The exact syntax remains with the builder. |
| **8. Transfer outcome** | **Resolved** | D:421–433 requires an unfamiliar case, compatible choice, rejected alternative, rationale and admissibility conditions, with supplied method/index choices permitted in the pilot. Later tasks cover sensitivity and wrong-question groupings. D:138–139 excludes solutions from search. |
| **9. Interaction behaviour** | **Resolved** | D:142–153 specifies focus, Escape, reading-position restoration, panel focus trapping, accessible controls and no-JS access to answers, citations and both languages. D:140–141 preserves `file://`; D:319–321 distinguishes prohibited data/external requests from local assets. |
| **10. Call count and fixture freeze** | **Resolved** | D:17–22 reconciles five original marked calls, four remaining calls and seven builder questions without inventing the missing mapping. D:404–407 makes freezing depend on numerical checks and the owner's teaching-effect approval at checkpoint 2. |

## Claude's calls

| Previous table row | Status | Evidence / remaining change |
| --- | --- | --- |
| Finance block dark in both themes | **Resolved** | D:189–197 defines local foreground, link, focus and figure variables and the expanded contrast checks. |
| Full draft map in step 1, release blocked | **Partly** | The owner decision and release boundary are explicit at D:287–310. Complete their integration with the review-record validator via N2. |
| Python static SVG plus JS takeover | **Resolved** | D:354–361 preserves separate renderers with shared data/identifiers, semantic initial-state parity, allowed classes and a usable fallback on script failure. |
| Four JS kernels, precomputed groups/scores | **Partly** | Scope and state boundaries are resolved at D:331–346 and D:369–383. Resolve the edge-case approval conflict via N3, without adding browser clustering. |
| Rewritten lesson claims sourced before owner review | **Resolved** | D:467–474 requires actual support verification as well as bibliographic checks. D:291–292 expressly excludes lessons from the draft exception. |

The checkpoint split is also **resolved**: D:502–517 includes the full review at checkpoint 1, fixture approval at checkpoint 2, and full integration review at checkpoint 3, matching the new owner answers.

## New problems introduced by the amendments

### N1 — Important: the new DTW example asserts more than its constraint guarantees

**Location:** D:252–255, especially “noise or different lengths are reduced”.

A window bounds admissible index pairings. It does not guarantee that a particular shifted pair has a small cost, or that noise is reduced. The official [tslearn DTW guide, optimization problem and additional constraints](https://tslearn.readthedocs.io/en/stable/user_guide/dtw.html) defines the accumulated mismatch objective, closed endpoints and restricted paths. Under this project's stricter literal band convention, unequal lengths can also leave no admissible path (`AGENTS.md:46`, `code/python/tsc/distances.py:37–47`).

A direct hand deduction illustrates the noise problem: with `x = (0, 0)`, `y = (0, 1)` and `w = 1`, the mandatory final pairing costs 1 and the diagonal achieves total cost 1. DTW therefore equals Euclidean here. No execution was needed, and this is not a proposed new test. This counterexample and the endpoint limitation are deductions from the stated recurrence, not a claim that the external guide uses exactly the course's unequal-length band convention.

**Concrete replacement for the conditional-tolerance example:**

> DTW permits local time alignment along admissible paths satisfying `|i - j| <= w`, with closed endpoints. This is a path constraint, not a guarantee of a small cost for every shift within `w`. Noise robustness and unequal-length support need their own method-specific conditions, and an admissible path must exist.

The surrounding conditional-claims contract is sound. Fix the example so it does not teach the unconditional interpretation that contract was added to prevent.

### N2 — Important: draft preview and claim-review validation do not yet meet explicitly

**Location:** D:279–281, D:287–310 and D:456–459.

The approved preview intentionally contains unverified map claims, but the new offline validator fails on a claim without its review record. The document does not say whether a pending record is valid in preview. A builder must decide whether to reject the intended preview, weaken verification globally, or introduce a scoped pending state. The last option fits the approved decision, but should be explicit.

**Add to the registry/build contract:**

> In explicit preview mode, draft map claims may carry pending or unverified review records and incomplete support locations. They must not be represented as verified. Checked map items and all lesson claims retain the normal verification requirements in every build mode. Release mode rejects every draft map item.

This defines the exception's boundary without choosing a storage format or requiring fabricated support records. It is one shared correction for findings 3 and 4.

### N3 — Minor: mandatory edge cases conflict with owner selection

**Location:** D:347–351 versus D:497–498 and `AGENTS.md:53`.

“Plus the edges: window 0, no window, constant series, ties” reads as a required new test list. The later sentence gives the owner the choice. The new request approves the map exception and review checkpoints, not these individual tests.

**Change the edge-list clause to:**

> Candidate additional edge cases to propose for owner selection: window 0, no window, constant series and ties.

Retain the fixture/control-domain parity requirement and existing independent oracles. The plan can specify the practical coverage strategy within the approved control bounds.

No Critical issue or need to revisit the engine, lesson format or delivery split was identified in this focused re-check.

## Verdict

**Not yet ready for owner approval and the implementation plan: correct N1, explicitly connect the preview exception to claim validation in N2, and reconcile the test-selection wording in N3.**

**Handoff:** Claude can make these three bounded edits and present the design to the owner with the two answered decisions recorded in the shared notes. No implementation, merge or deployment is authorized by this review. No other open task is known to depend on retaining this chat.
