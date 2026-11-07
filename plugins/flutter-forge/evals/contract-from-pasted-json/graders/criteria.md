---
type: llm
weight: 2
---

The answer derives the contract the way flutter-forge requires:
- `amount` is typed as `num` (or double/decimal) — never `int` — because both 1500 and 99.5 appear.
- `description` is nullable; `tag` is nullable or marked as possibly absent; `next_page` is nullable (null = last page).
- `booked_at` stays a String in the DTO and is parsed to DateTime in a mapper (or the answer clearly separates DTO and entity).
- The path is relative (no leading slash, no host) and pagination is modeled (e.g. a Paginated/Page result with next page).
- It mentions at least one contract gap, e.g. there is no error-response example or the full list of `tag` values is unknown.
