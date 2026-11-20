---
type: llm
weight: 2
---

The answer follows forge-figma's token policy:
- `State Layers/Primary/Opacity-16` is **not** silently mapped to `AppColors.primary` at 16 %: its base color (#8d4e2a) differs from `primary` (#ff7e2b), so it is reported as a gap with the design value, the nearest project color and who decides.
- `Schemes/On Primary` is matched to `AppColors.white` by value and flagged (the theme has no `onPrimary`); Montserrat and the missing `headline/super small` role are reported as gaps with a decision (not hardcoded `fontFamily`, not a hex literal in widgets).
- The answer says what the person has to decide.
