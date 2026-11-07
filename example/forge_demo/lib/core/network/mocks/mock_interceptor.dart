import 'dart:convert';

import 'package:dio/dio.dart';

class MockResponse {
  const MockResponse(
    this.status,
    this.body, {
    this.delay = const Duration(milliseconds: 400),
  });
  final int status;
  final String body;
  final Duration delay;
}

class MockRoute {
  const MockRoute(this.method, this.pattern, this.scenarios);
  final String method;
  final String pattern;
  final Map<String, MockResponse> scenarios;

  bool matches(RequestOptions options) {
    if (options.method.toUpperCase() != method) return false;
    final path = options.uri.path.replaceFirst(RegExp('^/'), '');
    final expected = pattern.split('/');
    final actual = path.split('/');
    final offset = actual.length - expected.length;
    if (offset < 0) return false;
    for (var i = 0; i < expected.length; i++) {
      final segment = expected[i];
      if (segment.startsWith('{') && segment.endsWith('}')) continue;
      if (segment != actual[i + offset]) return false;
    }
    return true;
  }
}

class MockInterceptor extends Interceptor {
  MockInterceptor(this.routes, {this.scenario = 'default'});

  final List<MockRoute> routes;
  final String scenario;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final route = routes.where((r) => r.matches(options)).firstOrNull;
    if (route == null) return handler.next(options);
    final response = route.scenarios[scenario] ?? route.scenarios['default']!;
    await Future<void>.delayed(response.delay);
    final result = Response<dynamic>(
      requestOptions: options,
      statusCode: response.status,
      data: jsonDecode(response.body),
    );
    if (response.status >= 400) {
      return handler.reject(
        DioException.badResponse(
          statusCode: response.status,
          requestOptions: options,
          response: result,
        ),
      );
    }
    handler.resolve(result);
  }
}
