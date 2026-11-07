# Story → brief mapping

This mapping works for the default template and for most handoff, PRD and ticket formats. When
a project's format is different, map its sections to these rows in the project's overlay.

| Story content | Look for | Becomes in the brief / later phases |
|---|---|---|
| Purpose, objective | Who and why | Feature name, slug, folder (`paths.features/<slug>`) |
| Happy path, alternatives | Steps and branches | The flow's steps → E2E test steps (`forge-e2e`) |
| Contingencies | Offline, expired session, server error, domain failures | `AppFailure` cases to handle per screen; `BusinessFailure` codes to ask backend for |
| Visibility conditions ("only if balance > 0") | Conditions to *show the entry* | A check at the **entry point** (caller), not inside the new page |
| Rules and validations | Min/max, formats, defaults, resets ("currency change resets amount") | Validators in domain/state; constants **only** from story or contract; reset logic in state |
| Exact messages | Error and confirmation copy | l10n keys with that copy as the source text (`forge-l10n`) |
| Permissions, roles | Who can act | Guards at the route/entry; a gap if the backend enforcement is unknown |
| Traceability ("no data persisted", "audit required") | Write/no-write, audit trails | Whether there is a write endpoint; receipts or notifications |
| Acceptance criteria | Given/When/Then | `AC-n` ids → test names in unit/widget/E2E tests and the coverage table of the report |
| Navigation in/out | Origin, destination, parameters | Route + arguments; destination flow must accept the parameters (gap if unknown) |
| States per screen | Loading, empty, error, success | Sealed state variants; which **block** of the page reacts (others stay interactive) |
| Non-functional | Optimistic UI, no flicker, debounce, retries | Local recompute + debounced requests + delayed loading flag + stale-response discard; retry policy |
| Design references | Nodes per state, tokens | Input list for `forge-figma` (one node per state, not full screens repeatedly) |
| Data and integration | Values shown/sent | "Screen value → source" table in `forge-blueprint`; unknown sources are gaps |
| Security | Sensitive data, masking, logging, re-auth, limits, screenshots | Requirements checked by `forge-security` against the code |
| Out of scope | Explicit exclusions | Scope guard: nothing outside it is built |

## Always a gap unless stated

- Endpoints and contracts, and which calculations happen on the server.
- Numeric limits for **every** variant: currency, level, user type.
- Parameters the destination flow must accept.
- How the entry condition is obtained, i.e. which existing state or repository already knows it.
- Copy for every error state the story mentions without text.
- Design tokens that don't exist in the project theme.

## Mock data is not data

Amounts, names and dates in design frames are illustrative. They can contradict each other
inside a single frame. Use them only to learn formatting: currency symbol, decimals, date
style.
