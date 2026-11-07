# Brief template (`.flutter-forge/runs/<slug>/brief.md`)

Under ~80 lines. Content is in `requirements.language`, and ids are neutral.

```markdown
# Brief — <Feature name>
Source: <story path/link/issue> · Status: <draft | approved YYYY-MM-DD> · Run: <slug>

## Scope
Feature folder: <paths.features>/<slug>/
In scope: <bullets> · Out of scope: <bullets>

## Flow
Entry: <origin screen/action> — visibility rule: <condition, evaluated at the caller>
Steps: 1. … 2. … 3. …
Exit: <destination + parameters> · Premature exit: <behavior>

## Screens and states
| Screen | States | Blocking region | Notes |
|---|---|---|---|
| <Screen> | loading · empty · error(retry: unlimited) · success · validation | <summary card only> | <debounce 300 ms, delayed loading 250 ms> |

## Rules and validations
| Id | Rule | Value | Source | Message key/copy |
|---|---|---|---|---|
| R-1 | Minimum transfer amount | 10.00 (account currency) | story §3 | "Ingresa un monto mayor a $10.00" |

## Acceptance criteria
AC-1 … AC-n (one line each, linking to the story for full text)

## Data needs
| Value | Direction | Source | Status |
|---|---|---|---|
| Own accounts with balance | read | GET accounts endpoint | known / mock agreed / **gap G-2** |

## Security
Sensitive: <fields> · Masking: <rule> · Never log: <fields> · Re-auth: <action> · Limits: <…>

## Design
Figma: <file/nodes per state> · Tokens without theme match: <list or none yet>

## Gaps
| Id | Question | Type | Placeholder if non-blocking |
|---|---|---|---|
| G-1 | Can a transfer be scheduled for a future date? | blocking | — |
| G-2 | Copy for the "daily limit reached" error | non-blocking | `TODO(G-2)` key with the generic error text |

## Decisions
- YYYY-MM-DD — G-3 answered: <answer> (by <who>)
```
