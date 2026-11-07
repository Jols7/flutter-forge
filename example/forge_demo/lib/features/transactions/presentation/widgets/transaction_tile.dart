import 'package:flutter/material.dart';

import '../../../../core/utils/formatters.dart';
import '../../domain/entities/transaction.dart';

class TransactionTile extends StatelessWidget {
  const TransactionTile({
    super.key,
    required this.transaction,
    required this.fallbackDescription,
  });

  final Transaction transaction;
  final String fallbackDescription;

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).toString();
    final colors = Theme.of(context).colorScheme;
    final amount = formatMoney(
      transaction.amount,
      currency: transaction.currency,
      locale: locale,
    );
    return ListTile(
      leading: Icon(
        transaction.isDebit ? Icons.arrow_upward : Icons.arrow_downward,
        color: transaction.isDebit ? colors.error : colors.primary,
        semanticLabel: null,
      ),
      title: Text(
        transaction.description.isEmpty
            ? fallbackDescription
            : transaction.description,
      ),
      subtitle: Text(formatDate(transaction.bookedAt, locale: locale)),
      trailing: Text(amount, style: Theme.of(context).textTheme.titleMedium),
    );
  }
}
