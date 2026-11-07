import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../config/app_config.dart';
import 'interceptors/auth_interceptor.dart';
import 'mocks/demo_mocks.dart';
import 'mocks/mock_interceptor.dart';

const _redactedHeaders = {'authorization', 'cookie', 'set-cookie'};

Dio buildDio(AppConfig config, AuthInterceptor authInterceptor) {
  final dio = Dio(
    BaseOptions(
      baseUrl: config.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      contentType: Headers.jsonContentType,
      responseType: ResponseType.json,
    ),
  );
  dio.interceptors.add(authInterceptor);
  if (kDebugMode) {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final headers = {
            for (final e in options.headers.entries)
              e.key: _redactedHeaders.contains(e.key.toLowerCase())
                  ? '<redacted>'
                  : e.value,
          };
          debugPrint('→ ${options.method} ${options.uri.path} $headers');
          handler.next(options);
        },
        onResponse: (response, handler) {
          debugPrint(
            '← ${response.statusCode} ${response.requestOptions.uri.path}',
          );
          handler.next(response);
        },
      ),
    );
  }
  if (MockConfig.enabled) {
    dio.interceptors.insert(
      0,
      MockInterceptor(demoMocks, scenario: MockConfig.scenario),
    );
  }
  return dio;
}
