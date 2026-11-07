import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/core/error/app_failure.dart';
import 'package:forge_demo/core/error/result.dart';
import 'package:forge_demo/core/utils/paginated.dart';
import 'package:forge_demo/features/transactions/data/models/transaction_dto.dart';
import 'package:forge_demo/features/transactions/data/repositories/transactions_repository_impl.dart';
import 'package:forge_demo/features/transactions/domain/entities/transaction.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../helpers/fixtures.dart';
import '../../../../helpers/mocks.dart';

void main() {
  late MockTransactionsRemoteDataSource remote;
  late TransactionsRepositoryImpl repository;

  setUp(() {
    remote = MockTransactionsRemoteDataSource();
    repository = TransactionsRepositoryImpl(remote);
  });

  void stubThrow(Object error) => when(
    () => remote.getTransactions(any(), page: any(named: 'page')),
  ).thenThrow(error);

  test('returns Success with mapped entities', () async {
    when(
      () => remote.getTransactions(any(), page: any(named: 'page')),
    ).thenAnswer(
      (_) async => TransactionsPageDto.fromJson(
        fixture('accounts/list_transactions_200.json'),
      ),
    );

    final result = await repository.getTransactions(accountId: 'acc_1');

    expect(result, isA<Success<Paginated<Transaction>>>());
    expect(result.valueOrNull!.items, hasLength(2));
  });

  final cases = <String, (Object, Type)>{
    'offline → NetworkFailure': (dioConnectionError(), NetworkFailure),
    '401 → UnauthorizedFailure': (dioError(401), UnauthorizedFailure),
    '404 → NotFoundFailure': (
      dioError(404, body: fixture('accounts/list_transactions_404.json')),
      NotFoundFailure,
    ),
    '500 → ServerFailure': (dioError(500), ServerFailure),
    'bad payload → ParsingFailure': (
      const FormatException('bad'),
      ParsingFailure,
    ),
  };
  cases.forEach((name, data) {
    test(name, () async {
      stubThrow(data.$1);

      final result = await repository.getTransactions(accountId: 'acc_1');

      expect(result, isA<Failure<Paginated<Transaction>>>());
      expect((result as Failure).failure.runtimeType, data.$2);
    });
  });

  test('404 keeps the server message', () async {
    stubThrow(
      dioError(404, body: fixture('accounts/list_transactions_404.json')),
    );

    final failure =
        (await repository.getTransactions(accountId: 'x') as Failure).failure;

    expect(failure.serverMessage, 'La cuenta no existe');
  });
}
