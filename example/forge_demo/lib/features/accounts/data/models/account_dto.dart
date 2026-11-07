import 'package:json_annotation/json_annotation.dart';

part 'account_dto.g.dart';

@JsonSerializable(fieldRename: FieldRename.snake, createToJson: false)
class AccountDto {
  const AccountDto({
    required this.id,
    required this.numberMasked,
    required this.currency,
    required this.balance,
    this.alias,
    this.type,
  });

  factory AccountDto.fromJson(Map<String, dynamic> json) =>
      _$AccountDtoFromJson(json);

  final String id;
  final String? alias;
  final String numberMasked;
  final String currency;
  final num balance;
  final String? type;
}

@JsonSerializable(createToJson: false)
class AccountsResponseDto {
  const AccountsResponseDto({required this.data});

  factory AccountsResponseDto.fromJson(Map<String, dynamic> json) =>
      _$AccountsResponseDtoFromJson(json);

  final List<AccountDto> data;
}
