---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Haz code review de este cubit (proyecto con Clean Architecture + Cubit):

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import '../../data/models/payment_dto.dart';
import '../../data/repositories/payments_repository_impl.dart';

class PaymentsCubit extends Cubit<PaymentsState> {
  PaymentsCubit() : super(PaymentsState());
  final repo = GetIt.I<PaymentsRepositoryImpl>();

  Future<void> load() async {
    emit(state.copyWith(isLoading: true, error: null));
    try {
      final List<PaymentDto> dtos = await repo.fetchRaw();
      emit(state.copyWith(isLoading: false, items: dtos));
    } catch (e) {
      emit(state.copyWith(isLoading: false, error: e.toString()));
    }
  }
}

class PaymentsState {
  PaymentsState({this.isLoading = false, this.items = const [], this.error});
  final bool isLoading;
  final List<PaymentDto> items;
  final String? error;
  PaymentsState copyWith({bool? isLoading, List<PaymentDto>? items, String? error}) =>
      PaymentsState(isLoading: isLoading ?? this.isLoading, items: items ?? this.items, error: error);
}
```
