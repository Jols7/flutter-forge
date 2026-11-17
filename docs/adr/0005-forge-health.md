# ADR 0005 — `forge-health`: a whole-repo baseline, scripts first

- Status: accepted
- Date: 2026-11-16

## Context

`forge-audit` limits its scope to a run, a diff or named paths, and `check_layers --summary`
only counts violations. Nothing answered "what state is this repo in, and what do we fix
first?" for a repository the agent did not write. Auditing a large repo with the model alone
would fill the context window with file reads and cost more than the answer is worth.

## Decision

- Add a skill, `forge-health`, that writes `health-report.md`: real versus declared
  architecture, debt per layer, security, performance, tests, dependencies, a ranked backlog,
  an incremental path per mode and the decisions that need a human.
- **Scripts count, the model judges.** `health_snapshot.py` runs `git_churn.py`,
  `lcov_summary.py`, `code_metrics.py` and the existing scanners, and the skill injects a digest
  of at most 250 lines with the `!` syntax. The model opens a bounded number of files to confirm
  signals (15 at first; ADR 0006 raises it to 30 with a ranked queue). Full data goes to `metrics.json`; `--section` drills down.
- **Reuse, don't copy.** The existing scripts run as subprocesses with `--format json`. The one
  change to old code is an additive `check_layers.py --matrix`, because the real layer-to-layer
  import counts were the missing input for "real versus declared".
- **Manual and isolated.** `disable-model-invocation: true` (a baseline is a deliberate act and
  `forge-deliver` never needs it), `context: fork` (the heavy context stays out of the main
  conversation) and `model: sonnet`. Tools are limited to reading, `python3`, read-only `git log`
  and `Write` for the report.
- **Priority = risk × change frequency ÷ effort.** Multiplying effort in would put the most
  expensive work first. Security and money findings are listed first whatever their frequency,
  and stable code that is ugly but never changes is left alone.
- **Python, not Bash or Dart.** The plugin's convention is stdlib Python 3.9+ with tests in CI;
  the same scripts run on a foreign repo with no Flutter SDK.
- **No test runs, no network by default.** Coverage is read from an existing `lcov.info`;
  `pub outdated` is the only network call and falls back to "not run".
- **Read-only on the audited repo.** The only writes are `metrics.json` and `health-report.md`
  in `.flutter-forge/health/` or a folder the person names.

## Consequences

- A repo without a profile is judged against an assumed preset, and the report says so. A repo
  whose folders match no layer is flagged first, since its layer numbers are unreliable.
- The digest can hide a signal below its cut-offs; `Limits` in the report lists what was not
  measured, and a clean scanner is never presented as proof of safety.
- Coverage counts `lib/` files that tests never import as 0%, which flags abstract classes with
  no executable lines. The skill tells the model to read before reporting.
- Open work: run it on 1–2 public Flutter repositories and publish the report with its false
  positives; measure token cost per run (gap B4); a `forge-upgrade` skill (gap B2).
