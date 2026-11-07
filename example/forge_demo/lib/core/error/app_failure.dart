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

final class NetworkFailure extends AppFailure {
  const NetworkFailure({super.cause, this.isTimeout = false});
  final bool isTimeout;
}

final class UnauthorizedFailure extends AppFailure {
  const UnauthorizedFailure({super.serverMessage, super.cause});
}

final class ForbiddenFailure extends AppFailure {
  const ForbiddenFailure({super.serverMessage, super.cause});
}

final class NotFoundFailure extends AppFailure {
  const NotFoundFailure({super.serverMessage, super.cause});
}

final class ValidationFailure extends AppFailure {
  const ValidationFailure({
    super.serverMessage,
    super.cause,
    this.fieldErrors = const {},
  });
  final Map<String, String> fieldErrors;
}

final class ConflictFailure extends AppFailure {
  const ConflictFailure({super.serverMessage, super.cause});
}

final class BusinessFailure extends AppFailure {
  const BusinessFailure({required this.code, super.serverMessage, super.cause});
  final String code;
}

final class ServerFailure extends AppFailure {
  const ServerFailure({
    required this.statusCode,
    super.serverMessage,
    super.cause,
  });
  final int? statusCode;
}

final class ParsingFailure extends AppFailure {
  const ParsingFailure({super.cause});
}
