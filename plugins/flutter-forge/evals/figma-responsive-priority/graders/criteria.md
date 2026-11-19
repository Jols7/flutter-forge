---
type: llm
weight: 2
---

The answer applies the "responsive first" priority of forge-figma:
- It does not copy 118, 71, 24 or 358 as widths or heights: the label is `Expanded` and the value `Flexible` (with `maxLines`/ellipsis, `FittedBox(scaleDown)` or wrapping), so the row cannot overflow at 320 dp, at 200 % text or with `$9,999,999,999.99`; 24 is a minimum or comes from the text.
- It keeps what must be exact: the `titleMedium` role and `onSurface` color for the value, the label's role and color, alignment and the gap, with no hardcoded literals.
- It writes the responsive behavior for `design.md` (width rule, what happens when space runs out) and names the devices to cover (phone from 320 dp, tablet, landscape, text scale up to 2.0).
