import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/core/error/app_failure.dart';
import 'package:forge_demo/core/error/result.dart';
import 'package:forge_demo/features/accounts/data/datasources/accounts_remote_data_source.dart';
import 'package:forge_demo/features/accounts/data/repositories/accounts_repository_impl.dart';
import 'package:forge_demo/features/accounts/domain/entities/account.dart';
import 'package:mocktail/mocktail.dart';

import '../../../helpers/fixtures.dart';
import '../../../helpers/mocks.dart';

void main() {
  late MockDio dio;
  late AccountsRepositoryImpl repository;

  setUp(() {
    dio = MockDio();
    repository = AccountsRepositoryImpl(AccountsRemoteDataSource(dio));
  });

  test(
    'maps the 200 fixture: alias null stays null, balance becomes double',
    () async {
      when(() => dio.get<Map<String, dynamic>>('accounts')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(),
          data: fixture('accounts/list_accounts_200.json'),
        ),
      );

      final accounts = (await repository.getAccounts()).valueOrNull!;

      expect(accounts, hasLength(2));
      expect(accounts.first.alias, 'Nómina');
      expect(accounts[1].alias, isNull);
      expect(accounts[1].balance, 820.0);
      expect(accounts[1].type, AccountType.savings);
    },
  );

  test('timeout → NetworkFailure(isTimeout: true)', () async {
    when(() => dio.get<Map<String, dynamic>>('accounts')).thenThrow(
      DioException.receiveTimeout(
        timeout: const Duration(seconds: 30),
        requestOptions: RequestOptions(),
      ),
    );

    final result = await repository.getAccounts();

    expect(result, isA<Failure<List<Account>>>());
    expect(
      (result as Failure).failure,
      isA<NetworkFailure>().having((f) => f.isTimeout, 'isTimeout', isTrue),
    );
  });
}
