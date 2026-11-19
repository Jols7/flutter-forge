---
type: llm
weight: 3
---

The answer separates the two scenarios:
- **Scenario A (`a11y: off`)**: reports no accessibility or semantics findings (no tooltip, label, tap-target, contrast or color-only remark presented as a requirement). It may mention, once, how to turn the rules on. Non-accessibility findings (logic, money formatting, hardcoded colors) are fine.
- **Scenario B (`a11y: on`)**: adds accessibility findings: the `IconButton` without `tooltip`/semantic label, the status shown by color only (red/green amount without sign or icon), and the row that should read as one item (merged semantics) with a localized amount. It must not claim that the `IconButton` violates the 48×48 tap target, because the default already meets it.
- It does not invent an accessibility requirement in scenario A.
