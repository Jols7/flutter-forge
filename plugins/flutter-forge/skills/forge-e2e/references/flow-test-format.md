# Flow test format

One file per flow: `<e2e_dir>/flows/<flow_snake>_test.dart`.

```dart
import '../common/flow_runner.dart';
import '../common/flow_test.dart';
import '../common/screens.dart';
import '../routines/navigation_routines.dart';

void main() {
  flowTest('Flow Transfer: AC-1..3 from account detail to preview', ($) async {
    final flow = FlowRunner(
      $,
      name: 'Transfer',
      entry: goToAccountDetail,
      entryProbe: Screens.accountDetail,
    );
    await flow.start();

    await flow.step('AC-1: tap "Transferir" opens the transfer form', () async {
      await $('Transferir').tap();
      await $(Screens.newTransfer).waitUntilVisible();
    }, reached: Checkpoint('new transfer', Screens.newTransfer, reach: openNewTransferFromDetail));

    await flow.step('AC-2: an amount below the minimum shows the error', () async {
      await $(#transfer_amount).enterText('5');
      await $('Ingresa un monto mayor a \$10.00').waitUntilVisible();
    });

    await flow.step('AC-3: a valid amount shows the preview', () async {
      await $(#transfer_amount).enterText('500');
      await $(#transfer_preview_card).waitUntilVisible(timeout: const Duration(seconds: 30));
    });

    // Stops before "Confirmar": creating real transfers needs explicit approval.
    flow.finish();
  });
}
```

## Rules

- **A step is one user action plus its assertion.** Name it after the behavior, prefixed with
  the AC id it proves.
- **Add a checkpoint after each screen that is safe to return to.** `reach` navigates from the
  flow's entry to that screen. Without it, a soft restart can only return to the entry.
- **Wait, don't sleep.** Use `waitUntilVisible(timeout:)` for network screens (30 s), and
  `pumpAndTrySettle()` after transitions.
- **Data preconditions.** If the flow needs data the test user may not have, check it first
  and `fail('<what is missing>')` with a clear reason.
- **Entry and exit through other flows** use those flows' routines. Assertions about another
  flow's screens belong in that flow's test.

## Output (`[FLOW <name>] …` lines)

| Event | Meaning |
|---|---|
| `START at entry (<checkpoint>)` | flow started at its entry |
| `OK <step>` | step passed |
| `CHECKPOINT <name>` | new safe screen |
| `FAIL "<step>" on <Screen>: <error>` | step failed (continues after recovery) |
| `VISIBLE TEXTS: a \| b \| c` | up to 25 texts at failure time |
| `RECOVERED level "<level>" → <checkpoint>` | which ladder level worked |
| `ERROR_APP in "<step>": <error>` | uncaught app exception → app bug |
| `SESSION_LOST in "<step>" (attempt n)` | session lost; recovered once |
| `ABORTED in "<step>": <reason>` | flow stopped |
| `END OK` / `END <n> failure(s)` | summary |
