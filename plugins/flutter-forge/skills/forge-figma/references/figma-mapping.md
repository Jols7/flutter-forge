# Figma → Flutter mapping

## Layout (auto-layout → widgets)

Dimensions are flexible by default; the full policy is `fidelity.md` (responsive first). Spacing
keeps the design's numbers and its nesting.

| Figma / CSS | Flutter |
|---|---|
| Auto-layout vertical / `flex-direction: column` | `Column` |
| Auto-layout horizontal / `row` | `Row` |
| `gap: N` | `spacing: N` on `Row`/`Column` (Flutter ≥ 3.27) or `SizedBox` between children; **one gap per nesting level, never merged with its parent's** |
| `padding` | `Padding` / `EdgeInsets` (spacing tokens when defined) |
| Fill container / `flex-grow: 1` | `Expanded` (or `Flexible` when content may be smaller) |
| Hug contents | default sizing, no fixed width |
| Fixed width on a container or text | do not copy it: constrain by parent, allow wrapping; record the rule in Responsive behavior. Keep it fixed only for the list in `fidelity.md` § 3 |
| `min-width` that exceeds 320 dp minus padding | ignore (the layout must fit the smallest phone); record it as an accepted difference |
| Text next to a value in a row | label `Expanded`, value `Flexible` with `maxLines` or `FittedBox(scaleDown)` |
| `justify-content` / `align-items` | `mainAxisAlignment` / `crossAxisAlignment` (keep the relation exactly) |
| Absolute children | `Stack` + `Positioned` (only for real overlays: badges, FABs) |
| Corner radius | `BorderRadius.circular(r)` (radius token if defined); exact |
| Border width and color | `Border.all(width, color: token)`; exact, including the 1 px borders of cards and notes |
| Drop shadow | `BoxShadow` from the elevation token / `Material(elevation:)` |
| Scrollable frame taller than the device | `SingleChildScrollView` / `CustomScrollView` |
| Bottom-anchored button | `bottomNavigationBar: SafeArea(child: Padding(...))` or the project's footer pattern |
| Row of equal items (chips, segments) | `Expanded` each, or `Wrap` when they may not fit |

## Tokens

| Figma | Flutter (default theme accessors; the profile may override) |
|---|---|
| `Schemes/Primary`, `color/primary` | `Theme.of(context).colorScheme.primary` |
| `Schemes/On Surface Variant` | `colorScheme.onSurfaceVariant` |
| `Schemes/Surface Container High` | `colorScheme.surfaceContainerHigh` |
| Brand tokens not in `ColorScheme` | a `ThemeExtension<AppColors>` (`Theme.of(context).extension<AppColors>()!.success`) |
| `State Layers/*` (opacity overlays) | usually handled by Material widgets' state layers; otherwise `color.withValues(alpha: x)` noted as a token gap |
| `Display/Headline/Title/Body/Label · Large/Medium/Small` | `textTheme.displayLarge` … `labelSmall` |
| Custom role (e.g. `headline/xs`) | gap → propose a `ThemeExtension` text style |
| Font family not in the theme or `pubspec.yaml` | gap with a decision (`fidelity.md` § 5), never a hardcoded `fontFamily` |
| Spacing variables (`space/16`) | `AppSpacing.md` (from `design.spacing`) |

Use `scripts/theme_tokens.py` to resolve names and values at once (a same-name token can have a
different value). Convert token names to camelCase (`On Surface Variant` → `onSurfaceVariant`). When the
profile's `design.colors` is a custom class (`AppColors`), use `AppColors.<token>` with the same
conversion. Confirm that the getter exists before you use it.

## Components

| Figma component (M3 kit or similar) | Flutter |
|---|---|
| Button / Filled · Tonal · Outlined · Text | `FilledButton` · `FilledButton.tonal` · `OutlinedButton` · `TextButton`, or the project's button from the catalog |
| Text field | `TextField`/`TextFormField` with `InputDecoration` (label, helper, error) or the project's input |
| Chip / Filter chip | `ChoiceChip` / `FilterChip` |
| Segmented button | `SegmentedButton` |
| Linear/Circular progress | `LinearProgressIndicator` / `CircularProgressIndicator` (value for determinate) |
| Switch / Checkbox / Radio | `Switch` / `Checkbox` / `RadioGroup` + `Radio` (Flutter ≥ 3.35 uses `RadioGroup`) |
| List item | `ListTile` (or catalog tile); compare its leading/trailing constraints and min height with the design first (`fidelity.md` § 5) |
| Bottom sheet | `showModalBottomSheet` with the project's sheet wrapper |
| Dialog | `showDialog` + `AlertDialog` (or catalog modal) |
| Skeleton / shimmer | project skeleton widget, or simple placeholder boxes with `colorScheme.surfaceContainerHighest` |
| Icon (Material Symbols) | `Icons.<name>` / `Symbols.<name>` if the project uses material_symbols_icons |
| Snackbar / toast | `ScaffoldMessenger.of(context).showSnackBar` (or project helper) |

## States in Figma → states in code

Each state node the brief lists maps to one branch of a sealed state. Typical branches are
loading skeleton, empty, error with retry, validation error, success and disabled. The node
tells you **how it looks**, and the brief tells you **when it happens**.
