# Dark theme: what we learned on "AI, one token at a time"

> Copied 2026-10-28 from a scratchpad of the ai-one-token-at-a-time session, sent on the owner's request. Binding for this course's dark theme (approved by the owner for the other course). Applies in the pilot plan via `site/theme.css`.

Source project: `/home/maxto/projects/personal/ai-one-token-at-a-time` (live: https://maxto.github.io/ai-one-token-at-a-time/).
Reference implementation: `site/template.html` lines 7-73 (CSS variables) and 182-207 (figure classes).
Full history with reasons: that repo's `LOG.md`, the three entries of 2026-10-28 about the dark theme.
Max approved every point below after three rounds. Use them as the starting point for this course's dark theme.

## 1. Principles (the mistakes we made first)

- **No near-black.** Use a "dimmed" dark theme. Our first version (bg `#10131a`, surface `#171b24`) looked flat: top bar, cards and title chips blended into the page. Max's complaint was "too dark, no contrast".
- **The problem is structure, not only text contrast.** Text already passed WCAG AA, yet the page felt flat because surfaces, borders and chips were too close in tone. Keep clear steps between layers: page < card < chip/raised box, and borders visible against both.
- **Cards stay lighter than the page** (surface on bg). Do not make cards darker: at about 1.07:1 against the page they disappear.
- **Fix it in CSS variables, not in each figure.** Figures use classes mapped to theme variables, so one change fixes all figures. Do not hand-edit SVG colours per figure.
- **Light theme must stay pixel-identical** when you change dark: point the new light variables at the old light values (e.g. `--fig-box: var(--surface)`).
- **Do not flip the figure background back and forth.** Max rejected a variant where the figure panel went back to the card colour. Pick one and keep it.

## 2. The palette that was approved (dark only)

Page and text:

| Variable | Dark value | Role |
|---|---|---|
| `--bg` | `#1c2029` | page |
| `--surface` | `#262b37` | cards, top bar |
| `--ink` | `#f2f4f8` | main text |
| `--ink-2` | `#ccd2de` | secondary text |
| `--muted` | `#a3aabb` | labels, meta |
| `--rule` | `#3e4657` | borders, dividers |
| `--chip` | `#333a49` | chips, hover |
| `--accent` / `--accent-ink` / `--accent-soft` | `#8ca3ff` / `#0b0e14` / `#2c3768` | links, buttons, highlighted |
| `--good` / `--good-soft` | `#69db7c` / `#1c3526` | |
| `--warn` / `--warn-soft` | `#ffa94d` / `#3a2b17` | |
| `--bad` / `--bad-soft` | `#ff8787` / `#3e2023` | |
| `--line` | `#8d98b0` | box borders in figures |
| `--on-fill` | `#0b0e14` | text on a solid colour fill |

Figures ("variant C": dark panel, lighter raised graphics inside):

| Variable | Dark value | Light value | Role |
|---|---|---|---|
| `--fig-bg` | `#171a21` | `var(--surface)` | panel behind the figure, darker than the card |
| `--fig-box` | `#353c4c` | `var(--surface)` | plain boxes, raised above the panel |
| `--fig-soft` | `#333a49` | `var(--chip)` | soft filled areas |
| `--fig-muted` | `#ccd2de` | `var(--muted)` | small figure text, muted lines/fills, caption |
| `--fig-ghost` | `#8d98b0` | `var(--chip)` | deliberately faint shapes |
| `--soft-mix` | `28%` | `16%` | how much of a category colour goes into its tinted fill |

Category colours are brighter in dark (e.g. blue `#748ffc`, purple `#da77f2`, teal `#3bc9db`, green `#69db7c`, orange `#ffa94d`). Tinted fills: `color-mix(in srgb, <colour> var(--soft-mix), var(--surface))`. Text in that colour: `color-mix(in srgb, <colour> 78%, var(--ink))`.

## 3. Figure rules

- Small text (≈11-13px) must reach at least 4.5:1 on **every fill it can sit on**, including tinted boxes. Our first attempt had small labels at 3.2:1 on module tints. That is why small figure text uses `--fig-muted` (`#ccd2de`), not the page `--muted`.
- A 16% tint is invisible in dark. Use about 28%.
- Plain boxes filled with the card colour only show a thin border: give them their own lighter fill (`--fig-box`) above a darker panel.
- "Faint on purpose" elements keep an order: if a sequence shows something emerging, each step must be brighter than the previous one. Check that a contrast fix does not invert it (we had to use `#8d98b0`, not `#ccd2de`, for that reason).
- For charts with data (time series, clusters), keep series colours distinguishable in both themes. Check each series colour against the panel (`--fig-bg`), not only against the page.

## 4. How to verify (what we actually ran)

1. Compute WCAG contrast for every text colour on every background it sits on: body text should be 10:1 or more, secondary and small text at least 4.5:1 (we reached 4.7:1 or better everywhere).
2. Render every figure in dark (headless Chrome with `colorScheme: 'dark'`) and look at a sample from different sections side by side, before and after.
3. Render all light figures and pixel-compare with the previous run: 0 differences expected.
4. Screenshots of home, a lesson and a figure in dark, looked at by Max.
5. Make the e2e test check the dark body colour.

## 5. Open points we left (do not decide them silently)

- Tiny labels on phones: at a 420px minimum SVG width, an 11.5px label renders at about 8.6px. This is size, not colour. To check on a real phone.
- Search box placeholder in dark: an explicit `var(--muted)`, opacity 1, was proposed. Max found the default readable, so it was not done.
