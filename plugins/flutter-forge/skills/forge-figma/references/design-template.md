# `design.md` template

The file is a **specification**, not a sketch: `forge-presentation` implements from it and does
not look at the design again. `scripts/lint_design.py` checks the structure; the rules for every
measure are in `fidelity.md`. Headings may be written in the project's language; the lint accepts
the Spanish forms (Tokens, Componentes, Pantallas, Medidas, Comportamiento responsivo, Referencias).

```markdown
# Design — <Feature>
Figma: <file>/<frame> · Read: YYYY-MM-DD · Mode: feature|standalone|delta · Story: yes|no · Calls: variables 1 · metadata 1 · context 2 · screenshots 3

## Tokens
| Figma token | Figma value | Flutter | Status |
|---|---|---|---|
| Schemes/Primary | #ff7e2b | AppColors.primary | ✓ |
| Schemes/Outline Variant | #d7c2b9 | AppColors.outlineVariant | ✓ |
| State Layers/Primary/Opacity-16 | #8d4e2a @16% | — | **gap D-1** |
| Schemes/On Primary | #ffffff | AppColors.white (same value) | **gap D-2** |

Typography: Title/Medium → titleMedium · Body/Small → bodySmall · Headline/Super small (Unbounded 20) → **gap D-3** ·
Family: Montserrat (title/*) not in the theme → **gap D-4**

## Gaps
| Id | Design value | Nearest in project | Visible difference | Decides |
|---|---|---|---|---|
| D-1 | #8d4e2a @16% | `primary` (#ff7e2b) @16% | border tint slightly warmer | team |
| D-4 | Montserrat Medium | DMSans | glyph shapes on titles, values and buttons | team |

## Components
| Figma component | Decision | Widget / path | Notes |
|---|---|---|---|
| Button · Filled | reuse | AppPrimaryButton (`lib/core/widgets/buttons/app_primary_button.dart`) | |
| Amount field | extend | AppAmountField + `currencyGap` (optional) | old callers unchanged |
| Account option | create (feature) | transfers/presentation/widgets/account_option_tile.dart | only in this flow (Figma description) |

Material widgets with their own measures (only the ones that differ):
| Widget | Design | Material default | Decision |
|---|---|---|---|
| ListTile leading | 40×40 avatar | 56 min width, 48 min leading | parameters (`minLeadingWidth`, `contentPadding`) |

## Screens
### New transfer (node 12:345) — layout
Nesting and gaps exactly as in Figma; never flatten a nested column.
```
Scaffold → SingleChildScrollView → Padding(h 16) → Column(gap 16)
  ├─ Column(gap 24)                                  ← the gap of this level is 24, not 16
  │    ├─ CurrencySelector
  │    ├─ Column(gap 8, center): label · AmountField · underline
  │    └─ LevelBar
  ├─ Row(gap 4): Divider · Icon(24) · Divider
  └─ PreviewCard (states below)
Footer: AppPrimaryButton("Transferir")
```

#### Measures
One row per visible element that has a measure the template cannot infer. Sizes say `fixed` or
`flexible`. Color and role are per element (a label and its value can differ). *Spacing* is the gap
between children (not a design gap). *Source*: `Figma` (design context), `metadata` or `capture`
(sampled); tag anything inferred as `[inferido]` or `[inferido: motivo]`. Hex values belong only in
Tokens, Gaps and References, not in this table.
| Element | Size | Padding | Spacing | Radius / border | Alignment | Type role | Color token | Source |
|---|---|---|---|---|---|---|---|---|
| Preview card | flexible (min none) | 16 | 16 | 16 / 1 · primary @16% (D-1) | center | — | surfaceContainerLow | Figma |
| "Ganarías" | flexible | — | — | — | end | bodySmall | onPrimaryContainer | Figma |
| Summary row label | flexible (`Expanded`) | — | 8 between rows | — | start | bodySmall | onSurfaceVariant | Figma |
| Summary row value | flexible (`Flexible`) | — | — | — | end | titleMedium | onSurface | Figma |
| Underline | fixed 1 high · width relative | — | — | — | center | — | primary `[inferido: muestreo]` | capture |

### States
| State | Node | Shows | Shares layout with |
|---|---|---|---|
| amount below minimum | 12:400 | field error text | main |
| preview loading | 12:410 | 3-line skeleton inside the card | main |
| preview error | 12:420 | inline error + "Reintentar" | main |

A state that shares a block with another one (header, chips, progress) does not repeat it: list it in
*Shares layout with*, and its verdict inherits the shared block's defects once.

## Responsive behavior
| Component | Width rule | When space runs out | Source |
|---|---|---|---|
| Summary row | label `Expanded`, value `Flexible` | label wraps; value `FittedBox(scaleDown)` | inferido |
| Preview card | fill; design min 300 ignored (does not fit 320 dp) | grows in height | Figma (auto-layout fill) |
| Underline | fixed 268 in the design | `FractionallySizedBox` of the amount width | inferido |
Devices: phones from 320 dp, tablet, landscape; text scale 1.0 to 2.0 (`fidelity.md` § 4).

## References
| Screen / state | Node | Capture |
|---|---|---|
| New transfer · result | 12:345 | `refs/new-transfer-result.png` |
| New transfer · loading | 12:410 | `refs/new-transfer-loading.png` |

## Semantics (only when `a11y: on`)
Omit this section when `off`. Labels per icon-only control, reading order, heading nodes, alt text
for meaningful images; rules in `forge-presentation/references/accessibility.md`.
| Component | Label / alt text | Role | Reading order |
|---|---|---|---|

## Assets
| Asset | Source node | Path | Variants |
|---|---|---|---|
| empty_transfers.png | 12:500 | assets/images/empty_transfers.png | 1x/2x/3x |

## Differences design ↔ story
- Button copy "Enviar" in Figma vs "Transferir" in story §5 → followed the story.
(Without a story: write "No story. Behavior marked `[por confirmar]`.")

## Accepted differences and verdict
Filled by the verify step (`fidelity.md` § 6). When a `delta.md` exists in the same folder, it holds
the detailed verdict and this section only points to it. Verdict per screen/state: pass · pass-with-accepted · fail.
| Screen / state | Verdict | Accepted differences (reason) | Defects (owner) |
|---|---|---|---|
```
