---
type: llm
weight: 2
---

The answer applies forge-figma's Material-widget policy:
- It compares the design's measures with each widget's defaults (`ListTile` height and padding versus 64 and the 40×40 avatar; `FilledButton` default height versus 40; `ChoiceChip` padding and tap-target versus 34 high chips) instead of assuming the default matches.
- For each component it chooses accept-default, adjust-with-parameters or create-a-widget, with the reason, and records it (a table or list of decisions).
- Heights are minimums and the amount cannot overflow on a narrow phone: it does not turn the avatar, row or chips into fixed boxes that can clip.
