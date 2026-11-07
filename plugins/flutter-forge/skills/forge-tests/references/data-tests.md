# Data and domain test templates

## Mappers

```dart
void main() {
  group('TransactionsPageDtoMapper', () {
    test('maps the 200 fixture to entities', () {
      final page = TransactionsPageDto.fromJson(fixture('accounts/list_transactions_200.json')).toEntity();

      expect(page.items, hasLength(2));
      expect(page.items.first.amount, -85.0);
      expect(page.items.first.bookedAt, DateTime.parse('2026-10-30T14:05:00Z').toLocal());
      expect(page.nextPage, 2);
    });

    test('null description and category fall back to defaults', () {
      final tx = TransactionsPageDto.fromJson(fixture('accounts/list_transactions_200.json')).toEntity().items[1];

      expect(tx.description, '');
      expect(tx.category, TransactionCategory.other);
    });

    test('integer amounts become doubles', () {
      final dto = TransactionDto.fromJson({...baseJson, 'amount': 12000});
      expect(dto.toEntity().amount, 12000.0);
    });

    test('malformed payload throws, so guard() reports ParsingFailure', () {
      expect(() => TransactionDto.fromJson({'id': 1}), throwsA(isA<TypeError>()));
    });
  });
}
```

## Data sources

```dart
void main() {
  late MockDio dio;
  late TransactionsRemoteDataSource dataSource;

  setUp(() {
    dio = MockDio();
    dataSource = TransactionsRemoteDataSource(dio);
  });

  test('GETs the encoded path with paging and returns the DTO', () async {
    when(() => dio.get<Map<String, dynamic>>(
          any(),
          queryParameters: any(named: 'queryParameters'),
          cancelToken: any(named: 'cancelToken'),
        )).thenAnswer((_) async => Response(
          requestOptions: RequestOptions(),
          data: fixture('accounts/list_transactions_200.json'),
        ));

    final dto = await dataSource.getTransactions('acc/1', page: 2);

    verify(() => dio.get<Map<String, dynamic>>(
          'accounts/acc%2F1/transactions',
          queryParameters: {'page': 2, 'size': 20},
          cancelToken: null,
        )).called(1);
    expect(dto.data, hasLength(2));
  });

  test('lets DioException through', () {
    when(() => dio.get<Map<String, dynamic>>(any(),
        queryParameters: any(named: 'queryParameters'),
        cancelToken: any(named: 'cancelToken'))).thenThrow(dioError(500));

    expect(dataSource.getTransactions('acc_1', page: 1), throwsA(isA<DioException>()));
  });
}
```

## Repositories

```dart
void main() {
  late MockTransactionsRemoteDataSource remote;
  late TransactionsRepositoryImpl repository;

  setUp(() {
    remote = MockTransactionsRemoteDataSource();
    repository = TransactionsRepositoryImpl(remote);
  });

  void stubThrow(Object error) => when(() => remote.getTransactions(any(), page: any(named: 'page')))
      .thenThrow(error);

  test('returns Success with mapped entities', () async {
    when(() => remote.getTransactions(any(), page: any(named: 'page'))).thenAnswer(
      (_) async => TransactionsPageDto.fromJson(fixture('accounts/list_transactions_200.json')),
    );

    final result = await repository.getTransactions(accountId: 'acc_1');

    expect(result, isA<Success<Paginated<Transaction>>>());
    expect(result.valueOrNull!.items, hasLength(2));
  });

  final cases = <String, (Object, Type)>{
    'offline → NetworkFailure': (dioConnectionError(), NetworkFailure),
    '401 → UnauthorizedFailure': (dioError(401), UnauthorizedFailure),
    '404 → NotFoundFailure': (dioError(404, body: fixture('accounts/list_transactions_404.json')), NotFoundFailure),
    '500 → ServerFailure': (dioError(500), ServerFailure),
    'bad payload → ParsingFailure': (const FormatException('bad'), ParsingFailure),
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
    stubThrow(dioError(404, body: fixture('accounts/list_transactions_404.json')));
    final failure = (await repository.getTransactions(accountId: 'x') as Failure).failure;
    expect(failure.serverMessage, 'La cuenta no existe');
  });
}
```

For business codes, assert `BusinessFailure` and its `code`, using the 409 fixture
(`create_transfer_409.json` → `INSUFFICIENT_FUNDS`).

## Domain (validators / use cases)

```dart
group('TransferAmount', () {
  test('R-1: below the minimum is invalid', () => expect(TransferAmount.parse('9.99').error, AmountError.belowMinimum));
  test('R-1: the minimum itself is valid', () => expect(TransferAmount.parse('10.00').isValid, isTrue));
  test('rejects non-numeric input', () => expect(TransferAmount.parse('1O').error, AmountError.notANumber));
});
```
