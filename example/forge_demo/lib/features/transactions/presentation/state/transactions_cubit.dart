import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/error/result.dart';
import '../../domain/repositories/transactions_repository.dart';
import 'transactions_state.dart';

class TransactionsCubit extends Cubit<TransactionsState> {
  TransactionsCubit(this._repository, {required this.accountId})
    : super(const TransactionsLoading());

  final TransactionsRepository _repository;
  final String accountId;

  Future<void> load() async {
    emit(const TransactionsLoading());
    final result = await _repository.getTransactions(accountId: accountId);
    if (isClosed) return;
    emit(switch (result) {
      Success(:final value) when value.items.isEmpty =>
        const TransactionsEmpty(),
      Success(:final value) => TransactionsLoaded(
        items: value.items,
        nextPage: value.nextPage,
      ),
      Failure(:final failure) => TransactionsFailure(failure),
    });
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is! TransactionsLoaded ||
        !current.hasMore ||
        current.isLoadingMore) {
      return;
    }
    emit(current.copyWith(isLoadingMore: true, loadMoreFailure: () => null));
    final result = await _repository.getTransactions(
      accountId: accountId,
      page: current.nextPage!,
    );
    if (isClosed) return;
    emit(switch (result) {
      Success(:final value) => current.copyWith(
        items: [...current.items, ...value.items],
        nextPage: () => value.nextPage,
        isLoadingMore: false,
      ),
      Failure(:final failure) => current.copyWith(
        isLoadingMore: false,
        loadMoreFailure: () => failure,
      ),
    });
  }
}
