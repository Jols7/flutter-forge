# health-report.md template

Fill every section. Write "none found" instead of dropping one. Keep the file under about 400
lines and refer to `metrics.json` for raw data. Language: `requirements.language`, otherwise the
language of the request.

````markdown
# Health report — <project name> · <date>

Repo: <path or remote> · Branch/commit: <short sha> · Window: last <N> days (<commits> commits, <authors> authors)
Profile: <present | none: assumed preset clean> · Mode: <adopt|improve|migrate|unset>
Data: metrics.json · Tools run: <commands, one line each> · Written by forge-health (read-only)

## 1. Summary
| Area | Status | One line |
|---|---|---|
| Architecture | 🟢 / 🟠 / 🔴 | |
| Security | | |
| Tests | | |
| Performance | | |
| Dependencies | | |

Top 3 quick wins · Top big bet · Decisions waiting for a human: <n>

## 2. Architecture: real versus declared
- Declared (<source>): …
- Real: preset guess <x> (<confidence>), state <y>, di <z>, router <r>
- Drift: <declared X, real Y → who should change>

| Layer | Files | Violations | Commits (window) | Dominant problem |
|---|---|---|---|---|

Real import edges that break the rules: <pair × count, with 2–3 `file:line`>
Blind spots (unclassified folders): …

## 3. Security
| ID | Severity | MASVS | Where | What | Fix · owner | Confidence |
|---|---|---|---|---|---|---|
Accepted risks (from overlay): <owner · expiry>
Scanner coverage: what the scanners cannot see (business logic, authorization).

## 4. Performance
Findings from widget sizes, long `build()`, list or image patterns, rebuild scope. Marked
"proposal: measure with DevTools" — this skill does not measure runtime.

## 5. Tests
Line coverage <x%> (lib files absent from lcov counted as 0%). Hot files with low coverage:
| File | Commits | Coverage | Risk if it breaks |
|---|---|---|---|

## 6. Dependencies
direct/dev/override counts; git/path/any; discontinued; major versions behind; packages on
main paths with a single maintainer. `pub outdated`: <run | not run>.

## 7. Backlog
Priority = risk × frequency ÷ effort (S=1, M=2, L=3). See references/prioritization.md.

### Do now (security and money; each item only here, with its priority number)
| ID | Item | R | F | E | Priority | Owner |
### Quick wins
| ID | Item | R | F | E | Priority | Owner |
### Big bets
| ID | Item | R | F | E | Priority | First reversible step | Proof it worked |
### Later · Leave alone
One line each, with the reason.

## 8. Incremental path (<mode>)
| Phase | Weeks | Contains | Done when |
|---|---|---|---|

## 9. Decisions that need a human
| # | Decision | Evidence | Recommendation | Level | If we decide wrong |
|---|---|---|---|---|---|

## 10. Limits and method
Commands run · not measured (<no lcov | pub outdated not run | no git history | assumed preset>) ·
confidence bar 0.8 · leads below the bar:
- <note>
A clean scanner is not proof of safety.
````
