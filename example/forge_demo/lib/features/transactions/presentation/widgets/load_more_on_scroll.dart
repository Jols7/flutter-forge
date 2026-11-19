import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../state/transactions_cubit.dart';

/// Asks the cubit for the next page when the list is close to its end.
class LoadMoreOnScroll extends StatelessWidget {
  const LoadMoreOnScroll({super.key, required this.child});

  final Widget child;

  static const double _threshold = 300;

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification.metrics.extentAfter < _threshold) {
          context.read<TransactionsCubit>().loadMore();
        }
        return false;
      },
      child: child,
    );
  }
}
