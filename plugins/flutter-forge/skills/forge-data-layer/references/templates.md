# Data-layer templates (preset `clean`, Dio, json_serializable)

Worked example: `GET accounts/{accountId}/transactions?page&size`, which returns
`{ "data": [...], "next_page": 2 | null }`. Replace names using the profile's paths and
package. The example app `example/forge_demo` compiles this exact code.

## 1. Entity — `domain/entities/transaction.dart`

```dart
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
  final String description;      // '' when the backend sends null
  final double amount;           // negative = debit
  final String currency;
  final DateTime bookedAt;       // local time
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
  int get hashCode => Object.hash(id, description, amount, currency, bookedAt, category);
}
```

`package:flutter/foundation.dart` is the only Flutter import allowed in domain, and only for
`@immutable`. A project that uses `equatable` or `freezed` keeps that convention instead.

## 2. Pagination — `core/utils/paginated.dart`

```dart
/// A page of results. Named `Paginated` to avoid clashing with Flutter's `Page`.
class Paginated<T> {
  const Paginated({required this.items, required this.nextPage});

  final List<T> items;
  final int? nextPage;

  bool get hasMore => nextPage != null;
}
```

## 3. Repository contract — `domain/repositories/transactions_repository.dart`

```dart
import '../../../../core/error/result.dart';
import '../../../../core/utils/paginated.dart';
import '../entities/transaction.dart';

abstract interface class TransactionsRepository {
  Future<Result<Paginated<Transaction>>> getTransactions({
    required String accountId,
    int page = 1,
  });
}
```

Use `package:<package>/…` imports instead of relative ones when the project prefers them, and
stay consistent with `analysis_options.yaml` (`always_use_package_imports` or
`prefer_relative_imports`).

## 4. DTOs — `data/models/transaction_dto.dart`

```dart
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

  factory TransactionDto.fromJson(Map<String, dynamic> json) => _$TransactionDtoFromJson(json);

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
```

- Use `createToJson: false` for response-only DTOs. Request DTOs use `createToJson: true`
  and `includeIfNull: false`.
- Keep dates as `String` in the DTO. The mapper parses them, so a malformed date becomes a
  `ParsingFailure` at a single point.

## 5. Mapper — `data/mappers/transaction_mapper.dart`

```dart
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

TransactionCategory _category(String? raw) => TransactionCategory.values.firstWhere(
      (value) => value.name == raw,
      orElse: () => TransactionCategory.other,     // unknown values never crash
    );
```

## 6. Remote data source — `data/datasources/transactions_remote_data_source.dart`

```dart
import 'package:dio/dio.dart';

import '../models/transaction_dto.dart';

class TransactionsRemoteDataSource {
  TransactionsRemoteDataSource(this._dio);

  final Dio _dio;

  Future<TransactionsPageDto> getTransactions(
    String accountId, {
    required int page,
    int size = 20,
    CancelToken? cancelToken,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      'accounts/${Uri.encodeComponent(accountId)}/transactions',
      queryParameters: {'page': page, 'size': size},
      cancelToken: cancelToken,
    );
    return TransactionsPageDto.fromJson(response.data!);
  }
}
```

Writes that need idempotency get the key from the caller, so a retry of the same attempt
reuses it:

```dart
Future<TransferReceiptDto> createTransfer(CreateTransferRequestDto body, {required String idempotencyKey}) async {
  final response = await _dio.post<Map<String, dynamic>>(
    'transfers',
    data: body.toJson(),
    options: Options(headers: {'Idempotency-Key': idempotencyKey}),
  );
  return TransferReceiptDto.fromJson(response.data!);
}
```

## 7. Repository implementation — `data/repositories/transactions_repository_impl.dart`

```dart
import '../../../../core/network/guard.dart';
import '../../../../core/error/result.dart';
import '../../../../core/utils/paginated.dart';
import '../../domain/entities/transaction.dart';
import '../../domain/repositories/transactions_repository.dart';
import '../datasources/transactions_remote_data_source.dart';
import '../mappers/transaction_mapper.dart';

class TransactionsRepositoryImpl implements TransactionsRepository {
  TransactionsRepositoryImpl(this._remote);

  final TransactionsRemoteDataSource _remote;

  @override
  Future<Result<Paginated<Transaction>>> getTransactions({
    required String accountId,
    int page = 1,
  }) =>
      guard(() async => (await _remote.getTransactions(accountId, page: page)).toEntity());
}
```

When the feature handles business codes:

```dart
guard(
  () async => (await _remote.createTransfer(draft.toDto(), idempotencyKey: draft.attemptId)).toEntity(),
  businessCodes: TransferErrorCodes.all,
);
```

`guard` lives in `core/network/guard.dart`, next to `dio_failure_mapper.dart`. It is the only
bridge from Dio to `Result`. `core/error` stays free of transport packages, which the layer rules
enforce.

## 8. Use case (only when earned) — `domain/usecases/create_transfer.dart`

```dart
class CreateTransfer {
  const CreateTransfer(this._repository);

  final TransfersRepository _repository;

  Future<Result<TransferReceipt>> call(TransferDraft draft) async {
    final validation = draft.validate();                 // domain rule from the brief
    if (validation != null) return Failure(validation);
    return _repository.createTransfer(draft);
  }
}
```

## Layered preset (`adopt` / `improve`)

Keep the project's `*Api` → `*Repository` shapes. The minimum quality bar for new code still
applies: DTO + mapper, nothing above the repository sees DTOs, a typed error or the project's
convention, and no duplicated error-handling blocks (extract a private helper). In `improve`
mode, new repository methods return `Result<T>`. See `forge-architecture/references/preset-layered.md`.
