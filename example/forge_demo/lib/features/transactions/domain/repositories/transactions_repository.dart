import '../../../../core/error/app_failure.dart';
import '../../../../core/error/result.dart';
import '../../../../core/utils/paginated.dart';
import '../entities/transaction.dart';

/// Read access to an account's movements.
abstract interface class TransactionsRepository {
  /// Newest-first page [page] (1-based) of [accountId]'s movements.
  ///
  /// Fails with [NotFoundFailure] for an unknown account and [NetworkFailure] when offline.
  Future<Result<Paginated<Transaction>>> getTransactions({
    required String accountId,
    int page = 1,
  });
}
