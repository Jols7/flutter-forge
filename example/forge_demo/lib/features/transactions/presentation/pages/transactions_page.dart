import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/l10n/failure_messages.dart';
import '../../../../core/widgets/feedback/empty_view.dart';
import '../../../../core/widgets/feedback/error_view.dart';
import '../../../../l10n/generated/app_localizations.dart';
import '../state/transactions_cubit.dart';
import '../state/transactions_state.dart';
import '../widgets/load_more_on_scroll.dart';
import '../widgets/transaction_tile.dart';
import '../widgets/transactions_list_footer.dart';

class TransactionsPage extends StatelessWidget {
  const TransactionsPage({super.key});

  static const routeName = 'transactions';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.transactionsTitle)),
      body: BlocBuilder<TransactionsCubit, TransactionsState>(
        builder: (context, state) => switch (state) {
          TransactionsLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
          TransactionsEmpty() => EmptyView(message: l10n.transactionsEmpty),
          TransactionsFailure(:final failure) => ErrorView(
            message: failure.message(l10n),
            retryLabel: l10n.commonRetry,
            onRetry: context.read<TransactionsCubit>().load,
          ),
          TransactionsLoaded() => _TransactionsList(state: state),
        },
      ),
    );
  }
}

class _TransactionsList extends StatelessWidget {
  const _TransactionsList({required this.state});

  final TransactionsLoaded state;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return LoadMoreOnScroll(
      child: ListView.builder(
        itemCount: state.listLength,
        itemBuilder: (context, index) {
          if (index >= state.items.length) {
            return TransactionsListFooter(state: state);
          }
          final item = state.items[index];
          return TransactionTile(
            key: ValueKey(item.id),
            transaction: item,
            fallbackDescription: l10n.transactionsNoDescription,
          );
        },
      ),
    );
  }
}
