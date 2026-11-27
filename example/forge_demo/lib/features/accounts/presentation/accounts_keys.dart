import 'package:flutter/widgets.dart';

/// Test keys of the accounts feature (flutter-forge conventions § 9).
abstract final class AccountsKeys {
  static const loading = Key('accounts_loading');
  static const empty = Key('accounts_empty');
  static const error = Key('accounts_error');
  static const list = Key('accounts_list');
  static Key item(String id) => Key('accounts_item_$id');
}
