# Explaining the work: "Por qué" and "Dónde revisar"

Every run tells the person **why** it decided what it did and **where** to look before
trusting it. The brief's `explain` field sets the depth; the default is `brief`.

| `explain` | `why[]` | `review_points[]` | `report.md` |
|---|---|---|---|
| `none` | empty | empty | no *Por qué / Dónde revisar* sections |
| `brief` (default) | 1–3 most consequential decisions | 1–3 points | both sections, short |
| `full` | every gate decision (brief gaps, blueprint, findings), each with its discarded alternatives | every place a human should check | both sections + a short note per alternative |

## `why[]`: decisions, not a diary

```json
{"decision": "No use case for loading transactions",
 "reason": "Pass-through call; no rule or reuse (forge-architecture: use cases must be earned)",
 "alternatives": ["GetTransactions use case", "Repository called from the page"]}
```

Good candidates:
- choices among architecture options (use case or not, one state manager or two, cache or not);
- how a gap was handled (placeholder, mock route, assumption);
- a convention adopted from the project over the default;
- a finding that was deferred or won't be fixed.

Leave out what the preset already dictates, unless the person is likely to question it.

## `review_points[]`: where a human must look

```json
{"point": "Confirm the 10.00 minimum applies per transfer, not per day",
 "location": "lib/features/transfers/domain/entities/transfer_amount.dart:12",
 "reason": "Story R-1 is ambiguous; the code assumes per transfer"}
```

Prioritize by risk: money and rounding, security and sensitive data, assumptions on open
gaps, mocked routes, tests that could not run (E2E pending), deferred findings and any
deviation from the project's conventions. `location` is `file[:line]`, a run-file section
(`brief.md#Gaps`), or a URL.

The person is an experienced Flutter developer: explain the decision, not Flutter basics.
