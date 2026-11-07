# `blueprint.md` template

```markdown
# Blueprint — <Feature>
Preset: clean · State: bloc (cubit) · Mode: new · Brief: brief.md · Contract: contract.md · Design: design.md
Status: draft | approved YYYY-MM-DD

## File plan (implementation order)
| # | Action | Path | Layer | Class(es) |
|---|---|---|---|---|
| 1 | create | lib/features/transfers/domain/entities/transfer_draft.dart | domain | TransferDraft |
| 2 | create | lib/features/transfers/domain/entities/transfer_receipt.dart | domain | TransferReceipt |
| 3 | create | lib/features/transfers/domain/repositories/transfers_repository.dart | domain | TransfersRepository |
| 4 | create | lib/features/transfers/data/models/create_transfer_request_dto.dart | data | CreateTransferRequestDto |
| … | | | | |
| 12 | modify | lib/features/accounts/presentation/pages/account_detail_page.dart | presentation | entry button "Transferir" (AC-1) |
| 13 | modify | lib/core/router/app_router.dart | composition | route `/transfers/new` (args: fromAccountId) |

## Classes
| Class | Responsibility | Depends on | Used by | ACs |
|---|---|---|---|---|
| TransfersRepository | createTransfer, previewTransfer → Result | — | TransferCubit | AC-2..5 |
| TransfersRepositoryImpl | guard + mappers + idempotency key | TransfersRemoteDataSource | DI | AC-3,5 |
| TransferCubit | form state, preview debounce, submit | TransfersRepository | TransferPage | AC-1..6 |

## Repository contract
```dart
abstract interface class TransfersRepository {
  Future<Result<TransferPreview>> previewTransfer({required String fromId, required String toId, required double amount, CancelToken? cancelToken});
  Future<Result<TransferReceipt>> createTransfer(TransferDraft draft);
}
```

## Value trace
| Screen value | Entity.field | DTO.field | Conversion / default |
|---|---|---|---|
| "Comisión $0.00" | TransferPreview.fee | fee (num) | toDouble() |
| "Recibirás USD 27.55" | TransferPreview.amountReceived + to.currency | amount_received (num) | toDouble(); currency from selected account |
| Reference on receipt | TransferReceipt.reference | reference (String) | — |

## State design
TransferState (record) — form: TransferForm · preview: PreviewStatus (sealed: idle | loading | ready(TransferPreview) | failed(AppFailure)) · submit: SubmitStatus (sealed: idle | submitting | succeeded(TransferReceipt) | failed(AppFailure))
Intents: selectDestination, amountChanged (local validation → debounce 300 ms → preview, stale discard), submit
Side effects: succeeded → navigate to receipt; BusinessFailure(INSUFFICIENT_FUNDS) → inline error on amount (AC-5)

## Widgets (reuse ladder)
| Design component | Decision | Path |
|---|---|---|
| Amount input | extend `AppAmountField` (+ `errorText`) | lib/core/widgets/inputs/app_amount_field.dart |
| Account selector tile | create (feature-local) | lib/features/transfers/presentation/widgets/account_option_tile.dart |

## Routes and DI
- Route `/transfers/new` → `BlocProvider(create: (_) => getIt<TransferCubit>(param1: fromAccountId))`
- DI: register data source, repository (contract type), cubit (factory) in `transfers_module.dart`

## L10n keys
transferTitle, transferAmountLabel, transferMinAmountError(amount), transferInsufficientFunds, …

## Test plan
| Test file | Cases | ACs |
|---|---|---|
| test/features/transfers/data/mappers/transfer_mapper_test.dart | fixtures 201/preview → entity; nulls → defaults | AC-3 |
| test/features/transfers/data/repositories/transfers_repository_impl_test.dart | success; 422 → ValidationFailure; 409 code → BusinessFailure; offline → NetworkFailure | AC-4,5 |
| test/features/transfers/presentation/state/transfer_cubit_test.dart | debounce + stale discard; min amount; submit success/failure | AC-2..6 |
| test/features/transfers/presentation/pages/transfer_page_test.dart | renders each state; inline errors; button disabled when invalid | AC-2,4,5 |
| patrol_test/flows/transfer_test.dart | entry from account detail → amount → preview → confirm (stops before submit on shared envs) | AC-1..3 |
Uncovered ACs: none

## Assumptions / decisions
- 2026-11-06 — No use case: validation is local to one cubit (not earned).
```
