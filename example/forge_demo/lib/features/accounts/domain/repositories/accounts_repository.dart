import '../../../../core/error/app_failure.dart';
import '../../../../core/error/result.dart';
import '../entities/account.dart';

/// Accounts of the signed-in user.
abstract interface class AccountsRepository {
  /// All accounts, in backend order. Fails with [NetworkFailure] when offline.
  Future<Result<List<Account>>> getAccounts();
}
