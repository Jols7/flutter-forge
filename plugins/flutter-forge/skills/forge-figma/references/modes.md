# Modes — how forge-figma is used

The skill works with or without a story (HU), and with or without `forge-deliver`. Pick the mode
from the request; when in doubt, ask one question.

| Mode | Trigger | Input | Output (folder) |
|---|---|---|---|
| **feature** | `forge-deliver` phase 2, or "maqueta esta pantalla" with a run folder | Figma nodes, brief (+ story) | `.flutter-forge/runs/<slug>/design.md` and `refs/` |
| **standalone** | A link with no run: "implementa este diseño", an isolated screen | Figma nodes | `.flutter-forge/design/<slug>/design.md` and `refs/` |
| **delta** | "el diseño cambió", "este botón no coincide con Figma", a visual improvement or a visual bug | Figma nodes + the screen's existing code | `<folder>/delta.md` (no `design.md` rewrite) |
| **verify** | "compara esto con el diseño", `forge-deliver` after presentation | `design.md` (or nodes) + code or capture | the verdict (`references/fidelity.md` § 6), appended to `design.md` |
| **css** | Pasted Figma CSS, no MCP | CSS | the widget tree in `references/css-mode.md` |

`<slug>` is the kebab-case screen or feature name. If `runs/<slug>/` already exists, use it and do
not create a second `design.md`. Standalone output is created on demand and needs no `state.json`.

## With and without a story

- **With a story or brief:** design is the source of truth for visuals, the story for behavior;
  differences go in "Differences design ↔ story" and the story wins on copy and amounts.
- **Without one:** read behavior only from the nodes. Mark every rule or state you infer
  `[por confirmar]`. Never fill a limit, a validation or a copy with a number from a mock, and never
  invent states the design does not show.

## Delta mode

For a change to something that already exists (bug, design update, visual improvement):

1. Locate the code. Take the path the person gave, else search the widget or page by name and by
   the visible texts. If several candidates remain, ask.
2. Read the Figma node (cheapest calls first, one node), and the code of that subtree only.
3. Compare with `references/fidelity.md` and write `delta.md`. When a `design.md` exists, walk its
   Measures table **row by row** and the layout tree level by level, so a difference nobody noticed
   (a gap, an alignment) is still caught; end with "rows checked N · differences M". Table:

   | # | Element | Design | Code (`file:line`) | Type | Weight | Evidence | Verdict | Fix owner |
   |---|---|---|---|---|---|---|---|---|

   *Weight*: `high` (visible at first glance or breaks a device) or `low` (cosmetic). *Evidence*:
   `static` (read from nodes and code), `visual` (compared on a capture) or `unverified`.

   Only defects and decisions are rows to act on; accepted differences are listed apart, with the
   reason; end with a verdict per screen and state (`fidelity.md` § 6). `delta.md` is where the verdict
   lives in this mode; when a `design.md` is in the same folder, it points here. A state that shares a
   layout block with another inherits that block's defects (list them once).

   A bug report limits the comparison to the reported element and its neighbors.
4. Stop there. `forge-presentation` applies the fixes (it never flattens a nested hierarchy or
   changes a shared widget's required parameters). Re-run **verify** afterwards.

## Not changing anything else

Delta and verify never rewrite an existing `design.md` section that was not affected, never touch
the widget catalog unless a component was created or extended, and report out-of-scope mismatches
as observations instead of fixing them.
