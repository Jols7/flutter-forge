import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/features/accounts/presentation/pages/accounts_page.dart';
import 'package:forge_demo/features/transactions/presentation/pages/transactions_page.dart';

/// Page probes and copy shared by flows.
abstract final class Screens {
  static final home = find.byType(AccountsPage);
  static final transactions = find.byType(TransactionsPage);

  /// The demo has no authentication, so there is no "session lost" screen.
  static final login = find.byKey(const ValueKey('no-login-screen-in-demo'));
}
