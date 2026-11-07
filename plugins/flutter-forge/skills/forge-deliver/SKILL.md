---
name: forge-deliver
description: Deliver a complete Flutter feature end to end with flutter-forge. The pipeline runs profile → requirement brief (Gate 1) → Figma design → API contract → class blueprint (Gate 2) → domain/data and presentation code → l10n → unit/widget tests → Patrol E2E → independent code audit and security review (Gate 3) → approved fixes → traceability report and result.json. It works interactively or unattended (when called by an orchestrator), can run a subset of phases, and resumes interrupted runs from .flutter-forge/runs/<slug>/. Use it when the user asks to implement, build or "bajar" a full feature, flow or user story, gives a story plus a design and/or endpoints, says "implementa el flujo", "baja este requerimiento completo", "de la HU al código", "entrega el feature con pruebas y auditoría", or continues a previous run.
---

# forge-deliver

This skill orchestrates the other forge skills. It owns the run state, the gates and the
final report. Each phase is executed by its own skill, so a phase never re-implements another
skill's rules.

## Step 0 — Start or resume

1. **Mode.** Use `unattended` when the arguments or the orchestrator brief say
   `mode: unattended` (or "desatendido"). Otherwise use `interactive`.
2. **Phases.** All of them by default. A brief can request a subset, e.g. `phases: [contract,
   blueprint]` or `[audit, security]`, and the phase table below says what each subset needs.
3. **Profile.** If `.flutter-forge/profile.yaml` is missing, run `forge-profile` first.
4. **Run folder.** The slug is the kebab-case feature name. In `.flutter-forge/runs/<slug>/`:
   - If `state.json` exists, **resume**. Read it, report the completed phases and the open
     gates, and continue from `next_phase`. Do not redo completed phases unless their inputs
     changed (for example, a new story version or a new contract).
   - Otherwise, create `state.json` from `references/run-state.md`.
5. If `.flutter-forge/overlays/forge-deliver.md` exists, read it; its rules win. Examples: phases
   to skip, extra gates, or the report language.

## Phases

| # | Phase | Skill | Needs | Writes | Gate |
|---|---|---|---|---|---|
| 1 | requirements | forge-requirements | story/description | `brief.md` (+`hu.md`) | **Gate 1** brief + gaps |
| 2 | design | forge-figma | Figma link/nodes (skip if none) | `design.md` | — |
| 3 | contract | forge-api-contract | collection/spec/pasted endpoints (skip if no data) | `contract.md`, fixtures | — |
| 4 | blueprint | forge-blueprint | brief (+ design, contract) | `blueprint.md` | **Gate 2** classes + test plan |
| 5 | data | forge-data-layer | blueprint, contract | code | — |
| 6 | presentation | forge-presentation | blueprint, design | code | — |
| 7 | l10n | forge-l10n | blueprint keys | ARB + generated | — |
| 8 | tests | forge-tests | blueprint test plan, fixtures | tests, `tests.md` | — |
| 9 | e2e | forge-e2e | flow from brief; device + credentials | flow test | — |
| 10 | review | forge-audit + forge-security (via flutter-reviewer) | file list | `findings.md` | **Gate 3** which findings to fix |
| 11 | fix | owner skill of each finding | approved findings | code, re-run checks | — |
| 12 | report | this skill | everything | `report.md`, `result.json` | — |

Rules between phases:
- After each phase, update `state.json`: `completed`, `next_phase`, files and counts. The run
  must be resumable from any point in a new session.
- **Tests failing (8–9).** Fix and re-run, up to 3 cycles per failure (the rule in
  `forge-tests`). After that, continue to the review and mark the run `status: failing-tests`.
  Never hide a failure.
- **E2E prerequisites missing** (no device or no credentials). The test stays written and is
  marked `pending-run`. The run still completes.
- **Scope guard.** Only what the brief and blueprint list gets built. Bugs found elsewhere go
  to the report's **Observations** and are not fixed.

## Gates

| Gate | Interactive | Unattended |
|---|---|---|
| 1 brief | Show the brief and all gaps in one message; wait | Blocking gaps → `status: blocked`, stop with questions; non-blocking → continue with placeholders |
| 2 blueprint | Show the file plan, classes, open decisions and test plan; wait | Continue; record assumptions |
| 3 findings | Show the summary + list; the person picks the ids to fix (default: all critical/high) | Fix critical and high automatically; defer the rest |

Record each answer in `state.json` (`gates`), and in the brief's or blueprint's **Decisions**,
with the date.

## Review (phase 10): independent when possible

- **Main session** (you can launch agents): start the `flutter-reviewer` agent and give it
  the project path, the run folder, the scope (the run's file list) and `kind: both`. Wait
  for its result. It writes `findings.md`.
- **Running as a subagent** (no agent tool): run `forge-audit`, then `forge-security`, inline.
  Set `review.independent: false` in `result.json`, and recommend that the orchestrator run
  `flutter-reviewer` separately.

## Fix (phase 11)

For each approved finding, apply the fix with its owner skill's rules. Then:
1. re-run analyze;
2. re-run the tests of the affected files;
3. re-run the specific check that found it (`check_layers`, `scan_secrets`,
   `check_platform_config`).

Mark each finding `fixed` / `wontfix` (with the reason) / `deferred`. Do **not** re-run the
whole review unless the fixes were broad, meaning they touched more than ~30 % of the scope.

## Report (phase 12)

- Write `report.md` from `references/report-template.md`, in the profile's
  `requirements.language`. It covers:
  - AC → implementation → test traceability;
  - the design mapping and the files;
  - the mocked routes;
  - tests and coverage;
  - findings and their status;
  - open gaps, assumptions and observations.
- Write `result.json` following `references/result.schema.json`. This is what
  orchestrators read.
- **Git.** Never commit, push or open PRs unless the person asked, or the orchestrator brief
  sets `git: commit` / `git: pr`. Propose a Conventional Commit message and the PR body
  (taken from the report) instead.

## Context discipline

- Each phase loads its own skill and only the references it needs. The run files carry state
  from phase to phase, so you don't need to keep it in context.
- Do not paste whole files into messages. Point to paths.
- Before a long implementation, if the session is already long, write `state.json` and tell
  the person they can resume in a fresh session with "continúa el run <slug>".

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Start coding before Gate 1/2 in interactive mode | Brief and blueprint approved first | Rework is the most expensive outcome |
| Ask questions in unattended mode | Decide with recorded assumptions, or stop as `blocked` | Orchestrators can't answer |
| Review your own code inline when an independent reviewer is available | `flutter-reviewer` | Self-review confirms its own reasoning |
| Fix everything the review found without asking | Gate 3 (or only critical/high when unattended) | The person decides the scope |
| Re-run every phase on resume | Continue from `next_phase` | Time and context |
| Report "done" with failing or unrun tests | `status: failing-tests` / `pending-run` with output | Honest status |
| Commit or push by default | Propose the message; act only when asked or authorized | Git actions are the person's call |

## Finish

End with:
- the `report.md` path, with its summary: status, ACs covered, tests, verdict and open gaps;
- the `result.json` path;
- the next step that the person must decide: answer gaps, approve fixes, or commit.
