# Responsive and adaptive layout

The single source of truth for how a screen adapts. `forge-figma` declares the behavior per
component (Measures and Responsive behavior in `design.md`; priority in
`../../forge-figma/references/fidelity.md` § 1), this file says how to build it, `forge-tests`
proves it (`../../forge-tests/references/widget-tests.md` § Responsive matrix) and `forge-audit`
points at the lines to check (`../../forge-audit/scripts/check_responsive.py`). It does **not**
depend on the `a11y` switch: a screen that breaks at large text is a layout defect.

## Targets

| Axis | Values |
|---|---|
| Phones (dp) | 320×568, 360×640, 390×844, 412×915 |
| Tablet | 768×1024 |
| Landscape | 844×390 |
| Text scale | 1.0, 1.5, 2.0 |
| Content | the longest label the ARB can produce; the largest amount the contract allows (for example `$9,999,999,999.99`) |

Window-size classes (Material 3 uses 600 and 840 dp) are *unverified* here: confirm the values in
the project's Flutter version before a layout branches on them.

## Rules

| Situation | Build it as | Never |
|---|---|---|
| Label next to a value in a `Row` | label `Expanded`, value `Flexible` (+ `FittedBox(fit: BoxFit.scaleDown)` for money, or `maxLines` and ellipsis for text) | a bare `Text` beside an `Expanded` |
| Several labels in one row | `Wrap`, or one `Expanded` per item | `Row` of bare `Text`s |
| Equal items (chips, segments) | `Expanded` each; `Wrap` when they may not fit | a fixed width per item |
| Width from the design | constraints from the parent; a fraction (`FractionallySizedBox`, `LayoutBuilder`) for a decorative line, of the reference `design.md` names (default: the available width) | `width: 343` copied from the frame |
| Height around text | minimum height (`ConstrainedBox(minHeight:)`, padding) | a fixed `height` that clips at 2.0 |
| Fixed size | only icons, avatars, thumbnails, divider and border thickness, progress-bar thickness, minimum touch areas (`../../forge-figma/references/fidelity.md` § 3) | fixed boxes for anything that holds text |
| Screen taller than the viewport | `SingleChildScrollView` or slivers; the primary action in the footer stays reachable | a `Column` that overflows |
| Forms | scrollable body (`resizeToAvoidBottomInset`), the focused field stays visible | a form the keyboard covers |
| Lists | `ListView.builder` / slivers; on tablet and landscape consider two columns or a max content width | `ListView(children: items.map(...))` |
| Tablet | cap the content width with `ConstrainedBox(maxWidth:)` and center it (the value comes from the design or the project) | stretching a phone layout across 768 dp |
| Screen size | `MediaQuery.sizeOf`, `paddingOf`, `textScalerOf`, or `LayoutBuilder` for the parent's width | `MediaQuery.of(context).size` |
| Images | `AspectRatio` or a bounded box + `fit`; decode large images with `cacheWidth` | an image with a frame-sized width |
| Notches | `SafeArea` | content under the status bar |

## Building from `design.md`

1. Implement the Measures table **exactly**: spacing, padding, radius, border, alignment, type role and
   color token per element. The layout tree's gaps are equally normative; if the two disagree, ask or
   follow the tree and note it.
2. Keep the nesting of the layout tree. Each level with its own gap is its own `Column`/`Row`
   (`spacing:` of that level). Do not flatten two levels into one list with spacers: an outer gap of
   24 is not a 16 plus a `SizedBox(8)` somewhere else.
3. Apply the Responsive behavior table row by row. A row marked `[inferido]` is a default of
   `forge-figma`; keep it unless the person says otherwise.
4. A design measure that would cause an overflow loses to the rule above; record the difference as
   accepted in `design.md` (Accepted differences), never silently.
5. When there is no `design.md` (isolated change), apply this file's rules to the code you touch and
   leave the rest as it is.

## Verify

Run `../../forge-audit/scripts/check_responsive.py` on the files you wrote and fix its findings, then
let `forge-tests` render the page across the targets. A `row-text-no-flex` finding is a real
overflow risk until proven otherwise.
