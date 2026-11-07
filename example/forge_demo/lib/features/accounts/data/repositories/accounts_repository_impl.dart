import '../../../../core/error/result.dart';
import '../../../../core/network/guard.dart';
import '../../domain/entities/account.dart';
import '../../domain/repositories/accounts_repository.dart';
import '../datasources/accounts_remote_data_source.dart';
import '../mappers/account_mapper.dart';

class AccountsRepositoryImpl implements AccountsRepository {
  AccountsRepositoryImpl(this._remote);

  final AccountsRemoteDataSource _remote;

  @override
  Future<Result<List<Account>>> getAccounts() =>
      guard(() async => (await _remote.getAccounts()).toEntity());
}
