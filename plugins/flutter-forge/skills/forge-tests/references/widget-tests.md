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
  `find.byKey(TransferKeys.submit)`, the `<Feature>Keys` constant from the blueprint
  (`forge-architecture/references/conventions.md` § 9). Do not add keys to the app from the tests:
  report a missing one so `forge-presentation` adds it.
- Assert user-visible outcomes (text, enabled state), not private widget
  internals.
- Disabled button: `expect(tester.widget<FilledButton>(find.byType(FilledButton)).onPressed, isNull)`.
- Accessibility tests: **only when the run's `a11y` is `on`**. With `off`, write none and assert
  nothing about semantics. When `on`, follow `../../forge-presentation/references/accessibility.md`
  § Tests: `tester.ensureSemantics()` before any `meetsGuideline`, both tap-target guidelines,
  `labeledTapTargetGuideline` and `textContrastGuideline`.

## Responsive matrix (always, independent of `a11y`)

Layout robustness is not an accessibility test (ADR 0010): every new or changed page and every shared
widget that holds text is rendered across the targets of `../../forge-presentation/references/responsive.md`
§ Targets, in its **longest-content** variant (longest ARB label, largest amount of the contract).

```dart
for (final size in const [Size(320, 568), Size(360, 640), Size(412, 915), Size(768, 1024), Size(844, 390)]) {
  for (final scale in const [1.0, 1.5, 2.0]) {
    testWidgets('AccountCard fits ${size.width.toInt()}x${size.height.toInt()} at x$scale', (tester) async {
      await tester.pumpAppAt(size, scale, AccountCard(account: longestAccount, title: longestTitle, onTap: () {}));
      expect(tester.takeException(), isNull);                         // no RenderFlex overflow
      expect(tester.getRect(find.text(longestTitle)).right, lessThanOrEqualTo(size.width)); // key content on screen
    });
  }
}
```

- Assert no layout exception **and** that the key content is on screen (`getRect` inside the viewport,
  or `findsOneWidget` for the amount): "no exception" alone passes when the text is clipped.
- A page taller than the viewport scrolls: use `tester.scrollUntilVisible` for content below the fold
  instead of failing on height.
- Keep the matrix to the page and to the states that change layout (loaded with the longest data,
  error, empty). Do not multiply it across every unit of the screen.
- On failure, fix the layout with `forge-presentation` rules (`Flexible`, `FittedBox`, minimum heights),
  never by shrinking the test matrix. Count each cycle in `retries` like any failing test.
- The helper `pumpAppAt` is in `helpers.md`.
