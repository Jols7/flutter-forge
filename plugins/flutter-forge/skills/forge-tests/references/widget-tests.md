# Widget test templates

## BLoC — mock the cubit (`bloc_test`'s `MockCubit`)

```dart
class MockTransactionsCubit extends MockCubit<TransactionsState> implements TransactionsCubit {}

void main() {
  late MockTransactionsCubit cubit;

  setUp(() => cubit = MockTransactionsCubit());

  Future<void> pump(WidgetTester tester, TransactionsState state) {
    when(() => cubit.state).thenReturn(state);
    return tester.pumpApp(BlocProvider<TransactionsCubit>.value(value: cubit, child: const TransactionsPage()));
  }

  testWidgets('shows a progress indicator while loading', (tester) async {
    await pump(tester, const TransactionsLoading());
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('shows the empty message', (tester) async {
    await pump(tester, const TransactionsEmpty());
    expect(find.text('Aún no tienes movimientos'), findsOneWidget);   // from the ARB
  });

  testWidgets('failure shows the mapped message and retries', (tester) async {
    when(() => cubit.load()).thenAnswer((_) async {});
    await pump(tester, const TransactionsFailure(NetworkFailure()));

    expect(find.text('Sin conexión. Revisa tu internet.'), findsOneWidget);
    await tester.tap(find.widgetWithText(TextButton, 'Reintentar'));
    verify(() => cubit.load()).called(1);
  });

  testWidgets('loaded renders one tile per transaction', (tester) async {
    await pump(tester, const TransactionsLoaded(items: [tx1, tx2], nextPage: null));
    expect(find.byType(TransactionTile), findsNWidgets(2));
  });
}
```

Side effects: use `whenListen(cubit, Stream.fromIterable([...]), initialState: …)` to drive
`BlocListener` navigation, and assert the destination with a mock router or `find.byType`
of the next page.

## Riverpod

Pump `ProviderScope(overrides: [transactionsProvider('acc_1').overrideWith(() =>
FakeTransactionsNotifier(state))], child: …)`, or override the repository provider and let
the real notifier run. The second option makes it an integration-style widget test, which
is still fast.

## Provider

Wrap the page in `ChangeNotifierProvider<TransactionsViewModel>.value(value: fakeViewModel)`.
A fake extends the ViewModel with a settable `state` and calls `notifyListeners`.

## Finders and rules

- Prefer `find.byType(WidgetClass)`, then `find.text(<ARB text>)`, then
  `find.byKey(const Key('transfer_submit'))`. Add keys to the app only when a finder is
  ambiguous, and mention it in the report.
- Assert user-visible outcomes (text, enabled state), not private widget
  internals.
- Disabled button: `expect(tester.widget<FilledButton>(find.byType(FilledButton)).onPressed, isNull)`.
- Accessibility and text-scale tests: **only when the run's `a11y` is `on`**. With `off`, write
  none and assert nothing about semantics. When `on`, follow
  `../../forge-presentation/references/accessibility.md` § Tests: `tester.ensureSemantics()`
  before any `meetsGuideline`, both tap-target guidelines, `labeledTapTargetGuideline`,
  `textContrastGuideline`, and a 2.0 text-scale test that asserts the content is still visible
  (not only that `tester.takeException()` is null).
