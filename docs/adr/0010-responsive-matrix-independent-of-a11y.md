# ADR 0010 — Responsive layout robustness is always on (amends ADR 0008)

- Status: accepted
- Date: 2026-11-19
- Entry: BIT-013 (phase 2)
- Amends: ADR 0008 (accessibility opt-in), only the text-scale test

## Context

ADR 0008 made accessibility opt-in and, with it, the text-scale 2.0 test (`widget-tests.md`,
`accessibility.md`). With `a11y: off` (the default) nothing then rendered a screen at large text,
long labels or small phones. BIT-013 phase 0 measured 23 of 54 size / text-scale combinations
overflowing on a real screen, none of them detected by any skill.

## Decision

- **Layout robustness is not accessibility.** Rendering at several sizes, text scales and longest
  content is a layout test and always runs; semantics (labels, order, guidelines, tap targets) stay
  opt-in behind `a11y`.
- **One source for the targets:** `forge-presentation/references/responsive.md` § Targets (phones from
  320 dp, tablet, landscape; text scale 1.0, 1.5, 2.0; longest content). `forge-tests` links to it and
  runs the matrix (`widget-tests.md` § Responsive matrix, helper `pumpAppAt`); `forge-audit` points at
  risky lines with `check_responsive.py`.
- ADR 0008 is otherwise unchanged: with `off` no skill requires or reports semantics.

## Consequences

- Runs with `a11y: off` now include a responsive matrix per new or changed page and text-holding
  shared widget. Cost: extra widget tests (about 15 per page at the full matrix); keep it to the
  states that change layout.
- `forge_demo` needed one fix (a bare balance `Text` beside an `Expanded` in `AccountCard`).
- Material 3 window-size breakpoints (600 and 840 dp) remain unverified and unused.
