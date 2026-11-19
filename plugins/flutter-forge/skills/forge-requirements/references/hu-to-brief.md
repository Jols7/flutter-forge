# Story → brief mapping

This mapping works for the default template and for most handoff, PRD and ticket formats. When
a project's format is different, map its sections to these rows in the project's overlay.

## Reading a story: hu-v1 and earlier stories

Stories are read **by section number (1–10)**, never by title. A hu-v1 story says
`Template: hu-v1` in its header. An earlier story has no `Template` field, and its titles can
differ: for example, §5 was "Screens, navigation and states". Both are read with these rules:

1. **Applies to this app?**
   - Read the header's `Surfaces` field. In earlier stories, read `Platform` instead.
   - The story applies when `Surfaces` contains `mobile`. For an earlier story, it applies when
     `Platform` names the mobile app (`App`, `mobile`).
   - Otherwise, for example `Surfaces: api · web`, the story is not for this app: stop and
     report it in the brief.
   - When several surfaces are listed, implement only the mobile part.
2. **§5 Interface, flows and states and §6 Design references:**
   - If the section has `### <surface>` subsections, read **only** `### mobile`. Ignore
     `### web` and any other surface.
   - If the section has no subsections (an earlier, flat story), read the whole section.
   - If `Surfaces` contains `mobile` but the section has subsections and no `### mobile`, that
     is a gap.
3. **`N/A — <reason>`.** A section with this line has nothing to map. The reason can explain
   a gap, for example "N/A — no design yet".
4. **Not used by this skill.** `Template`, `Epic`, `Points`, `Depends on` and the `NFR-n` ids
   are left as they are; no brief item comes from them. Non-functional *behavior* is still read
   from §5, as in the row below.

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

## Gap ids: `Q-n` in the story, `G-n` in the brief

A story numbers its open questions `Q-n` (§ open questions of the template). The brief numbers
every gap `G-n`, because it also collects gaps found in the design and the contract. When a story
question becomes a gap, keep the story's id in the question text: `G-2 (Q-1 of HU-12) …`. Answers
are recorded under the `G-n` id in the brief's Decisions, and the story's `Q-n` is updated by the
person who owns the story, never by the agent.

## Always a gap unless stated

- Endpoints and contracts, and which calculations happen on the server.
- Numeric limits for **every** variant: currency, level, user type.
- Parameters the destination flow must accept.
- How the entry condition is obtained, i.e. which existing state or repository already knows it.
- Copy for every error state the story mentions without text.
- Design tokens that don't exist in the project theme.
- Whether accessibility is required (`a11y: on | off`). Ask once if the story or requirements say nothing and the profile default is unclear; never turn it on silently.

## Mock data is not data

Amounts, names and dates in design frames are illustrative. They can contradict each other
inside a single frame. Use them only to learn formatting: currency symbol, decimals, date
style.
