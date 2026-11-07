import 'package:dio/dio.dart';

import '../error/app_failure.dart';
import '../error/result.dart';
import 'dio_failure_mapper.dart';

/// Runs a data-source call and maps every expected error to a [Failure].
Future<Result<T>> guard<T>(
  Future<T> Function() body, {
  Set<String> businessCodes = const {},
}) async {
  try {
    return Success(await body());
  } on DioException catch (e) {
    return Failure(mapDioException(e, businessCodes: businessCodes));
  } on FormatException catch (e) {
    return Failure(ParsingFailure(cause: e));
    // ignore: avoid_catching_errors — json_serializable reports malformed payloads as TypeError
  } on TypeError catch (e) {
    return Failure(ParsingFailure(cause: e));
  }
}
