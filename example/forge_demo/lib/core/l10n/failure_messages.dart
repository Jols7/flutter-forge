import '../../l10n/generated/app_localizations.dart';
import '../error/app_failure.dart';

extension AppFailureMessage on AppFailure {
  String message(AppLocalizations l10n) => switch (this) {
    NetworkFailure(isTimeout: true) => l10n.errorTimeout,
    NetworkFailure() => l10n.errorOffline,
    UnauthorizedFailure() => l10n.errorSessionExpired,
    ForbiddenFailure() => l10n.errorForbidden,
    NotFoundFailure() => l10n.errorNotFound,
    ValidationFailure(:final serverMessage) =>
      serverMessage ?? l10n.errorValidation,
    ConflictFailure() => l10n.errorConflict,
    BusinessFailure() => serverMessage ?? l10n.errorGeneric,
    ServerFailure() || ParsingFailure() => l10n.errorGeneric,
  };
}
