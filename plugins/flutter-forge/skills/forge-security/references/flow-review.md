# Flow review — follow the data

For each sensitive value in the brief (credentials, PII, financial or health data, location),
fill one row. Each row is evidence for the requirement table and the MASVS checks.

| Value | Enters (where) | Validated | Stored (where, how) | Sent (endpoint, how) | Shown (masked?) | Logged? | Cleared on logout? |
|---|---|---|---|---|---|---|---|
| Destination account | form field | `TransferDraft.validate` | memory only | POST transfers body (HTTPS) | `•••• 9034` | no | state disposed with the route |
| Access token | login response | — | secure storage | `Authorization` header via interceptor | never | redacted in debug log | `SecureStorage.clear()` in logout |

## Where to look in a Flutter codebase

```bash
grep -rn "SharedPreferences\|GetStorage\|Hive.box\|sqflite\|File(" lib/      # storage
grep -rn "FlutterSecureStorage\|SecureStorage" lib/                           # secure storage use
grep -rn "LogInterceptor\|debugPrint\|print(\|log(" lib/                      # logging
grep -rn "badCertificateCallback\|HttpOverrides\|SecurityContext" lib/        # TLS overrides
grep -rn "uriLinkStream\|getInitialLink\|app_links\|GoRouter(" lib/          # deep links
grep -rn "WebView\|JavascriptChannel\|addJavaScriptHandler" lib/              # webviews
grep -rn "Clipboard.setData" lib/                                             # clipboard
grep -rn "MethodChannel\|EventChannel" lib/                                   # platform channels
grep -rn "FLAG_SECURE\|secure_application\|screen_protector" lib/ android/    # screenshot protection
grep -rn "String.fromEnvironment\|dotenv" lib/                                # config sources
```

## Questions to settle

- Which story actions are sensitive (money movement, profile or credential changes, data
  export)? Does each one require confirmation or re-authentication, and does the code enforce
  it?
- Can a deep link or a push notification start that action? Is the action confirmed by the
  user afterwards?
- What does the app show when the session expires in the middle of the flow, and is any
  half-entered sensitive data kept?
- Are error messages free of internal details (stack traces, SQL, internal ids)?
- When the app goes to the background on a sensitive screen, what does the app switcher show?
