# ADR 0008 — Accessibility and semantics are opt-in (`a11y`)

- Status: accepted
- Date: 2026-11-19
- Entry: BIT-011

## Context

Until now semantics were always required: `forge-presentation` (page-patterns § Accessibility),
`forge-audit` (checklist §10) and `forge-tests` (widget-tests guidelines) all enforced them, with
no single source of truth. The current goal is to leave accessibility out for now and keep the
structure ready to implement it properly later.

## Decision

- **Switch `a11y: off | on`.** `forge-requirements` sets it in the brief from the story or
  requirements; `forge-deliver` passes it to blueprint, presentation, tests and audit. If nothing
  asks for it, it inherits `accessibility.default` from `.flutter-forge/profile.yaml` (default `off`).
- **`off`: no semantics rule** in any skill, blueprint, test or audit. Accepted risk: basic gaps
  (an `IconButton` without `tooltip`) are not reported.
- **`on`:** `forge-presentation/references/accessibility.md` is loaded and is the only source of
  truth; the other skills point to it instead of repeating thresholds.
- **Independent of BIT-012:** test keys and `Semantics(identifier:)` for Patrol are emitted
  regardless of `a11y`.
- **Sources adopted** (checked 2026-11-19): Flutter accessibility docs and `flutter_test`
  guidelines; WCAG 2.2 SC 2.5.8 (24×24 CSS px, AA) and 1.4.4; Android 48 dp and iOS 44 pt tap
  targets; *Effective Dart: Documentation* (`///`, one-sentence summary, blank line, `[refs]`).
  Flutter style guide read (no file-size limit, so size thresholds are empirical). The Apple HIG
  page could not be read automatically: 44 pt rests on the Flutter docs.
- **Code comments stay in English** (to be justified in `code-comments.md` in phase 2); `///` scope
  extends from `domain/` to `paths.shared_widgets`.

## Consequences

- Phase 1 onwards edits `forge-presentation`, then audit, tests, requirements, figma and blueprint
  templates behind the switch.
- `forge_demo` is unchanged while `a11y` is off.
