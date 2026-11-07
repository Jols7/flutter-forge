import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../features/accounts/presentation/pages/accounts_page.dart';
import '../../features/accounts/presentation/state/accounts_cubit.dart';
import '../../features/transactions/presentation/pages/transactions_page.dart';
import '../../features/transactions/presentation/state/transactions_cubit.dart';
import '../di/injection.dart';

final rootNavigatorKey = GlobalKey<NavigatorState>();

GoRouter buildRouter({String? initialLocation}) => GoRouter(
  navigatorKey: rootNavigatorKey,
  initialLocation: initialLocation ?? '/',
  routes: [
    GoRoute(
      path: '/',
      name: AccountsPage.routeName,
      builder: (context, state) => BlocProvider(
        create: (_) => getIt<AccountsCubit>()..load(),
        child: const AccountsPage(),
      ),
      routes: [
        GoRoute(
          path: 'accounts/:accountId/transactions',
          name: TransactionsPage.routeName,
          builder: (context, state) => BlocProvider(
            create: (_) => getIt<TransactionsCubit>(
              param1: state.pathParameters['accountId']!,
            )..load(),
            child: const TransactionsPage(),
          ),
        ),
      ],
    ),
  ],
);
