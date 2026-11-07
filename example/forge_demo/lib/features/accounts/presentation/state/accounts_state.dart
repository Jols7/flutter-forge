import 'package:flutter/foundation.dart';

import '../../../../core/error/app_failure.dart';
import '../../domain/entities/account.dart';

@immutable
sealed class AccountsState {
  const AccountsState();
}

final class AccountsLoading extends AccountsState {
  const AccountsLoading();

  @override
  bool operator ==(Object other) => other is AccountsLoading;

  @override
  int get hashCode => (AccountsLoading).hashCode;
}

final class AccountsEmpty extends AccountsState {
  const AccountsEmpty();

  @override
  bool operator ==(Object other) => other is AccountsEmpty;

  @override
  int get hashCode => (AccountsEmpty).hashCode;
}

final class AccountsFailure extends AccountsState {
  const AccountsFailure(this.failure);
  final AppFailure failure;
}

final class AccountsLoaded extends AccountsState {
  const AccountsLoaded(this.accounts);
  final List<Account> accounts;

  @override
  bool operator ==(Object other) =>
      other is AccountsLoaded && listEquals(other.accounts, accounts);

  @override
  int get hashCode => Object.hashAll(accounts);
}
