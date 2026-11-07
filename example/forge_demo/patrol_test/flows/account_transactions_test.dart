import 'package:flutter/material.dart';
import 'package:forge_demo/features/accounts/presentation/widgets/account_card.dart';
import 'package:forge_demo/features/transactions/presentation/widgets/transaction_tile.dart';

import '../common/flow_runner.dart';
import '../common/flow_test.dart';
import '../common/screens.dart';
import '../routines/navigation_routines.dart';

void main() {
  flowTest(
    'Flow Accounts → Transactions: list, open, read movements, go back',
    ($) async {
      final flow = FlowRunner(
        $,
        name: 'AccountTransactions',
        entry: goToHome,
        entryProbe: Screens.home,
      );
      await flow.start();

      await flow.step('Home lists both accounts with masked numbers', () async {
        await $(AccountCard).at(1).waitUntilVisible();
        await $('•••• 4821').waitUntilVisible();
        await $('•••• 9034').waitUntilVisible();
        await $(
          'Cuenta de ahorro',
        ).waitUntilVisible(); // alias null → type label
      });

      await flow.step(
        'Tapping "Nómina" opens its movements',
        () async {
          await $('Nómina').tap();
          await $(
            Screens.transactions,
          ).waitUntilVisible(timeout: const Duration(seconds: 30));
          await $(
            TransactionTile,
          ).at(1).waitUntilVisible(timeout: const Duration(seconds: 30));
        },
        reached: Checkpoint(
          'transactions',
          Screens.transactions,
          reach: goToTransactions,
        ),
      );

      await flow.step(
        'Movements show description and the fallback for empty ones',
        () async {
          await $('Café').waitUntilVisible();
          await $('Sin descripción').waitUntilVisible();
        },
      );

      await flow.step('Back returns to the accounts list', () async {
        await $(BackButton).tap();
        await $(Screens.home).waitUntilVisible();
      });

      flow.finish();
    },
  );
}
