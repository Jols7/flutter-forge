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

## Size thresholds (strict targets)

The defaults are deliberately strict: they describe how the code should look, not how a legacy
app looks today. They were set on 2026-11-19 after measuring UnitedApp (210 `build()`, 276
files) and `forge_demo`, and are meant to be recalibrated as more projects are measured.

| Measure | Default | Profile key | Level | UnitedApp at this value |
|---|---|---|---|---|
| `build()` lines | 50 | `quality.max_build_lines` | finding | 47 of 210 over |
| `build()` cyclomatic complexity (approx.) | 5 | `quality.max_build_complexity` | finding | 24 of 210 over |
| File lines | 250 | `quality.max_file_lines` | warn | 13 of 276 over |
| Indent depth (2-space levels of the whole file) | 12 | `quality.max_widget_depth` | warn | 64 of 276 over |
| Classes per file | 3 (state/ and sealed hierarchies exempt) | `quality.max_classes_per_file` | warn | few |

Notes:
- Indent depth counts the class body (1) and the method (2) too, so 12 leaves about 8 levels of
  widgets. A value of 10 flagged 38 % of UnitedApp and sits at the limit of `forge_demo`; a metric
  limited to the inside of `build()` would allow a stricter number later.
- Flutter's own style guide sets no file-size limit, so these numbers are empirical.
- **Modes.** The strict numbers are the default of `new` projects. In `adopt` and `improve` (from
  `architecture.mode`, or `--mode`) the script uses the looser legacy numbers (`build()` 120 lines,
  complexity 10, file 300, depth 20) and reports `build-lines` and `build-complexity` as warnings, so
  an existing app is not failed wholesale (UnitedApp at the strict numbers: 44 % of files with a
  finding). Values set in the profile always win. Run it with `--changed-from` to measure only new
  and changed files, and tighten the profile as the app improves.
- `forge_demo` meets all of them (its list screen was split into `_LoadMoreOnScroll`,
  `_ListFooter` and a `listLength` getter on the state to do so).

`forge-audit/scripts/check_presentation.py` checks these numbers and the naming rules; complexity
is approximate.

## Keys for tests

Interactive widgets and state containers should be named and placed so a test key can be added
later without restructuring. The key convention is decided in **BIT-012**, not here.
