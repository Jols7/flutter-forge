# Result and AppFailure

This is the error model for `architecture.errors: result`. Create the files once in
`paths.error` (default `lib/core/error/`); `forge-profile` does it in `mode: new`. It has no
dependencies besides Dart 3 sealed classes.

## `result.dart`

```dart
/// Outcome of an operation that can fail in an expected way.
///
/// Repositories return it; data sources throw; presentation switches on it.
sealed class Result<T> {
  const Result();

  const factory Result.success(T value) = Success<T>;
  const factory Result.failure(AppFailure failure) = Failure<T>;

  bool get isSuccess => this is Success<T>;

  T? get valueOrNull => switch (this) {
        Success<T>(:final value) => value,
        Failure<T>() => null,
      };

  R fold<R>({
    required R Function(T value) onSuccess,
    required R Function(AppFailure failure) onFailure,
  }) =>
      switch (this) {
        Success<T>(:final value) => onSuccess(value),
        Failure<T>(:final failure) => onFailure(failure),
      };

  Result<R> map<R>(R Function(T value) transform) => switch (this) {
        Success<T>(:final value) => Success(transform(value)),
        Failure<T>(:final failure) => Failure(failure),
      };

  Future<Result<R>> flatMap<R>(Future<Result<R>> Function(T value) next) async =>
      switch (this) {
        Success<T>(:final value) => next(value),
        Failure<T>(:final failure) => Failure(failure),
      };
}

final class Success<T> extends Result<T> {
  const Success(this.value);
  final T value;
}

final class Failure<T> extends Result<T> {
  const Failure(this.failure);
  final AppFailure failure;
}
```

`import 'app_failure.dart';` at the top. Use `void` results as `Result<void>`, returning
`const Success(null)`.

## `app_failure.dart`

```dart
/// Expected failures the UI knows how to explain. Unexpected bugs are NOT failures:
/// they propagate to the global error handler (FlutterError / PlatformDispatcher).
/// Implements [Exception] so APIs that expect thrown errors (e.g. Riverpod's AsyncValue)
/// can carry it without tripping `only_throw_errors`.
sealed class AppFailure implements Exception {
  const AppFailure({this.serverMessage, this.cause});

  /// User-facing message sent by the backend, if any. Never contains stack traces.
  final String? serverMessage;

  /// Original error, for logging only. Never shown to the user.
  final Object? cause;
}

final class NetworkFailure extends AppFailure {        // offline, DNS, timeout, TLS
  const NetworkFailure({super.cause, this.isTimeout = false});
  final bool isTimeout;
}

final class UnauthorizedFailure extends AppFailure {   // 401: session invalid
  const UnauthorizedFailure({super.serverMessage, super.cause});
}

final class ForbiddenFailure extends AppFailure {      // 403: authenticated, not allowed
  const ForbiddenFailure({super.serverMessage, super.cause});
}

final class NotFoundFailure extends AppFailure {       // 404
  const NotFoundFailure({super.serverMessage, super.cause});
}

final class ValidationFailure extends AppFailure {     // 400 / 422 with field errors
  const ValidationFailure({super.serverMessage, super.cause, this.fieldErrors = const {}});
  final Map<String, String> fieldErrors;
}

final class ConflictFailure extends AppFailure {       // 409: duplicate, stale version
  const ConflictFailure({super.serverMessage, super.cause});
}

final class ServerFailure extends AppFailure {         // 5xx and unexpected 4xx
  const ServerFailure({required this.statusCode, super.serverMessage, super.cause});
  final int? statusCode;
}

final class ParsingFailure extends AppFailure {        // response does not match the DTO
  const ParsingFailure({super.cause});
}
```

```dart
final class BusinessFailure extends AppFailure {       // known domain error code from the backend
  const BusinessFailure({required this.code, super.serverMessage, super.cause});
  final String code;                                   // e.g. 'INSUFFICIENT_FUNDS'
}
```

Feature-specific errors go through `BusinessFailure.code`. You cannot subclass `AppFailure`
in a feature, because sealed subclasses must live in the same library. That restriction is
what keeps every `switch` over `AppFailure` exhaustive. The feature declares its codes as
constants in its `domain/` (`abstract final class TransferErrorCodes { static const
insufficientFunds = 'INSUFFICIENT_FUNDS'; }`). The repository maps the backend's error code
into `BusinessFailure`. The UI then switches on the code where the HU defines a specific
message.

## `dio_failure_mapper.dart` (core/network)

```dart
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
  final message = _readMessage(e.response?.data, messageKey);
  final code = _readMessage(e.response?.data, codeKey);
  if (code != null && businessCodes.contains(code)) {
    return BusinessFailure(code: code, serverMessage: message, cause: e);
  }
  return switch (e.type) {
    DioExceptionType.connectionTimeout ||
    DioExceptionType.sendTimeout ||
    DioExceptionType.receiveTimeout =>
      NetworkFailure(cause: e, isTimeout: true),
    DioExceptionType.connectionError ||
    DioExceptionType.badCertificate =>
      NetworkFailure(cause: e),
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

String? _readMessage(Object? data, String key) =>
    data is Map && data[key] is String ? data[key] as String : null;

Map<String, String> _readFieldErrors(Object? data) {
  final errors = data is Map ? data['errors'] : null;
  if (errors is! Map) return const {};
  return {
    for (final entry in errors.entries)
      '${entry.key}': entry.value is List ? (entry.value as List).join('\n') : '${entry.value}',
  };
}
```

Set the defaults of `messageKey` and `codeKey` from `networking.error_message_key` in the profile
and from the error shape in `contract.md`, when the files are created. `businessCodes` holds the
codes the feature handles specifically, and the repository passes them in. Adapt
`_readFieldErrors` to the backend's validation shape.

## Guard helper for repositories — `core/network/guard.dart`

```dart
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
```

This removes the duplicated `try/on DioException` block from every repository method.
`TypeError` is caught **only** here, because a malformed payload surfaces as a cast error
inside `fromJson`. Other `Error`s (bugs) still propagate.

## Rules

| ❌ Don't | ✅ Do |
|---|---|
| `throw 'Error desconocido'` / throw any `String` | Return `Failure(…)` from repositories; throw typed exceptions in data sources |
| `catch (e) { return false; }` | Map to a specific `AppFailure`; the UI decides the message |
| Show `failure.cause.toString()` or `e.toString()` to users | Map the failure type to localized copy (`forge-presentation`); `serverMessage` only when the backend guarantees it is user-safe |
| Catch `Error` (bugs) broadly | Let it reach `PlatformDispatcher.onError` / crash reporting |
| Log `cause` with request bodies | Log type + status + endpoint; never tokens, PII or financial data (`forge-security`) |
| `Result` in data sources | Data sources throw; repositories are the only translators |
