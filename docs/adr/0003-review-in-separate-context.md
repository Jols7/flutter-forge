# ADR 0003 — Review runs in a separate, read-only agent, automation first

- Status: accepted
- Date: 2026-11-06

## Context

An agent that reviews code it just wrote tends to confirm its own reasoning. The public review
skills we evaluated each had a gap:
- [ECC flutter-dart-code-review](https://github.com/affaan-m/ECC) is broad but shallow;
- [flutter-llm-toolkit senior-review](https://github.com/rolandtolnay/flutter-llm-toolkit/tree/bb26ba8)
  is deep but tied to Riverpod and hooks;
- neither ran tools, and neither covered OWASP MASVS or layer rules.

## Decision

- Use a dedicated `flutter-reviewer` agent with read-only tools (Read, Grep, Glob, plus Bash for
  analyzers and scripts). It runs `forge-audit` and `forge-security`. It receives the changed
  file list and the blueprint, but not the implementation conversation.
- Order the review as follows:
  1. automated checks: `flutter analyze`, `dart format`, `check_layers.py`, `scan_secrets.py`,
     `check_platform_config.py`, and DCM when available;
  2. checklist;
  3. design lenses;
  4. MASVS.
- Report only findings with confidence above 80 %. Group similar findings. Use four severities
  (critical/high/medium/low) plus `improvement` for upgrades in `improve` mode.
- The verdict is `block` if any finding is critical or high, otherwise `pass-with-notes` or
  `pass`.

## Consequences

- Fixes are applied by the engineer after Gate 3. The reviewer never edits files.
- When the engineer runs as a subagent, it cannot spawn the reviewer. The audit then runs inline
  and is flagged as non-independent (ADR-documented limitation; see docs/architecture.md).
