import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/features/transactions/data/datasources/transactions_remote_data_source.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../helpers/fixtures.dart';
import '../../../../helpers/mocks.dart';

void main() {
  late MockDio dio;
  late TransactionsRemoteDataSource dataSource;

  setUp(() {
    dio = MockDio();
    dataSource = TransactionsRemoteDataSource(dio);
  });

  void stubGet(
    Future<Response<Map<String, dynamic>>> Function(Invocation) answer,
  ) => when(
    () => dio.get<Map<String, dynamic>>(
      any(),
      queryParameters: any(named: 'queryParameters'),
      cancelToken: any(named: 'cancelToken'),
    ),
  ).thenAnswer(answer);

  test('GETs the encoded path with paging and returns the DTO', () async {
    stubGet(
      (_) async => Response(
        requestOptions: RequestOptions(),
        data: fixture('accounts/list_transactions_200.json'),
      ),
    );

    final dto = await dataSource.getTransactions('acc/1', page: 2);

    verify(
      () => dio.get<Map<String, dynamic>>(
        'accounts/acc%2F1/transactions',
        queryParameters: {'page': 2, 'size': 20},
        cancelToken: null,
      ),
    ).called(1);
    expect(dto.data, hasLength(2));
  });

  test('lets DioException through', () {
    stubGet((_) => Future.error(dioError(500)));

    expect(
      dataSource.getTransactions('acc_1', page: 1),
      throwsA(isA<DioException>()),
    );
  });
}
