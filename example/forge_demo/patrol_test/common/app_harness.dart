import 'dart:io' show Platform;

import 'package:forge_demo/bootstrap.dart';
import 'package:forge_demo/core/config/app_config.dart';
import 'package:forge_demo/core/router/app_router.dart' show rootNavigatorKey;
import 'package:get_it/get_it.dart';
import 'package:patrol/patrol.dart';

import 'screens.dart';
import 'session.dart';

AppConfig testConfig() => AppConfig.fromEnvironment();

/// Mounts the app as if it was opened. Calling it again = restart with storage intact.
Future<void> launchApp(
  PatrolIntegrationTester $, {
  String? initialLocation,
}) async {
  await GetIt.I.reset();
  final app = await buildApp(testConfig(), initialLocation: initialLocation);
  await $.pumpWidget(app);
  await $.pumpAndTrySettle();
}

/// Session by API, then the flow's entry. No login UI.
Future<void> launchAt(
  PatrolIntegrationTester $,
  Future<void> Function(PatrolIntegrationTester $) entry,
) async {
  await ensureSession();
  await launchApp($, initialLocation: '/');
  await $(Screens.home).waitUntilVisible(timeout: const Duration(seconds: 30));
  await entry($);
}

/// Native back for the installed Patrol major (4.x).
Future<void> nativeBack(PatrolIntegrationTester $) async {
  if (Platform.isAndroid) {
    await $.platform.android.pressBack();
  } else {
    await $.platform.mobile.swipeBack();
  }
}

/// Pops the root navigator (used by the recovery ladder).
Future<void> popRoute() async => rootNavigatorKey.currentState?.maybePop();
