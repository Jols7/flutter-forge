---
name: forge-profile
description: Set up flutter-forge in a Flutter project. It detects the stack and architecture (state management, DI, router, HTTP, codegen, l10n pipeline, flavors, tests), asks whether to adopt, improve or migrate the existing architecture, and writes .flutter-forge/profile.yaml plus layer rules. For new projects it bootstraps the Clean core. Use it the first time flutter-forge runs in a repo, whenever .flutter-forge/profile.yaml is missing or outdated, or when the user asks to configure, initialize or re-detect the project. Spanish triggers include "configura flutter-forge", "inicializa el perfil", "detecta la arquitectura", "adapta el agente a este proyecto" and "proyecto nuevo de Flutter".
---

# forge-profile

Writes the one file every other forge skill reads: `.flutter-forge/profile.yaml`. The schema,
with defaults and a commented template, is in `references/profile-schema.md`.

## Step 0 — Resolve

1. Confirm you are at a Flutter project root (`pubspec.yaml` with a `flutter:` section). In a
   monorepo, ask which package, or take it from the orchestrator brief.
2. If `.flutter-forge/profile.yaml` already exists, read it and switch to **update mode**: only
   re-detect, show the diff, and migrate `schema` if it is older. Never overwrite the person's
   edits silently.
3. If `.flutter-forge/overlays/forge-profile.md` exists, read it; its rules win.

## Step 1 — Detect (read-only)

```bash
python3 <this skill dir>/scripts/detect_project.py <project root> --pretty
```

The JSON report contains:
- dependencies grouped by role, and `state_primary_in_code` (what the code actually uses,
  which may differ from what `pubspec` declares);
- the architecture guess, with evidence and confidence;
- features, flavors, l10n pipeline and test setup;
- `conventions_signals`, i.e. counts of patterns such as a service locator inside state
  managers, a manual auth header, or thrown strings.

Then confirm the guess by opening **one** representative feature end to end: page → state
→ repository → API/data source → DTO. The script finds structure; only reading code shows
conventions. Choose the feature with the most layers present, and propose it as
`canonical_feature`.

## Step 2 — Decide (one round of questions)

Show a short summary of the detected stack, architecture and evidence. Then ask **in a single
message** only what the detection could not settle:

| Situation | Ask |
|---|---|
| Existing project (`is_new_project: false`) | **Mode:** `adopt` (keep as is) · `improve` (keep layout, raise quality in new code) · `migrate` (new features in Clean). Recommend `improve` when `conventions_signals` show untestable patterns; otherwise `adopt` |
| New project | State manager (`bloc` · `riverpod` · `provider`), router (default `go_router`), locales |
| Several state packages, or code differs from pubspec | Which one new code must use |
| `security.level` | `high` for finance, health, identity or payments apps, otherwise `standard` |
| API sources | Where the Postman collection / OpenAPI lives, or a Postman cloud collection UID |
| Requirement sources | Where user stories live (files, Drive, Jira…) and their language |

Do not ask about anything the detection already answered with high confidence.

**Unattended mode.** There is nobody to ask. Use `adopt` for existing projects, and the brief's
preferences or `clean` + `bloc` for new ones. Record every assumption under `# assumed:`
comments in the profile and in the run's open questions.

## Step 3 — Write `.flutter-forge/`

1. **`profile.yaml`.** Start from the template in `references/profile-schema.md`. Fill it from the detection
   and the answers. Delete keys that only repeat the default. Keep the comments that explain
   non-obvious values.
2. **`layers.json`.** Needed in two cases: the preset is `layered`/`custom`, or the paths differ
   from the preset's (for example `lib/screens/**` instead of `lib/features/**`). Follow
   `references/layers-mapping.md`: copy the closest preset from
   `../forge-architecture/presets/` and rewrite only `paths`/`features_root`. Then check it in
   report-only mode:
   ```bash
   python3 <this skill dir>/../forge-audit/scripts/check_layers.py --root <project> --rules .flutter-forge/layers.json --summary
   ```
   In `adopt` mode an existing codebase must come out mostly clean against its own rules. If
   it shows hundreds of violations, the mapping is wrong, not the code. Fix the mapping, or
   move recurring legitimate exceptions into `allowed_imports`.
3. **Overlays.** Do not write any here. List the project conventions you saw that differ from
   the skills' defaults, such as a manual `Authorization` header, a custom scaffold widget, a
   provider created at the push callsite, or the intl_utils pipeline. Offer to record them
   with `forge-learn`, one overlay per affected skill.
4. **`.gitignore`.** Add `patrol_test/test_env.json` (or the configured credentials file). Ask
   whether `.flutter-forge/runs/` should be committed (traceability) or ignored.

## Step 4 — New projects only

Follow `../forge-architecture/references/core-bootstrap.md`. Before you add packages or
create `core/`, list exactly what you will create and ask for confirmation (interactive mode).
Add packages with `flutter pub add` and never write versions from memory. Then run the
profile's analyze command.

## Step 5 — CLAUDE.md

- **Missing.** Create one from `references/claude-md-template.md`: about 60–90 lines with
  commands, a one-paragraph architecture, unique gotchas and a pointer to `.flutter-forge/`.
- **Exists.** Propose adding only the `## flutter-forge` pointer section (4 lines). Ask before
  editing. If the file is longer than ~150 lines, or repeats content that now lives in the
  profile or overlays, report it as a suggestion with the duplicated sections named. Do not
  rewrite it unless the person asks.

## Step 6 — Validate

- Required keys exist, enum values are valid, and every path exists (except planned paths in
  `mode: new`).
- `sdk.flutter_command --version` runs, and the analyze command runs.
- No secrets in the profile: no tokens, keys or real hosts. Only *where* each one lives.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Assume Clean for an existing app | Detect, then ask adopt/improve/migrate | Migrating someone's architecture is their decision |
| Trust pubspec alone for state management | Use `state_primary_in_code` + reading one feature | Packages get added and abandoned |
| Write overlays from guesses | Propose them; record with `forge-learn` after confirmation | A wrong overlay silently corrupts every run |
| Copy a preset's `layers.json` unchanged onto a project with other paths | Rewrite `paths` to the real folders | Otherwise every file is "unclassified" |
| Rewrite the project's CLAUDE.md | Add a pointer section; suggest slimming | The file belongs to the team |
| Store the Postman API key or base URLs in the profile | Store where they live (`env POSTMAN_API_KEY`) | The profile is committed |

## Finish

Report in this order:
1. The detected stack.
2. The chosen mode, preset and state manager.
3. Files written.
4. The `check_layers` summary.
5. Proposed overlays.
6. CLAUDE.md suggestions.
7. Assumptions, in unattended mode.

When `forge-deliver` invoked this skill, return control to it.
