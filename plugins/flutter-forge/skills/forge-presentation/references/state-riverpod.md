# State with Riverpod

Templates target **Riverpod 3.x**. Check the installed version (`flutter pub deps | grep
riverpod`). For 2.x, use `FamilyAsyncNotifier` with `build(arg)` instead of a constructor
argument, and check `state` instead of `ref.mounted`. If the project uses
`riverpod_generator`, write `@riverpod class TransactionsNotifier extends
_$TransactionsNotifier`. The graph stays the same.

## Simple load: `AsyncNotifier` + `AsyncValue`

```dart
// presentation/state/transactions_notifier.dart
final transactionsProvider =
    AsyncNotifierProvider.family<TransactionsNotifier, Paginated<Transaction>, String>(
  TransactionsNotifier.new,
);

class TransactionsNotifier extends AsyncNotifier<Paginated<Transaction>> {
  TransactionsNotifier(this.accountId);

  final String accountId;

  @override
  Future<Paginated<Transaction>> build() async {
    final result = await ref.watch(transactionsRepositoryProvider).getTransactions(accountId: accountId);
    return switch (result) {
      Success(:final value) => value,
      Failure(:final failure) => throw failure,     // AppFailure implements Exception
    };
  }

  Future<void> retry() async => ref.invalidateSelf();
}
```

`AsyncValue` already models loading, error and data. Add a sealed state only when the screen
has more states than that: empty, pagination, or several regions.

## Page

```dart
class TransactionsPage extends ConsumerWidget {
  const TransactionsPage({super.key, required this.accountId});
  final String accountId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final transactions = ref.watch(transactionsProvider(accountId));
    return Scaffold(
      appBar: AppBar(title: Text(l10n.transactionsTitle)),
      body: switch (transactions) {
        AsyncData(:final value) when value.items.isEmpty => EmptyView(message: l10n.transactionsEmpty),
        AsyncData(:final value) => TransactionsList(items: value.items),
        AsyncError(:final error) => ErrorView(
            message: error is AppFailure ? error.message(l10n) : l10n.errorGeneric,
            onRetry: () => ref.read(transactionsProvider(accountId).notifier).retry(),
          ),
        _ => const Center(child: CircularProgressIndicator()),
      },
    );
  }
}
```

Put the `AsyncData` cases first, so a refresh with existing data keeps showing it. Riverpod
keeps `value` during reload, and `isRefreshing` indicates the refresh.

## Mutations (writes)

Keep writes in methods on the notifier. Check `ref.mounted` after each `await`. Side effects
go through `ref.listen` in the page:

```dart
ref.listen(transferProvider, (previous, next) {
  if (next case AsyncData(value: TransferSubmitted(:final receipt))) {
    context.goNamed(TransferReceiptPage.routeName, extra: receipt);
  }
});
```

## Dependencies

Repository providers live in `features/<f>/di/` (`forge-architecture/references/di.md`).
Notifiers read them with `ref.watch` inside `build`, and with `ref.read` inside methods.

## Testing hooks

Use `ProviderContainer(overrides: [transactionsRepositoryProvider.overrideWithValue(mock)])`,
or `ProviderScope(overrides: …)` in widget tests. Templates are in
`forge-tests/references/state-tests.md`.
