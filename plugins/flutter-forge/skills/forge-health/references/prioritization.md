# Prioritization: risk × change frequency ÷ effort

A finding is worth fixing in proportion to the damage it can do, how often that code changes,
and how little it costs to fix. Multiplying all three would rank the most expensive work first,
so effort divides.

```
priority = risk × frequency ÷ effort
```

## Risk (1–5), from the severity scale in `../forge-audit/references/severity.md`

| Severity | Risk | Add +1 (max 5) when the code touches |
|---|---|---|
| critical | 5 | money, credentials, session or personal data |
| high | 4 | the same |
| medium | 3 | the same |
| low | 2 | |
| improvement | 1 | |

## Frequency (1–5), from `git_churn` commits in the window (default 90 days)

| Score | Rule (file or area) |
|---|---|
| 5 | in the top 10% of changed files |
| 4 | in the top 25% |
| 3 | changed at least the median number of times |
| 2 | changed at least once |
| 1 | not changed in the window |

If the repo has no history (a shallow clone, a fresh export), set every frequency to 2 and say
so in Limits. Do not invent a ranking from nothing.

## Effort (S / M / L)

| | Divisor | Meaning |
|---|---|---|
| S | 1 | One file or one configuration change, no behavior change to protect, under half a day |
| M | 2 | One feature or one layer, needs a few tests, up to about three days |
| L | 3 | Crosses features or layers, needs characterization tests first, or needs another team |

## Buckets

- **Do now (always first):** security or money findings with risk ≥ 4, whatever their frequency.
  Exposure does not depend on how often someone edits the file.
- **Quick Wins:** effort S and `risk × frequency ≥ 8`. Examples: enable obfuscation in release
  scripts, remove a committed env file and rotate its secret, add a missing `const` in a hot
  widget, pin an `any` constraint.
- **Big Bets:** effort L and `risk × frequency ≥ 12`. Each one lists a **first reversible step**
  (for example "add characterization tests for `X`") and what would prove it worked.
- **Later:** everything else with `frequency ≥ 2`.
- **Leave alone:** `frequency = 1` and `risk ≤ 3`. Stable code that is ugly but works is not
  touched. Write one line saying why.

Within a bucket, sort by `priority` descending, then by risk.

## Order of remediation (what each phase is allowed to contain)

1. Security and money.
2. Bugs on the main paths.
3. Tests in hot zones, **before** any refactor of that zone.
4. Structure (layer violations, boundaries).
5. Style.

A refactor and a feature never share a change. A refactor with no test around it is a Big Bet
whose first step is the test.

## Mode

The path is phases of 1–3 weeks, each ending in something that ships.

| Mode | Standard to judge against | In the backlog | Path |
|---|---|---|---|
| `adopt` | The repo's own rules and overlays | Bugs, security, tests in hot zones | 1) security 2) hot-zone tests 3) bugs. No structural or style items |
| `improve` | Own layout; new and touched code at the preset's level | The above, plus `improvement` items on code being touched anyway | Add 4) fix violations as files are touched, 5) tighten rules in `layers.json` once clean |
| `migrate` | Clean preset for new features; legacy stays as it is | The above, plus a migration plan | Pick a canonical feature; characterization tests; one feature at a time next to the old code; the old feature is removed only after its tests pass on the new one |
| `unset` | Assumed preset, marked as such | Everything, flagged "depends on the mode" | Recommend a mode with evidence; the person chooses |

Recommend `improve` when untestable patterns are common (service locator inside state
managers, thrown strings). Recommend `adopt` when the repo is consistent and stable. Recommend
`migrate` only when there is measurable pain (bugs, slow onboarding, slow builds); never because
the architecture is unfashionable.
