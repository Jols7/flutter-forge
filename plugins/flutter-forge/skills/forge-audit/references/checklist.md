# Review checklist

The section structure is adapted from ECC's `flutter-dart-code-review` (MIT, © 2026 Affaan
Mustafa; see NOTICE). It was re-scoped to presets and profiles and extended with layer,
repository, Result and plan-conformance checks. Every item is a question. A "no" becomes a
finding only when it meets the confidence bar.

## 1. Architecture and layers

- Do all in-scope imports pass `check_layers`?
- Do DTOs, `Response`, `Map<String, dynamic>` and `DioException` stay below the repository?
- Do repositories implement a domain contract (`clean`) and return `Result<T>`, or follow the
  project's convention in `adopt`?
- Is domain free of Flutter (except `foundation.dart`), HTTP, JSON annotations, DI and storage?
- Does each use case earn its existence (combines repositories, holds a rule, or is reused)?
- Are cross-feature dependencies limited to `domain`?
- Does composition (router/DI) create and wire, while nothing else resolves from a container?
- Does each file match the blueprint: correct layer, name and signature?

## 2. State management (all)

- Is state immutable (`final` fields, new instances on change)?
- Is state sealed, or a record with sealed sub-statuses per region, rather than parallel
  booleans?
- Does every async gap check disposal before emitting or notifying?
- Are dependencies constructor-injected, with no `BuildContext`, no widgets and no localized
  strings in state?
- Do independently-loading regions have independent statuses?
- Are side effects (navigation, snackbars) triggered through listeners or returned outcomes,
  never from inside state?
- Are timers, subscriptions and controllers cancelled or disposed by their owner?

**bloc**
- Cubit for plain intents, Bloc only when transformers or event semantics are needed.
- `emit` never after `close`, states with value equality, `BlocProvider` in the route, and
  `buildWhen`/`listenWhen`/selectors where rebuilds are wide.

**riverpod**
- `ref.watch` in `build`, `ref.read` in callbacks, `ref.mounted` after awaits.
- Family arguments are immutable and have `==`. `keepAlive` only with a reason.
- No providers created inside widgets.

**provider**
- One ViewModel per route, created in the route builder.
- `Consumer`/`Selector` at the right depth, a `_disposed` guard, and `notifyListeners` only on
  real change.

## 3. Widgets

- Is `build` free of side effects (no I/O, no `.listen`, no state-manager creation)?
- Is `build` within `quality.max_build_lines`? With `ui_helpers: forbid`, are there no
  `_buildX()` methods?
- Do parts with their own rebuild boundary or state live in their own widgets?
- Is `const` used wherever possible?
- Are keys stable on reorderable or removable list items?
- Do colors, text styles and spacing come from the theme or tokens, with no hex literals and no
  raw `TextStyle`?
- Was the reuse ladder respected? Extended widgets add **optional** parameters only.
- Is a `StatefulWidget` used only for ephemeral UI state (animations, focus, controllers it
  owns)?

## 4. Dart idioms and null-safety

- Is the code free of implicit `dynamic`, unchecked casts of JSON outside DTOs, and `!` on
  values that can really be null?
- Is `late` used only when initialization is guaranteed before use?
- Are exhaustive `switch` statements written over sealed types without a default that hides
  new cases?
- Are collections exposed unmodifiably? Is `growable: false` used for mapped results?
- Do imports follow the project's style (package or relative) consistently, with no
  `src/` imports into other packages?

## 5. Async and lifecycle

- Is each `Future` either awaited or `unawaited(...)` deliberately?
- Is there an `if (!context.mounted) return;` after awaits that use `context`?
- Are stale responses discarded (request id or `CancelToken`) for repeatable requests?
- Is there no `Future.delayed` used as synchronization?
- Do debounce and timer values match the brief?

## 6. Errors

- Is the code free of thrown `String`s, of `catch (e) {}` that swallows, and of `catch (e) {
  return false; }`?
- Is each failure mapped once (`guard`), with business codes coming out as `BusinessFailure`?
- Is user-facing copy for each failure resolved in widgets through l10n?
- Do bugs (`Error`) still reach the global handlers?
- Are retries bounded where the brief requires it, or explicitly unlimited where allowed?

## 7. Data layer

- Is every field that the contract marks `?` or `[may be absent]` nullable in the DTO, with a
  default in the mapper?
- Is money `num`/`double`/decimal, never `int`? Are dates parsed in the mapper?
- Are path parameters percent-encoded and paths relative, with no hardcoded hosts?
- Do writes have idempotency keys when the contract requires them? Is the submit protected
  against double taps?
- Are pagination, cache and TTL as specified in the blueprint?
- Is there no hand-edited generated code? Did the build command run after DTO changes?

## 8. Performance

- Are lists built with `ListView.builder`/slivers?
- Are images sized (`cacheWidth`/`cacheHeight`) where they are decoded large?
- Is `MediaQuery.sizeOf`/`paddingOf` used instead of `MediaQuery.of`, which rebuilds on
  everything?
- Is the code free of heavy work in `build`, such as sorting or parsing on every frame?
- Is the code free of `Opacity`/`ClipRRect` in animations where cheaper alternatives exist?
- Do widgets rebuild narrowly (`select`, `buildWhen`, `const` subtrees)?

## 9. Testing

- Does each AC in the blueprint have its test, and does the test exist?
- Is each failure path that the screen handles tested at the repository and the state level?
- Do mapper tests use the contract fixtures?
- Do tests assert types and values, not just `isA<Failure>()`?
- Are tests deterministic: no real network or clock, `fakeAsync` for timers, no sleeps?
- Does coverage of new domain/data code meet `testing.coverage_min`?

## 10. Accessibility

- Do icon-only buttons have a tooltip or semantic label?
- Are tap targets at least 48×48?
- Does the layout survive a 2.0 text scale (no fixed heights around text)?
- Is meaning carried by more than color?
- Are decorative images excluded from semantics, and composite tiles merged?

## 11. l10n

- Is there no hardcoded user-facing text?
- Does every ARB locale have every key? Are placeholders and plurals used instead of
  concatenation?
- Are money and dates formatted with the current locale?
- Is the code free of l10n access from state managers in new code?

## 12. Navigation

- Is there one navigation approach per project, the one in the profile?
- Are routes typed (path or query parameters, or a typed `extra`) and validated? Deep links are
  checked by `forge-security`.
- Was the entry-point change applied? Is the visibility rule evaluated at the caller?
- Is `PopScope` used only where the brief defines premature-exit behavior?

## 13. Dependencies

- Were new packages added with `flutter pub add` (no invented versions)?
- Is each package justified and maintained, from a verified publisher when possible?
- Is there no second package for an existing concern (another HTTP client, a second state
  library)?
- Are there no `dependency_overrides` without a comment and an issue link?

## 14. Comments (`../forge-architecture/references/code-comments.md`)

Run `scripts/check_comments.py` on the scope first. It flags the mechanical cases:
commented-out code, `TODO`/`FIXME` without a reference, decorative banners, and missing
`///` on public domain contracts. Then judge what a script can't:
- Do comments explain *why* (rule with reference, workaround with link, counter-intuitive
  decision, regex/formula) rather than restate *what*?
- Would a rename or an extraction make the comment unnecessary?
- Do non-obvious business rules carry their reference (`AC-n`, `R-n`, `HU-n`, ADR link)?
- Are long explanations in code that belong in an ADR or a doc?
- Is the code free of history or authorship notes?

In `adopt` mode only new and changed lines count. Pre-existing comment debt is summarized,
never listed one by one.
