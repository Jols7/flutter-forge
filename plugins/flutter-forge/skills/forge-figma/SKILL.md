---
name: forge-figma
description: Turn a Figma design into a Flutter specification (design.md) that follows the project's theme and widgets, and verify code against it. Works with or without a story and with or without forge-deliver. Modes - feature, standalone, delta (bug, design change, visual improvement), verify and pasted-CSS. Use for a figma.com link or node, pasted Figma CSS, "maquetar este Figma", "pasar el diseño a Flutter", "el botón no coincide con el diseño", "qué widgets reutilizo"; and when forge-deliver reaches the design phase. Stops at design notes; state, navigation and wiring belong to forge-presentation.
---

# forge-figma

Output: a `design.md` that is a **specification**: tokens with values, component decisions, exact
measures per element, responsive behavior, reference captures and design gaps. `forge-blueprint`
and `forge-presentation` consume it. **The design is the source of truth for visuals; the story
(when there is one) for behavior.** When they disagree on copy or amounts, the story wins and the
difference goes in the report.

**Priority: responsive first** (`references/fidelity.md` § 1). Colors, fonts, order, alignment,
radius, borders and components follow the design exactly; dimensions are flexible so the UI never
breaks on small phones, tablets, landscape or large text.

## Step 0 — Resolve

1. **Mode** from the request (`references/modes.md`): feature, standalone, delta, verify or css.
   Output folder: `.flutter-forge/runs/<slug>/` when a run exists, else
   `.flutter-forge/design/<slug>/`.
2. Read the `design.*` keys of `.flutter-forge/profile.yaml`: colors and typography accessors, the
   spacing class, the scaffold widget, `widget_catalog`, and the optional `design.fidelity.*` and
   `design.screenshots`. Also `paths.shared_widgets` and `paths.widgets_barrel`.
3. Read `brief.md` and the story when they exist; its **Design** section lists the nodes per state.
   With no story, follow `references/modes.md` § With and without a story.
4. Check that the Figma MCP is available. If it is not connected or needs authorization, tell the
   person and continue only with screenshots or CSS they paste. If the MCP asks you to load its own
   design-to-code guidance first, load it before requesting design context (and pass the skill name
   it asks for).
5. If `.flutter-forge/overlays/forge-figma.md` exists, read it; its rules win.

## Step 1 — Read Figma, cheapest calls first

1. **Variables** on one full screen: the token set (name and value) for the whole flow.
2. **Metadata** of the frame: child nodes, and the ones per state.
3. **Design context** for **one full screen per distinct layout**, client framework Flutter/Dart.
   It carries the exact numbers (gaps per nesting level, padding, sizes, radii, type roles, token per
   text). Read them there; do not estimate from the picture.
4. For every other state, request **only the node that changes**. A token used only in that state shows
   up in its design context (CSS variable); do not call variables again per state.
5. **Screenshot** of every screen and every state that changes layout, saved to `refs/`
   (`references/fidelity.md` § 7). It is the reference for the verify step.
6. If the MCP offers code-connect mappings, read them. A mapped component is an exact reuse.

The returned code (often React + Tailwind) is a **visual reference**, never translated line by line.

## Step 2 — Resolve tokens

Run `python3 scripts/theme_tokens.py --root <project> --match "<Figma token>=<hex>" … --font <family>` with
the variables from step 1. It answers exact / value-differs / by-value / tie / overlay / gap for each
token and which fonts are missing, so no color file is read by hand. A `value-differs`, an overlay
with a different base, a missing font or a tie is a **design gap** (never a literal), written with
the fields of `fidelity.md` § 5.

## Step 3 — Map to Flutter

Apply `references/figma-mapping.md`. Key rules:
- **Ignore presentation chrome:** status bars, device frames, mockup shadows, canvas position.
- **Colors by token, not hex** (hex only confirms the match). **Typography by role.** A role without
  a text style, or a family missing from the theme, is a gap.
- **Spacing:** the design's number at each nesting level; spacing tokens when the profile defines
  them. Repeated values become token candidates.
- **Dimensions flexible** except the list in `fidelity.md` § 3. A fixed width in the frame becomes a
  rule in Responsive behavior, not a `width:`.
- **Material 3 components become Flutter widgets**, not SVG fragments. When the design's measures
  differ from the widget's defaults, decide with `fidelity.md` § 5 and record it.
- **Colors with no token** (dividers, underlines, tracks): `references/fidelity.md` § 8.
- **Assets:** download only real illustrations and images the project lacks; note each path and
  resolution variants.
- **Component descriptions** in Figma are requirements ("default MXN", "only used in this flow").
- **Mock data is not data**: use it only to learn formats. Ask when a rule would come from a mock.

## Step 4 — Reuse ladder and catalog

Open `design.widget_catalog`. If it is missing, build it first (`references/widget-catalog.md`); when you may
not write outside the output folder, list the proposed catalog rows under Components instead and say so. For
each component: exact match or code-connect → **reuse**; close match → **extend** with an optional
parameter whose default keeps every call site unchanged; no match → **create** (feature-local in
`presentation/widgets/`, or shared in `paths.shared_widgets`, exported from the barrel and added to
the catalog). Record each decision with its path. Fill "Figma equivalent" the first time a component
is matched.

## Step 5 — Write and lint `design.md`

Use `references/design-template.md`. Then run `python3 scripts/lint_design.py <design.md> --root <project>` and
fix every error; its summary gives the gap, reuse/extend/create and capture counts for `state.json`.

## Delta and verify

Delta (changes to existing screens) and verify (code against the design, verdict) are in
`references/modes.md` and `references/fidelity.md` § 6. Both stop before editing code: fixes go to
`forge-presentation`.

## CSS mode (pasted Figma CSS, no MCP)

Follow `references/css-mode.md`. The output is a semi-pseudocode Flutter widget tree with exact
numbers, token-mapped colors and the responsive rules applied, plus notes. If you don't know which
project or palette the CSS belongs to, ask before you map colors.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Design context on every state's full screen | Full screen once per layout, then changed nodes | Each call costs a lot of context |
| `Color(0xFF9E8B81)` | Theme accessor by token name | Theming, dark mode, rebrands |
| Match a token by name only | `theme_tokens.py`: name **and** value | A same-name token can have another value |
| `TextStyle(fontFamily: …, fontSize: 16)` | `textTheme.<role>` | Typography is a theme role |
| Translating React/Tailwind line by line | Use it as a visual reference | Absolute positions and web semantics |
| `width: 343` copied from the frame | Flexible layout, rule in Responsive behavior | Small phones, tablets, text scale |
| Flattening nested columns into one gap | Keep each level's gap | 24 on the outer level is not 16 + a spacer |
| Downloading SVG pieces of a progress bar | Native widget styled with tokens | M3 components are not assets |
| Estimating sizes from the screenshot | Numbers from design context; screenshot as the visual check | Exact measures |
| Omitting per-element color and type role | One row per element in Measures | The implementer cannot see the design |
| New widget without checking the catalog | Reuse ladder | Duplicates drift apart |
| Changing a widget's required params for one design | Optional param with the old default | Existing call sites keep working |
| Deriving rules from mock amounts | Ask (story gap) or `[por confirmar]` | Mock data is illustrative |
| Filing a missing font under "observations" | A design gap with a decision | The family is part of the look |

## Finish

- Write the output files and `refs/`; update the catalog if components were created or extended.
- With a run folder, update `state.json`: `phase: design`, the gap count and `design.captures`.
- Report: nodes read and calls made; tokens matched vs gaps (with the decisions needed); components
  reused / extended / created; captures saved; assets; design–story differences; the lint summary.
