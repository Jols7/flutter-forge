# OWASP MASVS v2 — Flutter checks

Rows marked **L2** apply only when `security.level: high`. The last column says where the
evidence comes from: **S** = a scanner, **R** = reading the code or flow.

## MASVS-STORAGE

| Check | Ev. |
|---|---|
| Tokens and credentials only in `flutter_secure_storage`. Never in `SharedPreferences`, files, `sqflite` without encryption, or Hive boxes without an encryption cipher | R |
| No sensitive data in logs (`print`, `debugPrint`, `log`, logger, Dio `LogInterceptor` without redaction, Crashlytics custom keys) | S+R |
| Debug log interceptor guarded by `kDebugMode`, with headers and bodies redacted | R |
| `android:allowBackup="false"` or backup rules excluding sensitive files; iOS file sharing off | S |
| Logout wipes the session: tokens, cached personal data, in-memory state managers | R |
| No sensitive data in `--dart-define`, assets, `.env` bundled through `flutter_dotenv` | S |
| **L2:** sensitive caches are encrypted at rest; temporary files are deleted | R |

## MASVS-CRYPTO

| Check | Ev. |
|---|---|
| No custom crypto. No hardcoded keys or IVs (`Key.fromUtf8('…')`). No ECB, no MD5 or SHA-1 for security purposes | S+R |
| Random values for security use `Random.secure()` | R |
| Keys live in the Keystore or Keychain (secure storage / platform APIs) and are never derived from constants | R |

## MASVS-AUTH

| Check | Ev. |
|---|---|
| Auth is enforced by the backend. Client-side checks (`if (isAdmin)`) only hide UI | R |
| 401 → one refresh attempt under a lock → logout. 403 → no silent retry loop | R |
| Re-authentication (biometrics, PIN, OTP) before the sensitive actions the story lists. `local_auth` result bound to the action, not a global flag | R |
| Biometrics are not the only factor for high-value actions when `level: high` (**L2**) | R |
| Session timeout or inactivity lock as required by the story | R |

## MASVS-NETWORK

| Check | Ev. |
|---|---|
| HTTPS only: no `http://` in config or code; Android cleartext off; iOS ATS on | S |
| Certificate validation never disabled (`badCertificateCallback = (_, __, ___) => true`, `HttpClient` overrides) | S+R |
| Pinning (**L2**, or `security.pinning`) with backup pins and a rotation plan; pins on the public key (SPKI) | R |
| Secrets and PII never in URLs or query strings (they get logged by proxies) | R |
| User CAs trusted only in `debug-overrides` | S |

## MASVS-PLATFORM

| Check | Ev. |
|---|---|
| Deep links / App Links / Universal Links: every parameter is validated in the router; links cannot trigger sensitive actions without confirmation; verified links preferred over custom schemes | S+R |
| Exported Android components are protected | S |
| WebViews: JavaScript off unless needed; no `addJavascriptChannel` exposing sensitive APIs; `navigationDelegate` restricts allowed hosts; no file access | R |
| Platform channels validate their arguments on the native side | R |
| Sensitive screens: `FLAG_SECURE` (Android) and a blur on app-switcher snapshots (iOS) when the story requires it or `level: high` | R |
| Clipboard: sensitive values are not copied, or are cleared, and the user is told | R |
| Push notification payloads carry no sensitive data | R |

## MASVS-CODE

| Check | Ev. |
|---|---|
| No secrets in source or binary (scanner); secrets found in git history must be rotated | S |
| Release signed with a release key; keystore and passwords out of the repo | S |
| Dependencies maintained, with no known CVEs (`pub outdated`, `osv-scanner`); no `dependency_overrides` without a reason | S |
| Input validation for anything that reaches files, SQL, URLs or WebViews | R |
| Mocks, test hooks and debug menus unreachable in release (const flags, asserts) | R |
| Minimum OS versions supported by security updates | S |

## MASVS-RESILIENCE (L2 only, unless the overlay asks for it)

| Check | Ev. |
|---|---|
| `--obfuscate --split-debug-info` on release builds; symbols uploaded to crash reporting | S |
| R8 enabled on Android | S |
| Root/jailbreak and emulator detection (e.g. `freeRASP` / platform integrity APIs) with a defined reaction (warn / block sensitive actions); never the only control | R |
| Play Integrity / App Attest used by the backend for high-value endpoints | R |
| No `debuggable` in release | S |

## MASVS-PRIVACY

| Check | Ev. |
|---|---|
| Each permission is needed, requested at use time, and explained | S+R |
| Analytics and crash reports exclude PII and financial values; user IDs are pseudonymous | R |
| Data minimization: the app requests and stores only what the screens need (compare with the value trace) | R |
| The privacy manifest (iOS `PrivacyInfo.xcprivacy`) is present when required-reason APIs are used | S+R |
