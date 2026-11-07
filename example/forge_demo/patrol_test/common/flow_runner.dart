import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:patrol/patrol.dart';

import 'app_harness.dart';
import 'flow_test.dart';
import 'screens.dart';
import 'session.dart';

typedef Routine = Future<void> Function(PatrolIntegrationTester $);

/// Optional pause after each passing step, for screen recordings and demos:
/// `--dart-define=E2E_STEP_DELAY_MS=1500`. Zero (default) in normal runs.
const _stepDelay = Duration(
  milliseconds: int.fromEnvironment('E2E_STEP_DELAY_MS'),
);

class Checkpoint {
  const Checkpoint(this.name, this.probe, {this.reach});

  final String name;
  final Finder probe;

  /// Navigation from the flow entry to this screen (used after a soft restart).
  final Routine? reach;
}

/// Runs a flow as steps with checkpoints, recovery and a session guard.
/// Prints `[FLOW <name>] …` lines that run_flow.sh turns into the report.
class FlowRunner {
  FlowRunner(
    this.$, {
    required this.name,
    required this.entry,
    required Finder entryProbe,
  }) : _checkpoint = Checkpoint('entry', entryProbe);

  final PatrolIntegrationTester $;
  final String name;
  final Routine entry;
  Checkpoint _checkpoint;
  final _failed = <String>[];

  void _log(String message) => debugPrint('[FLOW $name] $message');

  Future<void> start() async {
    await launchAt($, entry);
    await $(
      _checkpoint.probe,
    ).waitUntilVisible(timeout: const Duration(seconds: 30));
    _log('START at entry (${_checkpoint.name})');
    if (_stepDelay > Duration.zero) await Future<void>.delayed(_stepDelay);
  }

  Future<void> step(
    String title,
    Future<void> Function() body, {
    Checkpoint? reached,
  }) async {
    for (var attempt = 1; attempt <= 2; attempt++) {
      try {
        await body();
        final errors = AppErrors.drain();
        if (errors.isNotEmpty) {
          for (final error in errors) {
            _log('ERROR_APP in "$title": $error');
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
          _log(
            'FAIL "$title" on ${_currentScreen()}: ${'$error'.split('\n').first}',
          );
          _log('VISIBLE TEXTS: ${_visibleTexts().join(' | ')}');
          await _recover();
          return;
        }
        _log('SESSION_LOST in "$title" (attempt $attempt)');
        if (attempt == 2) {
          _abort(
            title,
            'session lost twice: test account used elsewhere or backend invalidates tokens',
          );
        }
        await ensureSession(force: true);
        await _softRestart();
      }
    }
  }

  void finish() {
    _log(_failed.isEmpty ? 'END OK' : 'END ${_failed.length} failure(s)');
    if (_failed.isNotEmpty) fail('Failed steps: ${_failed.join('; ')}');
  }

  bool _sessionLost() => Screens.login.evaluate().isNotEmpty;

  bool _atCheckpoint() => _checkpoint.probe.evaluate().isNotEmpty;

  Future<void> _recover() async {
    final ladder = <String, Future<void> Function()>{
      'overlays': () async {
        FocusManager.instance.primaryFocus?.unfocus();
        for (final finder in [
          find.byType(Dialog),
          find.byType(AlertDialog),
          find.byType(BottomSheet),
        ]) {
          if (finder.evaluate().isNotEmpty) await popRoute();
        }
      },
      'pop': () async {
        for (var i = 0; i < 6 && !_atCheckpoint(); i++) {
          await popRoute();
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
      } catch (_) {
        // try the next level
      }
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
    await $(
      _checkpoint.probe,
    ).waitUntilVisible(timeout: const Duration(seconds: 30));
  }

  Never _abort(String where, String reason) {
    _log('ABORTED in "$where": $reason');
    fail('Flow aborted: $reason');
  }

  String _currentScreen() {
    final pages = find
        .byWidgetPredicate((w) => w.runtimeType.toString().endsWith('Page'))
        .evaluate();
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
