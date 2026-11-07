---
name: forge-security
description: Security review of a Flutter feature and its whole flow, mapped to OWASP MASVS v2 (storage, crypto, auth, network, platform, code, resilience, privacy). Automated scanners run first (hardcoded secrets, bundled env files, sensitive logging, cleartext URLs, AndroidManifest/Info.plist/Gradle release settings, dependency vulnerabilities). Then a flow review follows the data from input to storage, network, logs and screens. It checks the story's security requirements (masking, re-authentication, limits, screenshots) and reports severity-ranked findings with fixes. It never edits code. Use it when the user asks for a security review, "revisión de seguridad", "audita la seguridad", "OWASP", "MASVS", "pentest del código", before releasing a feature that touches credentials, money or personal data, or when forge-deliver reaches the review phase.
---

# forge-security

This skill reports findings and never edits files. It reviews the **flow**, not only the files:
where sensitive data enters, where it is stored, where it travels, where it is shown, and where
it is logged.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`:
   - `security.level`: `standard` checks MASVS-L1; `high` adds L2 and RESILIENCE;
   - `security.sensitive_data` and `security.pinning`;
   - `networking.*`, `testing.forbidden_flavors` and `flavors.*`.
2. Set the scope as `forge-audit` does: the run's files first, then the diff, then the named
   paths. Platform configuration is **always** in scope, because a feature can be exposed by
   it.
3. Read the brief's **Security** section and the story's §8 (if they exist). These are
   requirements to verify, not suggestions.
4. If `.flutter-forge/overlays/forge-security.md` exists, read it; its rules win. It holds
   accepted risks with an owner and an expiry, and company policies.

## Step 1 — Automated scanners

```bash
python3 <this skill dir>/scripts/scan_secrets.py --root . [--files <scope…>]
python3 <this skill dir>/scripts/check_platform_config.py --root .
<flutter_command> pub outdated --json             # stale/discontinued packages
osv-scanner --lockfile=pubspec.lock               # only if installed; otherwise report "not run"
```

- **`scan_secrets.py`** finds private keys, cloud and vendor tokens, JWTs, secret-like literals,
  bundled `.env` and keystores, env files that are not gitignored, `http://` URLs, and logging
  calls that touch sensitive names. It masks values in its output. **Never print a secret's
  value** in the report either: give the location and the kind only.
- **`check_platform_config.py`** checks Android cleartext, backup, debuggable, exported
  components, custom URL schemes, permissions, release signing, R8 and hardcoded keystore
  passwords. On iOS it checks ATS, URL schemes, file sharing and usage strings. It also checks
  whether build scripts use `--obfuscate --split-debug-info`.
- Scanner findings outside the scope still count when they expose the app (a debug-signed
  release, ATS disabled). Mark them `pre-existing`. They block only if they are critical or the
  overlay says so.

## Step 2 — Flow review (MASVS)

Walk the checks in `references/masvs.md` for every category that applies, guided by
`references/flow-review.md`:
1. **Inputs:** forms, deep links, push payloads, platform channels, WebViews.
2. **Storage:** tokens only in secure storage; no sensitive data in prefs, files or logs; cache
   lifetime; what happens on logout.
3. **Network:** HTTPS only; certificate pinning when `security.pinning` or `level: high`;
   interceptor behavior on 401/403; token refresh; no secrets in query strings.
4. **Auth and session:** where tokens come from and how they expire; re-authentication before
   sensitive actions (as the story requires); logout wipes session data.
5. **UI exposure:** masking (last 4 digits); screenshots and the app-switcher snapshot on
   sensitive screens (`level: high`); clipboard use; error messages that leak internals.
6. **Code and build:** no secrets in the binary (anything in Dart, assets or `--dart-define` is
   extractable); obfuscation; no debug flags in release; mocks unreachable in release.
7. **Dependencies:** maintained packages, no known vulnerabilities, no plugins with dangerous
   unused permissions.
8. **Privacy:** data minimization, permission rationale, and analytics or crash reports
   without PII.

## Step 3 — Verify the story's security requirements

Each requirement in the brief's Security section becomes a row: requirement → code location
→ **met / not met / not verifiable**. A requirement that is not met is a finding of at least
**high**.

## Step 4 — Report

Append a `## Security` section to `.flutter-forge/runs/<slug>/findings.md`. Without a run,
write it to a file the person chooses. Use the format of `forge-audit/references/severity.md`
and add a `masvs` field to each finding. Order:
1. scanner table;
2. requirement table;
3. findings by severity;
4. accepted risks from the overlay;
5. verdict.

Severity guide:
- **critical:** secret or credential in the repo or binary; auth bypass; release signed with a
  debug key; cleartext transport of credentials.
- **high:** a token in insecure storage or logs; ATS disabled or cleartext allowed; a
  deep-link parameter used without validation in a sensitive action; an unmet story
  requirement.
- **medium:** missing pinning when required; backup enabled; exported components; custom schemes
  without validation.
- **low:** hardening and privacy polish.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Paste the found secret in the report | Location + kind + "rotate it" | The report is shared |
| "Use certificate pinning" for every app | Recommend it by `security.level`, with the rotation plan | Pinning without key rotation breaks apps |
| Treat `--dart-define` or obfuscation as secret storage | Secrets live on the backend; the app holds only per-user tokens | Everything in the binary is public |
| Edit platform files during the review | Report the fix; apply after Gate 3 | Platform changes need human review (release impact) |
| Review only the changed Dart files | Include platform config and the flow's data path | Most mobile exposures are configuration |
| Flag Firebase client keys as critical | Low: ensure API restrictions + App Check | They are public by design |

## Finish

- The `## Security` section is written. Update `state.json` with the security counts by
  severity and the verdict.
- Recommend rotating any secret found in history. Recommend that a person run a dynamic test
  (MobSF or a proxy) when `level: high`. Static review cannot replace it.
