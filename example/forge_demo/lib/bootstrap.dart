import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

import 'app/app.dart';
import 'core/config/app_config.dart';
import 'core/di/injection.dart';
import 'core/router/app_router.dart';

/// Builds the app without running it, so tests (Patrol, widget) can mount it.
Future<Widget> buildApp(AppConfig config, {String? initialLocation}) async {
  await configureDependencies(config);
  return App(router: buildRouter(initialLocation: initialLocation));
}

Future<void> bootstrap(AppConfig config) async {
  await runZonedGuarded(() async {
    WidgetsFlutterBinding.ensureInitialized();
    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      // send to crash reporting here (no PII)
    };
    PlatformDispatcher.instance.onError = (error, stack) {
      debugPrint('Uncaught: ${error.runtimeType}');
      return true;
    };
    runApp(await buildApp(config));
  }, (error, stack) => debugPrint('Zone error: ${error.runtimeType}'));
}
