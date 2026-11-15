# ADR 0004 — Reference architectures: what flutter-forge takes and what it leaves

- Status: accepted
- Date: 2026-11-14

## Context

flutter-forge's `clean` preset (feature-first Clean Architecture, BLoC/Cubit by default) was
written from experience. Before hardening it we compared it with four outside references, to
find conventions worth adopting and to check that the preset stands up to them.

| Reference | What it is |
|---|---|
| [`bmoraa16/test_valtre`](https://deepwiki.com/bmoraa16/test_valtre/1-overview) | A Pokémon catalog app: feature-first `domain/data/presentation`, `get_it` + `injectable`, `go_router`, `flutter_bloc`. Only a generated DeepWiki analysis (indexed 21 May 2025) is available, not the repository |
| [Flutter app architecture guide](https://docs.flutter.dev/app-architecture/guide) | UI layer (views + view models) and data layer (repositories + services); a domain layer is optional |
| [Very Good Ventures layered architecture](https://engineering.verygood.ventures/architecture) | Data → repository → business logic (bloc) → presentation, one-way, no skipped layers, repositories isolated |
| [VGV feature-first clean architecture](https://verygood.ventures/blog/feature-first-clean-architecture/) | The same ideas packaged per feature |

## Findings on `test_valtre`

It is a reasonable *demo*, but not a base for a preset:
- The analysis contradicts itself: the overview lists `dartz` and the domain/data pages say
  `multiple_result`; use cases are named `GetPokemonListUseCase` in one place and
  `GetPokemonListTokenUseCase` in another.
- A single `@singleton` bloc owns list loading, N+1 detail fetches, search, sort and pagination.
  Singleton state managers go stale when a screen is reopened (`di.md` anti-patterns).
- Use cases only forward one repository call.
- Route builders resolve from `get_it` and pass entities through `extra`, which the wiki calls
  "type-safe".
- No tests, no layer rules, hardcoded URLs, a class of fixed UI strings instead of l10n.

## Decision

Keep the `clean` preset as the base. Do **not** add presets for valtre, VGV or the official guide:
each would be a third thing to maintain and evaluate, and `layered` already covers apps that do
not follow Clean. Instead:

| Taken | From | Where it lives |
|---|---|---|
| Typed asset constants in `core/constants/` | valtre (`AppAssets`) | `conventions.md` §1, `core_constants` layer |
| Mapper naming mirrors the project | valtre (`toDomain`) | `naming.mapper_method` in the profile |
| Shell for tabs, router-driven app start | valtre had cubits for both; the pattern is go_router's | `page-patterns.md` |
| Repositories isolated, one-way flow | VGV | `conventions.md` §3, audit checklist |
| Services/data sources private to their repository; view ↔ view-model 1:1 | Flutter guide | `conventions.md` §4–5 |
| A closed service-locator layer (`composition_di`) | Our own audit, after reading valtre's `getIt` in router builders | `clean.layers.json` |

| Left | Why |
|---|---|
| `dartz` / `multiple_result` | ADR 0002: a sealed `Result<T>` adds no dependency |
| Singleton blocs, use-case-per-call, `execute()` | See above |
| `AppDictionary` of strings | l10n (`forge-l10n`) |
| A mandatory domain layer vs. optional (Flutter guide) | `clean` keeps the contract in `domain` and makes use cases optional; `layered` is the no-domain option |

## Consequences

- Existing projects are untouched: every new convention is optional, and a project's own
  `layers.json` is not rewritten.
- The preset gains a closed `composition_di` layer. A project that resolves `get_it` from
  widgets will now see violations in `check_layers`; `adopt` mode lists them as debt, never as a
  blocker. Riverpod projects get the layer opened by `forge-profile`.
- If valtre's repository becomes available, its tree can be checked read-only with
  `check_layers.py --summary` against both presets, instead of relying on the wiki.
