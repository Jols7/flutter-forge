---
type: llm
weight: 2
---

The answer applies forge-presentation's responsive rules to the specification:
- It keeps the two nesting levels as separate `Column`s with their own `spacing` (16 and 8) instead of flattening them into one list with spacers, and keeps the exact radius, border, type roles and color tokens (no hex, no `TextStyle(fontFamily…)`).
- The header's amount and each row's value are `Flexible` (with `FittedBox(scaleDown)` or equivalent) beside an `Expanded` label/title, so nothing overflows at 320 dp, text scale 2.0 or `$9,999,999,999.99`; no frame widths or fixed heights around text.
- It mentions verifying with `check_responsive.py` and/or the responsive matrix of `forge-tests` (sizes × text scales), and does not tie any of that to the `a11y` switch.
