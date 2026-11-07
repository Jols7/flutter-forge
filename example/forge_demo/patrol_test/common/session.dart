/// Session by API, never through the login UI.
///
/// The demo has no authentication: there is nothing to create. Apps with login call
/// their own auth repository here so tokens are stored exactly as the app stores them
/// (see forge-e2e/references/harness.md).
Future<void> ensureSession({bool force = false}) async {}
