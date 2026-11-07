import 'package:flutter/material.dart';

import '../../../../core/utils/formatters.dart';
import '../../domain/entities/account.dart';

class AccountCard extends StatelessWidget {
  const AccountCard({
    super.key,
    required this.account,
    required this.title,
    required this.onTap,
  });

  final Account account;
  final String title;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final locale = Localizations.localeOf(context).toString();
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: textTheme.titleMedium),
                    const SizedBox(height: 4),
                    Text(account.maskedNumber, style: textTheme.bodySmall),
                  ],
                ),
              ),
              Text(
                formatMoney(
                  account.balance,
                  currency: account.currency,
                  locale: locale,
                ),
                style: textTheme.titleLarge,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
