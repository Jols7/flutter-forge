# CLAUDE.md

Forge Demo — fictional personal-finance app used to demonstrate the flutter-forge plugin.
Flutter 3.38 (stable), no flavors; runs entirely on mocks.

## Commands

```bash
flutter pub get
flutter run --dart-define=USE_MOCKS=true                 # MOCK_SCENARIO=empty|offline for other states
flutter analyze
flutter test
dart run build_runner build --delete-conflicting-outputs  # after editing DTOs
flutter gen-l10n                                          # after editing lib/l10n/*.arb
../../plugins/flutter-forge/skills/forge-e2e/scripts/run_flow.sh --test patrol_test/flows/account_transactions_test.dart --env patrol_test/demo_env.json
```

## Architecture

Clean Architecture with Cubit (flutter_bloc), get_it and go_router. Features live in
`lib/features/<feature>/{domain,data,presentation,di}`; data flows page → cubit → repository
contract (domain) → repository impl → remote data source (Dio). Repositories return
`Result<T>` with a sealed `AppFailure` (`lib/core/error/`). Paths, rules and conventions:
`.flutter-forge/profile.yaml` and `.flutter-forge/overlays/`.

## Gotchas

- The API host is fictional; without `USE_MOCKS=true` every request fails with `NetworkFailure`.
- `dart run build_runner` must run after any DTO change; generated `*.g.dart` files are committed.

## flutter-forge

This project is configured for the flutter-forge plugin. Skills read `.flutter-forge/profile.yaml`
and `.flutter-forge/overlays/`. Deliver a feature with `forge-deliver`; record a convention with
`forge-learn` (not here).
