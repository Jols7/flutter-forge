import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/l10n/failure_messages.dart';
import '../../../../core/widgets/feedback/error_view.dart';
import '../../../../l10n/generated/app_localizations.dart';
import '../state/transactions_cubit.dart';
import '../state/transactions_state.dart';

/// The row after the last item: a retry view when loading more failed, else a spinner.
class TransactionsListFooter extends StatelessWidget {
  const TransactionsListFooter({super.key, required this.state});

  final TransactionsLoaded state;

  @override
  Widget build(BuildContext context) {
    if (state.loadMore case LoadMoreFailed(:final failure)) {
      final l10n = AppLocalizations.of(context);
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
  }
}
