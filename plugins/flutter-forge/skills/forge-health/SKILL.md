---
name: forge-health
description: Whole-repository health baseline for a Flutter project, written to health-report.md. Deterministic scripts measure git churn, coverage from an existing lcov.info, dependencies, widget sizes, layer violations (the forge-audit checker) and the security scanners; the model then confirms the top signals and writes the report. The report maps the real architecture against the declared one with debt per layer, lists security, performance, test and dependency findings, and ends with a backlog ranked by risk × change frequency ÷ effort (quick wins apart from big bets), an incremental path per adopt/improve/migrate mode, and the decisions that need a human. It never edits code. It is not a diff review (that is forge-audit) and not a security-only review (forge-security). Run it by hand, when taking over an unfamiliar repo or before planning a cleanup. Triggers include "forge-health", "salud del repositorio", "línea base del proyecto", "auditoría del proyecto completo", "baseline", "health report", "qué deuda tiene este repo", "por dónde empiezo a limpiar".
disable-model-invocation: true
context: fork
model: sonnet
allowed-tools: Read, Grep, Glob, Write, Bash(python3 *), Bash(git log *), Bash(git rev-parse *)
---

# forge-health

A health baseline answers "what state is this repo in, and what should we fix first?". It is
the whole-repo sibling of `forge-audit` (which judges one diff or run). It reports and
prioritizes; it **never edits project code**. It writes only inside the health folder: the
report, plus `metrics.json`, `layers.draft.json` and `profile.draft.yaml` from the snapshot
script. The two drafts are proposals; neither is ever placed where the repo reads it as its own.

Cost control comes from the split of work. Scripts count; you judge. The snapshot below is
already in your prompt, so do not walk the tree or re-run collectors. Open a file only when
a number in the snapshot needs confirming.

## Snapshot (collected before you started)

!`python3 "${CLAUDE_SKILL_DIR}/scripts/health_snapshot.py" --root . --outdated`

Extra instructions from the person (may be empty, such as a focus area or an output folder): $ARGUMENTS

If the snapshot says `no pubspec.yaml`, stop and tell the person to start Claude Code in the
Flutter package folder (for a monorepo, the app package).

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml` when it exists: `architecture.mode`, `architecture.preset`,
   `security.level`, `testing.coverage_min`, `requirements.language`. The report is written in
   `requirements.language`, otherwise in the language of the person's request.
2. **No profile (a repo you did not set up).** Say so at the top of the report. The snapshot
   drafts one (`profile.draft.yaml`, line `Profile:`): read it as *detected* values, never as
   what the team declared, and the mode stays `unset`. Layer rules come from, in this order:
   the repo's own `layers.json`; the `Layer map: INFERRED draft` (`layers.draft.json`, built
   from folder names and file suffixes, so mark every architecture statement
   `inferred layer map` and list its unmapped folders); the assumed preset
   (`assumed preset`). A draft is evidence for the report, not a decision for the team.
3. Read `.flutter-forge/overlays/forge-health.md` and, for severity remaps,
   `overlays/forge-audit.md` and `forge-security.md`. Their rules win. Accepted risks listed
   there are reported as accepted, with their owner and expiry, not as findings.
4. If the snapshot shows `mapping_suspect` (more than half the files match no layer, which
   is rare once a map is inferred), the layer numbers are unreliable. Report that as the first finding: "layer map does not fit
   this repo", with the folders that are unclassified. Do not rank layer debt from it.

## Step 1 — Read the snapshot, choose what to confirm

Open files from the snapshot's **Review queue**, best first, at most **30 files** (15 when
the person asked for a quick pass). The queue is ranked by scanners first, then by change
frequency, layer violations, low coverage and size, so work down it and stop early once the
picture is clear. It is mostly this order, which you may use to break ties:
1. every `critical` or `high` scanner finding (location and kind only);
2. the top violating files and the layer pair with the most violations;
3. the hot files with the lowest coverage;
4. the longest `build()` methods and the largest widgets that are also hot;
5. anything under `DRIFT:` or `Needs decision`.

For anything else, use `python3 "${CLAUDE_SKILL_DIR}/scripts/health_snapshot.py" --root . --no-write --section <name>`
instead of reading files. Never read generated code (`*.g.dart`, `*.freezed.dart`, `generated/`).

## Step 2 — Confirm and write findings

- Judge each candidate against `../forge-audit/references/severity.md` (scale
  `critical/high/medium/low/improvement`), the checklist in `../forge-audit/references/checklist.md`
  for the file kinds you opened, and `../forge-security/references/masvs.md` for security.
- Report only findings with confidence ≥ 0.8. Group repeated instances into one finding with
  a file list. Lower-confidence leads go to **Notes** and are not counted.
- A finding has: `id` (`H-1`…), severity, category (`architecture`, `security`, `performance`,
  `tests`, `dependencies`), `file:line`, what, why, fix, confidence, `owner` (the forge skill
  that would fix it) and an **effort** (`S`, `M`, `L`).
- A number from a script is evidence, but it is not a finding by itself. A 0%-covered file may
  hold only an abstract class; a long `build()` may be a flat list of constants. Read it first.
- **Never write a secret value, in the report or in your reply.** That covers tokens, API
  keys, `.env` contents, keystore and key passwords, and any password-like literal you see
  while reading a file, including ones in Gradle, plist or JSON files. Write the kind, the
  location (`file:line`) and "rotate it". If an example helps, use `<redacted>`.
- Before condemning a pattern that looks wrong but deliberate, check `git blame` or a nearby
  comment. If intent is unclear, put it in Section 9 as a question.

## Step 3 — Architecture: real versus declared

Build Section 2 from `declared`, `drift`, the guess in `Stack`, the per-layer table and the
import edges:
- **Declared:** profile, then CLAUDE.md / README / docs keywords. Say which source you used.
- **Real:** the architecture guess with its evidence, the state manager used in code, and the
  import edges that actually exist.
- A table of debt per layer: files, violations, commits in the window, and one sentence on
  the dominant problem. Debt in a layer nobody changes is low priority.
- Name each drift (declared X, real Y) and say whether the code or the documentation should
  change. That choice is the team's, so it also goes to Section 9.

## Step 4 — Prioritize the backlog

Follow `references/prioritization.md`. In short:

`priority = risk × change frequency ÷ effort`, with risk 1–5 from severity, frequency 1–5 from
commits in the window, and effort S=1, M=2, L=3. Security and money findings are listed first
whatever their frequency. Stable code that is ugly but never changes is not scheduled.

Split the result into **Quick Wins** (effort S, high priority) and **Big Bets** (effort L, high
priority, each with a first reversible step). Everything else is "later" or "not worth it", with
the reason. Never put a refactor ahead of the tests that protect the zone it touches.

## Step 5 — Incremental path by mode

Use `references/prioritization.md` § Mode. The path is phases, not a rewrite, and each phase
ends in something shippable:
- `adopt`: the repo's own rules are the standard; only bugs, security and tests in hot zones
  enter the backlog. No style or architecture items.
- `improve`: same layout, higher quality in new and touched code; legacy upgrades are
  `improvement` and never block.
- `migrate`: new features in Clean next to the old code, one feature at a time, with
  characterization tests before anything moves.
- `unset`: recommend one mode with the evidence (conventions, drift, hot debt) and mark the
  choice as a human decision. Do not run `forge-profile` or write a profile.

## Step 6 — Decisions that need a human

Use `references/human-decisions.md`. For every trigger that applies to this repo, write a row:
the decision, why it is a human call, your recommendation with the evidence, the risk level
(🔴 always human · 🟠 human reviews closely · 🟢 agent may decide, human samples) and the
cost of deciding wrong. Typical rows: the mode, which state manager wins if several exist,
accepting a security risk, drift between declared and real architecture, any rule about money,
and a migration that touches a hot zone with no tests.

## Step 7 — Write the report

Fill `references/report-template.md`. Write `health-report.md` to `.flutter-forge/health/`
(or the folder the person named in the arguments). Use the Write tool for that file and
nothing else. Keep it under about 400 lines; link to `metrics.json` instead of pasting data.

Before you finish, reread the draft once for credential-like literals (quoted strings next to
`password`, `secret`, `key`, `token`, or in parentheses after a finding) and replace each with
`<redacted>`. The same applies to your final reply.

Each backlog item appears in one bucket only. A security or money item that is also cheap stays
under "Do now" and gets its priority number there; do not repeat it under Quick Wins.

Include a **Limits** section: the commands run, what was not measured (no lcov, `pub outdated`
not run, no git history, assumed preset), and the reminder that a clean scanner is not proof
of safety: scanners match patterns and cannot judge business logic or authorization.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Explore the tree file by file | Start from the snapshot's review queue; open ≤ 30 files | Tokens go to judgment, not counting |
| Rank by severity alone | Risk × frequency ÷ effort | Cold, ugly code is not urgent; hot, fragile code is |
| Treat a script count as a finding | Read the code, then report at confidence ≥ 0.8 | Counts have false positives |
| Judge a repo against Clean by default | Judge against its profile or its own layout; mark `assumed preset` | The team's architecture is a decision |
| Propose a rewrite | Phases, each shippable and reversible | Rewrites without a measured pain are the costliest mistake |
| Decide the mode, the state manager or a risk acceptance | Recommend with evidence, list it in Section 9 | Those are human decisions |
| Edit code, run formatters or `pub upgrade` | Report the fix and its owner skill | Baselines are read-only |
| Paste secret values or customer data | Kind + location + "rotate it" | The report gets shared |

## Finish

- `health-report.md` and `metrics.json` exist in the output folder, next to `layers.draft.json`
  and `profile.draft.yaml` when the snapshot produced them. Say that both drafts are
  proposals for `forge-profile` to start from, not the team's decisions.
- Reply with: the traffic-light summary, the top 3 quick wins, the top big bet, the number of
  human decisions, and the report path. Keep it short; the details live in the file.
- Offer the next step as a choice, not an action: which quick win to start with, and which
  forge skill owns it (`forge-tests`, `forge-data-layer`, `forge-presentation`, `forge-security`).
