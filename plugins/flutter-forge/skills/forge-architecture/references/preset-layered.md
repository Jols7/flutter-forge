# Preset `layered`

This preset covers the three tiers many production apps already use:
`Api → Repository → state manager → UI`. The domain layer has no contracts. It exists so
`adopt` and `improve` can respect such apps without migrating them.
Machine rules: `../presets/layered.layers.json`.

Real projects rarely use these exact paths. `forge-profile` writes `.flutter-forge/layers.json`
that maps the project's real folders (e.g. `lib/screens/**` → `presentation`) onto these layer names.

## Default tree

```
lib/
├── core/ (network, error, storage, config, theme, utils)
├── models/<feature>/<name>_model.dart          # what the UI consumes
├── data/
│   ├── api/<feature>_api.dart                  # one method per endpoint
│   ├── dtos/<feature>/<name>_dto.dart (+ .g.dart)
│   ├── mappers/<feature>/<name>_mapper.dart
│   └── repositories/<feature>_repository.dart  # concrete; returns models
└── features/<feature>/
    ├── pages/
    ├── state/                                  # provider / bloc / notifier
    └── widgets/
```

## Rules kept from Clean (non-negotiable even in `adopt`)

1. DTOs never cross above the repository. The repository maps them to models.
2. Parsing happens once, in DTO + mapper, never in state managers or widgets.
3. The repository translates transport errors. The UI never sees `DioException`.
4. Each request has its own loading and error state. One error must not hide data that is
   already loaded.
5. Controllers, timers and streams are disposed by whoever created them.

## `improve` mode upgrades (applied to new code without breaking old call sites)

| Legacy pattern | Upgrade in new code | Compatibility trick |
|---|---|---|
| Repository throws `String` | New methods return `Result<T>` | Keep the old method; mark it `@Deprecated('Use xResult')` only if the team agrees |
| Service locator inside the state manager | Constructor parameters with defaults that resolve from the locator | `XViewModel({XRepository? repo}) : _repo = repo ?? getIt<XRepository>()` keeps existing callers and makes tests possible |
| Token passed from UI to every Api method | Auth interceptor, if the project agrees. Otherwise keep it, but read the token in the repository | Record the decision in the overlay |
| Boolean flags for state | Sealed state for new screens | Existing screens untouched |
| `try { … } catch (e) { rethrow; }` | Remove; it adds nothing | Pure refactor, safe |
| Localization accessed from state (`S.current`) | State exposes failures/enums; widgets resolve text | New screens only |

Every upgrade is listed in the run report under **Improvements applied**, so reviewers see
them as intentional.
