import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/features/transactions/data/mappers/transaction_mapper.dart';
import 'package:forge_demo/features/transactions/data/models/transaction_dto.dart';
import 'package:forge_demo/features/transactions/domain/entities/transaction.dart';

import '../../../../helpers/fixtures.dart';
import '../../../../helpers/sample_data.dart';

void main() {
  group('TransactionsPageDtoMapper', () {
    test('maps the 200 fixture to entities', () {
      final page = TransactionsPageDto.fromJson(
        fixture('accounts/list_transactions_200.json'),
      ).toEntity();

      expect(page.items, [tx1, tx2]);
      expect(page.nextPage, 2);
      expect(page.hasMore, isTrue);
    });

    test('maps the empty fixture to an empty last page', () {
      final page = TransactionsPageDto.fromJson(
        fixture('accounts/list_transactions_200_empty.json'),
      ).toEntity();

      expect(page.items, isEmpty);
      expect(page.hasMore, isFalse);
    });

    test('null description and category fall back to defaults', () {
      final tx = TransactionsPageDto.fromJson(
        fixture('accounts/list_transactions_200.json'),
      ).toEntity().items[1];

      expect(tx.description, '');
      expect(tx.category, TransactionCategory.other);
    });

    test('integer amounts become doubles and negative means debit', () {
      final page = TransactionsPageDto.fromJson(
        fixture('accounts/list_transactions_200.json'),
      ).toEntity();

      expect(page.items[1].amount, 12000.0);
      expect(page.items.first.isDebit, isTrue);
    });

    test(
      'malformed payload throws a TypeError, which guard() maps to ParsingFailure',
      () {
        expect(
          () => TransactionDto.fromJson({'id': 1}),
          throwsA(isA<TypeError>()),
        );
      },
    );
  });
}
