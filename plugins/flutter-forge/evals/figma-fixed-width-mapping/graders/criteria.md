---
type: llm
weight: 2
---

The answer applies forge-figma to the pasted CSS:
- It does **not** copy the frame widths (`343`, `311`, `149`, `139`) as `width:` on the card, header, title, amount or rows: the card fills its parent and children use `Expanded`/`Flexible`, so the layout fits a 320 dp phone.
- It keeps the exact padding (16), gaps (16 and 8, one per nesting level), radius (16) and 1 px border, and maps colors to `AppColors` tokens and fonts to text theme roles (no `Color(0xFF…)` literals, no hardcoded `fontFamily`).
- It says, briefly, what it made flexible and why (responsive behavior, or the fixed widths it dropped as accepted differences).
