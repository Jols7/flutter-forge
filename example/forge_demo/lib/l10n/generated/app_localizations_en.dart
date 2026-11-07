// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Forge Demo';

  @override
  String get accountsTitle => 'My accounts';

  @override
  String get accountsEmpty => 'You don\'t have accounts yet';

  @override
  String get accountTypeChecking => 'Checking account';

  @override
  String get accountTypeSavings => 'Savings account';

  @override
  String get accountTypeOther => 'Account';

  @override
  String get transactionsTitle => 'Transactions';

  @override
  String get transactionsEmpty => 'No transactions yet';

  @override
  String get transactionsNoDescription => 'No description';

  @override
  String get commonRetry => 'Retry';

  @override
  String get errorOffline => 'You\'re offline. Check your connection.';

  @override
  String get errorTimeout => 'The connection took too long. Try again.';

  @override
  String get errorSessionExpired => 'Your session expired. Sign in again.';

  @override
  String get errorForbidden => 'You don\'t have permission to do this.';

  @override
  String get errorNotFound => 'We couldn\'t find what you\'re looking for.';

  @override
  String get errorValidation => 'Check the data and try again.';

  @override
  String get errorConflict =>
      'The operation conflicted. Refresh and try again.';

  @override
  String get errorGeneric => 'Something went wrong. Try again.';
}
