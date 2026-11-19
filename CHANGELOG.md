# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **Accessibility is opt-in** (BIT-011, ADR 0008). A new switch `a11y: off | on` is set in the brief
  (`forge-requirements`, field in the story template) or inherited from `accessibility.default` in
  the profile (default `off`), and `forge-deliver` passes it to blueprint, presentation, tests and
  audit. With `off` no skill requires or reports semantics. Behavior change: runs that used to get
  accessibility findings by default no longer do; set `accessibility.default: on` to keep them.
  Test keys for Patrol (BIT-012) do not depend on it.
- `forge-presentation`: `references/accessibility.md` is now the single source of truth (loaded only
  with `a11y: on`; `page-patterns.md` and `SKILL.md` point to it). Shorter `description`, a Riverpod
  2.x template, and the check step runs `check_presentation.py`.
- `forge-audit` checklist §10, `flutter-reviewer`, `forge-tests` (widget tests need
  `ensureSemantics()`, both tap-target guidelines and a text-scale test that checks visible content),
  `design-template.md` (Semantics section) and `blueprint-template.md` (Semantics column) apply
  accessibility only with `a11y: on`.
- `code-comments.md` cites *Effective Dart* and the Flutter style guide, explains why comments are in
  English and adds a `///` writing guide with good and bad examples per layer.

### Added
- `forge-presentation/references/structure.md`: naming (`XPage`, `XTile`, `XCard`, `XSection`,
  `snake_case` files), folder skeleton, extract/promote rules and size thresholds measured on a real
  app and set as strict targets: `build()` 50 lines and cyclomatic complexity 5, file 250 lines,
  nesting 12, 3 classes. **Behavior change:** `quality.max_build_lines` now defaults to 50 (was 120),
  so projects that never set it get more findings; set it in the profile to keep the old value.
  In `adopt` and `improve` mode (`architecture.mode` or `--mode`) the check
  defaults to the looser legacy numbers (120 lines, complexity 10, file 300, depth 20) and reports
  `build-lines` and `build-complexity` as warnings, so an existing app (UnitedApp: 44 % of files at
  the strict numbers) is not failed wholesale; profile values always win.
- `forge-audit/scripts/check_presentation.py`: counts and matches size, approximate `build()`
  complexity, naming, `_buildX()` helpers, hardcoded colors/fonts, service locators in presentation
  and navigation inside state managers. `finding` fails the run; `warn` does not. Six unit tests.
- `check_comments.py --shared-widgets`: public classes in the shared widgets folder need `///`.
- Profile keys: `accessibility.default`, `quality.max_build_complexity`, `max_file_lines`,
  `max_classes_per_file`, `max_widget_depth`, `public_member_api_docs`.
- ADR 0008 (accessibility opt-in).
- Evals for `forge-presentation` (BIT-011): `presentation-sealed-state-and-disposal`,
  `presentation-a11y-semantics` (off requires nothing, on does) and
  `presentation-naming-and-structure`.
- Evals for `forge-metrics` (BIT-008): `metrics-interpret-run` (report from a script digest: API-price
  wording, estimated split, no savings without a baseline, sessions to confirm) and
  `metrics-incomplete-no-invention` (an `INCOMPLETE` run never gets an invented total).

## [0.7.0] - 2026-11-17

Additive only: `result.json` keeps `schema: 1` and does not change, and every existing skill and
agent name stays. The brief gains one optional field.

### Added
- `forge-metrics` (gap B4, BIT-008, ADR 0007): measures a run after its sessions close.
  - Runs by hand only (`disable-model-invocation`), in a forked context, on `sonnet`.
  - `run_metrics.py` links sessions to a run by the run folder they touched and reads the official
    cost per model from `cost-state`, with no price table. It also splits cost per phase, separates
    model, tool, question and waiting time, and reads the outcome from `state.json` and `result.json`.
  - It stores counters only in `.flutter-forge/metrics/`, ignored by git by default, and keeps a
    `history.jsonl` for median and range per run type.
- `forge-deliver` records real timestamps through `date -u`, plus `phase_log`, `gates.*.changed`,
  `retries` and the optional `baseline_estimate_hours` in `state.json`.
- Unit tests for the script.

## [0.6.0] - 2026-11-16

Same contract as 0.5.0: no brief field, `result.json` or skill name changes.

### Added
- `forge-health` standard depth (default; `--depth quick` keeps the old behavior), ADR 0006:
  - `infer_layers.py` drafts a `layers.json` from folder names and file suffixes when neither
    preset fits (28% → 99% of files classified on a large real repo).
  - `draft_profile.py` drafts a `profile.yaml` from what the code shows; the mode stays a human
    decision and it never writes `.flutter-forge/profile.yaml`.
  - The snapshot ranks a review queue (up to 30 files) and writes `layers.draft.json` and
    `profile.draft.yaml` to the health folder.
  - Tests and an eval (`health-standard-inferred-layers`).

## [0.5.0] - 2026-11-16

No change to the orchestrator contract: the brief fields, `result.json` (`schema: 1`), the
`hu-v1` template and every existing skill and agent name are untouched. `forge-deliver` does not
call the new skill.

### Added
- `forge-health` (gap B1, BIT-004): a whole-repo health baseline that writes `health-report.md`.
  - Runs by hand only (`disable-model-invocation`), in a forked context, on `sonnet`.
  - Scripts collect the data and a digest of at most 250 lines is injected into the prompt, so
    the model confirms signals instead of exploring the tree.
  - The report maps real versus declared architecture with debt per layer, then security,
    performance, tests (hot files without coverage), dependencies, a backlog ranked by
    `risk × change frequency ÷ effort` (quick wins apart from big bets), an incremental path
    per `adopt`/`improve`/`migrate`, and the decisions that need a human.
  - Scripts: `health_snapshot.py`, `git_churn.py`, `lcov_summary.py`, `code_metrics.py`. They
    reuse `detect_project.py`, `check_layers.py`, `scan_secrets.py` and
    `check_platform_config.py` as they are.
- `check_layers.py --matrix` prints the real layer → layer import counts; the JSON report always
  carries `matrix`.
- Tests for the collectors and the snapshot, an eval (`health-baseline-hotspots`), ADR 0005.

## [0.4.0] - 2026-11-14

No change to the orchestrator contract: the brief fields, `result.json` (`schema: 1`), the
`hu-v1` template and every skill and agent name are untouched. Everything added is optional.

### Added
- `forge-architecture/references/conventions.md`: typed assets in `core/constants/`, mapper
  naming, isolated repositories, private data sources, one state manager per screen,
  `StatefulShellRoute` shells and router-driven app start (`page-patterns.md`).
- ADR 0004: reference architectures compared (a Flutter demo analysed on DeepWiki, the official
  Flutter guide, Very Good Ventures) and what was adopted or left.
- `detect_project.py` reports `naming.mapper_method` and `needs_decision` (state, router, HTTP
  or l10n values the profile cannot express, such as `getx` or `beamer`). The profile gains the
  optional `naming.mapper_method` and `git.convention`; `forge-profile` documents a read-only mode.
- `check_comments.py --changed-from REF` and `--rules layers.json`.
- `check_layers.py` lists imports into unclassified files (blind spots, not violations).
- Tests: both presets are loaded against trees built from their own documentation, and every
  cross-skill file reference must resolve.

### Fixed
- `composition` allowed UI to import `core/di`, so a widget could call the global `getIt`
  without a violation. `core/di` is now the closed `composition_di` layer (Riverpod projects get
  it opened by `forge-profile`).
- The `layered` preset forbade `api → dtos`, so every layered project produced violations.
- `--changed-from` returned repo-root paths for an app inside a monorepo folder (for example
  `apps/mobile`) and matched nothing; paths are now relative to the app.
- The load-more state example mixed two flags (`isLoadingMore`, `loadMoreFailure`) against the
  sealed-state rule. It is now a sealed `LoadMore`, in the docs and in the demo with its tests.
- Domain repository contracts no longer carry `CancelToken` (Dio is banned in `domain`).
- `Page<T>` and `Paginated<T>` are unified as `Paginated<T>`.
- `BusinessFailure` never shows backend text; features map its `code` to an l10n key.
- Docs: `useMocks` → `MockConfig.enabled`, the disposal flag name, the confidence threshold,
  the `in-progress` status, `Q-n`/`G-n` gap ids, `"intégralo"` removed from `forge-data-layer`,
  overlapping triggers disambiguated, README script and eval counts, the broken
  `result-and-failures.md` and `check_comments.py` paths.
- The reviewer's single permitted write (`findings.md`) is documented, with a fallback to the reply.
- 0.3.0 listed unit tests for `run_flow.sh` and `add_ios_ui_test_target.rb`; only `shellcheck`
  covers the runner. The README no longer claims otherwise.

## [0.3.0] - 2026-11-08

### Changed
- Default user story template is now **hu-v1**, technology-neutral and multi-surface:
  - header fields `Template`, `Epic`, `Surfaces` (replaces `Platform`), `Points` and
    `Depends on`;
  - §5 "Interface, flows and states" and §6 hold one `### <surface>` block per UI surface;
  - §7 is contract-first (`operationId` or `METHOD /path`, contract status);
  - `N/A — <reason>` for sections that don't apply;
  - `Q-n (blocking: …)` open questions.

  Section numbers 1–10 and their meaning are unchanged.
- `hu-to-brief.md` reads stories by section number:
  - a story applies when `Surfaces` contains `mobile` (`Platform` for earlier stories);
  - §5/§6 read only `### mobile` when surface blocks exist, or the whole section otherwise;
  - `Epic`, `Points`, `Depends on` and `NFR-n` are not consumed.
- `forge-requirements` drafts standalone stories with `Surfaces: mobile` and `### mobile`
  blocks. Custom `requirements.template` files must keep sections 1–10 and the
  `### <surface>` convention.
- The example story `HU-01-transfer.md` is migrated to hu-v1.

### Added
- Story fixtures (`tests/fixtures/hu/`): an earlier flat story and a hu-v1 web+mobile story,
  plus a manual checklist.
- `test_hu_template.py`: template sections 1–10 in order, the header contract, and a
  reference reader proving that only `### mobile` is read and that earlier stories still read.

## [0.2.0] - 2026-11-07

### Added
- Agents declare `model: sonnet` (`flutter-engineer`, `flutter-reviewer`), so they no longer
  inherit the caller's model.
- Brief field `explain: none | brief | full` (default `brief`). Runs report **Por qué**
  (decisions and discarded alternatives) and **Dónde revisar** (`file:line` + reason) in
  `report.md`, the final message and `result.json` (`why[]`, `review_points[]`).
- `result.json`: optional `git` object (branch, commits, PR). The schema stays at `1`
  (additive), and a `result.example.json` is validated in CI.
- Git conventions for `git: commit | pr`: Conventional Commits with scope `mobile`,
  `<type>/<HU>-<slug>` branches, PR body *Qué / Por qué / Dónde revisar*, never merge or
  force-push, and the project's own convention respected when it has one.
- Code comments policy (`forge-architecture/references/code-comments.md`):
  - applied by `forge-data-layer` and `forge-presentation`;
  - audited by checklist §14 and the new `check_comments.py` (commented-out code, `TODO`
    without a reference, banners, missing `///` on domain contracts);
  - new eval `audit-comment-policy`.

### Changed
- Example app: domain contracts and entities documented with `///`; the CI checks the
  comments policy.
- `docs/subagent-contract.md`: `explain`, `why`/`review_points`, `git` and compatibility rules.
- CONTRIBUTING: commit scopes for this repository and for generated projects.

## [0.1.0] - 2026-11-06

### Added
- Marketplace and plugin manifests; MIT license with third-party attribution (NOTICE).
- Agents:
  - `flutter-engineer`: entry point for people and orchestrators;
  - `flutter-reviewer`: read-only, independent review.
- Skills:
  - `forge-deliver`: pipeline with 3 gates, resumable runs and `result.json`;
  - `forge-profile`: stack detection, adopt/improve/migrate, profile and layer mapping;
  - `forge-architecture`: `clean` and `layered` presets, layer rules in JSON, Result/AppFailure,
    DI, core bootstrap;
  - `forge-requirements`: story analysis or drafting (INVEST + Gherkin), brief and gaps;
  - `forge-figma`: Figma MCP, token mapping, reuse ladder, widget catalog, CSS mode;
  - `forge-api-contract`: Postman v2.1/v3/cloud and OpenAPI → contract and redacted fixtures;
  - `forge-blueprint`: class design, value trace, test plan;
  - `forge-data-layer`: entities, contracts, DTOs, mappers, data sources, repositories,
    mock-first;
  - `forge-presentation`: BLoC, Riverpod and Provider templates, sealed states, page patterns;
  - `forge-l10n`: gen-l10n and intl_utils;
  - `forge-tests`: unit, state and widget tests with fixtures and coverage;
  - `forge-e2e`: Patrol harness (Patrol 4 API), checkpoints, recording pace
    (`E2E_STEP_DELAY_MS`), runner script and iOS UI-test target script;
  - `forge-audit`: automated checks, checklist, design lenses, severity model;
  - `forge-security`: OWASP MASVS v2, secret and platform-config scanners, flow review;
  - `forge-learn`: overlays and proposals.
- Scripts with unit tests:
  - `detect_project.py`, `postman_to_contract.py`, `check_layers.py`;
  - `scan_secrets.py`, `check_platform_config.py`;
  - `run_flow.sh` and `add_ios_ui_test_target.rb`.
- Example app `example/forge_demo`:
  - accounts and transactions in the `clean` preset;
  - 29 tests and 82.6 % domain/data coverage;
  - a Patrol E2E flow passing on the iOS simulator (Xcode 27 ready);
  - a sample story and the README GIF.
- Evals for 5 cases; CI workflow (validate, scripts, example, leak guard read from a secret)
  and a manual/weekly evals workflow.
- Documentation: architecture, subagent contract, ADRs 0001–0003.
