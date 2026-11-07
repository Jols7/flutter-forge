// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'transaction_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TransactionDto _$TransactionDtoFromJson(Map<String, dynamic> json) =>
    TransactionDto(
      id: json['id'] as String,
      amount: json['amount'] as num,
      currency: json['currency'] as String,
      bookedAt: json['booked_at'] as String,
      description: json['description'] as String?,
      category: json['category'] as String?,
    );

TransactionsPageDto _$TransactionsPageDtoFromJson(Map<String, dynamic> json) =>
    TransactionsPageDto(
      data: (json['data'] as List<dynamic>)
          .map((e) => TransactionDto.fromJson(e as Map<String, dynamic>))
          .toList(),
      nextPage: (json['next_page'] as num?)?.toInt(),
    );
