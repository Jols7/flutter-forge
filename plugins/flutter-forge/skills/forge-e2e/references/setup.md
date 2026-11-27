# E2E setup (once per project)

## 1. Dependencies

```bash
flutter pub add dev:patrol
flutter pub add 'dev:integration_test:{"sdk":"flutter"}'
dart pub global activate patrol_cli        # installs `patrol` into ~/.pub-cache/bin
patrol doctor
```

Add the `patrol:` block to `pubspec.yaml`. Take the values from the native projects, never
from memory:

```yaml
patrol:
  app_name: <App name>
  test_directory: patrol_test           # = testing.e2e_dir
  flavor: <default flavor id>           # used when --flavor is omitted
  android:
    package_name: <applicationId from android/app/build.gradle(.kts)>
  ios:
    bundle_id: <PRODUCT_BUNDLE_IDENTIFIER from ios/Runner.xcodeproj/project.pbxproj>
```

## 2. Android

In `android/app/build.gradle(.kts)`:
- `defaultConfig`: `testInstrumentationRunner "pl.leancode.patrol.PatrolJUnitRunner"` and
  `testInstrumentationRunnerArguments clearPackageData: "true"`. With `clearPackageData`, each
  test file starts with a clean app; the harness restores the session through the API.
- `testOptions { execution "ANDROIDX_TEST_ORCHESTRATOR" }`.
- `dependencies { androidTestUtil "androidx.test:orchestrator:<latest>" }`.

Create `android/app/src/androidTest/java/<package path>/MainActivityTest.java`. Copy it from the
installed package (`~/.pub-cache/hosted/pub.dev/patrol-<version>/example/android/…/MainActivityTest.java`)
and change only the `package` line. Its `package` must match `MainActivity`. Follow the Patrol
setup guide for that version, because these snippets change between major versions.

## 3. iOS

**Check the UIScene life cycle first (apps built with the iOS 27 SDK).** The iOS 27 SDK refuses
to launch an app that does not adopt it: the app aborts at start with "UIScene life cycle is
required for apps built with this SDK", and Patrol then reports `Patrol app did not become ready
on port 8082` and 0 tests (`run_flow.sh` prints `NO_TESTS_RAN`). It depends on the SDK (Xcode) the
app is built with, not on a simulator point release. If `ios/Runner/Info.plist` has no
`UIApplicationSceneManifest`, migrate the Runner before anything else, following the Flutter
migration guide for the project's Flutter version. With Flutter 3.38 that meant a
`SceneDelegate: FlutterSceneDelegate` plus a manifest entry that names
`$(PRODUCT_MODULE_NAME).SceneDelegate`, keeping the existing `AppDelegate`. Newer Flutter versions
may use a different `AppDelegate` shape; do not copy the 3.38 snippet blindly. This is app
configuration, so tell the person and do it in its own change, not inside the E2E files.

Create the `RunnerUITests` UI-testing target with the skill's script. It uses the `xcodeproj`
gem, which ships with CocoaPods; never hand-edit `project.pbxproj`:

```bash
mkdir -p ios/RunnerUITests
cat > ios/RunnerUITests/RunnerUITests.m <<'OBJC'
@import XCTest;
@import patrol;
@import ObjectiveC.runtime;

PATROL_INTEGRATION_TEST_IOS_RUNNER(RunnerUITests)
OBJC
ruby <this skill dir>/scripts/add_ios_ui_test_target.rb ios/Runner.xcodeproj <PRODUCT_BUNDLE_IDENTIFIER>
```

The script mirrors Patrol's own example project:
- `TEST_TARGET_NAME = Runner`, a dependency on Runner, and the same deployment target and
  xcconfigs as Runner;
- `ENABLE_USER_SCRIPT_SANDBOXING = NO`;
- an `xcode_backend.sh build` phase first and `xcode_backend.sh embed_and_thin` last;
- the target added to the shared `Runner` scheme's test action.

Then add this to `ios/Podfile`, inside `target 'Runner'`:

```ruby
target 'RunnerUITests' do
  inherit! :complete
end
```

**Xcode 27+:**
- The minimum deployment target is iOS 15.0. Raise it in the project, and in the Podfile
  (`platform :ios, '15.0'`, plus a `post_install` override for pods).
- Its `lipo` rejects two-architecture simulator binaries, so set
  `EXCLUDED_ARCHS[sdk=iphonesimulator*] = x86_64` on every target and in the Podfile
  `post_install`. Devices and archives are unaffected.

Run `pod install` with a UTF-8 locale (`LANG=en_US.UTF-8`), otherwise recent CocoaPods/Ruby
crash with an encoding error.

With flavors, the Xcode scheme must equal the flavor and the build configurations must be
`<Mode>-<flavor>` (e.g. `Debug-dev`).

## 4. Testable app entry

The harness must mount the real app with a controlled config and an optional start location,
so the bootstrap is split:

```dart
// lib/bootstrap.dart
Future<Widget> buildApp(AppConfig config, {String? initialLocation}) async {
  await configureDependencies(config);
  return App(router: buildRouter(initialLocation: initialLocation));
}

Future<void> bootstrap(AppConfig config) async {
  WidgetsFlutterBinding.ensureInitialized();
  // error handlers …
  runApp(await buildApp(config));
}
```

The router must expose its root navigator key (`rootNavigatorKey` in `core/router`). The
recovery ladder uses it.

## 5. Harness and routines

Create the files from `harness.md` under `<e2e_dir>/common/` and `<e2e_dir>/routines/`.
Adapt only the marked `// ADAPT:` lines: login repository call, home probe, login screen probe,
config factory.

## 6. Credentials

```json
// <e2e_dir>/test_env.example.json (committed)
{ "TEST_EMAIL": "", "TEST_PASSWORD": "" }
```

Add `<e2e_dir>/test_env.json`, `<e2e_dir>/_scratch/`, `**/test_bundle.dart` (generated by Patrol) and `.patrol.env` to `.gitignore`. A person copies the
example and fills it. The agent never does.

## 7. Profile

Set `testing.e2e: patrol`, `testing.e2e_dir`, `testing.default_flavor` and
`testing.credentials_file`. Record the main navigation routines in the e2e overlay.

## integration_test fallback (`testing.e2e: integration_test`)

Use the same harness, swapping `patrolTest` for `testWidgets` (with
`IntegrationTestWidgetsFlutterBinding.ensureInitialized()`) and the native actions for no-ops.
Run with `flutter test integration_test/flows/<flow>_test.dart --flavor <id>`. Native dialogs
(permissions) cannot be handled. The flow must avoid them, or the person accepts them once.
