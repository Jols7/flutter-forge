enum Flavor { dev, qa, prod }

/// Runtime configuration built from `--dart-define`. Never holds secrets: anything
/// compiled into the app can be extracted.
class AppConfig {
  const AppConfig({required this.flavor, required this.baseUrl});

  factory AppConfig.fromEnvironment() {
    const flavorName = String.fromEnvironment('FLAVOR', defaultValue: 'dev');
    const baseUrl = String.fromEnvironment(
      'BASE_URL',
      defaultValue: 'https://api.forge-demo.invalid/v1/',
    );
    final config = AppConfig(
      flavor: Flavor.values.firstWhere(
        (f) => f.name == flavorName,
        orElse: () => Flavor.dev,
      ),
      baseUrl: baseUrl,
    );
    if (MockConfig.enabled && config.flavor == Flavor.prod) {
      throw StateError('USE_MOCKS is not allowed in prod');
    }
    return config;
  }

  final Flavor flavor;
  final String baseUrl;
}

/// Compile-time mock toggle: release builds without the define tree-shake the mocks away.
abstract final class MockConfig {
  static const enabled = bool.fromEnvironment('USE_MOCKS');
  static const scenario = String.fromEnvironment(
    'MOCK_SCENARIO',
    defaultValue: 'default',
  );
}
