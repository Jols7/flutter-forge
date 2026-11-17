# ADR 0006 — `forge-health` standard depth: infer first, then read

- Status: accepted
- Date: 2026-11-16

## Context

The first real run of `forge-health` on a large repo without a profile read few files. The
cause was not a missing auditor. The assumed preset classified only 28% of the files, so the
skill had to drop the layer analysis, and a fixed cap of 15 files left the rest unexamined.
Running `forge-audit`, `forge-architecture` and `forge-profile` for every repo would multiply
the cost, and a forked skill cannot start subagents, so it cannot orchestrate them anyway.

## Decision

- Add a `--depth quick|standard` switch to `health_snapshot.py`; `standard` is the default.
  `quick` is the previous behavior (assumed preset, queue of 15).
- `infer_layers.py`: tests both presets; when neither classifies at least 80% of the files,
  it builds a draft `layers.json` from folder names and file suffixes, reusing the `layered`
  preset's import rules. Nested `widgets/`, `models/` and similar folders stay inside their
  module. On the repo above, coverage went from 28% to 99% with no model tokens.
- `draft_profile.py`: renders a `profile.yaml` draft from `detect_project.py` and the layer
  inference. `architecture.mode` stays empty (a human decision), values the code cannot answer
  are listed as "Not detected", and the script refuses to write `.flutter-forge/profile.yaml`.
- `review_queue`: files ranked by scanner findings, change frequency, layer violations and test
  and size signals, capped at 30 (15 for `quick`). The model works down the list.
- Drafts go to `.flutter-forge/health/` (`layers.draft.json`, `profile.draft.yaml`). A repo's own
  `layers.json` and profile always win. Nothing is installed in the audited repo.

## Consequences

- The cost grows with the file cap only: the new scripts use no tokens, and the extra files are
  the 15 more the model may open. Not measured yet (gap B4).
- Roles come from names, so a folder such as `services` or `providers` can stay unmapped or be
  wrong. The report marks every architecture statement `inferred layer map`.
- Not done, by design: running `forge-audit` per hot zone. A `deep` level would need the skill to
  run without `context: fork` so it can delegate; decide it after measuring `standard`.
