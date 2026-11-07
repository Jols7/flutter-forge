import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/core/error/app_failure.dart';
import 'package:forge_demo/core/error/result.dart';
import 'package:forge_demo/core/utils/paginated.dart';
import 'package:forge_demo/features/transactions/domain/entities/transaction.dart';
import 'package:forge_demo/features/transactions/presentation/state/transactions_cubit.dart';
import 'package:forge_demo/features/transactions/presentation/state/transactions_state.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../helpers/mocks.dart';
import '../../../../helpers/sample_data.dart';

void main() {
  late MockTransactionsRepository repository;

  setUp(() => repository = MockTransactionsRepository());

  TransactionsCubit build() =>
      TransactionsCubit(repository, accountId: 'acc_1');

  void stubPage(int page, Result<Paginated<Transaction>> result) => when(
    () => repository.getTransactions(accountId: 'acc_1', page: page),
  ).thenAnswer((_) async => result);

  blocTest<TransactionsCubit, TransactionsState>(
    'load: emits Loading then Loaded',
    setUp: () =>
        stubPage(1, Success(Paginated(items: [tx1, tx2], nextPage: 2))),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => [
      const TransactionsLoading(),
      TransactionsLoaded(items: [tx1, tx2], nextPage: 2),
    ],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'load: an empty page emits Empty',
    setUp: () =>
        stubPage(1, const Success(Paginated(items: [], nextPage: null))),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => const [TransactionsLoading(), TransactionsEmpty()],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'load: failure keeps the failure type',
    setUp: () => stubPage(1, const Failure(NetworkFailure())),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => [
      const TransactionsLoading(),
      isA<TransactionsFailure>().having(
        (s) => s.failure,
        'failure',
        isA<NetworkFailure>(),
      ),
    ],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'loadMore appends the next page',
    setUp: () => stubPage(2, Success(Paginated(items: [tx2], nextPage: null))),
    build: build,
    seed: () => TransactionsLoaded(items: [tx1], nextPage: 2),
    act: (cubit) => cubit.loadMore(),
    expect: () => [
      TransactionsLoaded(items: [tx1], nextPage: 2, isLoadingMore: true),
      TransactionsLoaded(items: [tx1, tx2], nextPage: null),
    ],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'loadMore failure keeps loaded items',
    setUp: () => stubPage(2, const Failure(ServerFailure(statusCode: 500))),
    build: build,
    seed: () => TransactionsLoaded(items: [tx1], nextPage: 2),
    act: (cubit) => cubit.loadMore(),
    expect: () => [
      TransactionsLoaded(items: [tx1], nextPage: 2, isLoadingMore: true),
      isA<TransactionsLoaded>()
          .having((s) => s.items, 'items', [tx1])
          .having((s) => s.loadMoreFailure, 'failure', isA<ServerFailure>()),
    ],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'loadMore does nothing on the last page',
    build: build,
    seed: () => TransactionsLoaded(items: [tx1], nextPage: null),
    act: (cubit) => cubit.loadMore(),
    expect: () => <TransactionsState>[],
    verify: (_) => verifyNever(
      () => repository.getTransactions(
        accountId: any(named: 'accountId'),
        page: any(named: 'page'),
      ),
    ),
  );

  test('does not emit after close', () async {
    stubPage(1, Success(Paginated(items: [tx1], nextPage: null)));
    final cubit = build();
    final pending = cubit.load();
    await cubit.close();
    await expectLater(pending, completes);
  });
}
