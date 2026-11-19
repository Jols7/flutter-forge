---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Revisa esta pantalla de un proyecto Flutter con Cubit y dime qué está mal de su capa de
presentación. No cambies nada.

```dart
class TransactionsState {
  bool isLoading = false;
  bool hasError = false;
  String? error;
  List<Transaction>? data;
}

class TransactionsCubit extends Cubit<TransactionsState> {
  TransactionsCubit() : super(TransactionsState());

  Future<void> load() async {
    emit(TransactionsState()..isLoading = true);
    final result = await getIt<TransactionsRepository>().getTransactions();
    emit(switch (result) {
      Success(:final value) => TransactionsState()..data = value,
      Failure(:final failure) => TransactionsState()..hasError = true..error = S.current.errorGeneric,
    });
  }
}

class TransactionsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => TransactionsCubit()..load(),
      child: BlocBuilder<TransactionsCubit, TransactionsState>(
        builder: (context, s) => s.isLoading ? const CircularProgressIndicator() : Text('${s.data}'),
      ),
    );
  }
}
```
