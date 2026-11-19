# Structure and naming inside `presentation/`

Applies always (not tied to `a11y`). Numbers come from a read-only measurement of UnitedApp
(275 presentation files) and `forge_demo` (10 files), 2026-11-19. Re-measure before tightening. Flutter's own style guide sets no file-size limit, so the file, class
and depth numbers are empirical, not an external standard.

## Names

| Thing | Pattern | Example |
|---|---|---|
| File | `snake_case.dart` (lint `file_names`) | `transactions_page.dart` |
| Route-level page | `XPage` | `TransactionsPage` |
| State manager | `XCubit` / `XBloc` / `XNotifier` / `XController` | `TransactionsCubit` |
| State | `XState` (sealed), sub-states `XLoading`, `XLoaded`… | `TransactionsState` |
| Row / list item | `XTile` | `TransactionTile` |
| Boxed summary | `XCard` | `AccountCard` |
| Region of a page | `XSection` | `BalanceSection` |
| Full-area status | `XView` | `EmptyView`, `ErrorView` |

A state class named `XFailure` is confusing next to `Failure<T>` (the `Result` case): name the
state `XError`.

## Skeleton

```
features/<feature>/presentation/
  pages/    one XPage per route
  state/    manager + sealed state
  widgets/  feature-local widgets (XTile, XCard, XSection)
```

A long page may group `widgets/<page_name>/` subfolders by section. Shared widgets live in
`paths.shared_widgets`.

## Extract and promote

- Extract a widget when a region has its own state or rebuild boundary, repeats, or pushes
  `build` past the limit below.
- Promote a feature-local widget to shared when a **second feature** needs it; add its row to
  `design.widget_catalog`.

## Size thresholds (measured)

| Measure | Observed (UnitedApp) | Threshold | Level |
|---|---|---|---|
| `build()` lines | p95 77, max 134, 2 files over 120 | 120 (`quality.max_build_lines`) | finding |
| `build()` cyclomatic complexity | p95 7, max 17; 3 of 209 over 10, all under 120 lines | 10 (`quality.max_build_complexity`) | finding; move logic to the state or a mapper |
| File lines | p90 197, p95 247, max 458, 3 files over 300 | 300 | warn; split by section |
| Classes per file | p95 2, max 7 | 1 public + private helpers; more than 3 | warn |
| Indent depth (2-space levels) | p90 15, p95 18, max 25 | 20 | warn; extract a widget |

`forge_demo` stays well below all of them (max file 108, max `build` 38). `forge-audit/scripts/check_presentation.py` checks these
numbers and the naming rules; complexity is approximate.

## Keys for tests

Interactive widgets and state containers should be named and placed so a test key can be added
later without restructuring. The key convention is decided in **BIT-012**, not here.
