# Reading the metrics

## What each number means

| Number | Source | Trust |
|---|---|---|
| Total and per-model cost, tokens | `cost-state` of each closed session | Official, at API prices |
| Model time | `totalAPIDuration` of `cost-state` | Official |
| Phase cost | Official total split by each call's weighted tokens | Estimate |
| Phase boundaries | `phase_log` in `state.json`, then forge skill and reviewer calls | Exact with `phase_log`; without it, fix and report fall inside `review` |
| Active time | Gaps between transcript events, each capped at 3 minutes | Approximation; includes short human pauses |
| Tool time | From each tool call to its result; background work ends early | Lower bound |
| Waiting | From the last reply to the next real prompt | Person plus background jobs; never call it human time alone |
| Acceptance rate | `fixed / (fixed + wontfix)` over review findings | Exact, but small samples swing it |
| Savings | `baseline − active − human review`, in hours | Only with a baseline set before the run |

`unmarked` is work before the first marker of a session, or in a session with no marker.

## Where to look for waste

Report a pattern only when the numbers show it:

- **Context growth.** A phase whose average context is far above the earlier ones pays for that
  context on every call. Suggest resuming in a fresh session before that phase.
- **Cache writes.** Many short sessions each pay to write the context again. Compare the cost of
  the small sessions with the work they did.
- **Setup and retries.** Adjacent or `unmarked` cost that does not repeat on the next run is
  one-time. Separate it before projecting the next run.
- **Phase out of proportion.** Compare the share of cost with the share of active time, and name
  the phase that spends the most per minute.
- **Waiting.** Long waiting with few prompts usually means gates or a slow background job.
- **Light review.** Few calls in `review` next to a high code cost is a question for the team,
  not proof of a poor review.
- **Measurement cost.** A large `measurement` amount means the run was measured by hand. This
  skill replaces that.

## What not to conclude

- A cheap phase is not a good phase. A weak early phase can make later ones more expensive, so
  compare whole runs.
- Cost per acceptance criterion or per line compares only runs of similar scope.
- Do not rank models from one run. Compare configurations over several comparable runs.
