import 'package:dio/dio.dart';

import '../error/app_failure.dart';

/// Single place where transport errors become [AppFailure]s.
AppFailure mapDioException(
  DioException e, {
  String messageKey = 'message',
  String codeKey = 'code',
  Set<String> businessCodes = const {},
}) {
  final status = e.response?.statusCode;
  final message = _readString(e.response?.data, messageKey);
  final code = _readString(e.response?.data, codeKey);
  if (code != null && businessCodes.contains(code)) {
    return BusinessFailure(code: code, serverMessage: message, cause: e);
  }
  return switch (e.type) {
    DioExceptionType.connectionTimeout ||
    DioExceptionType.sendTimeout ||
    DioExceptionType.receiveTimeout => NetworkFailure(
      cause: e,
      isTimeout: true,
    ),
    DioExceptionType.connectionError ||
    DioExceptionType.badCertificate => NetworkFailure(cause: e),
    DioExceptionType.cancel => NetworkFailure(cause: e),
    _ => switch (status) {
      401 => UnauthorizedFailure(serverMessage: message, cause: e),
      403 => ForbiddenFailure(serverMessage: message, cause: e),
      404 => NotFoundFailure(serverMessage: message, cause: e),
      409 => ConflictFailure(serverMessage: message, cause: e),
      400 || 422 => ValidationFailure(
        serverMessage: message,
        cause: e,
        fieldErrors: _readFieldErrors(e.response?.data),
      ),
      _ => ServerFailure(statusCode: status, serverMessage: message, cause: e),
    },
  };
}

String? _readString(Object? data, String key) =>
    data is Map && data[key] is String ? data[key] as String : null;

Map<String, String> _readFieldErrors(Object? data) {
  final errors = data is Map ? data['errors'] : null;
  if (errors is! Map) return const {};
  return {
    for (final entry in errors.entries)
      '${entry.key}': entry.value is List
          ? (entry.value as List).join('\n')
          : '${entry.value}',
  };
}
