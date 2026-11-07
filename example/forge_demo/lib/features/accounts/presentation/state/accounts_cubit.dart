import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/error/result.dart';
import '../../domain/repositories/accounts_repository.dart';
import 'accounts_state.dart';

class AccountsCubit extends Cubit<AccountsState> {
  AccountsCubit(this._repository) : super(const AccountsLoading());

  final AccountsRepository _repository;

  Future<void> load() async {
    emit(const AccountsLoading());
    final result = await _repository.getAccounts();
    if (isClosed) return;
    emit(switch (result) {
      Success(:final value) when value.isEmpty => const AccountsEmpty(),
      Success(:final value) => AccountsLoaded(value),
      Failure(:final failure) => AccountsFailure(failure),
    });
  }
}
