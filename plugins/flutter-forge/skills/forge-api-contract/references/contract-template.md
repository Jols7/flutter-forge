# `contract.md` template

```markdown
# Contract — <feature>
Source: <collection file / cloud uid / openapi / pasted> · Extracted: YYYY-MM-DD

## Conventions
- Paths are relative to the configured base URL. Auth: bearer via interceptor (login: none).
- Envelope: `{ "data": <payload>, … }` on reads; writes return the resource unwrapped. → DTO wrapper `DataEnvelopeDto<T>` / unwrap in mapper.
- Pagination: `page` + `size` query; response `next_page: int?` (null = last page).
- Errors: `{ "code": String, "message": String, "errors"?: {field: [String]} }` → `error_message_key: message`.
- Business codes: `INSUFFICIENT_FUNDS` (409), `ACCOUNT_NOT_FOUND` (404), `VALIDATION_ERROR` (422).
- Dates: ISO-8601 UTC → `DateTime.parse(...).toLocal()` in mappers.
- Money: JSON numbers, int or double → `num` in DTO, `double` (or `Decimal`) in entity.

## Endpoints

### GET `accounts/{accountId}/transactions` — List transactions · status: real
Query: page (int, default 1), size (int, default 20)
200 → fixture `test/fixtures/transactions/list_transactions_200.json` (+ empty variant)
| Field | Type | Notes |
|---|---|---|
| data[].id | String | |
| data[].description | String? | null in examples |
| data[].amount | num | int and double seen; negative = debit |
| data[].booked_at | String (date-time) | → DateTime |
| data[].category | String? | enum-like: food, … (ask for full list → gap) |
| next_page | int? | null on last page |
404 `ACCOUNT_NOT_FOUND` → NotFoundFailure

### POST `transfers` — Create transfer · status: real
Headers: `Idempotency-Key` (new UUID per user attempt; reuse on retry of the same attempt)
Body → `create_transfer_request.json`: from_account_id String, to_account_id String, amount num, concept String?
201 → `create_transfer_201.json` · 422 → ValidationFailure(fieldErrors) · 409 `INSUFFICIENT_FUNDS` → BusinessFailure

## Screen value → source
| Brief data need | Endpoint · field | Status |
|---|---|---|
| Account balance | GET accounts · data[].balance | ✓ |
| Daily limit remaining | — | **gap C-1** |

## Contract gaps
| Id | Gap | Blocking? |
|---|---|---|
| C-1 | No endpoint returns the remaining daily limit | yes (AC-4) |
| C-2 | GET transfers/preview has no error example | no |
```

Keep only the endpoints in this feature's scope. The full collection stays in its source.
