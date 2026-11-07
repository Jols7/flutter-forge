# Preset `clean`

Feature-first Clean Architecture. Machine-readable rules: `../presets/clean.layers.json`
(consumed by `forge-audit/scripts/check_layers.py`).

## Tree

```
lib/
├── main.dart                     # or main_<flavor>.dart → bootstrap()
├── bootstrap.dart                # error zones, DI init, runApp
├── app/app.dart                  # MaterialApp.router, theme, localization delegates
├── core/
│   ├── config/                   # AppConfig (base URL from --dart-define / flavor), feature flags
│   ├── di/injection.dart         # container setup; calls each feature module
│   ├── error/                    # result.dart, app_failure.dart
│   ├── network/                  # api_client.dart, interceptors/, dio_failure_mapper.dart, mocks/
│   ├── storage/                  # secure_storage.dart, preferences.dart (wrappers, injectable)
│   ├── router/app_router.dart    # go_router config; creates state managers per route (bloc/provider)
│   ├── theme/                    # app_theme.dart, tokens (colors/spacing/typography extensions)
│   ├── widgets/<group>/          # shared widgets (+ optional widgets.dart barrel)
│   └── utils/                    # pure helpers: formatters, validators, extensions
├── l10n/                         # *.arb (gen-l10n) — or the project's pipeline
└── features/<feature>/
    ├── domain/
    │   ├── entities/<name>.dart
    │   ├── repositories/<feature>_repository.dart
    │   └── usecases/<verb_noun>.dart           # only when earned
    ├── data/
    │   ├── datasources/<feature>_remote_data_source.dart
    │   ├── datasources/<feature>_local_data_source.dart   # if cached
    │   ├── models/<name>_dto.dart (+ .g.dart)
    │   ├── mappers/<name>_mapper.dart
    │   └── repositories/<feature>_repository_impl.dart
    ├── presentation/
    │   ├── pages/<screen>_page.dart
    │   ├── state/                              # see variations below
    │   └── widgets/<widget>.dart
    └── di/<feature>_module.dart                # registrations for this feature
test/                              # mirrors lib/ one-to-one
├── features/<feature>/{domain,data,presentation}/…_test.dart
├── fixtures/<feature>/<endpoint>.json          # from forge-api-contract
└── helpers/                                    # pump_app.dart, mocks.dart, fakes
```

## State-manager variations

| `architecture.state` | `presentation/state/` holds | Created by |
|---|---|---|
| `bloc` | `<f>_cubit.dart` + `<f>_state.dart` (or `<f>_bloc.dart` + `_event` + `_state` when events carry meaning: debounce, transformers, analytics) | `BlocProvider` in the route builder (`core/router`) resolving from DI |
| `riverpod` | `<f>_notifier.dart` (`Notifier`/`AsyncNotifier`) + `<f>_state.dart`; providers declared next to the notifier | Riverpod; repository providers live in `features/<f>/di/` |
| `provider` | `<f>_view_model.dart` (`ChangeNotifier`) + `<f>_state.dart` | `ChangeNotifierProvider` in the route builder, constructor-injected |

State classes are **sealed** (`Initial | Loading | Loaded | Failure`) or an immutable record
with a sealed `status`. They are never a bag of booleans. Templates: `forge-presentation`.

## Dependency rule (what `check_layers.py` enforces)

| From \ To | domain | data | presentation | core_* | composition |
|---|---|---|---|---|---|
| domain | ✅ | ❌ | ❌ | error, utils | ❌ |
| data | ✅ | ✅ | ❌ | error, network, storage, config, utils | ❌ |
| presentation | ✅ | ❌ | ✅ | ui, error, utils | ✅ (Riverpod providers only) |
| composition | ✅ | ✅ | ✅ | ✅ | ✅ |

Package bans by layer:
- **domain:** no Flutter SDK except `foundation.dart`; no Dio/http; no `json_annotation`; no DI
  containers; no storage plugins.
- **data:** no widgets and no state-management packages.
- **presentation:** no Dio/http, no `json_annotation`, no `get_it` (a service locator in widgets
  hides dependencies) and no storage plugins.

Cross-feature imports are allowed for `domain` only.

## Naming

| Kind | File | Class |
|---|---|---|
| Entity | `transaction.dart` | `Transaction` |
| Repository contract | `transactions_repository.dart` | `TransactionsRepository` |
| Repository impl | `transactions_repository_impl.dart` | `TransactionsRepositoryImpl` |
| Remote data source | `transactions_remote_data_source.dart` | `TransactionsRemoteDataSource` |
| Response DTO | `transaction_dto.dart` | `TransactionDto` |
| Request DTO | `create_transfer_request_dto.dart` | `CreateTransferRequestDto` |
| Mapper | `transaction_mapper.dart` | `extension TransactionDtoMapper on TransactionDto` (`toEntity()`), `extension CreateTransferMapper on TransferDraft` (`toDto()`) |
| Use case | `create_transfer.dart` | `CreateTransfer` |
| Cubit / state | `transactions_cubit.dart` / `transactions_state.dart` | `TransactionsCubit` / `TransactionsState` |
| Page | `transactions_page.dart` | `TransactionsPage` |

## Why some things are *not* abstract

- **Data sources are concrete classes.** Dart classes are implicit interfaces, so mocktail
  mocks them directly. An abstract data-source interface with exactly one implementation
  is speculative generality.
- **The repository is the boundary.** Its contract lives in `domain` because presentation
  and use cases depend on it. Its implementation can then change (cache, offline, mock) and
  no caller changes.

## Data-layer policies (decide per feature in the blueprint)

- **Caching:** none, memory, or local data source with a TTL. State it in the blueprint.
- **Pagination:** the repository returns `Page<T>` (items + cursor/next), never raw lists for
  paginated endpoints.
- **Cancellation:** pass a `CancelToken` down when a request can be superseded (search, debounce).
