# Test matrix — what each kind of class must prove

| Layer | Class | Required cases | Optional |
|---|---|---|---|
| domain | Entity | derived getters (`isDebit`), equality if overridden | — |
| domain | Value object / validator | valid, each invalid reason, boundaries | property-style loops over ranges |
| domain | Use case | each rule short-circuits with the right failure; delegates to the repository on success | — |
| data | Mapper | each fixture → expected entity; nulls/absent → defaults; unknown enum → fallback; dates/money conversion | round trip for request DTOs (`toDto().toJson()` equals the request fixture) |
| data | Remote data source | request shape (method, path with encoding, query, headers, body); DTO returned; exceptions not swallowed | cancellation passes the token |
| data | Repository impl | `Success` mapping; every status → failure type; business codes; parsing; network/timeout | cache hit/miss/TTL when cached |
| presentation | State manager | initial; each load outcome; retry; pagination (append, end, load-more failure keeps items); debounce + stale discard; disposal guard; side-effect trigger | analytics events |
| presentation | Page | each sealed state renders its widget; intents on tap/type; error copy from failure mapping; submit disabled rules | goldens for stable components; text-scale 2.0 smoke |
| presentation | Shared widget (new or extended) | each parameter's effect; the **old default behavior unchanged** when extended | goldens |
| e2e | Flow (forge-e2e) | happy path from entry to exit; main failure path that is reachable in the test environment | — |

## Mapping acceptance criteria

- **Rule-like ACs** ("minimum is 10.00") → validator/use-case tests + state test + widget
  test of the message.
- **Flow ACs** ("from account detail, tapping Transferir opens…") → E2E step + widget test of the
  entry change.
- **Failure ACs** ("if funds are insufficient, show…") → repository test (code →
  `BusinessFailure`) + state test + widget test.
- **Non-functional ACs** ("no loading flicker") → state test with `fakeAsync`: no loading state
  before 250 ms.
