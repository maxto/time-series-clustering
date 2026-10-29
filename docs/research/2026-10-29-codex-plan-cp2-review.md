# Checkpoint 2 plan review

Reviewed against branch `redesign`, HEAD `4ed74ba`, with a clean working tree before this answer. `HANDOFF.md` predates the plan commit and still lists planning as pending. This review uses the committed request and its settled owner decisions. No implementation, builds, tests or browser runs were performed. Repository code and the installed container plugin were inspected, and the primary documentation linked below was opened. This is a plan review, not certification of the rewritten lesson's claims.

Locations below refer to `docs/superpowers/plans/2026-10-29-redesign-checkpoint-2.md` unless another file is named. The findings preserve the approved deep-dives, omitted summary lines, removal of soft-DTW, shortened silhouette section and selected parity cases.

1. **Important: the required static SVG metadata fails the existing validator.**

   **Location:** Task 2, lines 73–88 and 95.

   **Problem:** The generated SVG must carry `data-pair`, `data-w` and `data-path`, but `scripts/buildlib/svg.py:16–20,64–72` rejects every attribute outside its explicit allowlist. None of these attributes is allowed. Task 2 does not include that module among its modifications. The builder validates every SVG, including an explorer not yet referenced by a lesson, so the promised passing build cannot be reached as written.

   **Concrete fix:** Add `scripts/buildlib/svg.py` to Task 2. Permit those three attributes narrowly, with the declared value formats and element placement, and document the extension to the figure rules. Alternatively, remove the metadata requirement and compare parsed geometry using a separate expected-state artifact. Do not broadly allow arbitrary attributes to make the fixture pass.

2. **Important: the task boundaries cannot deliver the stated passing checks.**

   **Location:** Task 2, lines 75,90–97. Task 3, lines 121–134. Task 4, lines 140,153–156. Task 5, line 163.

   **Problem:** Task 3 tests and screenshots the live explorer in the real `dtw` lesson, but only Task 5 replaces that lesson's figure reference. It therefore cannot pass at Task 3. Earlier, Task 2 adds two figures to smoke alpha while `tests/e2e.mjs:119–120` expects exactly one figure title and one caption. Both Tasks 2 and 4 edit smoke alpha without arranging updated review records: `scripts/build.py:161–162` enforces those records even for smoke builds, and `tests/e2e.mjs:35–38` builds the permanent fixtures directly.

   **Concrete fix:** Exercise the component on the smoke fixtures in Task 3, and explicitly defer real-lesson integration assertions and screenshots to Task 5 after editorial review. Update the smoke figure assertions in Task 2 to preserve checks on the original static figure and separately identify both new live figures. In Tasks 2 and 4, include `tests/fixtures/smoke/_reviews.toml` and an explicit second-model review followed by recording through `review.py`. Do not bypass the gate or stamp records before review merely to obtain a green task.

3. **Important: the review-record command is not executable and does not record all citations.**

   **Location:** Task 5, line 167.

   **Problem:** `review.py record --lesson dtw` lacks required `--content`, `--by`, and the lesson fingerprint. Recording a lesson does not record its citations. The actual CLI requires a separate citation call with key, locator and paragraph fingerprint (`scripts/review.py:102–115,149–161,187–188`).

   **Concrete fix:** Replace the instruction with this sequence, using the values from the final reviewed text:

   ```bash
   uv run python scripts/review.py show --content content --lesson dtw
   uv run python scripts/review.py record --content content --lesson dtw --fingerprint '<lesson fingerprint>' --by '<actual reviewer>'
   uv run python scripts/review.py record --content content --lesson dtw --cite '<key>' --locator '<exact locator>' --paragraph '<paragraph fingerprint>' --by '<actual reviewer>'
   uv run python scripts/review.py show --content content --lesson dtw
   ```

   Repeat the citation call for each distinct citation tuple reported by `show`. Confirm that the lesson and every citation are recorded. If source identity edits reopen other lessons, review and record those affected lessons too before expecting the whole-site checks to pass.

4. **Important: the JSON escaping instruction is a no-op.**

   **Location:** Task 2, line 86.

   **Problem:** “`<` escaped as `<`” leaves the literal character unchanged. Inside a script element, a string containing `</script>` can terminate the element even when its type is `application/json`. The existing atlas implementation actually replaces `<` with the literal JSON escape `\u003c` (`scripts/buildlib/pages.py:233`).

   **Concrete fix:** State the exact operation: serialize JSON, then use `.replace("<", "\\u003c")` before embedding. Do not HTML-escape the JSON. Strengthen the existing embedding round-trip check with a permitted string containing `<`, checking both the parsed JSON and that no extra DOM element is created. This is a correction to the planned embedding test, not a new feature.

5. **Important: the kernel test protocol cannot represent its own non-finite input case.**

   **Location:** Task 1, lines 52–64.

   **Problem:** `[NaN]` is not valid JSON. Sending Python's permissively serialized `NaN` to Node's `JSON.parse` fails in the transport before the kernel is called. Converting it to `null` instead would test a different input. The public `dtwCost` result also contains typed arrays and `Infinity`, but the `{value}` wire format has no defined matrix or non-finite encoding. No listed parity case checks that exported operation.

   **Concrete fix:** Define a JSON-safe tagged input such as `{"special":"NaN"}` that the Node runner converts to `Number.NaN` immediately before invoking the kernel. Distinguish transport failures from kernel errors and assert one result per submitted case. If `dtwCost` stays public, serialize rows as arrays and encode unreachable cells explicitly, then include it in the existing reachable-state parity check against Python's accumulated table, comparing the infinity mask exactly and finite costs with a stated tolerance. Keep local shading costs distinct from that accumulated table. Also put the CLI runner scaffold before the first test run, so the initial failure is the intended missing kernel rather than a missing runner.

6. **Important: accepted data, component controls and the rendering budget do not yet form one contract.**

   **Location:** Task 2, lines 79–92. Task 3, lines 110–118,129.

   **Problem:** The JSON exposes configurable pair names, window bounds and initial settings, while Task 3 hardcodes the lesson's names and bounds. The smoke data is only described as “minimal valid,” leaving implementers to invent its dimensions and settings. The proposed unequal-length validation rejects only pairs whose minimum window is too small, although the component also computes Euclidean distance, which rejects all unequal lengths. The validator requirements do not explicitly enforce the 2,304-cell limit or non-empty finite numeric rows. Consequently, “no invalid state is reachable” is not guaranteed for every accepted file.

   **Concrete fix:** Give exact smoke data and expected results. Require the component to derive controls and Reset from its own validated data. For this component, require non-empty equal-length numeric rows, a maximum of 48 samples per row, valid pair references, a valid integer initial pair index, ordered non-negative integer window bounds, an in-range initial window and a Boolean `none`. Enforce this before output preparation. Preserve the broader unequal-length support in the DTW kernel. Define what unchecking No window does, for example restoring the retained slider value. Specify that redraw replaces prior cells, so the budget bounds the current DOM as well as one render's work.

7. **Important: the agreement checks can pass with an incorrectly drawn figure.**

   **Location:** Task 2, line 88. Task 3, lines 122–125,128–131.

   **Problem:** Equal `data-path` strings and correct readouts do not establish that the visible polyline uses those coordinates. The tests could pass with reversed axes, unchanged series after a pair change, a fixed band, wrong connecting links or accumulated-cost shading instead of local-cost shading. The spec explicitly requires agreement in series, band, path, labels and numbers (design 6.1 and 9). The current static grid uses local squared costs and a square-root opacity transfer (`scripts/figures.py:211–233,253–272`), whereas the new kernel's `dtwCost` returns accumulated costs.

   **Concrete fix:** Specify grid orientation, sample-to-coordinate transforms, local-cost shading and its scale, link sampling, labels and legend in the component contract. Compare actual SVG coordinates, band-cell membership and selected opacity values with fixture/Python-derived expectations, not just diagnostic attributes. Cover the initial state and the already planned pair/window changes, including window zero, unbounded window and resize. For resize, also compare rendered SVG width with content width, so a changed `viewBox` cannot pass while CSS still caps the live figure at 360 px. Update the caption and accessible description to remain true for the current pair and window, and include the meaning of the band, path and shading, not just the two distances.

8. **Important: failure after activation can display the baseline under another state's controls.**

   **Location:** Task 3, lines 107,113–116,127.

   **Problem:** After choosing `mon-wed, w = 10`, a kernel error restores the `mon-sat, w = 4` static SVG. The plan does not say whether controls reset, whether the previous dynamic title is removed, or how the baseline is identified. “This setting cannot be computed” alone does not state which setting the visible figure represents. The test only blocks script downloads, so it never exercises failure after replacement or a renderer exception. The existing context helper also treats deliberate request aborts as failures (`tests/e2e.mjs:67–80`).

   **Concrete fix:** Define an atomic activation and failure transition. On failure, restore the retained baseline SVG, reset or disable the controls consistently, and announce that the initial `mon-sat, w = 4` state is shown. Catch initialization, computation and rendering failures per figure, preserving the other instances. Extend the existing script-failure check with an injected exception after a successful state change. Use a dedicated failure context that exempts only the deliberately blocked resource or injected exception and continues to fail on unrelated errors.

9. **Important: the radio keyboard test specifies the wrong interaction, and the isolation check is too weak.**

   **Location:** Review Focus 1 and 4, lines 35,38. Task 3, lines 110,126,129,133.

   **Problem:** Tab normally enters a radio group at its checked radio, and arrow keys move between choices. Requiring Tab to reach both radios conflicts with the native radio interaction the plan otherwise requests. The [W3C radio pattern](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) documents this behavior. Two figures showing their initial pair names does not detect shared radio `name` values or handlers that update the wrong instance. Checking `outline-style` alone can pass with a zero-width or invisible outline.

   **Concrete fix:** Give each figure a separate radio-group name and an accessible group label. Use Tab to enter the group, arrows to choose the other pair, then Tab to the remaining controls. Verify checked state and keyboard-driven updates. In the existing two-instance check, change and reset one figure and assert that the other figure's checked inputs, path and readout remain unchanged. Check an effective visible focus indicator in both themes, using the existing focus-contrast approach rather than style name alone.

10. **Important: the source procedure permits inadequate support locations and an inappropriate substitute for current Python defaults.**

    **Location:** Task 5, lines 164–166.

    **Problem:** A documentation version and access date identify a snapshot, not the passage that supports a claim. Also, “or Giorgino 2009 for `dtw-python`” permits an R-package paper to stand in for evidence of the current Python API's defaults. The [2009 article](https://www.jstatsoft.org/article/view/v031i07) is explicitly about the R package. The current Python [`dtw` documentation](https://dynamictimewarping.github.io/py-api/html/api/dtw.dtw.html) gives the defaults, while its [`StepPattern` documentation](https://dynamictimewarping.github.io/py-api/html/api/dtw.StepPattern.html) explains `symmetric2` weighting.

    **Concrete fix:** Require documentation locators to include the function and relevant parameter, return value or named subsection, plus version and access date. Use Giorgino for the algorithm and step-pattern background, and Python documentation for Python defaults. Save a claim-to-support checklist in the Task 5 review request, distinguishing literature claims, consequences of the stated course definition and observations computed from the frozen fixture. Include front matter, figure descriptions, finance text and the shortened scoring explanation in that coverage check. Bibliographic matching remains separate from support verification.

    The proposed DTW and silhouette references are appropriate starting points. In particular, [Paparrizos et al., section 5.1](https://arxiv.org/html/2412.20574v1#S5.SS1) defines an unrooted accumulated squared cost, as does the inspected [aeon API definition](https://www.aeon-toolkit.org/en/stable/api_reference/auto_generated/aeon.distances.dtw_distance.html). The course's final square root must remain explicitly identified as its convention. [Rousseeuw's 1987 paper](https://doi.org/10.1016/0377-0427%2887%2990125-7) is the appropriate original silhouette reference. Its exact supporting passages still need reading during Task 5, rather than treating metadata or this plan review as editorial approval.

11. **Minor: the deep-dive title grammar and strict-container integration need an explicit decision.**

    **Location:** Task 4, lines 143–155.

    **Problem:** It is unclear whether the title is plain text or inline Markdown. Container titles arrive in `token.info`, not ordinary inline children, so the existing prose, citation and math walkers do not validate them automatically (`scripts/buildlib/content.py:432–457`). The installed plugin also auto-closes an unclosed container and emits a closing token anyway (`.venv/lib/python3.13/site-packages/mdit_py_plugins/container/index.py:114–119,168–182`). Merely checking balanced output tokens will therefore accept a forbidden unclosed block. Container headings change token depth, so validation needs to happen before section splitting and heading-ID collection.

    **Concrete fix:** Choose plain-text, HTML-escaped titles for this checkpoint, explicitly validate their prose and citation restrictions, and index the title together with its body. Specify a source-aware container-validation pass before `split_blocks` that distinguishes an explicit closer from plugin auto-closure, rejects nesting and headings at any depth, and does not interpret example syntax inside fenced code as a container. Keep body inline tokens on the existing citation, math, link and fingerprint paths. Add math and a prose-rule failure to the already planned positive/negative cases so those integrations are actually checked. This preserves the approved no-heading, section-level search destination.

12. **Minor: no-runtime-fetch is a constraint without a corresponding assertion.**

    **Location:** Global Constraints, line 21. Task 3 e2e checks, lines 121–131. Task 6, line 171.

    **Problem:** The existing request guard permits every local URL (`tests/e2e.mjs:70–74`). It catches external requests, but a same-origin `fetch` or XHR can pass even though the spec prohibits runtime data fetching. There is no explicit new check for that distinction.

    **Concrete fix:** Extend the normal e2e request guard to reject `fetch` and `xhr` requests while permitting the expected document, script, stylesheet and font loads. Exercise the existing controls and reset under both `file://` and the Pages subpath. Keep deliberate script-blocking tests separate as described in finding 8.

All findings and continuation requirements are captured here. Claude can revise the plan and resolve these findings with the owner without relying on this chat. No other open task depends on this chat.

Verdict: Needs changes before implementation, with 10 Important and 2 Minor findings and no Critical finding.
