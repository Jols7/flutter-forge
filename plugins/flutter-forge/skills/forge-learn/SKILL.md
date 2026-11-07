---
name: forge-learn
description: Teach flutter-forge a project-specific convention, by writing or updating an overlay in .flutter-forge/overlays/<skill>.md or a value in .flutter-forge/profile.yaml. Each rule gets a concrete example, the reason behind it, and a severity for the audit. Patterns that look useful to every project are proposed as contributions to the plugin. It can also turn findings that keep recurring in reviews into overlay rules. Use it when the user says "recuerda que en este proyecto…", "aprende esta convención", "siempre hazlo así aquí", "agrega esta regla al agente", "personaliza la skill X para este proyecto", or after forge-profile or a review proposes overlays.
---

# forge-learn

This is how flutter-forge grows without hardcoding projects. A convention becomes a small,
reviewable overlay that every later run applies. The overlay format and the precedence rules
are in `references/overlays.md`.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml` and list `.flutter-forge/overlays/`.
2. If `.flutter-forge/overlays/forge-learn.md` exists, read it; its rules win.

## Step 1 — Classify what was taught

| It is… | Goes to |
|---|---|
| A value: a path, class name, command, flavor, locale or enum choice | `profile.yaml` (edit the key) |
| An import or layer rule: "screens may import the core barrel" | `.flutter-forge/layers.json` (`allowed_imports`, `paths`, `barrels`) |
| A convention with code, an anti-pattern or a gotcha | `overlays/<skill>.md` of the skill that applies it |
| Something every Flutter project would benefit from | a proposal for the plugin (Step 4); keep a project overlay meanwhile |

Pick the **single** skill that would apply the rule. Examples:
- page and state wiring → `forge-presentation`;
- API, DTO and auth header → `forge-data-layer`;
- review severities → `forge-audit`.

When two skills need the rule, write it in the owning skill. Add a one-line pointer in the
other skill's overlay, rather than a copy.

## Step 2 — Write the rule

Every rule has these parts, kept short:

```markdown
## Rules
- **Pages with footer buttons wrap `build` in `Theme(dividerTheme: transparent)`.** `Scaffold`
  draws a divider above `persistentFooterButtons`.
  ```dart
  return Theme(
    data: Theme.of(context).copyWith(dividerTheme: const DividerThemeData(color: Colors.transparent)),
    child: …,
  );
  ```
  Audit: medium when missing. (learned 2026-11-06, source: <who/why>)
```

- Write a rule, not a story. Include a code example when the rule is about code.
- Give its **audit severity**, so `forge-audit` can enforce it.
- Add a `learned` date and a source. Overlays are reviewed like code.
- Before adding, search the existing overlays for a conflicting or duplicate rule. Update the
  existing rule instead of adding a contradictory one.

## Step 3 — Confirm

Show the diff of the overlay, profile or `layers.json` change and wait for confirmation
(interactive). An overlay written by mistake corrupts every run, so this step is never
skipped. Unattended runs never write overlays; they put proposals in the report.

## Step 4 — Generic patterns

When the rule would help any project, for example a better default, a missing check or a new
preset, draft a contribution:
- the target file in the plugin (skill, reference, preset or checklist);
- the change;
- the eval case that proves it.

Offer to save it as `.flutter-forge/proposals/<slug>.md`, so it can be submitted to the
flutter-forge repository as an issue or PR.

## Learning from reviews

When the same finding category shows up in 3 or more runs of the same project, for example
in `runs/*/findings.md`, propose either:
- a rule that **prevents** it in the implementing skill's overlay, or
- a severity change in the audit overlay, when the team decides that it is acceptable.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Put code conventions in CLAUDE.md | Overlay of the owning skill | Loaded only when relevant; no duplication |
| Copy the rule into several overlays | One owner, pointers elsewhere | One place to update |
| Overlays that restate the skill | Only differences | Overlays stay small and readable |
| Write overlays without confirmation | Show the diff, then write | A wrong overlay silently affects every run |
| Encode secrets or hosts in overlays | Where they live (env var, secret store) | Overlays are committed |

## Finish

Report:
- the files changed and the rule ids or headings;
- the skills affected;
- proposals created for the plugin.
