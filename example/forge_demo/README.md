# forge_demo

The example app for [flutter-forge](../../README.md). It is a small personal-finance app
(accounts → transactions) built with the plugin's `clean` preset: Cubit, get_it, go_router,
Dio and `Result`/`AppFailure`. Its purpose is to show what the skills produce and to serve as
the eval target.

```bash
flutter pub get
flutter run --dart-define=USE_MOCKS=true
flutter test

# E2E (Patrol CLI + a booted simulator/emulator)
dart pub global activate patrol_cli
../../plugins/flutter-forge/skills/forge-e2e/scripts/run_flow.sh \
  --test patrol_test/flows/account_transactions_test.dart --env patrol_test/demo_env.json
# slower, label-free run for screen recordings:
#   … -- --no-label --dart-define=E2E_STEP_DELAY_MS=1500
```

iOS notes:
- The app targets iOS 15.0, the minimum Xcode 27 supports.
- Simulator builds exclude `x86_64`, because Xcode 27's `lipo` rejects two-architecture
  simulator binaries.
- Both settings are in the project and in the Podfile.

| What | Where |
|---|---|
| Project profile and an overlay | `.flutter-forge/` |
| API contract source (Postman v2.1, fictional) | `api/forge_demo.postman_collection.json` |
| Contract extracted by `forge-api-contract` | `docs/api/contract.raw.md` + `test/fixtures/` |
| Sample story for a `forge-deliver` run | `docs/stories/HU-01-transfer.md` |
| Widget catalog | `docs/widget-catalog.md` |
| Patrol E2E harness and flow (iOS simulator verified) | `patrol_test/` |

Try the pipeline (from the repo root):

```bash
cd example/forge_demo
claude --plugin-dir ../../plugins/flutter-forge
# > /flutter-forge:forge-deliver Implementa la HU docs/stories/HU-01-transfer.md con la colección de api/
```

The release build reads its signing config from `android/key.properties` (gitignored). See
the Flutter docs on app signing.
