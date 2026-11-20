# Test helpers (create once per project)

## `test/helpers/fixtures.dart`

```dart
import 'dart:convert';
import 'dart:io';

/// Reads a JSON fixture written by forge-api-contract: `fixture('transactions/list_transactions_200.json')`.
Map<String, dynamic> fixture(String path) =>
    jsonDecode(File('test/fixtures/$path').readAsStringSync()) as Map<String, dynamic>;
```

## `test/helpers/mocks.dart`

```dart
import 'package:dio/dio.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}
class MockTransactionsRemoteDataSource extends Mock implements TransactionsRemoteDataSource {}
class MockTransactionsRepository extends Mock implements TransactionsRepository {}

/// Builds a DioException with a response, as the HTTP layer would.
DioException dioError(int status, {Map<String, dynamic>? body, String path = 'x'}) {
  final options = RequestOptions(path: path);
  return DioException.badResponse(
    statusCode: status,
    requestOptions: options,
    response: Response<dynamic>(requestOptions: options, statusCode: status, data: body),
  );
}

DioException dioConnectionError() => DioException.connectionError(
      requestOptions: RequestOptions(path: 'x'),
      reason: 'offline',
    );
```

Register fallback values in `setUpAll` for any custom type used with `any()`:
`registerFallbackValue(const CreateTransferRequestDto(...))`.

## `test/helpers/pump_app.dart`

```dart
extension PumpApp on WidgetTester {
  Future<void> pumpApp(Widget widget, {Locale locale = const Locale('es')}) => pumpWidget(
        MaterialApp(
          theme: AppTheme.light(),
          locale: locale,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: widget,
        ),
      );
}
```

Riverpod projects wrap it in `ProviderScope(overrides: overrides, child: …)`, and the helper
takes `List<Override> overrides`. Projects using intl_utils use `S.delegate` and
`S.delegate.supportedLocales`.

## `test/helpers/pump_app_at.dart` (responsive matrix)

```dart
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

import 'pump_app.dart';

extension PumpAppAt on WidgetTester {
  /// Renders [widget] in a logical [size] at [textScale] and resets the view when the test ends.
  Future<void> pumpAppAt(Size size, double textScale, Widget widget) async {
    view.physicalSize = size * 3;
    view.devicePixelRatio = 3;
    platformDispatcher.textScaleFactorTestValue = textScale;
    addTearDown(() {
      view.resetPhysicalSize();
      view.resetDevicePixelRatio();
      platformDispatcher.clearTextScaleFactorTestValue();
    });
    await pumpApp(widget);
  }
}
```

If `textScaleFactorTestValue` is deprecated in the project's Flutter version, wrap the widget in
`MediaQuery(data: MediaQueryData(textScaler: TextScaler.linear(textScale)), child: widget)` instead.

## Coverage of new domain/data files

```bash
<flutter_command> test --coverage test/features/<feature>/
python3 - <<'PY'
import re, sys
feature = "lib/features/<feature>/"
hit = total = 0
for block in open("coverage/lcov.info").read().split("end_of_record"):
    m = re.search(r"SF:(.+)", block)
    if not m or not m.group(1).startswith(feature) or "/presentation/" in m.group(1) or m.group(1).endswith(".g.dart"):
        continue
    lh = re.search(r"LH:(\d+)", block); lf = re.search(r"LF:(\d+)", block)
    hit += int(lh.group(1)) if lh else 0; total += int(lf.group(1)) if lf else 0
print(f"domain+data coverage: {hit}/{total} = {hit / total:.1%}" if total else "no lines found")
PY
```
