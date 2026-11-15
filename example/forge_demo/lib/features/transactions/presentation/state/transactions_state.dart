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

/// Progress of "load more" below an already visible list. Sealed so that "loading" and "failed"
/// can never be true at once.
@immutable
sealed class LoadMore {
  const LoadMore();
}

final class LoadMoreIdle extends LoadMore {
  const LoadMoreIdle();

  @override
  bool operator ==(Object other) => other is LoadMoreIdle;

  @override
  int get hashCode => (LoadMoreIdle).hashCode;
}

final class LoadMoreInProgress extends LoadMore {
  const LoadMoreInProgress();

  @override
  bool operator ==(Object other) => other is LoadMoreInProgress;

  @override
  int get hashCode => (LoadMoreInProgress).hashCode;
}

final class LoadMoreFailed extends LoadMore {
  const LoadMoreFailed(this.failure);
  final AppFailure failure;

  @override
  bool operator ==(Object other) =>
      other is LoadMoreFailed && other.failure == failure;

  @override
  int get hashCode => Object.hash(LoadMoreFailed, failure);
}

final class TransactionsLoaded extends TransactionsState {
  const TransactionsLoaded({
    required this.items,
    required this.nextPage,
    this.loadMore = const LoadMoreIdle(),
  });

  final List<Transaction> items;
  final int? nextPage;
  final LoadMore loadMore;

  bool get hasMore => nextPage != null;

  TransactionsLoaded copyWith({
    List<Transaction>? items,
    int? Function()? nextPage,
    LoadMore? loadMore,
  }) => TransactionsLoaded(
    items: items ?? this.items,
    nextPage: nextPage != null ? nextPage() : this.nextPage,
    loadMore: loadMore ?? this.loadMore,
  );

  @override
  bool operator ==(Object other) =>
      other is TransactionsLoaded &&
      listEquals(other.items, items) &&
      other.nextPage == nextPage &&
      other.loadMore == loadMore;

  @override
  int get hashCode => Object.hash(Object.hashAll(items), nextPage, loadMore);
}
