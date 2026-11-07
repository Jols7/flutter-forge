import 'package:intl/intl.dart';

String formatMoney(
  double amount, {
  required String currency,
  required String locale,
}) =>
    NumberFormat.simpleCurrency(locale: locale, name: currency).format(amount);

String formatDate(DateTime date, {required String locale}) =>
    DateFormat.yMMMd(locale).format(date);
