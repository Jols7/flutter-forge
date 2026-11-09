# Project profile — `.flutter-forge/profile.yaml`

Every flutter-forge skill reads this file in its Step 0 instead of guessing project values.
`forge-profile` creates it (detection + one round of questions); people edit it by hand
afterwards. It is the **only** place where project-specific values live: skills never hardcode
package names, paths or class names.

```
<flutter project>/
└── .flutter-forge/
    ├── profile.yaml          # this schema (required)
    ├── layers.json           # optional: layer rules when paths differ from the preset
    ├── overlays/<skill>.md   # optional: project rules that extend or replace a skill (forge-learn/references/overlays.md)
    ├── templates/            # optional: hu.md, report.md… replacing the defaults
    └── runs/<feature-slug>/  # state of each forge-deliver run (gitignore it or commit it: your call)
```

## Precedence

`explicit user request` > `overlays/<skill>.md` > `profile.yaml` > architecture preset > skill default.

## Schema (version 1)

Keys marked *(req)* must exist. Everything else falls back to the default shown.

```yaml
schema: 1                                  # (req) bump only on breaking changes

project:
  name: forge_demo                         # (req) human name
  package: forge_demo                      # (req) pubspec `name:`
  domain: personal finance                 # one line: helps requirement and security skills
  canonical_feature: transactions          # feature to mirror when generating code (adopt/improve)

sdk:
  flutter_command: flutter                 # "fvm flutter" when the repo pins an SDK with fvm
  dart_command: dart                       # "fvm dart"

architecture:
  preset: clean                            # (req) clean | layered | custom
  mode: new                                # (req) new | adopt | improve | migrate (see below)
  state: bloc                              # (req) bloc | riverpod | provider
  di: get_it                               # get_it | injectable | riverpod | provider | manual
  router: go_router                        # go_router | auto_route | navigator
  errors: result                           # result | exceptions | legacy
  use_cases: optional                      # required | optional | none
  ui_helpers: allow                        # allow | forbid  — private _buildX() methods in widgets
  layers_file: null                        # path to a custom layers.json (null = preset rules)

paths:                                     # relative to the project root
  features: lib/features
  core: lib/core
  shared_widgets: lib/core/widgets
  widgets_barrel: null                     # e.g. lib/core/widgets/widgets.dart
  di_setup: lib/core/di/injection.dart
  router: lib/core/router/app_router.dart
  error: lib/core/error                    # result.dart + app_failure.dart

networking:
  http: dio                                # dio | http
  client: lib/core/network/api_client.dart
  auth: interceptor                        # interceptor | manual-header | none
  error_message_key: message               # JSON key with the server's user-facing message
  envelope: null                           # e.g. {data: content, message: detail} when responses are wrapped
  base_url: dart-define                    # dart-define | dotenv | flavor-config
  mocks: interceptor                       # interceptor | none

serialization:
  codegen: json_serializable               # json_serializable | freezed | manual
  build_command: dart run build_runner build --delete-conflicting-outputs

l10n:
  pipeline: gen-l10n                       # gen-l10n | intl_utils | none
  arb_dir: lib/l10n
  template_locale: en
  locales: [en, es]
  accessor: AppLocalizations.of(context)   # S.of(context) for intl_utils
  generate_command: flutter gen-l10n

design:
  figma: true
  colors: Theme.of(context).colorScheme    # or a token class, e.g. AppColors
  typography: Theme.of(context).textTheme
  spacing: null                            # e.g. AppSpacing (lib/core/theme/app_spacing.dart)
  scaffold_widget: null                    # project scaffold to use instead of Scaffold
  widget_catalog: docs/widget-catalog.md

requirements:
  template: default                        # default (hu-v1) | path to a template (.flutter-forge/templates/hu.md);
                                           # a custom one keeps sections 1–10 and the `### <surface>` blocks in §5/§6
  language: es                             # language of user stories and user-facing reports
  sources: [file, paste]                   # file | paste | drive | jira | notion | linear
  index: null                              # where the story index lives (e.g. a sheet name)

api:
  sources:                                 # tried in this order
    - kind: postman-file                   # postman-file | postman-cloud | openapi | paste
      path: api/forge_demo.postman_collection.json
  postman_cli: postman                     # absolute path when the CLI is not on PATH
  contract_dir: docs/api                   # where forge-api-contract writes contract.md + fixtures

testing:
  unit: mocktail                           # mocktail | mockito
  coverage_min: 0.8                        # for new domain/data code
  widget: true
  e2e: patrol                              # patrol | integration_test | none
  e2e_dir: patrol_test
  default_flavor: dev
  forbidden_flavors: [prod]                # e2e never runs against these
  credentials_file: patrol_test/test_env.json   # gitignored; never written by the agent

flavors:
  names: []                                # e.g. [dev, qa, prod]
  entrypoint: lib/main.dart                # or a pattern: lib/main_{flavor}.dart
  flavor_id: null                          # pattern for --flavor, e.g. "{flavor}" or "app{Flavor}"

quality:
  analyze_command: flutter analyze
  format_command: dart format --output=none --set-exit-if-changed lib test
  dcm: false                               # Dart Code Metrics available
  max_build_lines: 120                     # build() size before it is a finding

security:
  level: standard                          # standard (MASVS-L1) | high (L2 + resilience: fintech, health)
  sensitive_data: [credentials, pii]       # credentials | pii | financial | health | location
  pinning: false                           # certificate pinning required by the business
```

## `architecture.mode`

| Mode | When | What the agent does |
|---|---|---|
| `new` | Empty or freshly created project | Creates the preset's structure and `core/` pieces before the first feature |
| `adopt` | Existing project; keep its architecture as is | Mirrors `canonical_feature`; audits **against the project's own rules** (custom `layers.json`); never proposes migrations |
| `improve` | Existing project; keep the architecture but raise quality | Same layout as `adopt`, but new code adds what is missing without breaking existing call sites (typed errors behind the existing API, testable constructors, sealed states). Audit reports gaps as `improvement` findings |
| `migrate` | Existing project moving to Clean | New features use the `clean` preset; old features are untouched unless the run says otherwise; the audit tracks migration debt separately |

`forge-profile` asks which mode to use whenever it detects an existing architecture. The
answer is stored here, and every later run respects it without asking again.

## Validation

`forge-profile` validates the file after writing it. It checks that required keys exist,
enums are valid, paths exist (except when `mode: new`), and commands run. When the schema
changes, `schema` is bumped and `forge-profile` migrates the file in place, reporting what
changed.

## Security

Never store secrets in the profile: no tokens, API keys, passwords or real base URLs.
Write only **where** a secret lives (`env var POSTMAN_API_KEY`, `patrol_test/test_env.json`).
