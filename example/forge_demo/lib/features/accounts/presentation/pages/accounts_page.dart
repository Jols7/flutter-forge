import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/l10n/failure_messages.dart';
import '../../../../core/widgets/feedback/empty_view.dart';
import '../../../../core/widgets/feedback/error_view.dart';
import '../../../../l10n/generated/app_localizations.dart';
import '../../domain/entities/account.dart';
import '../state/accounts_cubit.dart';
import '../state/accounts_state.dart';
import '../widgets/account_card.dart';

class AccountsPage extends StatelessWidget {
  const AccountsPage({super.key});

  static const routeName = 'accounts';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.accountsTitle)),
      body: BlocBuilder<AccountsCubit, AccountsState>(
        builder: (context, state) => switch (state) {
          AccountsLoading() => const Center(child: CircularProgressIndicator()),
          AccountsEmpty() => EmptyView(message: l10n.accountsEmpty),
          AccountsFailure(:final failure) => ErrorView(
            message: failure.message(l10n),
            retryLabel: l10n.commonRetry,
            onRetry: context.read<AccountsCubit>().load,
          ),
          AccountsLoaded(:final accounts) => ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: accounts.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final account = accounts[index];
              return AccountCard(
                key: ValueKey(account.id),
                account: account,
                title: account.alias ?? _typeLabel(l10n, account.type),
                onTap: () => context.pushNamed(
                  'transactions',
                  pathParameters: {'accountId': account.id},
                ),
              );
            },
          ),
        },
      ),
    );
  }

  String _typeLabel(AppLocalizations l10n, AccountType type) => switch (type) {
    AccountType.checking => l10n.accountTypeChecking,
    AccountType.savings => l10n.accountTypeSavings,
    AccountType.other => l10n.accountTypeOther,
  };
}
