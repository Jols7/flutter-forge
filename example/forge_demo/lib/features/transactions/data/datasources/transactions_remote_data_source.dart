import 'package:dio/dio.dart';

import '../models/transaction_dto.dart';

class TransactionsRemoteDataSource {
  TransactionsRemoteDataSource(this._dio);

  final Dio _dio;

  Future<TransactionsPageDto> getTransactions(
    String accountId, {
    required int page,
    int size = 20,
    CancelToken? cancelToken,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      'accounts/${Uri.encodeComponent(accountId)}/transactions',
      queryParameters: {'page': page, 'size': size},
      cancelToken: cancelToken,
    );
    return TransactionsPageDto.fromJson(response.data!);
  }
}
