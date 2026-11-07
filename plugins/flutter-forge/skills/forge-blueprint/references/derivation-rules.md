# Derivation rules

## State managers

- **One per screen** is the default.
- **One per flow** applies when several screens edit the same draft, as in a multi-step form.
  The state manager is scoped to the flow's route subtree: a `ShellRoute` in go_router, or a
  provider above the nested navigator.
- **Split** a state manager when two regions load independently and can fail independently,
  for example a list plus a preview card. Either use two state managers, or one state with two
  sealed sub-states. Never share one `isLoading` between them.
- State has no `BuildContext`, no widgets and no localized strings. It exposes data, sealed
  statuses, `AppFailure`s and validation enums. Widgets turn these into text.
- **Side effects** are modeled explicitly, not hidden in `build`: navigate on success, show a
  snackbar, open a confirmation. Use the preset's mechanism:
  - bloc: `BlocListener`;
  - riverpod: `ref.listen`;
  - provider: a one-shot event the page consumes.

## Non-functional rules → state design

| Rule in the brief | Design |
|---|---|
| "Optimistic UI" / "instant feedback" | Compute locally first (validation, derived values); the server confirms |
| "No flicker" / "loading only if slow" | Delayed loading flag (~250 ms) |
| Search / live calculation | Debounce (~300 ms) + discard stale responses (request id or `CancelToken`) |
| "Unlimited retry" | Retry action in the failed region only; inputs stay interactive |
| Limited retries / lockout | Counter in state; disable + message on limit; server is the source of truth |
| Pagination | `Page<T>` from repository; state holds items + `nextPage` + `isLoadingMore` + `loadMoreFailure` |
| Pull to refresh | Keeps current data visible while refreshing; replaces on success |

## Domain

- **Entities** are business concepts with the types the UI needs, such as `DateTime`, enums,
  `double` money (or a `Money` value object when currencies mix) and non-null defaults.
  Entities are immutable (`final` fields, `const` constructors) and have value equality when
  state comparisons need it: `==`/`hashCode`, `equatable`, or `freezed` if the profile uses it.
- **Value objects** model validated inputs (`TransferAmount.parse(raw) → Result`) when the
  same rule is used in several places.
- **Repository contract** methods are named after intent (`getTransactions`, `createTransfer`),
  return `Future<Result<T>>`, and take typed parameters, never `Map`.
- **Use cases** are created only when earned (rule in `forge-architecture`). When one exists,
  it is the only thing the state manager calls for that operation.

## Data

- **One data source per backend resource.** It has one method per endpoint, returns DTOs and
  throws transport exceptions.
- **One DTO per JSON object shape.** Nested objects get their own DTO class in the same file
  when they are used only there. Request bodies get request DTOs.
- **Envelope.** A generic wrapper DTO (`DataEnvelopeDto<T>`) when the shape is shared. The
  mapper unwraps it, so entities never see the envelope.
- **Mappers** are extensions with `toEntity()` / `toDto()`. They do all conversion, defaulting
  and sorting, and contain no I/O.
- **Repository implementation:** `guard(() => …)` + mapper. It is also where caching and
  idempotency keys go, when the contract requires them.

## Presentation and widgets

- Pages are route-level and contain no business logic. They read state and dispatch intents.
- For each component in `design.md`, record its reuse-ladder decision: **reuse** (path),
  **extend** (path + new optional parameter), or **create**. Create it in the feature's
  `widgets/` when only this flow uses it, or in `paths.shared_widgets` when it is reusable,
  and add it to the catalog.
- Each region that reacts to a state gets a small widget, and each state variant maps to one
  branch of an exhaustive `switch`.

## Naming

Always use the active preset's naming table. In `adopt`/`improve`, use the canonical feature's
naming even when it differs: consistency inside a project beats the generic convention.
