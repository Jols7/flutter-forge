import 'package:flutter/foundation.dart';

/// Account product; unknown backend values map to [other].
enum AccountType { checking, savings, other }

/// An account owned by the signed-in user. The number arrives already masked.
@immutable
class Account {
  const Account({
    required this.id,
    required this.alias,
    required this.maskedNumber,
    required this.currency,
    required this.balance,
    required this.type,
  });

  final String id;
  final String? alias; // null: the UI shows the account type instead
  final String maskedNumber; // already masked by the backend: "•••• 4821"
  final String currency;
  final double balance;
  final AccountType type;

  @override
  bool operator ==(Object other) =>
      other is Account &&
      other.id == id &&
      other.alias == alias &&
      other.maskedNumber == maskedNumber &&
      other.currency == currency &&
      other.balance == balance &&
      other.type == type;

  @override
  int get hashCode =>
      Object.hash(id, alias, maskedNumber, currency, balance, type);
}
