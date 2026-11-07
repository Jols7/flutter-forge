# Figma → Flutter mapping

## Layout (auto-layout → widgets)

| Figma / CSS | Flutter |
|---|---|
| Auto-layout vertical / `flex-direction: column` | `Column` |
| Auto-layout horizontal / `row` | `Row` |
| `gap: N` | `SizedBox(height/width: N)` between children, or `spacing: N` on `Row`/`Column` (Flutter ≥ 3.27) |
| `padding` | `Padding` / `EdgeInsets` (spacing tokens when defined) |
| Fill container / `flex-grow: 1` | `Expanded` (or `Flexible` when content may be smaller) |
| Hug contents | default sizing, no fixed width |
| Fixed width on a text container | remove; constrain by parent; allow wrapping |
| `justify-content` / `align-items` | `mainAxisAlignment` / `crossAxisAlignment` |
| Absolute children | `Stack` + `Positioned` (only for real overlays: badges, FABs) |
| Corner radius | `BorderRadius.circular(r)` (radius token if defined) |
| Drop shadow | `BoxShadow` from the elevation token / `Material(elevation:)` |
| Scrollable frame taller than the device | `SingleChildScrollView` / `CustomScrollView` |
| Bottom-anchored button | `bottomNavigationBar: SafeArea(child: Padding(...))` or the project's footer pattern |

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
| Spacing variables (`space/16`) | `AppSpacing.md` (from `design.spacing`) |

Convert token names to camelCase (`On Surface Variant` → `onSurfaceVariant`). When the
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
| List item | `ListTile` (or catalog tile) |
| Bottom sheet | `showModalBottomSheet` with the project's sheet wrapper |
| Dialog | `showDialog` + `AlertDialog` (or catalog modal) |
| Skeleton / shimmer | project skeleton widget, or simple placeholder boxes with `colorScheme.surfaceContainerHighest` |
| Icon (Material Symbols) | `Icons.<name>` / `Symbols.<name>` if the project uses material_symbols_icons |
| Snackbar / toast | `ScaffoldMessenger.of(context).showSnackBar` (or project helper) |

## States in Figma → states in code

Each state node the brief lists maps to one branch of a sealed state. Typical branches are
loading skeleton, empty, error with retry, validation error, success and disabled. The node
tells you **how it looks**, and the brief tells you **when it happens**.
