import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/l10n/failure_messages.dart';
import '../../../../core/widgets/feedback/empty_view.dart';
import '../../../../core/widgets/feedback/error_view.dart';
import '../../../../l10n/generated/app_localizations.dart';
import '../state/transactions_cubit.dart';
import '../state/transactions_state.dart';
import '../widgets/transaction_tile.dart';

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
    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification.metrics.extentAfter < 300) {
          context.read<TransactionsCubit>().loadMore();
        }
        return false;
      },
      child: ListView.builder(
        itemCount:
            state.items.length +
            (state.hasMore || state.loadMoreFailure != null ? 1 : 0),
        itemBuilder: (context, index) {
          if (index < state.items.length) {
            final item = state.items[index];
            return TransactionTile(
              key: ValueKey(item.id),
              transaction: item,
              fallbackDescription: l10n.transactionsNoDescription,
            );
          }
          final failure = state.loadMoreFailure;
          if (failure != null) {
            return ErrorView(
              message: failure.message(l10n),
              retryLabel: l10n.commonRetry,
              onRetry: context.read<TransactionsCubit>().loadMore,
              compact: true,
            );
          }
          return const Padding(
            padding: EdgeInsets.all(16),
            child: Center(child: CircularProgressIndicator()),
          );
        },
      ),
    );
  }
}
