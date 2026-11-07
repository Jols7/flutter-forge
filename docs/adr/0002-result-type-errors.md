# ADR 0002 — A home-grown sealed `Result<T>` with a sealed `AppFailure`

- Status: accepted
- Date: 2026-11-06

## Context

Expected failures (offline, 401, validation, business codes) must reach the UI with their
type intact, so the UI can show the right message and the right action. These alternatives
were considered and rejected:

| Alternative | Why it was rejected |
|---|---|
| Throwing strings | Loses the type and couples the repositories to UI copy |
| `fpdart`'s `Either` | Adds a functional-programming dependency and vocabulary to every project |
| Typed exceptions alone | The compiler does not force callers to handle them |

## Decision

Dart 3 sealed classes, generated into each project's `lib/core/error/` (code in
`forge-architecture/references/result-and-failures.md`):
- `Result<T> = Success<T> | Failure<T>(AppFailure)`.
- `AppFailure` is a sealed family. `BusinessFailure(code)` carries feature-specific errors.
- Data sources throw. Repositories translate with one `guard()` helper.
- Presentation switches exhaustively, and widgets map each failure to localized copy.

## Consequences

- There are no new dependencies, and `switch` is exhaustive at compile time.
- Feature-specific failures go through `BusinessFailure.code`, not new subclasses, so that
  exhaustiveness holds.
- Projects in `adopt` mode keep their legacy convention (`errors: legacy`). In `improve` mode,
  new methods return `Result` and existing call sites stay as they are.
