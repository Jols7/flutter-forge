import '../../../../core/error/result.dart';
import '../../../../core/network/guard.dart';
import '../../../../core/utils/paginated.dart';
import '../../domain/entities/transaction.dart';
import '../../domain/repositories/transactions_repository.dart';
import '../datasources/transactions_remote_data_source.dart';
import '../mappers/transaction_mapper.dart';

class TransactionsRepositoryImpl implements TransactionsRepository {
  TransactionsRepositoryImpl(this._remote);

  final TransactionsRemoteDataSource _remote;

  @override
  Future<Result<Paginated<Transaction>>> getTransactions({
    required String accountId,
    int page = 1,
  }) => guard(
    () async =>
        (await _remote.getTransactions(accountId, page: page)).toEntity(),
  );
}
