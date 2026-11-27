# Severity, confidence and report format

## Severity (by impact)

| Severity | Meaning | Typical examples | Merge |
|---|---|---|---|
| **critical** | Wrong behavior, data loss, security exposure or crash on a normal path | DTO non-nullable for a nullable field on a main screen; emitting after close in a loop; money parsed as `int`; layer violation that leaks secrets/tokens to UI; prod mocks enabled | block |
| **high** | Breaks the architecture contract or a likely bug on a less common path | DTO used in presentation; repository throws strings / swallows errors; state manager resolving from service locator (untestable); missing disposal of controllers/timers; AC without implementation; uncaught failure type in an exhaustive flow | block |
| **medium** | Maintainability or UX debt that will cost soon | bag-of-booleans state; duplicated widget; `build` > `quality.max_build_lines`; missing empty/error state; cross-feature import of data; flaky test pattern | notes |
| **low** | Local polish with low risk | missing `const`; non-descriptive name; minor a11y label (only when `a11y: on`) | notes |
| **improvement** | `improve` mode upgrades of legacy patterns in new code (never blocking) | new repository method could return `Result` | notes |

The automated checks map to severities like this:
- analyzer `error` → high;
- analyzer `warning` → medium;
- `check_layers` violations in scope:
  - `forbidden-import` → high;
  - `layer` → high;
  - `cross-feature` → medium.

`check_presentation.py` severities map as follows (the script marks them `finding` or `warn`):
- `build-lines`, `build-complexity` → medium (low when the script reports them as `warn`, i.e. in `adopt`/`improve`); `ui-helper`, `hardcoded-style` → medium;
- `locator-in-ui`, `navigation-in-state` → high in new code, low in legacy files in adopt mode;
- `file-lines`, `classes-per-file`, `nesting-depth`, `file-name` (`warn`) → low.
Complexity is approximate: confirm with DCM or by reading the method before reporting it.

`check_responsive.py` findings map to these severities:
- `row-text-no-flex` → medium in new code (high when the amount or label is money or can reach 14+
  characters), low when the script reports it as `warn` (`adopt`/`improve`);
- `fixed-width`, `fixed-height-text`, `row-texts-no-flex`, `form-no-scroll` → low, medium when a rendered
  matrix (`forge-tests`) overflows; `list-not-builder`, `media-query-of` → low.
A missing or `fail` verdict in `design.md` is medium; accepted differences without a reason are low.

`check_comments.py` findings map to these severities:
- `commented-out-code` → medium;
- `todo-without-ref` → low;
- `banner` → low;
- an interactive widget or sealed-state container in a `*_page.dart` without the key the blueprint lists (`conventions.md` § 9) → low (manual check; no script yet, calibrate before adding one).
- `missing-doc` on a domain contract → low.

A missing reference on a non-obvious **money or security** rule is medium.

An overlay can remap any rule, for example `forbidden-import package:get_it/ in presentation:
medium (legacy)`.

## Confidence

Report only findings with confidence of **0.8 or more**. Confidence is high when:
- a tool output proves the finding, or
- the code path is visible end to end and the failure scenario is concrete (input → wrong
  output or crash).

When in doubt, read the collaborator before you report. If confidence stays below 0.8, drop
the finding, or ask the question in **Notes** without counting it.

## `findings.md` format

```markdown
# Findings — <feature> · <date> · reviewer: flutter-reviewer (independent: yes|no)
Scope: 23 files (run file list) · Rules: .flutter-forge/layers.json · Mode: new

## Automated checks
| Check | Result |
|---|---|
| flutter analyze | 0 errors, 1 warning (F-4) |
| dart format | clean |
| check_layers (scope) | 1 violation (F-1) · project debt: 0 |
| dcm | not configured |

## Findings
### F-1 · high · architecture · lib/features/transfers/presentation/pages/transfer_page.dart:14
**What:** imports `data/models/transfer_preview_dto.dart` and reads `dto.amountReceived`.
**Why:** DTOs must not cross the repository; a backend rename would break the UI.
**Fix:** use `TransferPreview.amountReceived` from the cubit state; delete the import.
Confidence 0.95 · Owner: forge-presentation

### F-2 · medium · state · …

## Summary
| Severity | Count |
|---|---|
| critical | 0 |
| high | 1 |
| medium | 2 |
| low | 1 |
| improvement | 0 |

**Verdict: block** (1 high). Pre-existing debt outside scope: 63 layer violations (not blocking).

## Notes
- <questions below the confidence bar, observations for the team>
```

In `result.json`, findings appear as `{id, severity, category, file, line, summary, owner,
status}`, where `status` is `open | fixed | wontfix | deferred`.
