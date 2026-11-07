# State-manager test templates

## Cubit / Bloc — `bloc_test`

```dart
void main() {
  late MockTransactionsRepository repository;

  setUp(() => repository = MockTransactionsRepository());

  TransactionsCubit build() => TransactionsCubit(repository, accountId: 'acc_1');

  const page1 = Paginated(items: [tx1, tx2], nextPage: 2);

  blocTest<TransactionsCubit, TransactionsState>(
    'load: emits Loading then Loaded',
    setUp: () => when(() => repository.getTransactions(accountId: 'acc_1'))
        .thenAnswer((_) async => const Success(page1)),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => const [TransactionsLoading(), TransactionsLoaded(items: [tx1, tx2], nextPage: 2)],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'load: empty page emits Empty',
    setUp: () => when(() => repository.getTransactions(accountId: 'acc_1'))
        .thenAnswer((_) async => const Success(Paginated(items: [], nextPage: null))),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => const [TransactionsLoading(), TransactionsEmpty()],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'load: failure keeps the failure type',
    setUp: () => when(() => repository.getTransactions(accountId: 'acc_1'))
        .thenAnswer((_) async => const Failure(NetworkFailure())),
    build: build,
    act: (cubit) => cubit.load(),
    expect: () => [const TransactionsLoading(), isA<TransactionsFailure>().having((s) => s.failure, 'failure', isA<NetworkFailure>())],
  );

  blocTest<TransactionsCubit, TransactionsState>(
    'loadMore failure keeps loaded items',
    setUp: () => when(() => repository.getTransactions(accountId: 'acc_1', page: 2))
        .thenAnswer((_) async => const Failure(ServerFailure(statusCode: 500))),
    build: build,
    seed: () => const TransactionsLoaded(items: [tx1], nextPage: 2),
    act: (cubit) => cubit.loadMore(),
    expect: () => [
      const TransactionsLoaded(items: [tx1], nextPage: 2, isLoadingMore: true),
      isA<TransactionsLoaded>().having((s) => s.items, 'items', [tx1]).having((s) => s.loadMoreFailure, 'failure', isA<ServerFailure>()),
    ],
  );
}
```

States need value equality for `expect` lists of instances. Use `isA<…>().having(…)` for
states that hold failures without equality.

### Debounce and stale responses (`fakeAsync`)

```dart
test('AC-6: only the last amount is previewed and no loading shows before 250 ms', () {
  fakeAsync((async) {
    final completer1 = Completer<Result<TransferPreview>>();
    when(() => repository.previewTransfer(fromId: any(named: 'fromId'), toId: any(named: 'toId'), amount: 50, cancelToken: any(named: 'cancelToken')))
        .thenAnswer((_) => completer1.future);
    when(() => repository.previewTransfer(fromId: any(named: 'fromId'), toId: any(named: 'toId'), amount: 500, cancelToken: any(named: 'cancelToken')))
        .thenAnswer((_) async => const Success(preview500));
    final cubit = TransferCubit(repository)..selectAccounts(from, to);

    cubit.amountChanged('50');
    async.elapse(const Duration(milliseconds: 300));      // first request in flight
    cubit.amountChanged('500');
    async.elapse(const Duration(milliseconds: 100));
    expect(cubit.state.preview, isNot(isA<PreviewLoading>()));
    async.elapse(const Duration(milliseconds: 300));
    completer1.complete(const Success(preview50));          // stale: must be ignored
    async.flushMicrotasks();

    expect(cubit.state.preview, const PreviewReady(preview500));
    cubit.close();
  });
});
```

## Riverpod — `ProviderContainer`

```dart
ProviderContainer makeContainer(TransactionsRepository repository) {
  final container = ProviderContainer(overrides: [
    transactionsRepositoryProvider.overrideWithValue(repository),
  ]);
  addTearDown(container.dispose);
  return container;
}

test('build: loads the first page', () async {
  when(() => repository.getTransactions(accountId: 'acc_1')).thenAnswer((_) async => const Success(page1));
  final container = makeContainer(repository);

  expect(container.read(transactionsProvider('acc_1')), isA<AsyncLoading>());
  await expectLater(container.read(transactionsProvider('acc_1').future), completion(page1));
});

test('build: failure surfaces as AsyncError with the AppFailure', () async {
  when(() => repository.getTransactions(accountId: 'acc_1')).thenAnswer((_) async => const Failure(NetworkFailure()));
  final container = makeContainer(repository);
  final sub = container.listen(transactionsProvider('acc_1'), (_, __) {});
  await expectLater(container.read(transactionsProvider('acc_1').future), throwsA(isA<NetworkFailure>()));
  expect(sub.read(), isA<AsyncError>());
});
```

## Provider — ChangeNotifier

```dart
test('load: notifies and ends in Loaded', () async {
  when(() => repository.getTransactions(accountId: 'acc_1')).thenAnswer((_) async => const Success(page1));
  final viewModel = TransactionsViewModel(repository, accountId: 'acc_1');
  final states = <TransactionsState>[];
  viewModel.addListener(() => states.add(viewModel.state));

  await viewModel.load();

  expect(states, [const TransactionsLoading(), const TransactionsLoaded(items: [tx1, tx2], nextPage: 2)]);
});

test('no notification after dispose', () async {
  final completer = Completer<Result<Paginated<Transaction>>>();
  when(() => repository.getTransactions(accountId: 'acc_1')).thenAnswer((_) => completer.future);
  final viewModel = TransactionsViewModel(repository, accountId: 'acc_1');
  final pending = viewModel.load();
  viewModel.dispose();
  completer.complete(const Success(page1));
  await expectLater(pending, completes);                   // no "used after dispose" error
});
```
