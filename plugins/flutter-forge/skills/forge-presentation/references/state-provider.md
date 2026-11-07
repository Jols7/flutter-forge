# State with `provider` (ChangeNotifier ViewModel)

The ViewModel exposes the **same sealed state** as the bloc template (`TransactionsState`).
`ChangeNotifier` is only the delivery mechanism.

## ViewModel — `presentation/state/transactions_view_model.dart`

```dart
import 'package:flutter/foundation.dart';

class TransactionsViewModel extends ChangeNotifier {
  TransactionsViewModel(this._repository, {required this.accountId});

  final TransactionsRepository _repository;
  final String accountId;

  TransactionsState _state = const TransactionsLoading();
  TransactionsState get state => _state;

  bool _disposed = false;

  Future<void> load() async {
    _emit(const TransactionsLoading());
    final result = await _repository.getTransactions(accountId: accountId);
    _emit(switch (result) {
      Success(:final value) when value.items.isEmpty => const TransactionsEmpty(),
      Success(:final value) => TransactionsLoaded(items: value.items, nextPage: value.nextPage),
      Failure(:final failure) => TransactionsFailure(failure),
    });
  }

  void _emit(TransactionsState next) {
    if (_disposed) return;
    _state = next;
    notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
```

- Every `TextEditingController`, `Timer` and `StreamSubscription` the ViewModel creates is
  disposed in `dispose()`.
- Projects that keep separate fields per request, instead of one sealed state, should still
  give each request its own status. In `improve` mode, use a sealed status per request:
  `PreviewStatus preview = const PreviewIdle();`.

## Route

```dart
GoRoute(
  path: '/accounts/:accountId/transactions',
  builder: (context, state) => ChangeNotifierProvider(
    create: (context) => TransactionsViewModel(
      context.read<TransactionsRepository>(),          // or getIt<TransactionsRepository>()
      accountId: state.pathParameters['accountId']!,
    )..load(),
    child: const TransactionsPage(),
  ),
),
```

With Navigator, the same `ChangeNotifierProvider` goes in `MaterialPageRoute(builder: …)` at
the push callsite. Constructor parameters are passed there.

## Page

```dart
class TransactionsPage extends StatelessWidget {
  const TransactionsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Consumer<TransactionsViewModel>(
      builder: (context, viewModel, _) => Scaffold(
        appBar: AppBar(title: Text(l10n.transactionsTitle)),
        body: switch (viewModel.state) {
          TransactionsLoading() => const Center(child: CircularProgressIndicator()),
          TransactionsEmpty() => EmptyView(message: l10n.transactionsEmpty),
          TransactionsFailure(:final failure) => ErrorView(message: failure.message(l10n), onRetry: viewModel.load),
          final TransactionsLoaded loaded => TransactionsList(state: loaded, onLoadMore: viewModel.loadMore),
        },
      ),
    );
  }
}
```

Use `Selector<TransactionsViewModel, X>` or `context.select` for widgets that depend on one
field. One-shot side effects (navigate after submit) are handled by awaiting the method that
returns the outcome:

```dart
final receipt = await viewModel.submit();           // returns TransferReceipt? (null on failure)
if (receipt != null && context.mounted) context.goNamed('receipt', extra: receipt);
```

## Testing hooks

Construct the ViewModel directly with a mocktail repository. Listen to it with a counter to
assert notifications. Templates are in `forge-tests/references/state-tests.md`.
