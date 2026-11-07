import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';

import '../data/datasources/accounts_remote_data_source.dart';
import '../data/repositories/accounts_repository_impl.dart';
import '../domain/repositories/accounts_repository.dart';
import '../presentation/state/accounts_cubit.dart';

void registerAccountsModule(GetIt getIt) {
  getIt
    ..registerLazySingleton(() => AccountsRemoteDataSource(getIt<Dio>()))
    ..registerLazySingleton<AccountsRepository>(
      () => AccountsRepositoryImpl(getIt<AccountsRemoteDataSource>()),
    )
    ..registerFactory(() => AccountsCubit(getIt<AccountsRepository>()));
}
