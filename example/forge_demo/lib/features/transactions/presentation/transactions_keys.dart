import 'package:flutter/widgets.dart';

/// Test keys of the transactions feature (flutter-forge conventions § 9).
abstract final class TransactionsKeys {
  static const loading = Key('transactions_loading');
  static const empty = Key('transactions_empty');
  static const error = Key('transactions_error');
  static const list = Key('transactions_list');
  static Key item(String id) => Key('transactions_item_$id');
}
