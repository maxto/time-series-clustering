# SDD ledger — plan: docs/superpowers/plans/2026-10-28-pilot.md

Spec: docs/superpowers/specs/2026-10-28-course-design.md (approved 2026-10-28).
Branch: pilot (from master 196e416). Ruling: branch in the same checkout, no worktree — master stays untouched and no new Orca workspace is needed — if wrong, the branch moves to a worktree with no loss.
Global constraints for reviewers: global-constraints.md in this directory.

## Pre-flight scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 -> T3 | fixture CSV schema (ids, hour_group, shape_group, v00..v47) vs load_demand | consistent |
| T2 -> T3 | znorm, euclidean, dtw, sbd signatures vs grouping tests | consistent |
| T2 -> T4 | dtw contract vs R dtw_distance, parity CSV | consistent |
| T3 -> T6 | average_linkage, silhouette_from_matrix vs numbers.json `silhouette_dtw4_k2` | T3 sklearn test does not state k. Ruling R1 |
| T5 -> T7 | 00-smoke.md vs T7 "delete smoke, move assertions onto lesson 5" | lesson 5 only exists in T8, and lesson 5 has no fenced `##`. Ruling R2 |
| T5 -> T6 | `{{n:key}}` substitution vs numbers.json created only in T6 | T5 build must work without numbers.json. Ruling R3 |
| T5 (self) | F-group edge tests chosen by the owner vs "check by hand once" for TeX error and planned skip | owner chose them as tests. Ruling R4 |
| T5 -> T6/T7 | SVG validator rules vs generated and hand-made figures | consistent (role=img, title, classes) |
| T1 -> T5/T9 | package.json scripts `test`, `shots` vs files created in T5, T9 | consistent (scripts may point to later files) |
| T1 (self) | fixture design vs T3 recovery tests | consistent, tuning loop declared |
| T2 (self) | tests vs signatures, hand values checked by Codex and by hand | consistent |
| T3 (self) | E test wording ("all off-diagonal equal ... 4 identical points k=2") | ambiguous wording. Ruling R5 |
| T4 (self) | consistent |
| T6 (self) | consistent |
| T7/T8 (self) | prose punctuation rule vs content | consistent, enforced by build |
| T9 (self) | consistent |

## Rulings

- R1: `silhouette_dtw4_k2` and the T3 sklearn test use k=2 with average_linkage on the DTW w=4 matrix — the key name says k2 and the lessons use two groups — if wrong, one constant changes.
- R2: the smoke content becomes a permanent test fixture: `tests/fixtures/smoke/` (manifest + 2 published lessons + 1 planned lesson between them + a figure), built by `scripts/build.py --content <dir> --dist <dir>` into `tests/output/smoke-dist/`. e2e runs the smoke assertions there and the general assertions (navigation, no external requests, theme, 375 px) on the real `dist/`. T7 has no smoke file to delete — keeps the fenced-`##`/TeX/link assertions alive after the pilot instead of losing them — cost if wrong: one extra test folder.
- R3: build loads `content/figures/numbers.json` only if it exists; a `{{n:...}}` placeholder with no file or no key is an error — T5 runs before T6 — no cost.
- R4: F-group checks automated: `tests/test_build.py` (pytest via uv) builds temp content with `$\frac{$` and asserts exit 1 naming the file; the planned-lesson skip is asserted in e2e on the smoke fixture — the owner chose these as tests — cost: a few seconds of test time.
- R5: E test = 4 identical series (all-zero distance matrix) with k=2 must raise ValueError (maxclust yields 1 cluster); a 3-point matrix with distinct distances and k=3 returns 3 labels — matches the intent "too few clusters detected" — no cost.

## Progress
- Task 1: dispatched (BASE 196e416, implementer sonnet)
- Task 1: complete (commits 196e416..6a8bc72, review clean, 7 minor noted)
  - Minor noted: "local-timing" variant is a global ±0.5 h shift, not a local warp (make_fixtures.py:61-76). Ruling: keep for the pilot — lessons 1 and 5 need only global shifts (mon/sat is a 1.5 h shift) — if lesson 5 text claims local warping on this fixture, Task 8 must not say so. Carry to Task 8 dispatch.
  - Minor noted: AGENTS.md layout lists files not yet created. Ruling: Task 5 implementer re-checks AGENTS.md layout against reality.
- Task 2: dispatched (BASE 6a8bc72, implementer sonnet)
- Plan amended (owner, via ai-one-token session): approved dark palette + figure variables from docs/design/dark-theme.md replace provisional dark tokens; Task 5 theme.css and e2e dark body check, Task 9 contrast step. global-constraints.md regenerated. Commit after Task 2 lands.
- Task 2: complete (commits 6a8bc72..5b0dea3, review clean, 4 minor noted)
  - Ruling: reviewer omitted the explicit "Task quality" line; spec ✅ and no Critical/Important, so read as Approved — cost if wrong: none, findings are all Minor.
  - Minor noted: tie-break order of dtw_path not pinned by a test; w=True and np.int64 windows untested; sbd may return -1e-16 for identical inputs; helper type hints. Ruling: parked for the final review wave — figure reproducibility is checked in Task 9 by regenerating with no diff.
- Task 3: dispatched (BASE 816e04e, implementer sonnet)
- Task 3: complete (commits 816e04e..3197dda, review clean, 5 minor noted). Fixture frozen. Values: ARI hour 1.0, ARI shape 1.0, hour vs shape -0.1, mon/sat dtw4 0.2171 vs euclid 3.7144, DTW silhouette k2 0.5257.
  - Minor noted: average_linkage reports NaN as "not symmetric"; load_demand lacks type hints and fails with IndexError on empty file; cramped one-liners with ";" in test_validity.py. Parked for the final review wave.
- Task 4: R dtw 1.23.3 installed in user library by controller (owner-approved library). Dispatched (BASE 3197dda, implementer sonnet)
- Task 4: complete (commits 3197dda..a99b2bc, review clean, 5 minor noted). R 4.6.1, dtw 1.23.3, worst diff 0 (reviewer re-ran, id-matched, independent).
  - Minor noted: stale py CSV not detected if R script run alone; R accepts w=4.0 where Python rejects; diagonal assumed 0. Parked for final review.
- Task 5: dispatched (BASE a99b2bc, implementer opus — multi-file engine with design judgment). Rulings R2-R4 carried; extra rulings: build exits 0 with a note when content/_course.md is absent; previews only for default content; e2e real-dist part skips until content exists.
- Owner (2026-10-28, mid-run): "content first, code later, starting from existing libraries" — meant for the course; pilot continues to the end as is. Ruling: from Task 5 on, task reviews are done by Codex (GPT-6 Astra) in its Orca pane as adversarial reviewer (request/answer files in this workspace), replacing Sonnet task reviewers — owner asked for Codex adversarial review "as usual" and cross-model review catches more — cost if wrong: slower turnaround per task. Final whole-branch review: Codex too.
- Task 5: implementer DONE df22549 (npm test green, 37 pytest). Codex review requested (task-5-codex-request.md -> task-5-codex-review.md).
- Task 5: Codex review = Needs fixes (3 Important: small-text contrast <4.5:1; fragment links without heading ids, http accepted vs message; real-course nav assertions vacuous). Review file task-5-codex-review.md.
  - Ruling (contrast vs exact tokens): token values stay as constrained (brand); affected small text switches to --ink-2 / a stronger figure text class — keeps the exact-token rule and meets 4.5:1 — cost if wrong: slightly darker meta text.
  - Task 5: minor (deferred): numbers.json non-object values give TypeError; SVG viewBox not numerically validated and external marker URLs pass; light cards/pager get white backgrounds absent from mockup (Ruling: accept, owner judges in Task 9 screenshots); notes after pager at 375 px (check in Task 9); Pages needs master + content (expected).
- Task 5: fix round 1 implemented e5c6986 (38 pytest, npm test green, mutation check on nav). Codex scoped re-review requested.
- Task 5: fix round 1/5 (3 addressed, 0 open; commits df22549..e5c6986). Codex re-review clean.
- Task 5: minor (deferred): e2e manifest reader needs exact spaces around pipes and no CRLF (false failures only).
- Task 5: complete (commits a99b2bc..e5c6986, review clean after 1 fix round)
- Task 6: dispatched (BASE e5c6986, implementer opus — visual judgment). numbers.json values as 2-decimal strings (Task 5 concern).
- Task 6: implementer DONE_WITH_CONCERNS f147268 (figure scale at 1280, light --line 2.04:1 links, 10.4 px labels at 375). Codex review requested.
- Task 6: Codex review = Needs fixes (2 Important: shading descriptions false in dark + no local-cost key; series colours vs constraint).
  - Ruling (Important 2, conflicts with plan text): grouping figures colour by group, two-series figures keep A ink / B accent. The controller's dispatch asked for this and Codex allowed an explicit amendment; plan Global Constraints amended (uncommitted doc edit, committed with the next docs commit). Cost if wrong: re-colour three figures.
  - Task 6: minor (deferred): alignment links use .ln-soft 2.04:1 (use .ln-muted 4.54:1); size cap ~520 px for generated charts + small labels 13 units; dtw-window axis cues (i/mon ↑, j/sat →) and half-cell offset of side traces; ineffective stroke-width="1.5" attributes. Final review to triage (visual, before owner review).
- Task 6: fix round 1 implemented ef3e721; plan colour amendment committed; Codex scoped re-review requested.
- Task 6: fix round 1/5 (1 addressed, 0 open; commits f147268..ef3e721). Codex re-review clean. Desktop captures to be retaken unobstructed at final visual review.
- Task 6: complete (commits e5c6986..ef3e721, 1 fix round; Important 2 settled by ruling 5295eff)
- Ruling for Task 7: lesson 5 is `planned` in the manifest until Task 8 creates its file and flips it to `published` — published entries need a file — no cost.
- Task 7: dispatched (BASE 5295eff, implementer opus — content writing).
- Task 7: implementer DONE d5c44b6 (build, npm test incl. real dist, 38 pytest). Committed 7 preview SVGs. Codex review requested.
- Task 7: Codex review = Needs fixes (2 Important: "by ignoring the other" implies Euclidean ignores shape; finance note overreaches). Claim "z-norm alone or SBD alone still splits early/late" independently CONFIRMED by Codex. Fix round 1 sent to implementer.
  - Task 7: minor (deferred to Task 9 content pass): overview box labels ("sequence inputs" / "explicit representations", navigation families not disjoint levels); qualify SBD shift tolerance (boundary/overlap effects); label tslearn KShape as related method, not the pipeline used; overview small labels ~10.4 px at 375.
- Task 7: fix round 1 implemented 4665ec4; Codex scoped re-review requested.
- Task 7: fix round 1/5 (2 addressed, 0 open; commits d5c44b6..4665ec4). Codex re-review clean.
- Task 7: complete (commits 5295eff..4665ec4, 1 fix round)
- Task 8: dispatched (BASE 4665ec4, implementer opus — content). Carried: mon/sat is a global shift, no local-warp claim (Task 1 minor).
- Task 8: implementer DONE 364d5e1 (build, npm test, 38 pytest; 5 links resolve; added Blondel-Mensch-Vert 2021). Concern: .katex-display lacks overflow-x. Codex review requested.
- Task 8: Codex review = Needs fixes (1 Important: soft-DTW divergence stated without the source's conditions). Numbers, convention, card, specimens confirmed. Fix round 1 sent.
  - Task 8: minor (deferred to Task 9 content pass): say raw soft-DTW has no final square root (05-dtw.md:85); ".katex-display { overflow: auto hidden }" engine hardening with an over-wide display test at 375 px; "for equal-length series, with w=0" (line 54); singleton silhouettes are zero (line 134).
- Task 8: fix round 1/5 (1 addressed, 0 open; commits 364d5e1..ef52f00). Ruling: scoped re-review done by controller diff inspection — the fix is the reviewer's own two sentences inserted verbatim, one line changed — Codex sees it again in the final whole-branch review.
- Task 8: complete (commits 4665ec4..ef52f00, 1 fix round)
- Final review: whole-branch package 196e416..ef52f00 sent to Codex with deferred-minor triage (final-codex-request.md).
- Final review (Codex): Ready for owner review after listed fixes. 2 Important (stale owner screenshots; deferred visual/content items now affect the review target), 2 Minor (document distance_matrix assumptions; AGENTS.md drift). Triage: 13 FIX, 17 LEAVE (see final-codex-review.md).
  - Ruling: LEAVE items stay parked as Codex triaged them (code hardening, tests the owner may pick later, light cards white = owner to judge) — cost if wrong: a later hardening pass.
- Final fix wave + Task 9 checks dispatched (BASE ef52f00, implementer opus, one fixer with the full FIX list).
- Final fix wave DONE ef52f00..0575db2 (5 commits; checks green; labels 12.17 px at 375). Codex scoped re-review requested.
