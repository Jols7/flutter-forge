# Dependency injection

**Golden rule:** every class gets its dependencies through its constructor. Only composition
(`core/di`, `core/router`, `features/<f>/di`, `main*.dart`) talks to the container. Tests then
build any class with mocks, with no global state to reset.

## `get_it` (manual) — `architecture.di: get_it`

```dart
// lib/core/di/injection.dart
final getIt = GetIt.instance;

Future<void> configureDependencies(AppConfig config) async {
  getIt
    ..registerSingleton<AppConfig>(config)
    ..registerLazySingleton<SecureStorage>(SecureStorage.new)
    ..registerLazySingleton<Dio>(() => buildDio(config, getIt<SecureStorage>()));
  registerTransactionsModule(getIt);          // one call per feature
}
```

```dart
// lib/features/transactions/di/transactions_module.dart
void registerTransactionsModule(GetIt getIt) {
  getIt
    ..registerLazySingleton(() => TransactionsRemoteDataSource(getIt<Dio>()))
    ..registerLazySingleton<TransactionsRepository>(
      () => TransactionsRepositoryImpl(getIt<TransactionsRemoteDataSource>()),
    )
    ..registerFactory(() => TransactionsCubit(getIt<TransactionsRepository>()));
}
```

Lifetimes:
- **Lazy singletons:** clients, data sources and repositories (they are stateless).
- **Factories:** state managers, because each route gets a fresh one.
- Register a repository with its **contract** type (`<TransactionsRepository>`).

## `injectable` — `architecture.di: injectable`

Same lifetimes, written as annotations: `@lazySingleton` on data sources, `@LazySingleton(as:
TransactionsRepository)` on the impl, `@injectable` on cubits. Run the profile's
`serialization.build_command` after changes. Do not mix manual registrations with
annotations for the same feature.

## Riverpod — `architecture.di: riverpod`

```dart
// lib/features/transactions/di/transactions_providers.dart
final transactionsRemoteDataSourceProvider = Provider(
  (ref) => TransactionsRemoteDataSource(ref.watch(dioProvider)),
);

final transactionsRepositoryProvider = Provider<TransactionsRepository>(
  (ref) => TransactionsRepositoryImpl(ref.watch(transactionsRemoteDataSourceProvider)),
);
```

The notifier reads `ref.watch(transactionsRepositoryProvider)` in `build()`. Tests override
the provider with a mock through `ProviderContainer(overrides: [...])`. If the project uses
`riverpod_generator`, write `@riverpod` functions instead, with the same graph.

## `provider` package — `architecture.di: provider`

Repositories go at the app root with `MultiProvider` (`Provider<TransactionsRepository>`).
State managers are created **per route** with `ChangeNotifierProvider(create: (context) =>
TransactionsViewModel(context.read<TransactionsRepository>())..load())`. A project that uses
`get_it` together with `provider` creates the ViewModel in the route builder from `getIt`
instead.

## Where state managers are created

| State | Created in | Example |
|---|---|---|
| bloc/cubit | route builder (`core/router`) | `BlocProvider(create: (_) => getIt<TransactionsCubit>()..load(), child: const TransactionsPage())` |
| riverpod | lazily by Riverpod | page is a `ConsumerWidget`; `ref.watch(transactionsNotifierProvider)` |
| provider | route builder | `ChangeNotifierProvider(create: …, child: const TransactionsPage())` |

Pages never instantiate their own state manager. That keeps them reusable, and widget tests
can inject a mocked one.

## Anti-patterns

| ❌ | ✅ | Why |
|---|---|---|
| `getIt<X>()` inside a widget, cubit or repository body | Constructor parameter | Hidden dependency; tests need global setup |
| Registering a repository impl without its contract type | `registerLazySingleton<Contract>(() => Impl(...))` | Callers would depend on the impl |
| Singleton cubit/notifier for one screen | Factory/route-scoped | Stale state when the user reopens the screen |
| One giant `injection.dart` | A module per feature called from `injection.dart` | Merge conflicts; features become removable |
