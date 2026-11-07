---
name: forge-architecture
description: Shared architecture reference for flutter-forge. It defines the Clean and Layered presets for BLoC/Cubit, Riverpod and Provider; folder layout; layer and import rules (layers.json); naming; dependency injection wiring; and the Result/AppFailure error model. Other forge skills load it before they design, generate or audit code. Use it directly when the user asks about the project's architecture, the folder structure for a feature, where a class belongs, how layers may depend on each other, how to model errors, or how to migrate to Clean Architecture. Spanish triggers include "estructura de carpetas", "arquitectura limpia", "dónde va esta clase", "capas" and "patrón repositorio".
---

# forge-architecture

This skill holds the architecture knowledge that every other forge skill relies on. It writes no
feature code itself. It says **where** things go and **what may depend on what**.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml` (schema: `../forge-profile/references/profile-schema.md`). Take these keys from it:
   - `architecture.preset`
   - `architecture.state`
   - `architecture.di`
   - `architecture.router`
   - `architecture.errors`
   - `architecture.use_cases`
   - `architecture.mode`
2. If there is no profile, stop and run `forge-profile` first. Never assume a preset for an
   existing project.
3. Read **only** the reference for the preset in use:
   - `references/preset-clean.md`, or
   - `references/preset-layered.md`, or
   - for `custom`, the project's `.flutter-forge/layers.json` plus the closest preset.
4. Read `references/di.md` only when you are about to register or resolve dependencies.
   State-manager templates live in `forge-presentation`, not here.
5. If `.flutter-forge/overlays/forge-architecture.md` exists, read it. Its rules win over this file.

## Presets at a glance

| | `clean` (default for new code) | `layered` (existing apps) |
|---|---|---|
| Layers | domain · data · presentation · core · composition | api · dtos/mappers · repositories · models · presentation · core |
| Repository | abstract contract in `domain/`, implementation in `data/` | one concrete class in `data/repositories/` |
| Errors | `Result<T>` with a sealed `AppFailure` | project's own convention (`legacy`); `improve` mode wraps it |
| Use cases | `optional`: only when they hold logic (see below) | none |
| Machine rules | `presets/clean.layers.json` | `presets/layered.layers.json` |

The dependency rule always points inward: **presentation → domain ← data**. Only composition
(DI setup, router, `main*.dart`) may see every layer.

## Where does a class go? (clean)

| Class | Layer / path | Name |
|---|---|---|
| Business object used by UI and logic | `features/<f>/domain/entities/` | `Transaction` |
| Repository contract | `features/<f>/domain/repositories/` | `TransactionsRepository` (`abstract interface class`) |
| Use case (earned, see rule) | `features/<f>/domain/usecases/` | `CreateTransfer` (callable `call`) |
| HTTP calls for one resource | `features/<f>/data/datasources/` | `TransactionsRemoteDataSource` |
| Local cache / storage | `features/<f>/data/datasources/` | `TransactionsLocalDataSource` |
| Wire format | `features/<f>/data/models/` | `TransactionDto`, `CreateTransferRequestDto` |
| DTO ⇄ entity conversion | `features/<f>/data/mappers/` | `extension TransactionDtoMapper on TransactionDto` |
| Repository implementation | `features/<f>/data/repositories/` | `TransactionsRepositoryImpl` |
| Screen state + logic | `features/<f>/presentation/state/` | `TransactionsCubit`/`TransactionsState`, `TransactionsNotifier`, `TransactionsViewModel` |
| Route-level widget | `features/<f>/presentation/pages/` | `TransactionsPage` |
| Feature-local widget | `features/<f>/presentation/widgets/` | `TransactionTile` |
| Widget reused by 2+ features | `core/widgets/<group>/` | `AppPrimaryButton` |
| DI registrations of a feature | `features/<f>/di/` | `transactions_module.dart` |

`references/preset-clean.md` has the full tree. It also explains the per-state-manager variations.

## Use cases: when they are earned

Pass-through use cases add files and nothing else. With `use_cases: optional`, create one only
when **at least one** of these holds:
- It combines two or more repositories.
- It holds a business rule that the UI must not own, such as limits, eligibility or computed totals.
- More than one state manager reuses it.
- It is a write operation that has preconditions.

Otherwise the state manager calls the repository contract directly. With `required`, always
create one. With `none`, never create one.

## Errors: `Result<T>` + `AppFailure`

`references/result-and-failures.md` contains the Dart code to create in `core/error/`, the Dio
mapper and the rules:
- Data sources throw.
- Repositories catch, map and return `Result<T>`.
- Presentation switches on the result and maps each `AppFailure` to localized text in the widget
  layer.
- Strings are never thrown, and `catch (e)` never swallows an error without mapping it.

## Modes (from the profile)

| Mode | Rule |
|---|---|
| `new` | Create `core/` from `references/core-bootstrap.md` before the first feature |
| `adopt` | Mirror `project.canonical_feature`; the project's `layers.json` is the law |
| `improve` | Same layout; new code adds typed errors, injectable constructors and sealed states behind existing APIs; no call site breaks |
| `migrate` | New features use `clean`; legacy features stay unless the run includes them |

## Dependency injection

`references/di.md` covers each container:
- `get_it` (manual or `injectable`)
- Riverpod providers
- `provider` (`MultiProvider`/`ChangeNotifierProvider`)
- manual constructors

Every container follows one rule: **classes receive their dependencies through the
constructor.** Only composition resolves them. That is what makes every class testable with
mocktail.

## Code comments

Code that the forge skills generate follows `references/code-comments.md`: the code says
*what*, a comment says *why*. Typical comments are rule references (`// AC-4 (HU-12): …`),
links to workarounds, `///` on domain contracts and `TODO(#issue)`. The audit checks it
(`forge-audit` checklist §14 and `scripts/check_comments.py`).

## Output

When another skill loads this one, it needs nothing back. When the user asks directly, answer
with these items:
- the relevant part of the tree;
- the layer and name of each class in question;
- the import rule that applies;
- for a refactor, the minimal sequence of moves that keeps the build green.
