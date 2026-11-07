import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';

import '../data/datasources/transactions_remote_data_source.dart';
import '../data/repositories/transactions_repository_impl.dart';
import '../domain/repositories/transactions_repository.dart';
import '../presentation/state/transactions_cubit.dart';

void registerTransactionsModule(GetIt getIt) {
  getIt
    ..registerLazySingleton(() => TransactionsRemoteDataSource(getIt<Dio>()))
    ..registerLazySingleton<TransactionsRepository>(
      () => TransactionsRepositoryImpl(getIt<TransactionsRemoteDataSource>()),
    )
    ..registerFactoryParam<TransactionsCubit, String, void>(
      (accountId, _) => TransactionsCubit(
        getIt<TransactionsRepository>(),
        accountId: accountId,
      ),
    );
}
