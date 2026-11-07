import 'package:flutter/foundation.dart';

import '../../../../core/error/app_failure.dart';
import '../../domain/entities/transaction.dart';

@immutable
sealed class TransactionsState {
  const TransactionsState();
}

final class TransactionsLoading extends TransactionsState {
  const TransactionsLoading();

  @override
  bool operator ==(Object other) => other is TransactionsLoading;

  @override
  int get hashCode => (TransactionsLoading).hashCode;
}

final class TransactionsEmpty extends TransactionsState {
  const TransactionsEmpty();

  @override
  bool operator ==(Object other) => other is TransactionsEmpty;

  @override
  int get hashCode => (TransactionsEmpty).hashCode;
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
  final AppFailure? loadMoreFailure;

  bool get hasMore => nextPage != null;

  TransactionsLoaded copyWith({
    List<Transaction>? items,
    int? Function()? nextPage,
    bool? isLoadingMore,
    AppFailure? Function()? loadMoreFailure,
  }) => TransactionsLoaded(
    items: items ?? this.items,
    nextPage: nextPage != null ? nextPage() : this.nextPage,
    isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    loadMoreFailure: loadMoreFailure != null
        ? loadMoreFailure()
        : this.loadMoreFailure,
  );

  @override
  bool operator ==(Object other) =>
      other is TransactionsLoaded &&
      listEquals(other.items, items) &&
      other.nextPage == nextPage &&
      other.isLoadingMore == isLoadingMore &&
      other.loadMoreFailure == loadMoreFailure;

  @override
  int get hashCode => Object.hash(
    Object.hashAll(items),
    nextPage,
    isLoadingMore,
    loadMoreFailure,
  );
}
