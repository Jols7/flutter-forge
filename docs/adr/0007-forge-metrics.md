# ADR 0007 — `forge-metrics`: measure a run after it closes

- Status: accepted
- Date: 2026-11-17

## Context

Gap B4: nothing answered what a run costs, how long it takes or what it saves. The first real
feature delivered with the plugin was measured by hand. That produced a useful report, and the
session that wrote it cost about 14 % of the run it measured. It also showed what a measurement
inside the run cannot do:

- A session's official cost (`cost-state`) appears when the session closes, so the report phase
  cannot know the cost of its own session.
- Work continued after the report: running E2E in a new session and the final commits.
- The model has no clock. `state.json` held `00:00:00Z` timestamps.
- One run spanned eight sessions, and some that overlapped it in time were unrelated.
- The implementation session wrote its files through Bash, so `Write`/`Edit` are not a reliable
  signal.

## Decision

- Add a skill, `forge-metrics`, instead of a phase of `forge-deliver`. It is manual
  (`disable-model-invocation: true`), forked and on `sonnet`, like `forge-health`, and it also
  serves reviews, `forge-health` and single skills.
- **Scripts count, the model judges.** `run_metrics.py` produces every number; the model only
  interprets them.
- **Link by evidence.** A session belongs to a run if it touched `.flutter-forge/runs/<slug>`.
  Sessions that read the transcripts are measurement and are excluded. Nearby sessions are listed
  but not counted; `--include` and `--exclude` settle doubtful cases.
- **Official totals, estimated splits.** Totals come from `cost-state`, so there is no price table
  to keep current. A session without one has an unknown cost and the result is `incomplete`.
  Fixed relative weights only split a session's per-model cost between phases.
- **Separate output.** `.flutter-forge/metrics/<id>.json` and `history.jsonl`, not a block in
  `result.json`, which is closed and often committed before the measurement exists. The folder
  gets its own `.gitignore` when created, because costs are not always meant to be shared.
- **`forge-deliver` records only what cannot be recovered later:** real times from `date -u`,
  `phase_log`, `gates.*.changed`, `retries` and a `baseline_estimate_hours` given before the run.

## Consequences

- Measuring costs a small forked session instead of a long manual analysis.
- Runs made before this version have no `phase_log`, so fix and report count inside `review`.
- The script depends on a transcript format that is not a public contract. Unknown records are
  skipped, and missing cost makes the result incomplete instead of wrong.
- Savings stay uncomputed without a prior baseline and a human review time. Fewer than five
  complete runs of a type are reported as anecdotal.
- An orchestrator that runs the engineer as a subagent is not covered per run yet: its cost lands
  in the orchestrator's session, which can be measured with `--session`.

## Alternatives rejected

- **Model self-report:** invented numbers.
- **A script in phase 12:** misses the current session's official cost and everything after it.
- **Hooks and OpenTelemetry:** useful for teams with a collector, too much setup for a generic
  plugin. They can complement this later.
