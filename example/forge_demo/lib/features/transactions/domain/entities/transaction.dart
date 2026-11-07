import 'package:flutter/foundation.dart';

enum TransactionCategory { food, transport, salary, other }

@immutable
class Transaction {
  const Transaction({
    required this.id,
    required this.description,
    required this.amount,
    required this.currency,
    required this.bookedAt,
    required this.category,
  });

  final String id;
  final String description;
  final double amount;
  final String currency;
  final DateTime bookedAt;
  final TransactionCategory category;

  bool get isDebit => amount < 0;

  @override
  bool operator ==(Object other) =>
      other is Transaction &&
      other.id == id &&
      other.description == description &&
      other.amount == amount &&
      other.currency == currency &&
      other.bookedAt == bookedAt &&
      other.category == category;

  @override
  int get hashCode =>
      Object.hash(id, description, amount, currency, bookedAt, category);
}
