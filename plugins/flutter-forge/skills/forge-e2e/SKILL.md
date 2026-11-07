---
name: forge-e2e
description: Write, update and run end-to-end flow tests for a Flutter app with Patrol, falling back to integration_test, on a simulator or emulator. There is one test file per flow, and each starts at the flow's entry point with a session created through the API, so the login UI is only tested by its own routine. Steps are user actions plus assertions, with checkpoints that recover from failures (overlays → pop → native back → soft restart) and a session guard. A runner script filters the report and stops hung runs. Forbidden flavors such as prod are refused. Use it when the user asks to test a flow on a device, "prueba E2E", "prueba en simulador", "automatiza el flujo", "corre la regresión", mentions Patrol or integration tests, says "pruébalo" after building a flow, or when forge-deliver reaches the E2E phase.
---

# forge-e2e

Each flow has one test that walks it like a user. The suite stays in the repo as regression.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`:
   - `testing.e2e` (`patrol` · `integration_test` · `none`), `testing.e2e_dir`,
     `testing.default_flavor`, `testing.forbidden_flavors` and `testing.credentials_file`;
   - `flavors.*`, for building the `--flavor` id and the entrypoint.
2. If `testing.e2e: none`, report that E2E is disabled and stop.
3. If `<e2e_dir>/common/` does not exist, the project is not set up yet: do **Setup** first
   (`references/setup.md`).
4. Read the run's `brief.md` (flow steps, entry and exit) and the blueprint's E2E row.
5. If `.flutter-forge/overlays/forge-e2e.md` exists, read it; its rules win. It typically
   holds the project's login screens, session-loss behavior and main navigation routines.

## Modes (picked from the request; do not ask what it already says)

| Request | Mode |
|---|---|
| Project without the harness, or "configura Patrol" | **Setup** |
| A new flow was just built | **Write** + **Run** that flow |
| An existing flow changed | **Update** its test + **Run** that flow |
| "prueba / corre el flujo X" | **Run** X |
| "corre todas", or a non-default flavor | **Run** the suite / that flavor, only when explicitly asked |

## Setup (once per project)

Follow `references/setup.md`. It covers:
- dependencies and the `patrol:` block;
- the Android runner and orchestrator, and the iOS `RunnerUITests` target;
- a **testable app entry** (`buildApp(config, {initialLocation})`);
- the harness files from `references/harness.md`: `flow_test.dart`, `flow_runner.dart`,
  `app_harness.dart`, `session.dart`, `screens.dart`, `test_env.dart`;
- the routines in `routines/`;
- a committed `test_env.example.json`, and the real file added to `.gitignore`.

When it is done, update the profile's `testing` section.

## Write / Update a flow test

1. **Entry.** Find the flow's entry point and the route from Home. Reuse a routine from
   `routines/navigation_routines.dart`, or add one there (`goTo<Screen>`) so other flows can
   reuse it. Never put navigation inline in the test.
2. **File.** Create `<e2e_dir>/flows/<flow>_test.dart` from `references/flow-test-format.md`:
   - `flowTest(...)`, never a plain `patrolTest`, so uncaught app errors become `ERROR_APP`
     lines instead of killing the run;
   - `FlowRunner(entry: …, entryProbe: Screens.<entry>)`, then `await flow.start()`;
   - one `flow.step()` per user action plus its assertion, and a `Checkpoint` after each
     screen that is safe to return to;
   - `flow.finish()` at the end.
3. **Independence.** The test passes on its own. If it needs another flow to arrive or leave,
   it calls that flow's routine without repeating its assertions. Login UI belongs only to
   the login routines.
4. **Finders**, in this order:
   1. an existing `Key`;
   2. `Screens.<page>` (by type);
   3. text from the ARB;
   4. an icon.

   Add `Key('<screen>_<element>')` to app widgets only when a finder is ambiguous, and say so
   in the report.
5. **Side effects.** Flows that create real operations (payments, transfers, orders) stop
   before the final confirmation unless the person approves running them on the default
   flavor with test data.
6. Analyze `<e2e_dir>` until it is clean.

## Run

Always run through the script, from the project root:

```bash
<this skill dir>/scripts/run_flow.sh \
  --test <e2e_dir>/flows/<flow>_test.dart|all \
  [--flavor <flavor id>] [--device <id>] [--timeout 900] \
  [--env <credentials_file>] [--forbid "<comma-separated forbidden flavor ids>"] \
  [--runner patrol|integration_test]
```

- Pass extra Patrol arguments after `--`, e.g. `-- --no-label --dart-define=E2E_STEP_DELAY_MS=1500`
  for a slower, label-free run that is easy to screen-record.
- It refuses forbidden flavors. It runs Patrol with `--show-flutter-logs` (without it, the
  `[FLOW]` lines are not printed), prints only the report lines and the log path, and stops
  the process when the summary appears or at the timeout. Patrol can hang on iOS after a
  failure.
- Exit codes: `0` green, `1` failures, `2` timeout, `3` usage or refused.
- Before running, check two preconditions:
  - **credentials file exists.** If not, ask the person to create it from the example.
    **Never write credentials yourself.**
  - **a device is booted** (`xcrun simctl list devices booted` / `adb devices`).

  If either is missing, the test stays written and is reported as **pending run**.
- Run only the flow you are working on. When fixing, re-run only the failing file.
  Throwaway diagnostic tests go in `<e2e_dir>/_scratch/` (gitignored) and are deleted
  afterwards.

## Report

Parse the `[FLOW <name>]` lines (format in `references/flow-test-format.md` § Output):
1. Flow, flavor, device and result.
2. Each `FAIL`: the step, the screen, the visible texts, and a verdict — **app bug**, **test bug**,
   or **data** (for example, the test user has no accounts).
3. Each `ERROR_APP`: an app bug, an exception nobody catches. Report its file. Do not "fix the
   test".
4. Each `RECOVERED` level used, and any `SESSION_LOST` or `ABORTED`.
5. Keys added to the app.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Log in through the UI in every flow | Session by API (`launchAt`) | Login is tested once; flows stay fast and independent |
| Hardcode or commit credentials | `--dart-define-from-file` with a gitignored file | Credentials never in code |
| One file walking several unrelated flows | One file per flow | One failure must not block the others |
| `pumpAndSettle()` on screens with spinners or skeletons | `waitUntilVisible` / `pumpAndTrySettle` | Infinite animations never settle |
| `Future.delayed` to wait for data | `waitUntilVisible(timeout:)` | Flaky and slow |
| Retrying a failed step in a loop | Recover to the checkpoint and continue; retry once only on session loss | Retries hide real bugs |
| Running against prod | `forbidden_flavors`, enforced by the script and the harness | Real money, real users |
| Full suite after each fix | Only the failed flow | Same signal, much faster |

## Finish

- Report as above, and add an E2E row to `.flutter-forge/runs/<slug>/tests.md`.
- Update `state.json` with `e2e: passed|failed|pending-run` and the reason.
