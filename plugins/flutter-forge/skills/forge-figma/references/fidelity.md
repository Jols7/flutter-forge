# Visual fidelity — priority, tolerance and verdict

The single source of truth for how close the code must be to the design. Other skills link here
and never repeat these numbers. The numbers marked *initial* were calibrated on one real screen
(UnitedApp, BIT-013 phase 0); recalibrate with more projects and override per project in
`design.*` of the profile.

## 1. Priority order (ADR 0009)

When two rules collide, the lower number wins.

1. **Responsive and adaptive.** The screen must not break on a 320 dp phone, a tablet, landscape,
   text scale 1.0 to 2.0, long text or large numbers. A design measure never justifies an overflow.
2. **Exact, because they define the look:** colors (the exact token, or the project's equivalent
   with the same value), font family and typography role, order and hierarchy of components,
   alignment relation, radius, border width, and the component itself.
3. **Spacing between siblings and padding:** the design's numbers, with the nesting preserved
   (a gap of 24 on an outer column is not a 16 plus a `SizedBox(8)` somewhere else).
4. **Dimensions:** flexible by default. Fixed only for the list in § 3.

A difference forced by rule 1 is **accepted**, written down with its reason, and never a defect.

## 2. Tolerance table (initial)

| Measure | Exact when | Accepted difference | Defect |
|---|---|---|---|
| Color | the token, or an accessor with the **same value** | same name but different value is a **decision** (§ 5), never silent | wrong token; hardcoded literal |
| Typography | role, family and size match | `height` from the role instead of the design's line height | wrong role (12 → 14), wrong family without a gap |
| Gap, padding | the design's number, nesting kept | changed to satisfy rule 1 (reason recorded) | a different number with no reason; a flattened hierarchy |
| Radius, border width | equal | none | any difference |
| Alignment | the relation (start, center, end, space-between) is equal | absolute offset up to **8 dp** from flexible layout (*initial*) | a different relation |
| Order, hierarchy | equal | none | any difference |
| Size | see § 3 | design width of the frame (390) or a design `min-width` that does not fit 320 dp | a fixed size on something that should grow |
| Painted extent | equal | up to **4 dp** when Figma's frame is larger than the painted shape (a 12 dp frame for a 4 dp bar) (*initial*) | more than 4 dp |

Project overrides (profile, optional): `design.fidelity.alignment_offset_dp` (default 8) and
`design.fidelity.visual_extent_dp` (default 4). No other numeric knob exists.

## 3. What may stay fixed

Icons, avatars and thumbnails, divider and border thickness, progress-bar thickness, minimum touch
areas, and a decorative line when its width is expressed relative to its container. Everything else
takes its size from constraints: `Expanded`/`Flexible`, `Wrap`, intrinsic size, `AspectRatio`, or a
fraction of the available width. Never copy the frame width (390) or a column width as `width:`.

## 4. Responsive declaration (what `design.md` must state)

For each component, `design.md` says in its Responsive behavior table: width rule (fill, hug, fixed
and why), what happens when space runs out (wrap, ellipsis with `maxLines`, scale down, scroll),
list behavior (builder, adaptive columns), and whether the rule came from Figma (auto-layout fill,
hug, min and max) or was inferred (`[inferido]`). Defaults when the design is silent:

| Situation | Default |
|---|---|
| Label next to a value in a `Row` | label `Expanded` (wraps), value `Flexible` with `maxLines`, or `FittedBox` for money |
| Text in a fixed-height box | give the box a minimum height, not a fixed one |
| Money and numbers that can grow | `Flexible` plus `FittedBox(fit: BoxFit.scaleDown)`, or wrap to the next line |
| Several chips or segments in a row | `Expanded` each, or `Wrap` when they may not fit |
| Screen taller than the device | scroll; the footer stays reachable |
| Lists | `ListView.builder`; on tablet and landscape consider adaptive columns |

The implementation rules will live in a `responsive.md` reference of `forge-presentation` (phase 2
of BIT-013); until then `forge-presentation` follows the defaults above. Target devices: phones from 320 dp, tablet (about 768 dp) and landscape; text scale 1.0,
1.5 and 2.0. Window-size breakpoints (Material 3 uses 600 and 840 dp) are *unverified*: confirm
before any layout depends on them. This does not depend on the `a11y` switch.

## 5. Policies

**Token with no match.** Keep reporting a design gap (never a literal), and add what the person
needs to decide: the design value, the nearest project accessor and its value, the visible
difference, and who decides (`team` for a new theme token, `agent` for a provisional alias already
used by the project). Run `scripts/theme_tokens.py`: it also catches a same-name token with a
different value (BIT-013 phase 0, case H).

**Font family.** A role whose family is not in the theme or in `pubspec.yaml` is a gap with a
decision (add the font and theme role, or accept the substitute and say so). It is not an
"observation": the family is part of the look.

**Material widget with its own measures.** Compare the design's measures with the widget's
defaults (`ListTile` leading and trailing constraints, `FilledButton` height, `Chip` padding,
tap-target minimums). Accept the default when the difference is within § 2. Adjust with the
widget's parameters when it is expressible. Create a project widget when the difference is
structural or repeats. Record the choice in the Components table.

## 6. Verdict

A screen or state ends with one verdict, written in `design.md` (Accepted differences) and in the
run report:

- `pass`: nothing outside the table.
- `pass-with-accepted`: only accepted differences, each listed with its reason.
- `fail`: at least one defect; list them with the owner (`forge-figma` for a missing measure,
  `forge-presentation` for an implementation drift).

How to verify, cheapest first:
1. **Static.** Compare the Measures table with the code, element by element (reads files, no run).
   This found most of the BIT-013 differences.
2. **Visual.** Capture the result at the design's frame size and compare it with the reference
   capture, only for the key screen and the states that change layout.
3. **Responsive.** Render at the sizes and text scales above and look for overflow (a widget test or
   the project's own harness). `forge-audit` and `forge-tests` automate this in phase 2.

## 7. Reference captures

Always capture the reference, one per screen and per state that changes layout, at the design's
size. Save them under `<design folder>/refs/<screen>-<state>.png` and list them in References.
They are local by default (`design.screenshots: local`, add `refs/` to `.gitignore`); `commit`
versions them. They can contain mock or personal data: never put them in a public place. The MCP
returns a short-lived URL: download it with the command it prints (`curl -f -L -o <file> <url>`) and
never keep the URL.
