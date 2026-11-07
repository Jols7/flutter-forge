# Core bootstrap (`architecture.mode: new`)

These are the pieces to create before the first feature of a new project, so features only add
their own folders. Create each one only if it is missing, and adapt names to the profile.

| File | Contents |
|---|---|
| `lib/core/config/app_config.dart` | `AppConfig { baseUrl, flavor, useMocks }` built from `--dart-define` (`String.fromEnvironment`). Never hardcode URLs. Never put secrets in client config (`forge-security`) |
| `lib/bootstrap.dart` | `runZonedGuarded` + `FlutterError.onError` + `PlatformDispatcher.instance.onError` → logger/crash reporter; `WidgetsFlutterBinding.ensureInitialized()`; `configureDependencies`; `runApp` |
| `lib/main.dart` / `main_<flavor>.dart` | Builds `AppConfig` and calls `bootstrap` |
| `lib/app/app.dart` | `MaterialApp.router` with theme, router, `localizationsDelegates`, `supportedLocales` |
| `lib/core/error/result.dart`, `app_failure.dart` | From `result-and-failures.md` |
| `lib/core/network/api_client.dart` | `buildDio(config, storage)`: base URL, timeouts (connect 15 s, receive 30 s), JSON headers, interceptors |
| `lib/core/network/interceptors/auth_interceptor.dart` | Adds `Authorization` from secure storage on each request; on 401, attempts **one** refresh under a lock, then signals logout through a stream that the app listens to. It never navigates by itself |
| `lib/core/network/interceptors/log_interceptor.dart` | Debug-only (`kDebugMode`); redacts `authorization`, `cookie`, `password`, `token`, `pin`, card and account fields |
| `lib/core/network/dio_failure_mapper.dart`, `guard.dart` | From `result-and-failures.md` |
| `lib/core/network/mocks/mock_interceptor.dart` | Serves fixture JSON per route when `AppConfig.useMocks` is set (only allowed when the flavor is not prod; asserted at startup). Template in `forge-data-layer` |
| `lib/core/storage/secure_storage.dart` | Thin wrapper over `flutter_secure_storage` (tokens only) |
| `lib/core/di/injection.dart` | Container setup (`di.md`) |
| `lib/core/router/app_router.dart` | `GoRouter` with typed route names and a redirect for auth state |
| `lib/core/theme/app_theme.dart` | `ThemeData` from `ColorScheme.fromSeed` or the design tokens; `ThemeExtension`s for spacing/radius when Figma defines them |
| `analysis_options.yaml` | `include: package:flutter_lints/flutter.yaml` (or `very_good_analysis`); `strict-casts`, `strict-inference`, `strict-raw-types`; exclude generated files |
| `test/helpers/pump_app.dart` | `pumpApp(widget, {overrides})` with theme + localization, used by every widget test |

`pubspec.yaml` dependencies depend on the profile. A typical setup has:
- runtime: `dio`, `go_router`, `flutter_secure_storage`, `json_annotation`, the state package,
  and the DI package;
- dev: `build_runner`, `json_serializable`, `mocktail`, `bloc_test` (bloc), `patrol` (e2e) and
  the lint package.

Add packages with `flutter pub add <name>` (or `dev:<name>`) so the versions resolve. Never
write version numbers from memory.

If `flutter pub add` fails on version solving (a known case is `bloc_test` together with a
recent `json_serializable`, which disagree on `analyzer`), add the conflicting packages in one
command with `:any` constraints. Then replace `any` with a caret on the resolved versions from
`pubspec.lock`. Never downgrade the Flutter SDK to fix it.

