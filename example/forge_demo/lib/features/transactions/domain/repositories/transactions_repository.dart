import '../../../../core/error/result.dart';
import '../../../../core/utils/paginated.dart';
import '../entities/transaction.dart';

abstract interface class TransactionsRepository {
  Future<Result<Paginated<Transaction>>> getTransactions({
    required String accountId,
    int page = 1,
  });
}
