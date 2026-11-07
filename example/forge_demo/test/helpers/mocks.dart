import 'package:dio/dio.dart';
import 'package:forge_demo/features/accounts/domain/repositories/accounts_repository.dart';
import 'package:forge_demo/features/transactions/data/datasources/transactions_remote_data_source.dart';
import 'package:forge_demo/features/transactions/domain/repositories/transactions_repository.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

class MockTransactionsRemoteDataSource extends Mock
    implements TransactionsRemoteDataSource {}

class MockTransactionsRepository extends Mock
    implements TransactionsRepository {}

class MockAccountsRepository extends Mock implements AccountsRepository {}

/// Builds a DioException with a response, as the HTTP layer would.
DioException dioError(
  int status, {
  Map<String, dynamic>? body,
  String path = 'x',
}) {
  final options = RequestOptions(path: path);
  return DioException.badResponse(
    statusCode: status,
    requestOptions: options,
    response: Response<dynamic>(
      requestOptions: options,
      statusCode: status,
      data: body,
    ),
  );
}

DioException dioConnectionError() => DioException.connectionError(
  requestOptions: RequestOptions(path: 'x'),
  reason: 'offline',
);
