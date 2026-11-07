# `design.md` template

```markdown
# Design — <Feature>
Figma: <file>/<frame> · Read: YYYY-MM-DD · Calls: variables 1 · metadata 1 · context 2 · screenshots 1

## Tokens
| Figma token | Flutter | Status |
|---|---|---|
| Schemes/Primary | colorScheme.primary | ✓ |
| Schemes/Surface Container | colorScheme.surfaceContainer | ✓ |
| Custom/Success | AppColors.success (ThemeExtension) | ✓ |
| State Layers/Primary/Opacity-16 | — | **gap D-1** |

Typography: Title/Large → titleLarge ✓ · Body/Medium → bodyMedium ✓ · Display/XS → **gap D-2**

## Components
| Figma component | Decision | Widget / path | Notes |
|---|---|---|---|
| Button · Filled | reuse | AppPrimaryButton (core/widgets/buttons) | |
| Amount field | extend | AppAmountField + `helperText` (optional) | old callers unchanged |
| Account option | create (feature) | transfers/presentation/widgets/account_option_tile.dart | only in this flow (Figma description) |

## Screens
### New transfer (node 12:345) — layout
Scaffold(appBar: title) → SingleChildScrollView → Column(spacing: 16, padding: 16)
  ├─ SectionTitle("Desde")  → AccountOptionTile × n (selectable)
  ├─ SectionTitle("Hacia")  → AccountOptionTile × n
  ├─ AppAmountField(currency of origin)
  └─ PreviewCard (region; states below)
Bottom: AppPrimaryButton("Transferir"), disabled until valid

### States
| State | Node | Shows |
|---|---|---|
| amount below minimum | 12:400 | field error text |
| preview loading | 12:410 | 3-line skeleton inside the card |
| preview error | 12:420 | inline error + "Reintentar" |

## Assets
| Asset | Source node | Path | Variants |
|---|---|---|---|
| empty_transfers.png | 12:500 | assets/images/empty_transfers.png | 1x/2x/3x |

## Differences design ↔ story
- Button copy "Enviar" in Figma vs "Transferir" in story §5 → followed the story.
```
