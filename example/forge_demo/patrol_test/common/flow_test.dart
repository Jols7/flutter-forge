import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show appFlavor;
import 'package:patrol/patrol.dart';

/// Flavors E2E must never run against (= testing.forbidden_flavors).
const _forbiddenFlavors = {'prod'};

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

/// `patrolTest` that reports uncaught app errors as `ERROR_APP` instead of ending the run.
void flowTest(
  String description,
  Future<void> Function(PatrolIntegrationTester $) body,
) {
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
