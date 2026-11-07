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
        BusinessFailure() => serverMessage ?? l10n.errorGeneric,
        ServerFailure() || ParsingFailure() => l10n.errorGeneric,
      };
}
```

- Show `serverMessage` only when the contract says the backend sends user-safe copy in the
  app's language.
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
  if (_isDisposed || id != _requestId) return;                        // stale or closed
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

## Accessibility (checked by forge-audit)

- Icon-only buttons get a `tooltip:` or `Semantics(label:)`.
- Tap targets are at least 48×48 (`MaterialTapTargetSize.padded`, `minimumSize`).
- The layout survives `textScaler` at 2.0: no fixed heights around text; use `Flexible` or
  `Wrap`.
- Status is never shown by color alone. Pair red and green amounts with a sign or an icon.
- `ExcludeSemantics` on decorative images. `MergeSemantics` on composite tiles, so they read
  as one item.
- Errors are announced. Inline error text sits next to its field (`InputDecoration.errorText`
  does this).

## Responsiveness and platform

- Use `MediaQuery.sizeOf(context)`, not `MediaQuery.of(context).size` (fewer rebuilds).
- Wrap content in `SafeArea`. Pages with inputs must scroll when the keyboard opens.
- Back navigation: `PopScope` only when the brief defines a premature-exit behavior.
