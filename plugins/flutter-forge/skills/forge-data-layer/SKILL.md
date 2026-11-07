---
name: forge-data-layer
description: Implement the domain and data layers of a Flutter feature from its blueprint and API contract. That covers entities, repository contracts, earned use cases, DTOs (json_serializable or freezed), mappers, remote and local data sources over Dio, repository implementations returning Result/AppFailure, pagination, idempotency, and a mock-first interceptor for endpoints that are not ready. It follows the profile's preset (clean or layered) and the project's overlays. Use it when the user asks to consume or integrate an endpoint, create or change a DTO, model or repository, add a field to a response, fix a parsing error, wire a mock for an endpoint that does not exist yet, or says "conecta el endpoint", "crea el repositorio", "agrega el DTO", "intégralo"; and when forge-deliver reaches implementation.
---

# forge-data-layer

Everything below presentation: entities, contracts, DTOs, mappers, data sources and
repositories. Presentation only ever sees entities and `Result`.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`. Load `forge-architecture`, its preset reference and
   `references/result-and-failures.md` when `errors: result`.
2. Read the run's `blueprint.md` (file plan, contract signatures, value trace) and `contract.md`
   with its fixtures. Without a blueprint, make a mini-plan with the same tables and show it first.
3. In `adopt`/`improve`, open the canonical feature's data source, repository, DTO and mapper.
   Mirror their shapes: constructor style, HTTP client wrapper, how auth is attached and file
   locations.
4. If `.flutter-forge/overlays/forge-data-layer.md` exists, read it; its rules win. A typical
   example is a project that attaches the auth header per request instead of in an interceptor.

## Step 1 — Core, once per project

Check that these pieces from `forge-architecture/references/core-bootstrap.md` exist: the
`core/error` files, `dio_failure_mapper.dart`, `guard()`, the API client with its interceptors,
and the mock interceptor. Create only the missing ones. In `adopt` mode, use the project's
equivalents and don't add a parallel stack.

## Step 2 — Implement in this order

Follow `references/templates.md`. Each item is a separate file:

1. **Entities.** Fields come from the value trace, with UI-ready types. Use `const`
   constructors, `final` fields, value equality when state compares them, and derived getters
   for UI logic (`isDebit`).
2. **Repository contract.** Use `abstract interface class` with the blueprint's signatures,
   returning `Future<Result<T>>`.
3. **Use cases**, only when the blueprint lists them. They are callable classes that receive
   the contract.
4. **DTOs.** Mirror the JSON exactly (rules in `references/dto-rules.md`). Run the profile's
   `serialization.build_command`.
5. **Mappers.** Use extensions: `toEntity()` and `toDto()`. They do all conversions, defaults
   and sorting. Use the fixtures to verify them.
6. **Data source.** One method per endpoint, returning DTOs. It uses relative paths,
   percent-encodes path parameters, passes `CancelToken`, and sends idempotency headers on
   writes when the contract asks for them. It throws and never catches.
7. **Repository implementation.** `guard(() async => (await remote.x()).toEntity(),
   businessCodes: …)`. Caching and offline policy go here, as decided in the blueprint.
8. **DI.** Register in the feature module: data source and repository with the contract type
   (`forge-architecture/references/di.md`).
9. **Mocks** for every endpoint with `status: mock-agreed` or `gap`, plus a dev toggle (see
   `references/mock-interceptor.md`). List each mocked route in the run report.

## Step 3 — Verify

```bash
<serialization.build_command>              # if DTOs changed
<quality.analyze_command>
```

Mapper and repository tests are written by `forge-tests`. When this skill runs alone, offer
to run it next.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Return DTOs, `Response` or `Map` from a repository | Return `Result<Entity>` | DTOs never cross the repository |
| `try { … } catch (e) { rethrow; }` in data sources | No try/catch in data sources | It adds nothing; `guard` translates once |
| Copy the `on DioException` block into every repository method | `guard()` | One translation point; consistent failures |
| `throw 'Error'` / return `false` on failure | Return a typed `AppFailure` | The UI needs the type to choose the message and action |
| Parse `response.data['x']` outside DTOs | DTO `fromJson` + mapper | Parsing lives in one typed place |
| Non-nullable DTO fields for values that can be null or absent | Nullable + default in mapper | Prevents `Null is not a subtype` crashes |
| `int` for money | `num` in DTO → `double`/decimal in entity | `500.5` breaks `int` parsing |
| `'accounts/$id'` with raw user input | `'accounts/${Uri.encodeComponent(id)}'` | Path injection / broken URLs |
| `'/accounts'` or a full URL in a data source | `'accounts'`; base URL from config | Flavor-specific hosts live in config |
| Mock logic in repositories (`if (useMocks) return fake`) | Mock interceptor at the HTTP layer | Everything above the client stays final code |
| Mocks enabled by a runtime flag in release builds | `const bool.fromEnvironment('USE_MOCKS')` + assert not prod | Tree-shaken out of release; never a silent fake |
| Hand-editing `*.g.dart` | Change the DTO and rerun the build command | Generated files are overwritten |

## Finish

- Build and analyze must pass.
- Update `state.json` with the files written.
- Report:
  - entities, contracts, DTOs, mappers, data sources and repositories created or modified;
  - the DI registrations;
  - every mocked route;
  - every field made nullable because of an unclear contract.
