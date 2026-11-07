import 'package:bloc_test/bloc_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:forge_demo/core/error/app_failure.dart';
import 'package:forge_demo/features/transactions/presentation/pages/transactions_page.dart';
import 'package:forge_demo/features/transactions/presentation/state/transactions_cubit.dart';
import 'package:forge_demo/features/transactions/presentation/state/transactions_state.dart';
import 'package:forge_demo/features/transactions/presentation/widgets/transaction_tile.dart';
import 'package:mocktail/mocktail.dart';

import '../../../../helpers/pump_app.dart';
import '../../../../helpers/sample_data.dart';

class MockTransactionsCubit extends MockCubit<TransactionsState>
    implements TransactionsCubit {}

void main() {
  late MockTransactionsCubit cubit;

  setUp(() => cubit = MockTransactionsCubit());

  Future<void> pump(WidgetTester tester, TransactionsState state) {
    when(() => cubit.state).thenReturn(state);
    return tester.pumpApp(
      BlocProvider<TransactionsCubit>.value(
        value: cubit,
        child: const TransactionsPage(),
      ),
    );
  }

  testWidgets('shows a progress indicator while loading', (tester) async {
    await pump(tester, const TransactionsLoading());
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('shows the empty message', (tester) async {
    await pump(tester, const TransactionsEmpty());
    await tester.pumpAndSettle();
    expect(find.text('Aún no tienes movimientos'), findsOneWidget);
  });

  testWidgets('failure shows the mapped message and retries', (tester) async {
    when(() => cubit.load()).thenAnswer((_) async {});
    await pump(tester, const TransactionsFailure(NetworkFailure()));
    await tester.pumpAndSettle();

    expect(find.text('Sin conexión. Revisa tu internet.'), findsOneWidget);
    await tester.tap(find.widgetWithText(TextButton, 'Reintentar'));
    verify(() => cubit.load()).called(1);
  });

  testWidgets(
    'loaded renders one tile per transaction and the description fallback',
    (tester) async {
      await pump(tester, TransactionsLoaded(items: [tx1, tx2], nextPage: null));
      await tester.pumpAndSettle();

      expect(find.byType(TransactionTile), findsNWidgets(2));
      expect(find.text('Sin descripción'), findsOneWidget);
    },
  );

  testWidgets('load-more failure keeps the list and offers retry', (
    tester,
  ) async {
    await pump(
      tester,
      TransactionsLoaded(
        items: [tx1],
        nextPage: 2,
        loadMoreFailure: const ServerFailure(statusCode: 500),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(TransactionTile), findsOneWidget);
    expect(find.text('Algo salió mal. Intenta de nuevo.'), findsOneWidget);
  });

  testWidgets('meets tap-target and labeled tap-target guidelines', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    await pump(tester, const TransactionsFailure(NetworkFailure()));
    await tester.pumpAndSettle();
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
    await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
    handle.dispose();
  });
}
