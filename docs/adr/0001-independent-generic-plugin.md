# ADR 0001 — A generic plugin, with project knowledge kept in the project

- Status: accepted
- Date: 2026-11-06

## Context

An earlier private plugin proved that Claude Code skills can take a Flutter flow
from its design handoff to tested code. That plugin had these properties:
- it was written for a single architecture (Api → Repository → ChangeNotifier);
- it hardcoded class and path names of its projects;
- it covered E2E tests only, not unit or widget tests;
- it had no audit or security review;
- it assumed that the user story and the endpoint JSON already existed.

## Decision

Build flutter-forge as a new, independent, public plugin:
- It contains no code or text from the earlier plugin. It reuses the *lessons* only: brief with
  gaps before code, mock-first networking, a widget reuse ladder, a checkpointed E2E harness
  and a traceability report.
- Project values go in `.flutter-forge/profile.yaml`.
- Project rules go in `.flutter-forge/overlays/<skill>.md`.
- Import rules go in `.flutter-forge/layers.json`.
- Architectures are presets: `clean` (default) and `layered`, crossed with three state
  managers (BLoC/Cubit, Riverpod, Provider).
- On existing projects the agent detects the architecture and asks whether to adopt it,
  improve it in place, or migrate to Clean.

## Consequences

- Every skill begins with a Step 0 that reads the profile and its overlay. Skills can never
  hardcode a project value. Reviews of the plugin check for this.
- Supporting a new architecture means adding a preset (`layers.json` + reference). Skills do
  not change.
- Projects can tailor any skill without forking the plugin.
