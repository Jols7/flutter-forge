# Harness (`<e2e_dir>/common/`)

These files are generic. Adapt only the lines marked `// ADAPT:`. Native actions changed names
between Patrol majors, so `nativeBack` is the single place to keep in sync with the installed
version. A compiled, passing copy of this harness lives in `example/forge_demo/patrol_test/` of
the flutter-forge repository.

## `test_env.dart`

```dart
abstract final class TestEnv {
  static const email = String.fromEnvironment('TEST_EMAIL');
  static const password = String.fromEnvironment('TEST_PASSWORD');

  static void requireCredentials() {
    if (email.isEmpty || password.isEmpty) {
      throw StateError('Missing TEST_EMAIL/TEST_PASSWORD: run with --dart-define-from-file=<credentials_file>');
    }
  }
}
```

## `flow_test.dart` — never let a stray app error kill the run

```dart
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show appFlavor;
import 'package:patrol/patrol.dart';

const _forbiddenFlavors = {'prod'};                      // ADAPT: = testing.forbidden_flavors (flavor ids)

abstract final class AppErrors {
  static final _errors = <String>[];
  static void add(Object error) {
    final text = '$error'.split('\n').first;
    _errors.add(text);
    debugPrint('[APP_ERROR] $text');
  }

  static List<String> drain() {
    final copy = List.of(_errors);
    _errors.clear();
    return copy;
  }
}

void flowTest(String description, Future<void> Function(PatrolIntegrationTester $) body) {
  patrolTest(description, ($) async {
    if (_forbiddenFlavors.contains(appFlavor)) {
      throw StateError('E2E refused on flavor "$appFlavor"');
    }
    final previousFlutterError = FlutterError.onError;
    final previousPlatformError = PlatformDispatcher.instance.onError;
    FlutterError.onError = (details) => AppErrors.add(details.exception);
    PlatformDispatcher.instance.onError = (error, _) {
      AppErrors.add(error);
      return true;
    };
    try {
      await body($);
    } finally {
      FlutterError.onError = previousFlutterError;
      PlatformDispatcher.instance.onError = previousPlatformError;
    }
  });
}
```

With Clean code (repositories return `Result`, so state managers never rethrow), uncaught
errors are rare. Every `ERROR_APP` is therefore a real app bug to report.

## `app_harness.dart`

```dart
import 'dart:io' show Platform;

import 'package:get_it/get_it.dart';
import 'package:patrol/patrol.dart';
import 'package:<package>/bootstrap.dart';
import 'package:<package>/core/router/app_router.dart' show rootNavigatorKey;

import 'screens.dart';
import 'session.dart';

AppConfig testConfig() => AppConfig.fromEnvironment();      // ADAPT: the app's config factory

/// Mounts the app as if it was opened. Calling it again = restart with storage intact.
Future<void> launchApp(PatrolIntegrationTester $, {String? initialLocation}) async {
  await GetIt.I.reset();                                     // ADAPT: remove if the app does not use get_it
  final app = await buildApp(testConfig(), initialLocation: initialLocation);
  await $.pumpWidget(app);
  await $.pumpAndTrySettle();
}

/// Session by API, then the flow's entry. No login UI.
Future<void> launchAt(PatrolIntegrationTester $, Future<void> Function(PatrolIntegrationTester $) entry) async {
  await ensureSession();
  await launchApp($, initialLocation: '/');                   // ADAPT: home route
  await $(Screens.home).waitUntilVisible(timeout: const Duration(seconds: 30));
  await entry($);
}

Future<void> nativeBack(PatrolIntegrationTester $) async {
  // Patrol 4.x API; Patrol 3.x used $.native.pressBack()
  if (Platform.isAndroid) {
    await $.platform.android.pressBack();
  } else {
    await $.platform.mobile.swipeBack();
  }
}
```

## `session.dart` — the session goes through the app's own code

```dart
import 'package:get_it/get_it.dart';

import 'test_env.dart';

/// Reuses a valid stored session; otherwise logs in through the app's repository,
/// so tokens are stored exactly as the app stores them.
Future<void> ensureSession({bool force = false}) async {
  TestEnv.requireCredentials();
  final auth = GetIt.I<AuthRepository>();                     // ADAPT: the app's auth contract
  if (!force && await auth.hasValidSession(minRemaining: const Duration(minutes: 5))) return;
  final result = await auth.login(email: TestEnv.email, password: TestEnv.password);
  if (result case Failure(:final failure)) {
    throw StateError('Test login failed: ${failure.runtimeType}');   // never print credentials
  }
}
```

If DI only exists after `buildApp`, call `configureDependencies(testConfig())` first. Do not
duplicate HTTP calls in the harness.

## `screens.dart` — probes

```dart
import 'package:flutter_test/flutter_test.dart';

abstract final class Screens {
  static final home = find.byType(HomePage);                  // ADAPT
  static final login = find.byType(LoginPage);                // ADAPT: what the app shows after losing the session
  static final transactions = find.byType(TransactionsPage);
  // add one probe per page a flow asserts; copy that flows reuse goes here, not inline
}
```

## `flow_runner.dart` — steps, checkpoints, recovery, session guard

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:patrol/patrol.dart';
import 'package:<package>/core/router/app_router.dart' show rootNavigatorKey;

import 'app_harness.dart';
import 'flow_test.dart';
import 'screens.dart';
import 'session.dart';

typedef Routine = Future<void> Function(PatrolIntegrationTester $);

/// Optional pause after each passing step, for screen recordings and demos:
/// `--dart-define=E2E_STEP_DELAY_MS=1500`. Zero (default) in normal runs.
const _stepDelay = Duration(milliseconds: int.fromEnvironment('E2E_STEP_DELAY_MS'));

class Checkpoint {
  const Checkpoint(this.name, this.probe, {this.reach});
  final String name;
  final Finder probe;
  final Routine? reach;                                        // from the flow entry to this screen
}

class FlowRunner {
  FlowRunner(this.$, {required this.name, required this.entry, required Finder entryProbe})
      : _checkpoint = Checkpoint('entry', entryProbe);

  final PatrolIntegrationTester $;
  final String name;
  final Routine entry;
  Checkpoint _checkpoint;
  final _failed = <String>[];

  void _log(String message) => debugPrint('[FLOW $name] $message');

  Future<void> start() async {
    await launchAt($, entry);
    await $(_checkpoint.probe).waitUntilVisible(timeout: const Duration(seconds: 30));
    _log('START at entry (${_checkpoint.name})');
  }

  Future<void> step(String title, Future<void> Function() body, {Checkpoint? reached}) async {
    for (var attempt = 1; attempt <= 2; attempt++) {
      try {
        await body();
        final errors = AppErrors.drain();
        if (errors.isNotEmpty) {
          for (final e in errors) {
            _log('ERROR_APP in "$title": $e');
          }
          throw StateError('uncaught app error');
        }
        if (_sessionLost()) throw const _SessionLost();
        _log('OK $title');
        if (reached != null) {
          _checkpoint = reached;
          _log('CHECKPOINT ${reached.name}');
        }
        if (_stepDelay > Duration.zero) await Future<void>.delayed(_stepDelay);
        return;
      } catch (error) {
        if (error is! _SessionLost && !_sessionLost()) {
          _failed.add(title);
          _log('FAIL "$title" on ${_currentScreen()}: ${'$error'.split('\n').first}');
          _log('VISIBLE TEXTS: ${_visibleTexts().join(' | ')}');
          await _recover();
          return;
        }
        _log('SESSION_LOST in "$title" (attempt $attempt)');
        if (attempt == 2) {
          _abort(title, 'session lost twice: test account used elsewhere or backend invalidates tokens');
        }
        await ensureSession(force: true);
        await _softRestart();                                  // back to the checkpoint, then retry once
      }
    }
  }

  void finish() {
    _log(_failed.isEmpty ? 'END OK' : 'END ${_failed.length} failure(s)');
    if (_failed.isNotEmpty) fail('Failed steps: ${_failed.join('; ')}');
  }

  bool _sessionLost() => Screens.login.evaluate().isNotEmpty && !identical(_checkpoint.probe, Screens.login);

  bool _atCheckpoint() => _checkpoint.probe.evaluate().isNotEmpty;

  Future<void> _recover() async {
    final ladder = <String, Future<void> Function()>{
      'overlays': () async {
        FocusManager.instance.primaryFocus?.unfocus();
        for (final finder in [find.byType(Dialog), find.byType(AlertDialog), find.byType(BottomSheet)]) {
          if (finder.evaluate().isNotEmpty) await rootNavigatorKey.currentState?.maybePop();
        }
      },
      'pop': () async {
        for (var i = 0; i < 6 && !_atCheckpoint(); i++) {
          await rootNavigatorKey.currentState?.maybePop();
          await $.pumpAndTrySettle();
        }
      },
      'native back': () async {
        for (var i = 0; i < 2 && !_atCheckpoint(); i++) {
          await nativeBack($);
          await $.pumpAndTrySettle();
        }
      },
      'soft restart': _softRestart,
    };
    for (final MapEntry(key: level, value: action) in ladder.entries) {
      try {
        await action();
        await $.pumpAndTrySettle();
      } catch (_) {/* try the next level */}
      if (_atCheckpoint()) {
        _log('RECOVERED level "$level" → ${_checkpoint.name}');
        return;
      }
    }
    _abort('recovery', 'could not return to ${_checkpoint.name}');
  }

  Future<void> _softRestart() async {
    await launchAt($, entry);
    await _checkpoint.reach?.call($);
    await $(_checkpoint.probe).waitUntilVisible(timeout: const Duration(seconds: 30));
  }

  Never _abort(String where, String reason) {
    _log('ABORTED in "$where": $reason');
    fail('Flow aborted: $reason');
  }

  String _currentScreen() {
    final pages = find.byWidgetPredicate((w) => w.runtimeType.toString().endsWith('Page')).evaluate();
    return pages.isEmpty ? 'unknown' : pages.last.widget.runtimeType.toString();
  }

  List<String> _visibleTexts() => find
      .byType(Text)
      .evaluate()
      .map((e) => (e.widget as Text).data)
      .whereType<String>()
      .where((t) => t.trim().isNotEmpty)
      .take(25)
      .toList();
}

class _SessionLost implements Exception {
  const _SessionLost();
}
```

## `routines/navigation_routines.dart`

```dart
Future<void> goToHome(PatrolIntegrationTester $) async {
  await $(Screens.home).waitUntilVisible();
}

Future<void> goToTransactions(PatrolIntegrationTester $) async {
  await goToHome($);
  await $(AccountCard).first.tap();                           // ADAPT
  await $(Screens.transactions).waitUntilVisible(timeout: const Duration(seconds: 30));
}
```

Routine names stay `goTo<Screen>`. Each starts from Home and ends with `waitUntilVisible` on
its probe. A routine that fails because the test user lacks data must `fail('<what is
missing>')`, not time out.

## `routines/login_routines.dart`

There are two routines, and they are the only code that drives the login UI:
- `loginFresh($)`: clear storage → `launchApp` → onboarding skip → credentials → submit →
  dismiss optional prompts (biometrics, notifications) → Home.
- `loginFromLockedSession($)`: only when the app has a lock or inactivity screen. It unlocks with
  the password and lands on Home.

Each one has its own flow test (`login_fresh_test.dart`). No other flow calls them.
