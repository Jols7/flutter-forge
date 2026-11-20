# ADR 0009 — Visual fidelity: responsive first, one tolerance source

- Status: accepted (thresholds provisional)
- Date: 2026-11-19
- Entry: BIT-013

## Context

`forge-figma` turned designs into layouts but nobody declared how close the code had to be, and
nothing compared the result with the design. A real case (UnitedApp, BIT-013 phase 0) showed
twelve measured differences, most of them silent omissions in `design.md` or a flattened column in
presentation, and 23 of 54 size / text-scale combinations overflowing. A Sonnet control of the design
phase showed the omission came from the `design.md` contract, not from the model.

## Decision

- **Priority order** (`forge-figma/references/fidelity.md` § 1): responsive and adaptive first; then
  exact colors (token or same-value equivalent), typography role and family, order, alignment
  relation, radius, border width and components; then spacing and padding; dimensions flexible except
  a short list. A difference forced by responsiveness is *accepted* and recorded, not a defect.
- **One source of truth** for tolerance: `forge-figma/references/fidelity.md`. Other skills link to it
  and never repeat its numbers (same rule as ADR 0008). Two numeric knobs are overridable in the
  profile (`design.fidelity.alignment_offset_dp`, `visual_extent_dp`). The values are initial,
  calibrated on one screen; recalibrate with more projects.
- **`design.md` becomes a specification:** per-element measures (gap per nesting level, padding,
  radius/border, alignment, type role, color token), a responsive-behavior table, reference captures,
  design gaps with value / nearest / difference / decider, and a verdict.
- **Captures are local by default** (`design.screenshots: local`), versioned only on request.
- **Verification is agent-guided** and cheapest-first: static comparison of Measures against the code,
  then a visual comparison for key screens, then responsive rendering. No new dependency; pixel diff
  is not adopted (fonts, data and anti-aliasing give false positives) until data says otherwise.
- **Scripts, not hooks.** Deterministic work moves to scripts the skill calls at a fixed step
  (`theme_tokens.py`, `lint_design.py`). Plugin hooks are not shipped: the plugin has none, they would
  fire on every edit of any project, and the skills already call the scripts explicitly.
- **Modes without a run:** standalone (`.flutter-forge/design/<slug>/`) and delta (compare against
  existing code) so isolated work, bug fixes, design updates and visual improvements do not need
  `forge-deliver`.

## Consequences

- Phase 2 of BIT-013 changes the consumers: `forge-presentation` (a `responsive.md` reference, never
  flatten nested gaps), `forge-tests` (a responsive matrix that does not depend on `a11y`),
  `forge-audit` (`check_responsive.py`, one checklist question) and `forge-deliver` (verdict in
  `result.json`).
- That phase **amends ADR 0008**: the text-scale 2.0 test becomes layout robustness and always runs;
  semantics stay opt-in. It will be recorded in its own ADR or an addendum.
- Breakpoints (Material 3: 600 and 840 dp) are unverified and are not used until confirmed.
- BIT-009 changes only if, with the same specification, presentation still diverges between models.
