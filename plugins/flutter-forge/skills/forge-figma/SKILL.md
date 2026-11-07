---
name: forge-figma
description: Translate a Figma design into Flutter design notes and widgets that follow the project's theme and existing widgets. It reads Figma through the Figma MCP, cheapest calls first (variables, metadata, one full screen per layout, then only the nodes that change between states). It maps tokens by name to the theme, typography by role, and Material 3 components to native widgets, and decides for each component whether to reuse an existing widget, extend it or create a new one, keeping a widget catalog. It also converts CSS pasted from Figma into a Flutter widget tree. Use it when the user shares a figma.com link or node, pastes Figma CSS, or asks to "maquetar", "pasar el diseño a Flutter", "construye esta pantalla del Figma", "qué widgets reutilizo"; and when forge-deliver reaches the design phase.
---

# forge-figma

Output: `.flutter-forge/runs/<slug>/design.md`. It contains tokens, component decisions,
widget outlines per screen and design gaps. `forge-blueprint` and `forge-presentation`
consume it. **The design is the source of truth for visuals; the story is the source of
truth for behavior.** When they disagree on copy or amounts, the story wins and the
difference goes in the report.

## Step 0 — Resolve

1. Read the `design.*` keys of `.flutter-forge/profile.yaml`: colors and typography accessors,
   the spacing class, the scaffold widget, `widget_catalog`. Also read
   `paths.shared_widgets` and `paths.widgets_barrel`.
2. Read `brief.md` when it exists. Its **Design** section lists the nodes per state.
3. Check that the Figma MCP is available. If it is not connected or needs authorization, tell
   the person to connect it and continue only with screenshots or CSS they paste. If the MCP
   provides its own design-to-code guidance (a skill or instructions it asks you to load first),
   load it before requesting design context.
4. If `.flutter-forge/overlays/forge-figma.md` exists, read it; its rules win. Examples: the
   project's token naming, the Figma library ↔ widget pairs, a color class.

## Step 1 — Read Figma, cheapest calls first

1. **Variables / tokens**: one variables call on one full screen gives the token set for the
   whole flow.
2. **Metadata** of the frame, to list child nodes and find the ones per state.
3. **Design context** for **one full screen per distinct layout**, with the client framework
   set to Flutter/Dart.
4. For every other state the brief lists, request **only the node that changes** (the field in
   error, the result card loading). Do not request the whole screen again.
5. Take a **screenshot** only when you need a visual target for a node you have not seen.
6. If the MCP offers code-connect mappings, read them. A mapped component is an exact reuse.

Process one screen at a time. The returned code (often React + Tailwind) is a **visual
reference** and is never translated line by line.

## Step 2 — Map to Flutter

Apply `references/figma-mapping.md`. The key rules:
- **Ignore presentation chrome:** status bars, device frames, camera cutouts, mockup shadows
  and the frame's canvas position.
- **Colors by token name, not hex.** A semantic variable maps to the theme accessor from
  `design.colors`. The hex is only for confirming the match. A token with no theme match is a
  **design gap**; never fall back to a literal.
- **Typography by role:** `title/medium` maps to `textTheme.titleMedium`. A role with no text
  style is a gap.
- **Spacing and radii** use the spacing tokens when the profile defines them. Otherwise keep
  the exact numbers and flag repeated values as token candidates.
- **Material 3 components become Flutter widgets**, not SVG fragments. This applies to progress
  indicators, chips, switches, sliders, dividers and icons (`Icons.*` or the project's icon
  set).
- **Assets:** download only real illustrations and images the project lacks. Note each asset's
  path and resolution variants.
- **Component descriptions** in Figma are requirements, for example "default MXN" or "only
  used in this flow".
- **Mock data is not data.** Use it only to learn formats: currency symbol, decimals and date
  style.

## Step 3 — Reuse ladder and catalog

Open `design.widget_catalog`. If it is missing, build it first from the shared widgets folder
and its barrel (`references/widget-catalog.md`) and commit it with the feature. For each
component:

1. **Exact match** in the catalog, or a code-connect mapping → **reuse** it.
2. **Close match** → **extend** it with an optional parameter whose default keeps every
   current call site unchanged.
3. **No match** → **create** it:
   - only this flow uses it → `presentation/widgets/`;
   - reusable → `paths.shared_widgets/<group>/`, exported from the barrel and added to the catalog.

Record each decision with its path in `design.md`. Fill the catalog's "Figma equivalent"
column the first time a component is matched, which makes later flows faster.

## Step 4 — Write `design.md`

Use `references/design-template.md`. It contains:
- the token table (Figma name → Flutter accessor, matched or **gap**);
- the typography roles;
- the component decisions;
- one widget outline per screen (structure only; `forge-presentation` writes the code);
- the states, and which node shows each one;
- the assets;
- design–story differences.

## CSS mode (pasted Figma CSS, no MCP)

Follow `references/css-mode.md`. The output is a semi-pseudocode Flutter widget tree, with
exact numbers and token-mapped colors, plus notes. If you don't know which project or palette
the CSS belongs to, ask before you map colors.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Design context on every state's full screen | Full screen once per layout, then changed nodes | Each call costs a lot of context |
| `Color(0xFF9E8B81)` | Theme accessor by token name | Theming, dark mode, rebrands |
| `TextStyle(fontFamily: …, fontSize: 16)` | `textTheme.<role>` | Typography is a theme role |
| Translating React/Tailwind line by line | Use it as a visual reference | Absolute positions and web semantics |
| Fixed widths from the frame (`width: 343`) | Flexible layout + padding | Different screen sizes and text scale |
| Downloading SVG pieces of a progress bar | Native widget styled with tokens | M3 components are not assets |
| New widget without checking the catalog | Reuse ladder | Duplicates drift apart |
| Changing a widget's required params for one design | Optional param with the old default | Existing call sites keep working |
| Deriving rules from mock amounts | Ask (story gap) | Mock data is illustrative |

## Finish

- Write `design.md`, and update the catalog if components were created or extended.
- Update `state.json` with `phase: design` and the design-gap count.
- Report:
  - nodes read and calls made;
  - tokens matched vs gaps;
  - components reused / extended / created;
  - assets;
  - design–story differences.
