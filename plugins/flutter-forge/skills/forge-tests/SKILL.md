---
name: forge-tests
description: Write and run unit and widget tests for a Flutter feature. Mappers are tested against the contract fixtures; repositories with mocked data sources check every Result/AppFailure path; use cases and validators are tested on their own; state managers are tested with bloc_test, a ProviderContainer, or a plain ChangeNotifier listener; widget tests cover every sealed state, inline errors and interactions. Tests are named after acceptance criteria, use mocktail, and are checked against the coverage target. Use it when the user asks for tests, "pruebas unitarias", "test de widget", "cubre este cubit", "sube la cobertura", "por qué falla este test", after implementing a feature, or when forge-deliver reaches the test phase.
---

# forge-tests

Proves the blueprint's test plan. Each acceptance criterion gets at least one test that
fails when the behavior breaks.

## Step 0 — Resolve

1. From `.flutter-forge/profile.yaml`, read the `testing` section (`unit`, `coverage_min`,
   `widget`) and the `architecture` section (`state`, `di`, `router`).
2. Read the run's `blueprint.md` test plan and the fixtures in `test/fixtures/<feature>/`.
   Without a blueprint, derive the cases from the class list using `references/test-matrix.md`.
3. Look at the existing helpers under `test/helpers/` (`pump_app.dart`, `fixtures.dart`,
   mocks) and reuse them. Create a missing helper from `references/helpers.md` before the
   first test that needs it.
4. If `.flutter-forge/overlays/forge-tests.md` exists, read it; its rules win.

## Step 1 — Write the tests

Mirror `lib/` in `test/`, one test file per class under test. Use the templates:

| Class | Reference | Must cover |
|---|---|---|
| Mapper | `references/data-tests.md` §Mappers | every fixture parses; null/absent → defaults; enum fallback; dates to local; int/double money |
| Remote data source | §Data sources | path (encoded), query, headers (idempotency), body; returns DTO; lets `DioException` through |
| Repository impl | §Repositories | success → `Success(entity)`; each mapped status → its `AppFailure`; business codes → `BusinessFailure`; parsing error → `ParsingFailure`; offline/timeout → `NetworkFailure` |
| Use case / validator | §Domain | each rule from the brief (R-n), boundaries (min − 0.01, min, max, max + 0.01) |
| State manager | `references/state-tests.md` | initial state; load success/empty/failure; retry; pagination; debounce + stale discard; no emit after close; side effects |
| Page / widget | `references/widget-tests.md` | one test per sealed state; interactions dispatch the right intent; inline errors; disabled submit; semantics on icon buttons |

Naming: `group('<Class>')` + `test('AC-3: shows the insufficient funds error under the amount',
…)`. Use the AC or rule id when the test proves one, and plain behavior wording otherwise.

## Step 2 — Run

```bash
<flutter_command> test test/features/<feature>/ --reporter expanded
<flutter_command> test --coverage test/features/<feature>/      # when coverage_min is set
```

- Run only the feature's tests while iterating. Run the whole suite once at the end.
- **Coverage.** Compute line coverage for the feature's new `domain/` and `data/` files from
  `coverage/lcov.info` (`references/helpers.md` § Coverage). It must be at least
  `coverage_min`. Below the target, add the missing cases. Coverage is never raised with
  trivial assertions.
- **Failing test.** First decide whether the test or the code is wrong; the brief and the
  contract are the referees. Fix it, re-run that file, and allow up to **3 fix cycles** per
  failure. After that, stop and report the failure with its output. Never weaken an assertion
  to make it pass.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Hand-written JSON in mapper tests | The contract fixtures | Tests prove the real contract |
| `expect(result, isA<Failure>())` only | Assert the failure **type** and fields | The UI depends on the type |
| Mocking the class under test or mappers | Mock the boundary (data source, repository) | Otherwise the test proves nothing |
| `await tester.pump(Duration(seconds: 2))` to "wait for data" | Mock returns a value; `pump()` once or `pumpAndSettle()` when there are no infinite animations | Flaky and slow |
| One test asserting ten behaviors | One behavior per test | Failures point to the cause |
| Real network, real secure storage, real clock in unit tests | mocktail, fakes, injectable clock/timers (`fakeAsync`) | Deterministic tests |
| States without `==` and `expect: [isA<...>()]` everywhere | Value equality on states; exact expected states | Catches wrong field values |
| Snapshot/golden tests as the only widget tests | Behavior tests first; goldens only for stable visual components | Goldens break on unrelated changes |
| Skipping failure paths because "the happy path works" | Every `AppFailure` the screen handles | Errors are where apps break |

## Finish

- The feature's tests pass, coverage of new domain/data code meets the target, and analyze
  is clean (including `test/`).
- Write `.flutter-forge/runs/<slug>/tests.md`:
  - the AC → test file/name table (and any uncovered AC, with the reason);
  - pass/fail counts and the coverage %;
  - commands run.
- Update `state.json`.
