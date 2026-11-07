import '../../../../core/utils/paginated.dart';
import '../../domain/entities/transaction.dart';
import '../models/transaction_dto.dart';

extension TransactionDtoMapper on TransactionDto {
  Transaction toEntity() => Transaction(
    id: id,
    description: description ?? '',
    amount: amount.toDouble(),
    currency: currency,
    bookedAt: DateTime.parse(bookedAt).toLocal(),
    category: _category(category),
  );
}

extension TransactionsPageDtoMapper on TransactionsPageDto {
  Paginated<Transaction> toEntity() => Paginated(
    items: data.map((dto) => dto.toEntity()).toList(growable: false),
    nextPage: nextPage,
  );
}

TransactionCategory _category(String? raw) =>
    TransactionCategory.values.firstWhere(
      (value) => value.name == raw,
      orElse: () => TransactionCategory.other,
    );
