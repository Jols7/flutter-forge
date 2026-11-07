# State with `flutter_bloc` (Cubit by default, Bloc when events carry meaning)

Use **Cubit** for plain intents. Use **Bloc** when you need event transformers (debounce,
`restartable`, `droppable` from `bloc_concurrency`) or an event log for analytics.

## State — `presentation/state/transactions_state.dart`

```dart
import 'package:flutter/foundation.dart';

import '../../../../core/error/app_failure.dart';
import '../../domain/entities/transaction.dart';

@immutable
sealed class TransactionsState {
  const TransactionsState();
}

final class TransactionsLoading extends TransactionsState {
  const TransactionsLoading();
}

final class TransactionsEmpty extends TransactionsState {
  const TransactionsEmpty();
}

final class TransactionsFailure extends TransactionsState {
  const TransactionsFailure(this.failure);
  final AppFailure failure;
}

final class TransactionsLoaded extends TransactionsState {
  const TransactionsLoaded({
    required this.items,
    required this.nextPage,
    this.isLoadingMore = false,
    this.loadMoreFailure,
  });

  final List<Transaction> items;
  final int? nextPage;
  final bool isLoadingMore;
  final AppFailure? loadMoreFailure;    // shown inline at the list end; list stays visible

  bool get hasMore => nextPage != null;

  TransactionsLoaded copyWith({
    List<Transaction>? items,
    int? Function()? nextPage,
    bool? isLoadingMore,
    AppFailure? Function()? loadMoreFailure,
  }) =>
      TransactionsLoaded(
        items: items ?? this.items,
        nextPage: nextPage != null ? nextPage() : this.nextPage,
        isLoadingMore: isLoadingMore ?? this.isLoadingMore,
        loadMoreFailure: loadMoreFailure != null ? loadMoreFailure() : this.loadMoreFailure,
      );
}
```

The `T? Function()?` parameters let `copyWith` set a nullable field back to `null`. Add `==`
and `hashCode` (or `equatable`) when tests compare states with `equals`. `bloc_test`'s
`expect:` uses `==`, so value equality is **required** for every state that has fields.

## Cubit — `presentation/state/transactions_cubit.dart`

```dart
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/error/result.dart';
import '../../domain/repositories/transactions_repository.dart';
import 'transactions_state.dart';

class TransactionsCubit extends Cubit<TransactionsState> {
  TransactionsCubit(this._repository, {required this.accountId}) : super(const TransactionsLoading());

  final TransactionsRepository _repository;
  final String accountId;

  Future<void> load() async {
    emit(const TransactionsLoading());
    final result = await _repository.getTransactions(accountId: accountId);
    if (isClosed) return;
    emit(switch (result) {
      Success(:final value) when value.items.isEmpty => const TransactionsEmpty(),
      Success(:final value) => TransactionsLoaded(items: value.items, nextPage: value.nextPage),
      Failure(:final failure) => TransactionsFailure(failure),
    });
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is! TransactionsLoaded || !current.hasMore || current.isLoadingMore) return;
    emit(current.copyWith(isLoadingMore: true, loadMoreFailure: () => null));
    final result = await _repository.getTransactions(accountId: accountId, page: current.nextPage!);
    if (isClosed) return;
    emit(switch (result) {
      Success(:final value) => current.copyWith(
          items: [...current.items, ...value.items],
          nextPage: () => value.nextPage,
          isLoadingMore: false,
        ),
      Failure(:final failure) => current.copyWith(isLoadingMore: false, loadMoreFailure: () => failure),
    });
  }
}
```

## Route — creates and starts the cubit (`core/router/app_router.dart`)

```dart
GoRoute(
  path: '/accounts/:accountId/transactions',
  name: TransactionsPage.routeName,
  builder: (context, state) => BlocProvider(
    create: (_) => getIt<TransactionsCubit>(param1: state.pathParameters['accountId']!)..load(),
    child: const TransactionsPage(),
  ),
),
```

Register with `registerFactoryParam<TransactionsCubit, String, void>((accountId, _) =>
TransactionsCubit(getIt(), accountId: accountId))`.

## Page — consumes only

```dart
class TransactionsPage extends StatelessWidget {
  const TransactionsPage({super.key});
  static const routeName = 'transactions';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.transactionsTitle)),
      body: BlocBuilder<TransactionsCubit, TransactionsState>(
        builder: (context, state) => switch (state) {
          TransactionsLoading() => const Center(child: CircularProgressIndicator()),
          TransactionsEmpty() => EmptyView(message: l10n.transactionsEmpty),
          TransactionsFailure(:final failure) => ErrorView(
              message: failure.message(l10n),
              onRetry: context.read<TransactionsCubit>().load,
            ),
          TransactionsLoaded() => TransactionsList(state: state),
        },
      ),
    );
  }
}
```

Side effects (navigate, snackbar) use `BlocListener` with `listenWhen`, wrapping the region
they relate to. Use `BlocSelector` or `context.select` when a widget needs one field only.

## Bloc with a debounced event

```dart
EventTransformer<E> debounce<E>(Duration d) => (events, mapper) => events.debounceTime(d).switchMap(mapper);
// requires rxdart; or use bloc_concurrency's `restartable()` + a Timer in the cubit

on<AmountChanged>(_onAmountChanged, transformer: debounce(const Duration(milliseconds: 300)));
```

`restartable()` cancels the previous handler, which discards stale responses for free.

## Testing hooks

`bloc_test` covers `build` / `act` / `expect`. Repositories are mocked with mocktail.
`forge-tests/references/state-tests.md` has the templates.
