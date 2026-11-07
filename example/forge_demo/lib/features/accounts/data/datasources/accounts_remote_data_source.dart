import 'package:dio/dio.dart';

import '../models/account_dto.dart';

class AccountsRemoteDataSource {
  AccountsRemoteDataSource(this._dio);

  final Dio _dio;

  Future<AccountsResponseDto> getAccounts() async {
    final response = await _dio.get<Map<String, dynamic>>('accounts');
    return AccountsResponseDto.fromJson(response.data!);
  }
}
