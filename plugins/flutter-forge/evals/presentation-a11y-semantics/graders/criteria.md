---
type: llm
weight: 3
---

The answer separates the two scenarios:
- **Scenario A (`a11y: off`)**: reports no accessibility or semantics findings (no tooltip, label, tap-target or color-only remark as a requirement). It may mention, once, how to turn the rules on (`a11y: on` in the brief or `accessibility.default: on` in the profile).
- **Scenario B (`a11y: on`)**: flags the `IconButton` without `tooltip`/label, the 48×48 (Android) / 44×44 (iOS) tap target, the status shown by color only (red/green amount without sign or icon), the composite tile that should be merged for screen readers, and the amount that is not localized. It points to `references/accessibility.md` as the rule source and, for tests, asks for `tester.ensureSemantics()` before `meetsGuideline`.
- It does not invent an accessibility requirement in scenario A.
