# CLAUDE.md template (60–90 lines)

`CLAUDE.md` loads into **every** session, so it holds only what every session needs.
Conventions with code go in overlays, and values go in the profile. Fill the `<…>` and delete
any section that does not apply.

````markdown
# CLAUDE.md

<App name> — <one sentence: what the product does and for whom>. Flutter <version> (<fvm?>),
flavors <dev/qa/prod or none>.

## Commands

```bash
<flutter_command> pub get
<flutter_command> run -t <entrypoint> --flavor <flavor_id>
<flutter_command> analyze
<flutter_command> test
<build_command>                        # after editing DTOs / injectable / freezed
<l10n generate_command>                # after editing ARB files
patrol test -t patrol_test/flows/<flow>_test.dart --flavor <dev flavor>
```

## Architecture (one paragraph)

<preset> architecture with <state manager>, <DI>, <router>. Features live in <features path>;
each one has <layers>. Data flows <UI → state → repository contract → data source>. Errors are
<Result/AppFailure | convention>. Details, paths and rules: `.flutter-forge/profile.yaml`,
`.flutter-forge/layers.json`, `.flutter-forge/overlays/`.

## Gotchas

<Only facts that are surprising AND not enforced by a tool. One line each, with the file.>
- <e.g. The auth interceptor forces logout on 401 — `lib/core/network/interceptors/auth_interceptor.dart`.>

## flutter-forge

This project is configured for the flutter-forge plugin. Skills read `.flutter-forge/profile.yaml`
and the overlays in `.flutter-forge/overlays/`. To deliver a feature, use `forge-deliver`. To
record a new convention, use `forge-learn` (do not add code conventions here).
````

## What does NOT belong in CLAUDE.md

| Content | Where it goes |
|---|---|
| Code samples of conventions (how a page/provider is written) | `overlays/forge-presentation.md` |
| Tables of paths, class names, flavors | `profile.yaml` |
| Rules a linter or `check_layers.py` already enforces | nowhere (the tool enforces them) |
| The same rule stated in several sections | once, in the most specific place |
| Instructions for a specific skill (e.g. Patrol recovery) | that skill's overlay |
