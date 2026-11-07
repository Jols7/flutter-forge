import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';

import '../../features/accounts/di/accounts_module.dart';
import '../../features/transactions/di/transactions_module.dart';
import '../config/app_config.dart';
import '../network/api_client.dart';
import '../network/interceptors/auth_interceptor.dart';
import '../storage/secure_storage.dart';

final getIt = GetIt.instance;

Future<void> configureDependencies(AppConfig config) async {
  getIt
    ..registerSingleton<AppConfig>(config)
    ..registerLazySingleton<SecureStorage>(SecureStorage.new)
    ..registerLazySingleton<AuthInterceptor>(
      () => AuthInterceptor(getIt<SecureStorage>()),
    )
    ..registerLazySingleton<Dio>(
      () => buildDio(config, getIt<AuthInterceptor>()),
    );
  registerAccountsModule(getIt);
  registerTransactionsModule(getIt);
}
