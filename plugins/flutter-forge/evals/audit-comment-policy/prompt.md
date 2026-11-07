---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Revisa los comentarios de este código Flutter de un feature nuevo (Clean Architecture + Cubit).
No cambies nada, solo dime qué comentarios sobran, cuáles faltan y cuáles están bien.

```dart
// ============ DOMAIN ============
abstract interface class TransfersRepository {
  Future<Result<TransferReceipt>> createTransfer(TransferDraft draft);
}

class TransferCubit extends Cubit<TransferState> {
  TransferCubit(this._repository) : super(const TransferState.initial());

  final TransfersRepository _repository;

  // increment attempts
  int _attempts = 0;

  Future<void> submit(TransferDraft draft) async {
    // AC-4 (HU-12): transfers over 50,000 need biometric re-authentication
    if (draft.amount > 50000 && !draft.reauthenticated) {
      emit(state.copyWith(needsReauth: true));
      return;
    }
    _attempts++;
    // final result = await _legacyRepository.send(draft);
    // emit(state.copyWith(receipt: result));
    // TODO arreglar esto
    final result = await _repository.createTransfer(draft);
    if (isClosed) return;
    // Matches CLABE: 18 digits, the last one is a weighted mod-10 check digit.
    final clabe = RegExp(r'^\d{18}$');
    emit(state.fromResult(result, clabeValid: clabe.hasMatch(draft.toAccount)));
  }
}
```
