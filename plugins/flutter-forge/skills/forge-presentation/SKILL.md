---
name: forge-presentation
description: Implement the presentation layer of a Flutter feature from its blueprint and design notes. That covers pages, state managers with sealed states (BLoC/Cubit, Riverpod Notifier/AsyncNotifier, or Provider ChangeNotifier), feature and shared widgets via a reuse ladder, navigation (go_router, auto_route or Navigator), the entry-point change, failure-to-message mapping, forms, debounce, pagination and accessibility. It follows the profile's state manager and the project's overlays. Use it when the user asks to create or change a screen, page, flow, view, state, cubit, bloc, notifier, provider or ViewModel, wire navigation, or says "crea la pantalla", "maqueta la vista", "agrega el estado de carga", "conecta la pantalla con el repositorio"; and when forge-deliver reaches implementation.
---

# forge-presentation

Everything the user sees and touches. State managers get entities and `Result` from the
domain, and widgets get state. Nothing in this layer knows about HTTP or JSON.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`:
   - `architecture.state`, `architecture.router` and `architecture.ui_helpers`;
   - `paths.shared_widgets` and `paths.widgets_barrel`;
   - `design.*` (colors, typography, spacing, scaffold widget);
   - `l10n.accessor`.
2. Load **only** the reference for your state manager:
   - `references/state-bloc.md`, or
   - `references/state-riverpod.md`, or
   - `references/state-provider.md`.

   Load `references/page-patterns.md` too.
3. Read the run's `blueprint.md` (state design, widgets, routes) and `design.md` when it exists.
   The design notes say which widgets to reuse, extend or create, and which tokens to use.
4. In `adopt`/`improve`, open the canonical feature's page and state manager, and mirror where
   the state manager is created, how the page consumes it and which scaffold or buttons it
   uses.
5. If `.flutter-forge/overlays/forge-presentation.md` exists, read it; its rules win. Typical
   cases are a mandatory scaffold widget, a theme wrapper, or the state manager being created
   at the navigation callsite.

## Step 1 — State

- Implement the blueprint's state design with sealed classes, or an immutable record with sealed
  sub-statuses for regions that load independently. Never use a bag of booleans.
- State managers receive their dependencies through the constructor: repository contracts or
  use cases. They hold **no** `BuildContext`, widgets or localized strings.
- Check for disposal after every `await`, and never emit after close:
  - bloc: `if (isClosed) return;`
  - riverpod: `if (!ref.mounted) return;` (in Riverpod 2.x: keep a link or check `state`)
  - provider: a `_disposed` flag.
- Live calculations use local recompute, a debounce, a delayed loading flag and stale-response
  discard (`page-patterns.md` § Live input).

## Step 2 — Widgets and page

- A page is route-level. Its `build` selects the state once, at the top, and delegates each
  region to a small widget. The switch over each sealed state is exhaustive.
- **Reuse ladder** for every component in `design.md`:
  1. exact match → reuse it;
  2. close match → extend it with an **optional** parameter whose default keeps the old
     behavior;
  3. otherwise create it: feature-local in `presentation/widgets/`, or shared in
     `paths.shared_widgets`. A shared widget is exported from the barrel when there is one,
     and gets a row in `design.widget_catalog`.
- Use the theme for all styling: colors, text styles and spacing tokens from `design.*`. There
  are no hex literals and no `TextStyle(fontFamily: …)`. A token that is missing from the theme
  is a gap reported by `forge-figma`; never replace it with a literal.
- All text comes from l10n through `l10n.accessor`, using the keys listed in the blueprint. Add
  the keys with `forge-l10n`. Failure messages come from the `AppFailure` mapping
  (`page-patterns.md` § Failures).
- Accessibility (`page-patterns.md` § Accessibility): semantic labels on icon-only buttons,
  tap targets of at least 48×48, layouts that still work at 200 % text scale, and no meaning
  conveyed by color alone.
- When `architecture.ui_helpers: forbid`, extract widgets instead of `_buildX()` methods. With
  `allow`, short private helpers are fine, but whatever has its own state or rebuild boundary
  must still be a widget.

## Step 3 — Navigation and DI

- Register the route as the blueprint says:
  - go_router: a route in `paths.router`, with typed path or query parameters;
  - Navigator: a `MaterialPageRoute` at the callsite, following the overlay.

  The route creates the state manager (`forge-architecture/references/di.md` § Where state
  managers are created). Riverpod creates it lazily.
- Apply the **entry-point change** to the existing screen. If the brief has a visibility rule,
  evaluate it at the caller.
- Register the state manager in the feature's DI module (factory, or route-scoped).

## Step 4 — Verify

Run `quality.analyze_command` until it is clean. Widget and state tests come from
`forge-tests`. When this skill runs alone, offer to run it next.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| `bool isLoading, hasError; String? error; List? data` | Sealed state per region | Invalid combinations become unrepresentable; exhaustive UI |
| One loading flag for list + preview | Independent sub-states | One failure must not hide loaded data |
| `getIt<Repo>()` / `ServiceLocator` inside a widget or state manager | Constructor injection; resolve in route/DI | Testable without globals |
| Creating the state manager inside the page's `build` | Create it in the route builder (or let Riverpod do it) | Recreated on rebuild; page not reusable in tests |
| `S.current` / `AppLocalizations` inside a state manager | State exposes failures/enums; widget maps to text | Locale changes and tests stay simple |
| `emit` / `notifyListeners` after `await` without a disposal check | `isClosed` / `ref.mounted` / `_disposed` guard | "emit after close" errors and leaks |
| Calling repository or `context.read` in `build` | Load in the route builder (`..load()`) or `build()` of the notifier | `build` runs many times |
| `context.watch` scattered in helper methods | Select once at the top; pass state down | One rebuild boundary; readable |
| Spinner on every keystroke | Debounce + delayed loading + stale discard | No flicker; correct results |
| Hex colors and raw `TextStyle`s | Theme / tokens from the profile | Theming and dark mode keep working |
| Changing an existing widget's required parameters | Optional parameter, old behavior as default | Every call site keeps compiling |
| Navigation inside a state manager | Side effect via listener (`BlocListener`, `ref.listen`, one-shot event) | State stays UI-agnostic |

## Finish

- Analyze is clean.
- Update `state.json`.
- Report:
  - pages, state managers and widgets, marked reused / extended / created with their paths;
  - routes, plus the entry-point change (file and method);
  - l10n keys requested;
  - catalog rows added.
