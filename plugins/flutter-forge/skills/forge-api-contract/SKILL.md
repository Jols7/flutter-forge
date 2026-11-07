---
name: forge-api-contract
description: Build the API contract for a Flutter feature from a Postman collection, either an exported v2.1 JSON, a v3 git-native folder, or a cloud collection through the Postman CLI or MCP. It also accepts an OpenAPI/Swagger spec, or endpoints, JSON or cURL that the user pastes. It lists the endpoints the feature needs and infers request and response schemas (nullability, int vs double, dates). It records auth, pagination, envelope and error shapes, writes redacted JSON fixtures for DTOs, mocks and tests, and reports contract gaps. Use it when the user mentions Postman, a collection, Swagger/OpenAPI, endpoints, "consume este servicio", "conecta con el back", "estos son los endpoints", pastes a JSON response or cURL, or when forge-deliver reaches the contract phase.
---

# forge-api-contract

Output: `contract.md` for the run, plus JSON fixtures. Together they are the only source for
DTOs (`forge-data-layer`), mock routes and test fixtures (`forge-tests`). **The contract comes
from backend artifacts, never from the UI.**

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`:
   - `api.sources`, tried in order;
   - `api.postman_cli`;
   - `api.contract_dir`;
   - `networking.envelope`, `networking.error_message_key` and `networking.auth`.
2. Read the run's `brief.md` when it exists. Its **Data needs** table says which endpoints
   matter. Never extract the whole collection into the run.
3. If `.flutter-forge/overlays/forge-api-contract.md` exists, read it; its rules win.

## Step 1 — Get the source (fallback order)

The details and exact commands are in `references/sources.md`.

1. **Collection file in the repo:** a v2.1 `*.postman_collection.json`, or a v3 folder
   `postman/collections/<name>/`.
2. **Postman cloud.** Use the CLI (`postman collection list --workspace <id> --json`, then
   `postman collection get <uid> --json > <scratch>/collection.json`), or the Postman MCP if
   it is connected. Both need a session that a person started with `postman login`. Never
   pass `--api-key` on the command line, and never read environment values.
3. **OpenAPI/Swagger:** a JSON spec, or a simple YAML spec.
4. **Pasted endpoints, JSON or cURL.** Build the contract by hand in the same format. Save each
   pasted response as a fixture.
5. **Nothing exists yet** (endpoint not built). Ask for the **mock agreed with backend**. Record
   it as `status: mock-agreed`, with who agreed and when. Never invent a contract silently.

## Step 2 — Extract

```bash
python3 <this skill dir>/scripts/postman_to_contract.py <source> --list
python3 <this skill dir>/scripts/postman_to_contract.py <source> \
  --filter "<name or path fragment>" [--filter …] \
  --fixtures-dir test/fixtures/<feature> \
  --out .flutter-forge/runs/<slug>/contract.raw.md
```

The script reads Postman v2.1, Postman v3 (JSON or folder) and OpenAPI 3. It then:
- merges every saved example per status code, and marks fields that are null in some examples
  `?` and fields that are absent `[may be absent]`;
- flags `num` when an example has both int and double, and empty lists whose item type is
  unknown;
- redacts sensitive-looking keys in fixtures, such as tokens, passwords, card numbers and
  account identifiers;
- prints variable **names** only.

## Step 3 — Write `contract.md`

Turn the raw extraction into `.flutter-forge/runs/<slug>/contract.md` using
`references/contract-template.md`. Decide and write down:

| Topic | Decide | Feeds |
|---|---|---|
| Base path and auth | Relative paths (no host); auth scheme per endpoint (bearer, none, inherited) | Data source, interceptor |
| Envelope | Is the payload wrapped (`data`, `content`, `result`)? Is it the same for every endpoint? | DTO wrapper + mapper unwrap; `networking.envelope` |
| Pagination | page/size, cursor, `next_page`, `has_more`? | `Page<T>` entity, state |
| Error shape | Message key, field errors, business `code` values | `error_message_key`, `BusinessFailure` codes, l10n of codes |
| Types | int vs double vs `num`, dates (ISO-8601, timezone), enums as strings | DTO field types, mapper conversions |
| Nullability | Every `?` / `[may be absent]` → nullable DTO field + default in mapper | DTO + mapper |
| Idempotency / side effects | Write endpoints: idempotency key? retry-safe? | Data source headers, retry policy |
| Screen value → source | Each brief **Data need** → endpoint field, or **gap** | `forge-blueprint` |

## Step 4 — Contract gaps

Add to the run's gaps (blocking when an acceptance criterion depends on it):
- an endpoint with no example responses;
- no error example, so the error shape is unknown, for any endpoint a screen handles failures for;
- an empty list in every example, so the item type is unknown;
- a type `mixed`, or an int/double ambiguity in money fields (ask for decimals as strings or numbers);
- values the UI needs that no endpoint provides;
- unlocalized text from the backend (e.g. `"360 days"`) in a multi-language app. Compose the copy
  in l10n from structured fields instead.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Copy the whole collection into the run | `--filter` to the feature's endpoints | Context budget; irrelevant endpoints confuse the blueprint |
| Read or print Postman environment values | Use variable names only | Environments hold tokens and real hosts |
| `--api-key` on the command line | `postman login` by the person, once | The key would leak into shell history and logs |
| Make every field non-nullable because one example had it | Merge all examples; nullable unless proven required | `type 'Null' is not a subtype…` crashes |
| `int` for money because the example was `500` | `num`/`double` or decimal string, as agreed; ask when unclear | `500.5` later crashes the parser |
| Treat a mock you wrote as the contract | Mock agreed with backend, recorded with who and when | A guessed contract becomes a silent integration bug |
| Commit unredacted response bodies as fixtures | Redacted fixtures (script does it); review them | Fixtures are public in the repo |

## Finish

- Write `contract.md` and the fixtures under `test/fixtures/<feature>/`. Update `state.json`
  with `phase: contract` and the number of contract gaps.
- Report:
  - each endpoint with its method and path, and its status (`real` / `mock-agreed` / `gap`);
  - the fixtures written;
  - the envelope, pagination and error-shape decisions;
  - the gaps.
