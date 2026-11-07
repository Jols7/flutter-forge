import '../../domain/entities/account.dart';
import '../models/account_dto.dart';

extension AccountDtoMapper on AccountDto {
  Account toEntity() => Account(
    id: id,
    alias: (alias?.trim().isEmpty ?? true) ? null : alias!.trim(),
    maskedNumber: numberMasked,
    currency: currency,
    balance: balance.toDouble(),
    type: AccountType.values.firstWhere(
      (t) => t.name == type,
      orElse: () => AccountType.other,
    ),
  );
}

extension AccountsResponseDtoMapper on AccountsResponseDto {
  List<Account> toEntity() =>
      data.map((dto) => dto.toEntity()).toList(growable: false);
}
