# Decisions that need a human

The agent applies rules. A person decides which rule is worth applying, when to break it, and
who carries the risk. A health report lists these decisions with a recommendation and its
evidence, and never makes them.

Risk levels: 🔴 always a human · 🟠 a human reviews closely · 🟢 the agent may decide and a human samples.

## Triggers, and what to write for each

| If the snapshot or your review shows | Decision | Level | Senior criterion |
|---|---|---|---|
| Existing repo, no profile or `mode` unset | Adopt, improve or migrate | 🔴 | Cost of change versus a measured pain. Do not migrate by taste. Consistency inside the repo beats purity |
| More than one state package, or code differs from `pubspec` | Which state manager new code uses, and whether to converge | 🔴 | The team and the code base first, then ecosystem, testability, learning curve. Switching is the costliest front-end decision |
| `DRIFT:` lines, or docs that contradict the code | Change the code or change the docs | 🟠 | Prefer fixing the doc when the code is the working truth |
| A `critical` or `high` security finding | Fix now, or accept the risk | 🔴 | An acceptance needs an owner, an expiry date and a mitigation. The agent never accepts risk |
| Secret in the repo or its history | Rotate, then clean history or not | 🔴 | Rotation first, always; rewriting history affects every clone |
| Any rule about amounts, currency, rounding, limits, idempotency | Confirm the rule with the business owner | 🔴 | A rule about money is never "assumed and moved on". The code may be right and the rule wrong |
| Client-side checks that look like business controls | Add the server-side check | 🔴 | The client is UX, not control. Whatever a user can manipulate is validated on the backend too |
| Pinning, obfuscation, root detection missing | Whether the threat model justifies them | 🔴 | Start from who attacks, what they gain and what defense costs. Pinning without a rotation plan causes outages |
| Hot file with low coverage and a proposed refactor | Write characterization tests first, or leave it | 🟠 | Tests before moving code. Small reversible steps. No refactor and feature in the same change |
| Hot, large, untested file with a single owner | Bus-factor and knowledge-transfer plan | 🟠 | Risk is the person as much as the code |
| Pattern that looks wrong but is consistent across the repo | Intentional or debt | 🟠 | Ask the team or read `git blame` before condemning it (Chesterton's fence) |
| `git`/`path`/`any` dependency, override, discontinued or far-behind package on a main path | Replace, pin or keep | 🟠 | Last release, maintainers, license, size, security surface, and whether 30 lines would do |
| Major Flutter or Dart upgrade needed | When and how | 🔴 | Isolated branch, changelog read, CI green, critical flows on a real device. A separate piece of work |
| Modularization or monorepo split suggested | Whether to do it | 🟠 | Boundaries follow change, not technical layers; count the CI and versioning cost |
| Abstractions with one implementation | Keep or collapse | 🟠 | Earned only by two real implementations or a needed test seam |
| Analytics or crash-report events that may carry personal data | Remove or redact | 🔴 | Minimum necessary. No personal data, card numbers or tokens in logs or analytics |
| Data leaves the repo toward an AI provider | What may be sent | 🔴 | Company policy decides what code and stories can leave |
| Anything against production, a store release or a merge | Go or no-go | 🔴 | Always a human, with a rollback plan |

## How to write a row in Section 9

```
| # | Decision | Evidence | Recommendation | Level | If we decide wrong |
|---|---|---|---|---|---|
| D-1 | Mode for this repo | 4 service-locator calls in state; drift on state manager | improve | 🔴 | Cost of a migration nobody asked for |
```

Rules:
- Evidence is a number or a `file:line`, never an impression.
- Recommend, but say what would change your mind.
- The last column is the cost of being wrong, not the cost of the fix.
- If a decision belongs to the business (limits, minimum amounts, eligibility), name the owner
  type ("product owner", "security owner") and not a person.

## Not in the report

Do not report a vulnerability in someone else's code as a public comment. In the report, name
the responsible channel (the security owner) and keep the finding out of any shared issue
tracker until they decide.
