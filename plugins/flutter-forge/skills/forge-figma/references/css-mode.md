# CSS mode — pasted Figma CSS → Flutter widget tree

Use this when the person pastes CSS from Figma's inspect panel instead of a link.

## Output contract (always in this shape)

1. **One-line summary** of the component and its visible variants or states.
2. **Structure note** in Flutter terms (Column/Row/Stack, alignment) when the layout is not
   trivial.
3. **Semi-pseudocode widget tree:**
   - It is a tree, not a file. Leave out imports, the class and `build`.
   - Use native Flutter widgets, plus catalog widgets when the catalog has an exact match.
   - Keep the **exact numbers**: padding, gaps, sizes, radii and letter spacing.
   - CSS `line-height` becomes `height: lineHeightPx / fontSizePx`, written as the division so
     the source stays visible (`height: 24 / 16`).
   - Put repeated children once in a named helper (`_Item(...)`).
4. **Color table** `Hex | Token`: each hex mapped to the theme token by the profile's palette.
   When several tokens share a hex, pick the one that fits the context and flag the tie.
   With no palette known, leave the raw `Color(0xFF…)` values and say so; never invent tokens.
5. **Notes for the implementer:** ambiguous matches, assets to confirm, and states the CSS
   hints at but doesn't show (selected, disabled, error).

## CSS → Flutter cheat sheet

| CSS | Flutter |
|---|---|
| `display:flex; flex-direction:column` | `Column` |
| `gap: 12px` | `SizedBox(height: 12)` between children (or `spacing: 12`) |
| `padding: 16px 24px` | `EdgeInsets.symmetric(vertical: 16, horizontal: 24)` |
| `border-radius: 12px 12px 0 0` | `BorderRadius.vertical(top: Radius.circular(12))` |
| `border: 1px solid #…` | `Border.all(width: 1, color: token)` |
| `align-self: stretch` | `crossAxisAlignment: CrossAxisAlignment.stretch` on the parent |
| `flex: 1 0 0` | `Expanded` |
| `font-weight: 600` | `FontWeight.w600` (prefer the role's text style + `copyWith` only if the role differs) |
| `opacity: .38` | `Opacity` only for disabled visuals; prefer the widget's disabled state |
| `box-shadow` | `BoxShadow(offset, blurRadius, spreadRadius, color)` |

## Questions (only when they change the output)

- Which project or palette, if colors need mapping and it is unclear.
- Which states or variants exist beyond the pasted one.
