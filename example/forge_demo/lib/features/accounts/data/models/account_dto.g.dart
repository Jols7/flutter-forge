// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'account_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AccountDto _$AccountDtoFromJson(Map<String, dynamic> json) => AccountDto(
  id: json['id'] as String,
  numberMasked: json['number_masked'] as String,
  currency: json['currency'] as String,
  balance: json['balance'] as num,
  alias: json['alias'] as String?,
  type: json['type'] as String?,
);

AccountsResponseDto _$AccountsResponseDtoFromJson(Map<String, dynamic> json) =>
    AccountsResponseDto(
      data: (json['data'] as List<dynamic>)
          .map((e) => AccountDto.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
