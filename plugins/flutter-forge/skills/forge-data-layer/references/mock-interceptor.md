# Mock-first networking

Use this when an endpoint is `mock-agreed` (or a non-blocking gap). The DTO, data source,
repository, state and UI are then **final code** from day one, because only the HTTP layer
is faked. When the endpoint ships, delete its mock route. If the real JSON differs, only the
DTO and the mapper change.

## Toggle (compile-time, never shipped)

```dart
// lib/core/config/app_config.dart
abstract final class MockConfig {
  static const enabled = bool.fromEnvironment('USE_MOCKS');
  static const scenario = String.fromEnvironment('MOCK_SCENARIO', defaultValue: 'default');
}
```

Run with `--dart-define=USE_MOCKS=true [--dart-define=MOCK_SCENARIO=empty]`. Because the
flag is `const`, release builds without the define tree-shake the mocks away. Assert at
startup that mocks are never enabled on a forbidden flavor:

```dart
assert(!(MockConfig.enabled && config.flavor == Flavor.prod), 'Mocks are not allowed in prod');
if (MockConfig.enabled && config.flavor == Flavor.prod) throw StateError('USE_MOCKS in prod');
```

## Routes — `lib/core/network/mocks/<feature>_mocks.dart`

```dart
import 'mock_interceptor.dart';

/// Agreed with backend (<name>, 2026-11-06). Source: test/fixtures/transfers/*.json
const transfersMocks = <MockRoute>[
  MockRoute('GET', 'transfers/preview', {
    'default': MockResponse(200, r'''{"fee":0,"exchange_rate":0.0551,"amount_received":27.55,"total_debited":500}'''),
  }),
  MockRoute('POST', 'transfers', {
    'default': MockResponse(201, r'''{"id":"tr_1","status":"completed","reference":"FD-000123","created_at":"2026-11-01T10:00:00Z"}'''),
    'insufficient_funds': MockResponse(409, r'''{"code":"INSUFFICIENT_FUNDS","message":"Saldo insuficiente"}'''),
  }),
];
```

Keep the JSON identical to the fixture. The mapper tests parse the fixture, and the app parses
the mock, so both prove the same contract.

## Interceptor — `lib/core/network/mocks/mock_interceptor.dart`

```dart
import 'dart:convert';

import 'package:dio/dio.dart';

class MockResponse {
  const MockResponse(this.status, this.body, {this.delay = const Duration(milliseconds: 400)});
  final int status;
  final String body;
  final Duration delay;
}

class MockRoute {
  const MockRoute(this.method, this.pattern, this.scenarios);
  final String method;
  final String pattern;                     // relative path; {param} segments match anything
  final Map<String, MockResponse> scenarios;

  bool matches(RequestOptions options) {
    if (options.method.toUpperCase() != method) return false;
    final path = options.uri.path.replaceFirst(RegExp('^/'), '');
    final expected = pattern.split('/');
    final actual = path.split('/');
    final offset = actual.length - expected.length;   // tolerate a base-path prefix
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
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final route = routes.where((r) => r.matches(options)).firstOrNull;
    if (route == null) return handler.next(options);
    final response = route.scenarios[scenario] ?? route.scenarios['default']!;
    await Future<void>.delayed(response.delay);   // exercises loading states
    final result = Response<dynamic>(
      requestOptions: options,
      statusCode: response.status,
      data: jsonDecode(response.body),
    );
    if (response.status >= 400) {
      return handler.reject(
        DioException.badResponse(statusCode: response.status, requestOptions: options, response: result),
      );
    }
    handler.resolve(result);
  }
}
```

Register it **first** in `buildDio` when `MockConfig.enabled`, so auth and logging still run
for real routes:

```dart
if (MockConfig.enabled) {
  dio.interceptors.insert(0, MockInterceptor([...transfersMocks], scenario: MockConfig.scenario));
}
```

## Rules

- Use one mocks file per feature. Each file's header names who agreed to the contract, and when.
- Every mocked route appears in the run report under **Mocked routes**, so a reviewer cannot
  miss it.
- Mocks are not tests. Unit tests use mocktail and fixtures; they never use the interceptor.
- Remove the route when the real endpoint is live. `forge-audit` reports mocks whose endpoint
  is now `real` in the contract.
