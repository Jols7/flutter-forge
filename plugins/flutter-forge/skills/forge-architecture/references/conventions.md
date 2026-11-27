# Conventions

Small rules that every preset shares. They come from three sources: this plugin's own audits,
the official Flutter app-architecture guide and Very Good Ventures' layered architecture. Each
rule says whether the checker enforces it or the audit reads for it. The reasoning for choosing
them is in `docs/adr/0004-reference-architectures.md`.

## 1. Constants and assets (`core/constants/`)

- **Asset paths** live in one `abstract final class AppAssets` with `static const String` fields:
  `AppAssets.emptyAccounts`, never `'assets/images/empty.svg'` in a widget. A typo then fails at
  compile time, and `forge-figma` has one place to register exported assets.
- **Constants are pure.** No widgets, no Dio, no `get_it` (the `core_constants` layer forbids
  them). Anything that depends on the environment (base URL, flavor, mocks) is `AppConfig` /
  `MockConfig`, built from `--dart-define`. It is not a constants file.
- **Texts are not constants.** User-facing strings go through l10n (`forge-l10n`), not a class of
  `static const` labels. A constants class of labels cannot be translated.
- **Route names** stay with the router (`core/router/`), typed, next to the route definitions.
- Enforced by: `check_layers.py` (`core_constants` layer, `unclassified-target` report).

## 2. Mapper naming

- New code names the DTO → entity extension method `toEntity()` and the reverse `toDto()`.
- In `adopt`/`improve`, mirror the project: `forge-profile` stores what it found in
  `naming.mapper_method` (`toDomain`, `toModel`), and `forge-data-layer` uses it. A second name
  in the same codebase is worse than a name this plugin would not have chosen.

## 3. Repositories stay isolated

- A repository talks to its own data sources. It never calls another repository.
- Work that needs two repositories is a **use case** (or, for one screen, the state manager) that
  receives both contracts and combines their `Result`s. That is the "earned use case" rule in
  `SKILL.md`.
- Why: a repository that depends on another one turns a per-resource boundary into a chain, and
  tests need the whole chain.
- Enforced by: `forge-audit` checklist (design lenses), not by `check_layers.py`.

## 4. Data sources are private to their repository

- A data source wraps one external API or store, holds no state and has no side effects beyond the
  call. Only the repository implementation of the same feature uses it. Presentation and use cases
  never receive a data source.
- Enforced by: the `presentation → data` ban in `check_layers.py`.

## 5. One state manager per screen

- A page has one view model: a Cubit/Bloc, a Notifier or a ChangeNotifier. It is created in the
  route, not shared across routes through a singleton (`di.md` anti-patterns).
- Shared state across screens (the signed-in user, the cart) is a **domain concept** exposed by a
  repository stream, not a state manager that other state managers import.

## 6. Bottom navigation and shells

Use `StatefulShellRoute.indexedStack` (go_router) for tabs: each tab keeps its own navigation
stack and the shell owns the selected index. Do **not** keep the selected tab in a Cubit that
widgets must also update. Details and a template: `forge-presentation/references/page-patterns.md`
§ Shell.

## 7. App start

The first screen is decided by a `redirect` on the router, reading an auth/bootstrap state
that `bootstrap.dart` initialises before `runApp`. A splash screen is a page that shows while that
state is `unknown`. It is not a cubit that navigates. Details: `page-patterns.md` § App start.

## 8. Naming of classes the plugin generates

| Kind | Rule |
|---|---|
| Use case | Verb + noun, callable: `CreateTransfer` (not `CreateTransferUseCase`, not `execute()`) |
| Repository contract / impl | `XRepository` / `XRepositoryImpl` |
| State | `XState` sealed; subtypes `XLoading`, `XLoaded`, `XFailure` |
| Sub-status inside a state | its own sealed type (`LoadMore`), never two flags |

## 9. Test keys (BIT-012, ADR 0011)

The single source for keys that tests find widgets by. Other skills link here and do not repeat it.
Keys are independent of the `a11y` switch.

- **Who gets one.** Elements a flow interacts with or checks (action buttons, fields, tabs, list
  items) and the container of each sealed state (loading, error, empty, content). Not every widget.
- **Name.** `snake_case`, `<screen>_<element>`; list items `<screen>_item_<id>`. Never personal or
  sensitive data in a name (MASVS).
- **Declared once per feature**, in `presentation/<feature>_keys.dart`:

  ```dart
  abstract final class TransferKeys {
    static const submit = Key('transfer_submit');
    static const amount = Key('transfer_amount');
    static Key item(String id) => Key('transfer_item_$id');
  }
  ```

  The page, the widget tests and Patrol all use the constant: `key: TransferKeys.submit`,
  `find.byKey(TransferKeys.submit)`, `$(TransferKeys.submit)`. No `GlobalKey` for tests.
- **Declared upstream.** The blueprint lists them (Widgets table, "Test keys" column) and
  `forge-presentation` emits and applies them. `forge-e2e` and `forge-tests` only consume them: a
  missing key is a **finding in the report**, never an edit to production code.
