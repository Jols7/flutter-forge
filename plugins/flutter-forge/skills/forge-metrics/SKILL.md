---
name: forge-metrics
description: Measure what a finished flutter-forge run cost and what it delivered, written to .flutter-forge/metrics/. A script reads Claude Code's local transcripts, links the sessions that worked on the run, and reports the official cost per model, an estimated split per phase, the time spent on the model, tools, questions and waiting, and the run's outcome (acceptance criteria, findings accepted, gates changed). The model only interprets those numbers and says what cost more than it should. It keeps counters, never conversation text, and sends nothing anywhere. It also measures reviews, forge-health and single skills by session id, and summarizes past runs with median and range. Run it by hand after the run's sessions are closed. Triggers include "forge-metrics", "métricas del run", "cuánto costó el run", "cuánto tardó", "telemetría del agente", "costo por feature", "run metrics", "how much did this run cost".
disable-model-invocation: true
context: fork
model: sonnet
allowed-tools: Read, Write, Bash(python3 *)
---

# forge-metrics

This skill answers "what did this run cost, where did the cost go, and what did we get?". It
runs **after** the work, outside the run, because the official cost of a session is recorded
only when that session closes. It never edits project code.

Scripts count; you judge. Never estimate a token count, a cost or a duration yourself: every
number in your report comes from the script's output.

Request from the person: $ARGUMENTS

## Step 0 — Resolve

1. Read `requirements.language` from `.flutter-forge/profile.yaml` when it exists. Write the
   report in it, otherwise in the language of the request.
2. If `.flutter-forge/overlays/forge-metrics.md` exists, read it; its rules win.
3. Choose the mode from the request:

| Request | Arguments for the script |
|---|---|
| Nothing, or "qué puedo medir" | `--list` |
| A run slug | `--slug <slug> --write` |
| One or more session ids (a review, `forge-health`, a single skill) | `--session <id> ... --id <name> --write` |
| "resumen", "historial", "comparar corridas" | `--summary` |

Add `--include <id> ...` or `--exclude <id> ...` when the person names sessions to add or drop,
and `--review-hours <h>` when they say how long their review and rework took.

## Step 1 — Run the script

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/run_metrics.py" --root . <arguments>
```

- With `--list` or `--summary`, relay the output and stop. Say that fewer than 5 complete runs of
  a type are an anecdote, not a baseline.
- `Unavailable` means there are no transcripts for this folder, or no session touched the run.
  Report the reason and stop. Do not reconstruct numbers from memory or from the run files.

## Step 2 — Check what was counted

Read the output's session lists before interpreting anything:
- **core** invoked a forge skill and touched the run. **linked** touched the run without a forge
  skill, and may be a closing session or just a question.
- **adjacent** sessions ran close in time but never touched the run. They are not counted, yet
  they can be real run cost, such as installing the plugin or connecting an MCP server.
- **measurement** sessions read the transcripts to measure. They stay out of the run's cost and
  are shown apart.
- If the output is `INCOMPLETE`, a session has no `cost-state`. Its cost is unknown, so tell the
  person to close it and run this again. Never fill the gap with an estimate.

You cannot ask questions from this context. List the doubtful sessions in the report, with the
exact `--include` or `--exclude` that would change the result.

## Step 3 — Interpret

Follow `references/reading-metrics.md`. Report at most five findings, each tied to a number from
the output and to one concrete change for the next run.

## Step 4 — Write the report

Fill `references/report-template.md` and write it with the Write tool to
`.flutter-forge/metrics/<id>.md`, next to the `<id>.json` the script wrote. That is the only file
you write. The script already updated `history.jsonl`.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Estimate tokens, cost or time | Quote the script | The model cannot see its own usage |
| Open transcripts to look for more detail | Work from the script's output | They hold code and conversation, and reading them costs tokens |
| Quote prompts, code or file contents | Numbers, phase names and session ids only | The report may be shared |
| Present the cost as what was paid | "At API prices" | A subscription is billed differently |
| Claim savings without a baseline set before the run | Say savings are not computable | An estimate made afterwards is biased |
| Generalize from one run | Say it is one run; use `--summary` when there are at least 5 | One feature proves nothing |
| Treat a phase cost as exact | Call it an estimated split | Only the session and model totals are official |

## Finish

- `.flutter-forge/metrics/<id>.json`, `<id>.md` and `history.jsonl` exist. The folder has its own
  `.gitignore` on first use, so nothing is versioned unless the team removes it.
- Reply with the total cost, active and model time, the most expensive phase, the top finding
  and the report path. Add any session the person should confirm. Keep it short.
