# Design lenses

These lenses are adapted from `flutter-senior-review` in flutter-llm-toolkit (MIT, © 2026
Roland Tolnay, commit `bb26ba8`; see NOTICE). They were rewritten to be independent of the
state manager, and their examples were replaced. They look at **how code will evolve**, not
at style or lint. Report a lens finding only with a concrete alternative that names the
types or widgets.

## Lens 1 — State modeling: can the code represent invalid states?

| Signal | Smell | Better |
|---|---|---|
| `isLoading`, `hasError`, `data` side by side | 8 combinations, 4 valid | sealed `Loading | Failure | Loaded | Empty` |
| `String? error` + `T? data` both set | contradictory state | `Failure(AppFailure)` variant |
| Same value stored in two places (list + selected copy) | drift between copies | store `selectedId`, derive the item |
| Several parameters always passed together (`amount`, `currency`, `accountId`) | data clump | a value object (`TransferDraft`) |
| `enum Status` + nullable fields valid only for some statuses | fields meaningful per status | sealed class with fields per variant |
| Type hierarchy with a `type` field + `switch` everywhere | manual dispatch | sealed hierarchy or polymorphism |

Self-check: *"Can I construct an instance of this state that the UI can't render
meaningfully?"* If the answer is yes, there is a finding.

## Lens 2 — Responsibility boundaries: if this feature were removed, how many files change?

| Signal | Smell | Better |
|---|---|---|
| Removing the feature touches the shared widgets, other features and the core | feature knowledge leaked | keep it in the feature; share through domain contracts |
| A widget receives 6 callbacks to do work for its parent | dependency through callbacks | pass data in; raise one intent; or give the widget its own state manager |
| Two widgets render the same visual block with copy-paste | missing shared visual pattern | one widget with parameters (via the reuse ladder) |
| A configurable widget with many boolean flags (`showX`, `isCompact`, `variantB`) | configuration over composition | compose small widgets; slots (`leading`, `trailing`, `child`) |
| Wrapper widgets that only forward parameters | pass-through layer | remove it or give it a responsibility |
| Methods that must be called in order (`init()` before `load()`) | temporal coupling | constructor establishes invariants; one entry method |

## Lens 3 — Abstraction timing: is the abstraction earned?

| Signal | Smell | Better |
|---|---|---|
| Interface with one implementation and no test seam need (data sources) | speculative generality | concrete class; mocktail mocks it |
| Use case that forwards one call | ceremony | call the repository contract (unless `use_cases: required`) |
| Generic base class for two screens "for the future" | premature reuse | duplicate twice; extract on the third, when the shape is known |
| Inconsistent error handling across features (one throws, one returns `null`, one `Result`) | missing abstraction where it *is* earned | one model (`Result` + `guard`) everywhere |
| The **repository contract** missing in `clean` | under-abstraction at the boundary that matters | contract in domain, impl in data |

The boundary between presentation and data is always earned. Most other abstractions have
to prove they are needed.

## Report format for lens findings

```
### F-7 · medium · design/state-modeling · lib/features/transfers/presentation/state/transfer_state.dart:8
**What:** `TransferState` holds `bool isPreviewLoading`, `TransferPreview? preview`, `AppFailure? previewError`.
**Why:** the UI can receive loading + error at once (seen after a retry), and the switch can't be exhaustive.
**Fix:** `sealed class PreviewStatus { Idle | Loading | Ready(TransferPreview) | Failed(AppFailure) }`; `TransferState.preview: PreviewStatus`.
Confidence 0.9 · Owner: forge-presentation
```

When a lens finds nothing, say so in one line, e.g. *"Lens 3: no speculative or missing
abstractions in scope"*. Never pad a lens with weak findings.
