import '../../../../core/error/result.dart';
import '../entities/account.dart';

abstract interface class AccountsRepository {
  Future<Result<List<Account>>> getAccounts();
}
