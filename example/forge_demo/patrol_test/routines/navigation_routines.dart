import 'package:forge_demo/features/accounts/presentation/widgets/account_card.dart';
import 'package:patrol/patrol.dart';

import '../common/screens.dart';

Future<void> goToHome(PatrolIntegrationTester $) async {
  await $(Screens.home).waitUntilVisible();
  await $(
    AccountCard,
  ).first.waitUntilVisible(timeout: const Duration(seconds: 30));
}

Future<void> goToTransactions(PatrolIntegrationTester $) async {
  await goToHome($);
  await $(AccountCard).first.tap();
  await $(
    Screens.transactions,
  ).waitUntilVisible(timeout: const Duration(seconds: 30));
}
