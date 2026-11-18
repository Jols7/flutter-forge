---
type: llm
weight: 2
---

The answer is a metrics report that follows the forge-metrics rules, not a generic cost summary.
- Every figure comes from the digest ($15.43, 93.1/64.6/29.9 min, the phase costs). Nothing is
  invented, recomputed from guessed prices, or estimated from memory.
- It says the cost is "at API prices", not what was paid, and that the phase split is an estimate
  while the session and model totals are official.
- The most expensive phase is `tests` ($2.36, 15.3%). The answer names it and may note that `contract`
  and `review` follow. `unmarked` is not presented as a real phase of work.
- At most 5 findings, each tied to a number from the digest and to one concrete change for the next
  run. Examples that fit the data: opus carries 98% of the cost; context grows toward 234K in the
  late phases (`e2e`, `tests`, `blueprint`); waiting is 43 min; `phase_log` is missing so `review`
  also holds fix and report. It does not claim a waste the numbers do not show.
- Savings are reported as "not computable" because there was no baseline set before the run.
  It does not give hours saved.
- It states this is one run and not a baseline (fewer than 5 runs of the type).
- It lists the sessions to confirm, namely the adjacent ones and `1ac9e0ce` (linked), with the exact
  `--include` or `--exclude` option that would change the result. It does not silently add them to the total.
- It does not quote code, prompts or file contents.
