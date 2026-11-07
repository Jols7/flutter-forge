# Overlays — project-specific versions of a skill

The skills are generic. An overlay holds a project's own version of a skill **inside the
project**, so the plugin stays generic and the project owns its rules.

```
.flutter-forge/overlays/<skill-name>.md     # e.g. forge-data-layer.md
```

## Format

```markdown
---
skill: forge-data-layer        # must match the skill name
mode: extend                   # extend (default) | replace
---

## Rules
- Every API method receives the auth token as its first parameter and sets the
  `Authorization: Bearer` header itself; the interceptor only handles 401/403.

## Anti-patterns
| ❌ Don't | ✅ Do | Why |
|---|---|---|
| Rely on the interceptor for auth | Set the header in each Api method | The interceptor forces logout on 401 |

## Templates
<code blocks that replace the skill's default templates>
```

- **`extend`**: the skill applies its own rules, then the overlay's. When the two conflict,
  the overlay wins.
- **`replace`**: an overlay section whose heading matches a skill section (`## Templates`,
  `## Naming`, …) replaces that section entirely. Sections the overlay doesn't mention keep
  the skill's content.

## How skills load them

Each skill does this as the last action of its Step 0: *"If
`.flutter-forge/overlays/<this skill>.md` exists, read it now; its rules win over this file."*
Overlays are read on demand only, never preloaded, so they cost nothing in sessions that don't
use that skill.

## What belongs where

| Kind of knowledge | Put it in |
|---|---|
| Values: paths, class names, commands, enums | `profile.yaml` |
| Layer/import rules that differ from the preset | `layers.json` |
| Conventions with code, project anti-patterns, gotchas a skill must apply | `overlays/<skill>.md` |
| What every session needs to know (commands, one-paragraph architecture) | the project's `CLAUDE.md` (keep it short, and point to `.flutter-forge/`) |
| A pattern useful to **every** project | a contribution to the plugin (preset, reference or skill) — see CONTRIBUTING.md in the flutter-forge repository |

`forge-learn` writes overlays for you: tell it "remember that in this project…" and it adds
the rule to the right overlay, with an example.

## Keep overlays small

An overlay states only the differences. If it starts repeating the skill, delete those parts.
If it grows past ~150 lines, the project probably needs a custom preset (`layers.json` +
`architecture.preset: custom`) rather than a longer overlay.
