# SDD ledger — plan: docs/superpowers/plans/2026-10-29-redesign-checkpoint-1.md

Spec: docs/superpowers/specs/2026-10-28-redesign-design.md (approved 2026-10-29).
Branch: redesign (from pilot), in the main clone (no worktree: branch isolation, not master).
Start HEAD: 9fd7cdf (plan commit). Task 1 Step 1 (branch) done by controller.
Models: implementers sonnet, task reviewers sonnet, final whole-branch review Codex (pane term_58cbd4cb..., owner's advisor).
Edge tests: owner delegated the choice, controller recommended all four Review Focus groups (2026-10-29), adopted.

## Pre-flight scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 self | tests mutate v2 smoke created in Step 2 | consistent |
| T1-T2 | Lesson.blocks, content.py inline rule, smoke alpha "## Engine features" | consistent |
| T1-T5 | build.py temporary rendering replaced by pages.py | consistent. T1 keeps pilot aside notes, T5 must drop the aside checks in e2e |
| T2 self | lesson fingerprint covers whole file | CONFLICT: existing positive tests that edit a lesson (semicolon in code passes, number substituted, figure in finance builds, repeated heading suffix) will fail the lesson review gate |
| T2-T3 | content/_sources.toml, _reviews.toml created T2 Step 5, modified T3 | consistent after plan fix |
| T2-T4 | Reviews.items/fits, review.py extended | consistent |
| T2-T6 | T6 consumes `cited_sources (Task 2)` | GAP: T2 interface does not define cited_sources |
| T3 self | Step 3 needs Codex review by the controller before Step 4 records | process split needed |
| T4-T6 | minimal div.draft-banner T4, styled T6 | consistent |
| T5-T6 | contents links to home #map/#sectors and sources page before T6 builds them | links only, not fetched: consistent |
| T7-T8 | script order names search-index.js before T8 | GAP: file absent during T7 |
| T7-T8 | TSC.layers | consistent |
| T9 | contrast, widths over everything | consistent |

## Rulings

- Ruling: T2 adds a test helper `record_lesson(content, id)` (via review.py) and every positive test that edits a lesson calls it before building — the gate is design 5.1/8 and must stay on in tests — cost if wrong: test helper churn only.
- Ruling: T2 adds `cited_sources(lessons) -> dict[key, list[lesson_id]]` to cite.py (T6 consumes it) — interface gap in plan — trivial.
- Ruling: T3 runs in two dispatches: A (Steps 1-3: script, sources, sentence written, no records) then controller sends the sentence to Codex, then B (Steps 4-5: records, commit) — design 1.1 requires a second-model review before recording — cost: one extra dispatch.
- Ruling: T7 loads only course.js and map.js. T8 inserts search-index.js before course.js — file does not exist before T8 — none.
- Ruling: T3 if the Sakoe and Chiba paper cannot be read from a legitimate copy, the implementer reports NEEDS_CONTEXT instead of citing from memory — design 1.1 "read at the supporting point" — cost: a pause on one sentence.

## Progress
- Task 1: dispatched (BASE 9fd7cdf, implementer sonnet ab2a94522ef7ac1e5)
- Task 1: implementer DONE 678b20e (49 pytest, e2e ok). Review dispatched (sonnet ad8d8970e3a6318c0), package review-9fd7cdf..678b20e.diff
- Task 1: complete (commits 9fd7cdf..678b20e, review clean, Minor only)
  - Parked Minor for owner edge-case list: ## Code rules untested (two python fences, non-paragraph content), lowercase "## lesson"/"## check" fall through without hint, julia test asserts only "julia".
  - Carry to Task 5: section title slug uses raw content while ### uses rendered text, and build.py escapes title raw (math/link in a ## title would show raw). Paragraphs inside ## Code collected but not rendered yet.
- Task 2: dispatched (BASE 678b20e)
- Task 2: implementer DONE 395e35e (59 pytest, e2e ok). Concern: citation in a heading not collected.
- Task 2: complete (commits 678b20e..395e35e, review clean, Minor only)
  - Parked Minor (owner edge-case list / final review): citation in a "## " heading left as literal text without error, malformed key "[@Sakoe78, ...]" renders as text without error, test_changed_source_identity_reopens assertion not specific, no test for review.py refusing a stale fingerprint, cited_sources unused until Task 6.
- Task 3A: dispatched (BASE 395e35e), Steps 1-3 only
- Task 3A: implementer DONE fd48aa8 (59 pytest, 4 ids matched). Sentence sent to Codex (request docs/research/2026-10-29-codex-sakoe-citation-request.md)
- Task 3: Codex approved citation as is (docs/research/2026-10-29-codex-sakoe-citation-review.md). Implementer resumed for Steps 4-5.
- Task 3: implementer DONE 0dda6c2 (59 pytest, e2e ok, real release build passes, 4 matched). Review dispatched.
- Task 3: review Needs fixes (manual unvalidated, matched-manual 5th state, uncaught exceptions, Crossref 404 as mismatch, AGENTS field list). Fix round 1 sent to implementer (FIX_BASE 0dda6c2).
  - Task 3: minor (deferred): _sources-check.json goes stale after registry edits; manual record applies to both ssrn and url; script untested (no independent value).
- Task 3: fix round 1/5 (4 addressed, 1 open — all-unavailable summary counts ssrn/url; commits 0dda6c2..a5e9bc1). Round 2 sent.
  - Task 3: minor (deferred): arXiv no-entry is mismatch while Crossref 404 is unavailable (defensible, document), empty arXiv title -> mismatch rather than unavailable.
- Task 3: fix round 2/5 sent and done d34daa3, re-review dispatched (haiku)
- Task 3: complete (commits 395e35e..d34daa3, 2 fix rounds, review clean)
- Task 4: dispatched (BASE d34daa3, sonnet a2415acc7ebd5481f)
- Task 4: implementer DONE_WITH_CONCERNS 7fd386c (74 pytest, e2e ok, release 94 draft lines). Concerns: DTW length ignore dropped, controller-unlisted mapping choices (question ids, starts, finance split), extra sector 'about', shots.mjs preview, empty fields need no source.
- Task 4: review Approved with Important points. Controller check: Silhouette cond and all sector `about` texts are in the mockup (not invented), finance `dynamics` text from the brief.
  - Ruling: question text/starts and sector about/curve are recommendations shown on the home, so they get the same derived review gate — design 5.1 marks sector cards draft and release refuses unreviewed recommendations — cost: small extra records.
  - Fix round 1 sent (FIX_BASE 7fd386c): question/sector gate, parametrised fingerprint-coverage test, preview-in-dist writes nothing.
  - Task 4: minor (deferred): cond/tag cond no own support requirement, no test for record-item/record-fit refusing stale fingerprint, failed release leaves no output (untested), e2e header comment run-on, banner only when drafts exist.
- Task 4: fix round 1 done e0d74e1 (86 pytest, e2e ok, release 107 draft lines). Re-review dispatched.
- Task 4: complete (commits d34daa3..e0d74e1, 1 fix round, review clean)
- Task 5: dispatched (BASE e0d74e1)
- Task 5: implementer DONE 1217957 (86 pytest, e2e ok incl. no-JS). Controller looked at light/dark 1440 crops: matches mockup. Review dispatched.
- Task 5: review Needs fixes. Ruling: planned lessons plain li.coming (no link) accepted, home carries li#lesson-<id> — pilot e2e forbids links to planned lessons — cost: none. Ruling: figures to column width — design 4.1 one width for everything. Ruling: no-JS contents fallback below 1180 — design 4.1 pages read without JS.
  - Fix round 1 sent (FIX_BASE 1217957): phone drawer full width, figure width, no-JS contents, finance bg computed check, ## title math/code test.
  - Task 5: minor (deferred): a.gh and course name hidden on phones, nav h2 before h1 in outline, KaTeX duplicated in jump/toc labels, tablist lacks aria-controls/tabpanel (Task 7), possible unused imports in build.py.
- Task 5: fix round 1 done 9427e72 (87 pytest, e2e ok). Re-review dispatched.
- Task 5: complete (commits e0d74e1..9427e72, 1 fix round, review clean)
  - Task 5: minor (deferred, owner packet): static figures now scale to 760 px, so SVG label text grows about 1.46x on desktop. Design 6 says live figures redraw at real width (checkpoint 2). Show the owner.
- Task 6: dispatched (BASE 9427e72)
- Task 6: implementer DONE 0cc37ce (87 pytest, e2e ok). Controller checked: sakoe78 shows Cited in lesson 5 (implementer's 'every source not cited' claim inaccurate, harmless); looked at map 1440 light and sectors 1440 dark. Minor: finance second question wraps unaligned. Review dispatched.
- Task 6: review Needs fixes. Ruling: NEED_LABELS accepted as UI vocabulary for a fixed tag set (like the plan's ignore labels), not claims — cost: owner may reword at review. "None of the listed properties" dropped (a claim the data does not make).
  - Fix round 1 sent (FIX_BASE 0cc37ce): drop empty-ignores sentence, phone filter CSS, dict lookup.
  - Task 6: minor (deferred): span.ln name reuse on sources page, rule after figure-classes marker, no dark e2e for draft marks, no assertion of absent "free" label.
- Task 6: fix round 1 done a0e0822 (87 pytest, e2e ok). Re-review dispatched (haiku).
- Task 6: complete (commits 9427e72..a0e0822, 1 fix round, review clean). Duplicate item names are rejected by atlas (Task 4 test), so the dict lookup is safe.
- Task 7: dispatched (BASE a0e0822)
- Task 7: implementer DONE 5d485d9 (87 pytest, e2e ok). Concerns: smoke kaufman90 added, ignore AND matrix, dimmed chips opacity .45 below 4.5:1, no connector lines. Review dispatched.
- Task 7: review Needs fixes. Ruling: connector lines implemented with a root box (owner-approved mockup had root + lines, design 5 constrains them) — cost: small DOM addition in pages.py. Ruling: dimmed chips keep 4.5:1 text — design 4.1 contrast. Popover tab order folded in (cheap a11y).
  - Fix round 1 sent (FIX_BASE 5d485d9).
  - Task 7: minor (deferred): no Home/End on tabs, legacyCopy untested and no focus restore, decodeURIComponent on malformed href, code language not remembered, 375 px scrim-click point may hit the nav.
- Task 7: fix round 1 done a9fb273 (87 pytest, e2e ok). Only root-to-Compare line in the 760 column (branches 1+2 layout). Re-review dispatched.
- Task 7: fix round 1/5 (3 addressed, 1 new open — popover links inherit finance link colour; commits 5d485d9..a9fb273). Round 2 sent.
- Task 7: complete (commits a0e0822..cf86881, 2 fix rounds, review clean)
  - Task 7: minor (deferred, owner packet): only one connector line (root to Compare) in the 760 px column, since Group and Validate sit below. Popover hover colour unmeasured.
- Task 8: dispatched (BASE cf86881)
- Task 8: implementer DONE a908cf2, c351d05 (88 pytest, e2e ok). Deviations: section entries not matched on lesson title alone, extra lesson-level entry. Review dispatched.
- Task 8: complete (commits cf86881..c351d05, review clean)
  - Task 8: minor (deferred, carry to Task 9): #results .draft spacing may be flush; e2e asserts planned-lesson href but not that #lesson-beta exists; q.form assumption; Unicode mark length.
- Task 9: dispatched (BASE c351d05), Steps 1-6 (Step 7 owner packet by controller)
- Task 9: implementer DONE f4b24fa (88 pytest, e2e ok, contrast matrix no failures, 16 shots, 4 matched, release exit 1 draft-only). Review dispatched.
- Task 9: review Needs fixes (body-text classification by tag weakens 10:1 for inline normal-colour text). Fix round 1 sent (FIX_BASE f4b24fa): colour-based body rule, bodyScope, 4.48 self-check, inline clip guard, no-op key.
  - Task 9: minor (deferred): drawer state measured only at 820, other states at 1280; figure background matched by bounding box.
- Task 9: fix round 1 done d9cd733 (e2e ok, no row between 4.5 and 10 under colour-based rule). Re-review dispatched.
- Task 9: complete (commits c351d05..d9cd733, 1 fix round, review clean). ALL TASKS COMPLETE.
- Final review: sent to Codex (request docs/research/2026-10-29-codex-cp1-branch-review-request.md). Preview served via symlink .mockups/preview -> ../preview on 60610.
- Final review (Codex, docs/research/2026-10-29-codex-cp1-branch-review.md): ready after changes, 7 Important (fingerprint whitespace and field boundaries, map refs without source identity, classification/question dependencies, cond support, fixed-block fragments, symlinked dist, contrast roles in finance/measure), Minor caption text in review.py show, scrim assertion, output-preservation wording.
  - Ruling: all 7 Important plus 3 Minor fixed in one wave; old review records re-recorded after the fingerprint version change, real lesson text checked unchanged first — the version change invalidates every record by design — cost: re-recording only.
  - Fix wave dispatched (FIX_BASE d9cd733, sonnet), brief final-fix-brief.md.
- Fix wave done 7f28d4f (113 pytest, e2e ok, release draft-only). Trailer reads Sonnet 5.5 (not amended: history rewrite needs owner ok). Scoped re-review dispatched.
