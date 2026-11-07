import 'package:forge_demo/features/transactions/domain/entities/transaction.dart';

final tx1 = Transaction(
  id: 'tx_1',
  description: 'Café',
  amount: -85,
  currency: 'MXN',
  bookedAt: DateTime.utc(2026, 10, 30, 14, 5).toLocal(),
  category: TransactionCategory.food,
);

final tx2 = Transaction(
  id: 'tx_2',
  description: '',
  amount: 12000,
  currency: 'MXN',
  bookedAt: DateTime.utc(2026, 10, 29, 9).toLocal(),
  category: TransactionCategory.other,
);
