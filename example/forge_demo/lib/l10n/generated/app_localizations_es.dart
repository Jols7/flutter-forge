// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Spanish Castilian (`es`).
class AppLocalizationsEs extends AppLocalizations {
  AppLocalizationsEs([String locale = 'es']) : super(locale);

  @override
  String get appTitle => 'Forge Demo';

  @override
  String get accountsTitle => 'Mis cuentas';

  @override
  String get accountsEmpty => 'Aún no tienes cuentas';

  @override
  String get accountTypeChecking => 'Cuenta de cheques';

  @override
  String get accountTypeSavings => 'Cuenta de ahorro';

  @override
  String get accountTypeOther => 'Cuenta';

  @override
  String get transactionsTitle => 'Movimientos';

  @override
  String get transactionsEmpty => 'Aún no tienes movimientos';

  @override
  String get transactionsNoDescription => 'Sin descripción';

  @override
  String get commonRetry => 'Reintentar';

  @override
  String get errorOffline => 'Sin conexión. Revisa tu internet.';

  @override
  String get errorTimeout => 'La conexión tardó demasiado. Intenta de nuevo.';

  @override
  String get errorSessionExpired => 'Tu sesión expiró. Inicia sesión de nuevo.';

  @override
  String get errorForbidden => 'No tienes permiso para realizar esta acción.';

  @override
  String get errorNotFound => 'No encontramos lo que buscas.';

  @override
  String get errorValidation => 'Revisa los datos e intenta de nuevo.';

  @override
  String get errorConflict =>
      'La operación entró en conflicto. Actualiza e intenta de nuevo.';

  @override
  String get errorGeneric => 'Algo salió mal. Intenta de nuevo.';
}
