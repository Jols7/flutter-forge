import 'package:json_annotation/json_annotation.dart';

part 'transaction_dto.g.dart';

@JsonSerializable(fieldRename: FieldRename.snake, createToJson: false)
class TransactionDto {
  const TransactionDto({
    required this.id,
    required this.amount,
    required this.currency,
    required this.bookedAt,
    this.description,
    this.category,
  });

  factory TransactionDto.fromJson(Map<String, dynamic> json) =>
      _$TransactionDtoFromJson(json);

  final String id;
  final String? description;
  final num amount;
  final String currency;
  final String bookedAt;
  final String? category;
}

@JsonSerializable(fieldRename: FieldRename.snake, createToJson: false)
class TransactionsPageDto {
  const TransactionsPageDto({required this.data, this.nextPage});

  factory TransactionsPageDto.fromJson(Map<String, dynamic> json) =>
      _$TransactionsPageDtoFromJson(json);

  final List<TransactionDto> data;
  final int? nextPage;
}
