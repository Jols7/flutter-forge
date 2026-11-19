---
type: llm
weight: 2
---

The answer works in forge-figma's delta mode without a run or a story:
- It does not edit code. It lists the differences (element, design, code, fix) and finds: the flattened hierarchy (block gap 24 versus 16 plus a `SizedBox(8)`), the amount/currency gap and alignment (8, bottom aligned versus 4 centered), the wrong colors (`onPrimaryContainer`), the row type roles (`bodySmall`/`titleMedium`) and the missing 1 px border.
- The fixes keep the layout responsive: they restore the nested column with its gap instead of adding spacers, and do not introduce fixed widths.
- It names where the result lives or who applies it (a standalone design folder such as `.flutter-forge/design/<slug>/`, or `forge-presentation`), and marks anything it cannot confirm as to confirm.
