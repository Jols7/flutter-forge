# Contributing to flutter-forge

## Ground rules

1. **No project values in skills.** Package names, paths, class names, URLs and copy come from
   `.flutter-forge/profile.yaml` or overlays. Examples use the neutral demo domain
   (`transactions`, `transfers`, `forge_demo`).
2. **No secrets, hosts, customer or employer data.** Not in skills, fixtures, evals, examples or
   CI files. The CI leak guard reads its denylist from the `LEAK_GUARD_TERMS` repository secret.
3. **Every behavior change comes with an eval.** Add or update a case under
   `plugins/flutter-forge/evals/`.
4. **Skills stay usable on their own.** `forge-deliver` composes skills, but a skill must not
   require it.

## Anatomy of a skill

```
plugins/flutter-forge/skills/forge-<name>/
├── SKILL.md            # < ~300 lines: Step 0, procedure, anti-patterns, Finish
├── references/*.md     # loaded on demand; one topic each
└── scripts/            # Python 3.9+ stdlib only, or POSIX shell; with tests in tests/
```

Every `SKILL.md` follows the same skeleton:

1. **Frontmatter.** Set `name` and `description`. The description says what the skill does and
   when to use it, with English and Spanish trigger phrases.
2. **Step 0 — Resolve.** Read the profile. Load only the references this run needs. Read
   `.flutter-forge/overlays/<name>.md` last; its rules win.
3. **Procedure.** Numbered steps with concrete outputs.
4. **Anti-patterns.** A `❌ / ✅ / Why` table.
5. **Finish.** The checks that must pass and the report format, including the run-file
   section the skill writes when `forge-deliver` invoked it.

## Adding…

| You want to support | Add |
|---|---|
| A new architecture | `forge-architecture/presets/<name>.layers.json` + `references/preset-<name>.md`; mention it in the profile schema |
| A new state manager | Templates in `forge-presentation/references/state-<name>.md`, tests in `forge-tests/references/`, audit rules in `forge-audit/references/checklist.md` |
| A new requirement or API source | A section in `forge-requirements` / `forge-api-contract` with its fallback order |
| A new security check | `forge-security/references/masvs.md` (+ script rule if it can be automated) |
| A brand-new capability | A new skill, plus its row in README and `docs/architecture.md`, plus evals |

## Development loop

```bash
claude plugin validate . --strict                      # manifests, skills, agents
python3 -m pytest plugins/flutter-forge/tests -q        # script tests
cd example/forge_demo && claude --plugin-dir ../../plugins/flutter-forge
claude plugin eval plugins/flutter-forge --case '<glob>' --runs 1
```

## Versioning and releases

- Semver in `plugins/flutter-forge/.claude-plugin/plugin.json`:
  - patch: fixes and wording;
  - minor: new skills, presets or options;
  - major: breaking changes to the profile schema or the subagent contract.
- Update `CHANGELOG.md` in the same PR. Tag releases as `v<version>`.
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) in English,
  imperative, at most 72 characters:
  - **in this repository**, the scope is the skill or area: `feat(forge-audit): …`,
    `fix(forge-e2e): …`, `docs(contract): …`, `ci: …`, `test(example): …`;
  - **in projects the agent works on**, the scope is `mobile` (see
    `forge-deliver/references/git-conventions.md`);
  - breaking changes use `!` plus a `BREAKING CHANGE:` footer and bump the major version.
- Code comments follow `forge-architecture/references/code-comments.md`; the CI runs
  `check_comments.py` on the example app.
