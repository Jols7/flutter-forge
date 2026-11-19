# Page patterns

## Failures → localized messages (`lib/core/l10n/failure_messages.dart`)

Create this once per project. Features override specific `BusinessFailure` codes in their own
widgets.

```dart
extension AppFailureMessage on AppFailure {
  String message(AppLocalizations l10n) => switch (this) {
        NetworkFailure(isTimeout: true) => l10n.errorTimeout,
        NetworkFailure() => l10n.errorOffline,
        UnauthorizedFailure() => l10n.errorSessionExpired,
        ForbiddenFailure() => l10n.errorForbidden,
        NotFoundFailure() => l10n.errorNotFound,
        ValidationFailure(:final serverMessage) => serverMessage ?? l10n.errorValidation,
        ConflictFailure() => l10n.errorConflict,
        BusinessFailure() => l10n.errorGeneric,   // a feature maps `code` to its own key
        ServerFailure() || ParsingFailure() => l10n.errorGeneric,
      };
}
```

- Show `serverMessage` only when the contract says the backend sends user-safe copy in the
  app's language. That is why `ValidationFailure` may use it, while `BusinessFailure` never
  does: its `code` is mapped to an l10n key by the feature (`forge-l10n`), and unknown codes fall
  back to the generic message.
- `UnauthorizedFailure` usually never reaches a page, because the auth interceptor ends the
  session first. Keep the branch so the switch stays exhaustive.

## Regions, not pages

When one part of the screen is loading or failing, only that region changes. Inputs, tabs and
selectors stay interactive unless the brief marks them blocking.

```dart
Column(children: [
  AccountSelector(...),                 // always interactive
  AmountField(...),                     // live validation, local
  switch (state.preview) {              // only this block reacts to the network
    PreviewIdle() => const SizedBox.shrink(),
    PreviewLoading() => const PreviewSkeleton(),
    PreviewReady(:final preview) => PreviewCard(preview: preview),
    PreviewFailed(:final failure) => InlineError(message: failure.message(l10n), onRetry: onRetry),
  },
]);
```

## Live input (debounce + delayed loading + stale discard)

In a state manager without event transformers (Cubit, Notifier, ViewModel):

```dart
static const _debounce = Duration(milliseconds: 300);
static const _loadingDelay = Duration(milliseconds: 250);
Timer? _debounceTimer;
Timer? _loadingTimer;
int _requestId = 0;

void amountChanged(String raw) {
  final amount = TransferAmount.parse(raw);             // local validation, instant
  _update(form: state.form.copyWith(amount: amount));
  _debounceTimer?.cancel();
  if (!amount.isValid) {
    _requestId++;                                       // invalidate in-flight responses
    _update(preview: const PreviewIdle());
    return;
  }
  _debounceTimer = Timer(_debounce, () => _preview(amount.value));
}

Future<void> _preview(double amount) async {
  final id = ++_requestId;
  _loadingTimer?.cancel();
  _loadingTimer = Timer(_loadingDelay, () {
    if (id == _requestId) _update(preview: const PreviewLoading());   // only if slow
  });
  final result = await _repository.previewTransfer(...);
  if (_disposed || id != _requestId) return;                        // stale or closed
  _loadingTimer?.cancel();
  _update(preview: switch (result) {
    Success(:final value) => PreviewReady(value),
    Failure(:final failure) => PreviewFailed(failure),
  });
}
```

Cancel both timers in `close()`/`dispose()`. With Bloc, use `restartable()` plus a debounce
transformer instead.

## Forms

- Each field has a controller owned by the widget (`StatefulWidget`/hooks) or by the state
  manager. Follow the project convention, and **dispose it where it was created**.
- Validation is pure and lives in domain value objects or validators. It returns enums or
  failures, and the widget maps them to text.
- Validate as the user types, but show errors only after the field was touched or a submit
  was attempted.
- Disable the submit button while the form is invalid **or** while it is submitting. A
  double tap must not send two requests. Writes that need it carry an idempotency key.
- For money input, use the formatter and parser from `core/utils`. Never use
  `double.parse` on localized text.

## Lists and pagination

- Use `ListView.builder` or `SliverList.builder`, never `Column` + `map` for unbounded data.
- Load the next page at about 80 % of the scroll extent. The end of the list shows a loader
  while loading more, or an inline retry after a failure. Already-loaded items stay visible.
- Give items a stable `Key` (`ValueKey(item.id)`) when they can be reordered or removed.
- Pull to refresh keeps the current data while refreshing.

## Accessibility (opt-in)

Only when `a11y: on`: see `accessibility.md`. With `off`, nothing here applies.

## Responsiveness and platform

Layout rules (flexible sizes, text beside values, scroll, lists, tablet, `MediaQuery.sizeOf`,
`SafeArea`, keyboard) are in `responsive.md`: the single source of truth.

- Back navigation: `PopScope` only when the brief defines a premature-exit behavior.


## Shell: tabs and bottom navigation

Use go_router's `StatefulShellRoute.indexedStack`. The shell owns the selected index and each
branch keeps its own back stack, so a Cubit for "current tab" is unnecessary.

```dart
StatefulShellRoute.indexedStack(
  builder: (context, state, shell) => HomeShell(shell: shell),
  branches: [
    StatefulShellBranch(routes: [
      GoRoute(path: '/accounts', name: AccountsPage.routeName, builder: (_, __) => const AccountsPage()),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: '/profile', name: ProfilePage.routeName, builder: (_, __) => const ProfilePage()),
    ]),
  ],
)

// HomeShell: `body: shell`, `onDestinationSelected: (i) => shell.goBranch(i, initialLocation: i == shell.currentIndex)`
```

State managers are still created per route inside each branch. Do not hold the selected tab in
a state manager that other widgets update.

## App start (splash)

The router decides the first screen. `bootstrap.dart` resolves the session **before** `runApp`
(or exposes it as a `Listenable` while it loads), and the router redirects from it:

```dart
GoRouter(
  refreshListenable: authState,                      // notifies on sign-in / sign-out
  redirect: (context, state) {
    final status = authState.status;                 // unknown | signedOut | signedIn
    if (status == AuthStatus.unknown) return '/splash';
    final atAuth = state.matchedLocation == '/login';
    if (status == AuthStatus.signedOut) return atAuth ? null : '/login';
    return (atAuth || state.matchedLocation == '/splash') ? '/accounts' : null;
  },
  routes: [...],
)
```

`/splash` is a plain page that shows while the status is `unknown`. A cubit that calls
`context.go` from `emit` mixes state with navigation (the anti-pattern in `forge-presentation`),
and a refresh-token failure then has no single place to end the session. The auth interceptor
signals logout through the same `authState` (`core-bootstrap.md`).
