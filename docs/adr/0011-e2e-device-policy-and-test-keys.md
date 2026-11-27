# ADR 0011 — E2E device policy and test keys

- Status: accepted
- Date: 2026-11-26
- Entry: BIT-012

## Context

Two `forge-deliver` runs looped in the E2E phase: Patrol asked which of three devices to use, nobody
answered and the prompt repeated. `run_flow.sh` passed `--device` only when the person gave one. Separately,
there was no key convention, so the E2E phase edited audited production code and every run invented names.

## Decision

- **Device.** A deterministic script chooses the device (requested → booted iOS simulator → booted Android
  emulator; physical, desktop and web only if named). The runner always passes `--device`, runs with stdin
  closed, and aborts on a repeated chooser (exit 5). No device → exit 4 → `pending-run`. Asking is limited
  to interactive runs with several candidates, and the answer is saved as `testing.device`.
- **Keys.** One source (`conventions.md` § 9): `<Feature>Keys` constants declared in the blueprint, emitted
  by `forge-presentation`, consumed by tests. A missing key is a finding in the E2E report, never a `lib/`
  edit. Independent of the `a11y` switch (ADR 0008).
- `Semantics(identifier:)` is not adopted: Patrol support was not confirmed.

## Consequences

- The fragile decisions live in a script and a template, not in the model's judgment.
- The prompt detector matches Patrol/Flutter chooser text (`Please choose one` and variants); it must be
  re-checked against a real log if Patrol changes its wording.
- `flutter-patrol-flows` (PGI plugin) is outside this repo and needs the same policy.
