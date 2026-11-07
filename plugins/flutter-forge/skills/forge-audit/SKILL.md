---
name: forge-audit
description: Audit Flutter/Dart code for architecture conformance, design quality, redundancy, best practices, performance, testing and accessibility, against the project's own preset and layer rules. Automated checks run first (analyzer, formatter, layer/import checker, DCM when available). Then come a checklist review and three design lenses (state modeling, responsibility boundaries, abstraction timing). Findings are ranked critical/high/medium/low/improvement, with file:line, why and fix, a confidence bar above 80% and a merge verdict. It never edits code itself. Use it after implementing or before merging, when the user asks for a code review, "audita el código", "revisa la calidad", "busca redundancias", "valida la arquitectura", "code review del feature", or when forge-deliver reaches the review phase (usually inside the flutter-reviewer agent).
---

# forge-audit

This skill reviews code and reports. It **does not modify files**: fixes are applied by the
implementing skill after Gate 3. When the plugin's `flutter-reviewer` agent is available,
the audit runs there, in a context that did not write the code.

## Step 0 — Resolve scope and rules

1. Read `.flutter-forge/profile.yaml`: `architecture.*`, `quality.*`, `testing.coverage_min`.
2. **Scope.** In priority order, review:
   - the run's file list from `state.json` or `blueprint.md`;
   - the diff against the base branch (`git diff --name-only <base>...`);
   - the folder or files the person named.

   Review the files in scope. Read their direct collaborators only to judge them.
3. **Rules.** Use `.flutter-forge/layers.json` if present, or the preset's file
   (`../forge-architecture/presets/<preset>.layers.json`). Read the preset reference.
4. Read `blueprint.md` and `brief.md` when present. The audit checks the code against the plan
   and the acceptance criteria, not only against generic rules.
5. If `.flutter-forge/overlays/forge-audit.md` exists, read it. It can raise or lower rule
   severities and add project rules, and its rules win.

## Step 1 — Automated checks (run every one; they are evidence)

```bash
<quality.analyze_command>                                   # analyzer + lints
<quality.format_command>                                    # formatting (non-zero = unformatted files)
python3 <this skill dir>/scripts/check_layers.py --rules <rules> --files <scope files…>
python3 <this skill dir>/scripts/check_layers.py --rules <rules> --summary --no-fail   # project debt, for context only
python3 <this skill dir>/scripts/check_comments.py --root . --files <scope dart files…>
dart run dart_code_metrics:metrics analyze lib  # only if quality.dcm: true (or `dcm analyze lib`)
```

- Analyzer errors and layer violations **in scope** are findings with a known severity
  (`references/severity.md`).
- Violations outside the scope are **pre-existing debt**. Summarize them in one line and never
  let them block.
- Record the commands and their outcomes in the report.

## Step 2 — Checklist review

Go through `references/checklist.md` section by section, only for the file kinds in scope.
The sections are:
1. architecture and layers
2. state management (with the active state manager's rules)
3. widgets
4. Dart idioms and null-safety
5. async and lifecycle
6. errors
7. data layer
8. performance
9. testing
10. accessibility
11. l10n
12. navigation
13. dependencies
14. comments

## Step 3 — Design lenses

Apply the three lenses in `references/design-lenses.md`:
- **State modeling:** can the code represent invalid states?
- **Responsibility boundaries:** if this feature were removed, how many files would change?
- **Abstraction timing:** is each abstraction earned, or speculative?

Report a lens finding only with a concrete suggestion that names the types or widgets
involved. Never force a finding.

## Step 4 — Redundancy

Follow `references/redundancy.md`:
- a duplicated widget versus the catalog;
- a duplicated error-handling block versus `guard`;
- copy-pasted mappers or validators;
- a second HTTP client or formatter;
- dead code: unused files, exports and l10n keys in scope;
- a mock route for an endpoint that the contract now marks `real`.

## Step 5 — Plan conformance

Compare the code with the blueprint:
- missing or extra files;
- signatures that differ from the contract;
- an AC listed as covered whose test does not exist;
- the entry-point change not applied.

## Step 6 — Report

Use the format in `references/severity.md`:
- findings ranked by severity, each with `id`, `severity`, `category`, `file:line`, what,
  why, fix, `confidence`, and `owner` (the skill that fixes it);
- a summary table;
- the verdict: `block` (any critical/high) · `pass-with-notes` · `pass`.

Rules:
- Report only findings with confidence ≥ 0.8. Group repeated instances into one finding with
  a file list.
- Severity comes from impact, not taste. Style that a linter would catch is not a finding;
  the linter's output is.
- In `adopt` mode, never report the project's own conventions as findings. In `improve` mode,
  upgrades are `improvement`, never blocking.
- Each finding says exactly what to change. "Consider refactoring" is not a fix.

Write `.flutter-forge/runs/<slug>/findings.md`. When a security review is also requested,
`forge-security` appends its section to the same file.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Edit files during the audit | Report; fixes come after Gate 3 | Separation of review and implementation |
| Report 40 nitpicks | Confidence ≥ 0.8, grouped, impact-based severity | Signal over noise |
| Flag the project's established conventions in `adopt` mode | Judge against its own rules and overlays | The team chose them |
| Block a run on pre-existing debt | Summarize debt separately | Scope is the change under review |
| Findings without a fix | `file:line` + concrete change + owner skill | Actionable in one step |
| Skip the automated checks "because the code looks fine" | Run them all and record their output | Tools find what reading misses |

## Finish

- `findings.md` is written. Update `state.json` with the counts by severity and the verdict.
- Return the summary table and the verdict. In interactive mode, Gate 3 is handled by
  `forge-deliver`, or by the person when this skill runs alone: the person picks which
  findings to fix.
