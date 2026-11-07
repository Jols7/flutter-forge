---
name: forge-blueprint
description: Design every class a Flutter feature needs before any code is written, from the brief, the design notes and the API contract, following the project's architecture preset. It covers pages, state managers and their sealed states, widgets (reuse or create), repository contracts and implementations, data sources, entities, DTOs, mappers, use cases when they are earned, routes, DI registrations, l10n keys, and a test plan mapped to acceptance criteria. Use it after requirements and contract are known, when the user asks "qué clases necesito", "diseña la solución", "arma el blueprint", "planea la implementación del feature", or when forge-deliver reaches the blueprint phase (Gate 2).
---

# forge-blueprint

Output: `.flutter-forge/runs/<slug>/blueprint.md`, the plan that the implementation skills
execute file by file and that `forge-audit` compares against later.

## Step 0 — Resolve

1. Read `.flutter-forge/profile.yaml`. Load `forge-architecture` and the reference for the
   active preset; it defines where each class goes and how it is named.
2. Read these run files when they exist:
   - `brief.md` (required);
   - `contract.md`;
   - `design.md` (output of `forge-figma`).

   With no `contract.md`, the data part of the blueprint is marked **provisional**.
3. Open `project.canonical_feature` in `adopt`/`improve` mode, or the closest existing
   feature. Mirror its real shapes, which win over generic templates.
4. If `.flutter-forge/overlays/forge-blueprint.md` exists, read it; its rules win.

## Step 1 — Derive the classes

Apply `references/derivation-rules.md`. In short:

| From | Derive |
|---|---|
| Brief screens + states | One page per route; one state manager per screen (or per flow when screens share live state); a sealed state per independently-loading region |
| Brief rules/validations | Validators (pure functions/value objects in domain); use case only when the rule set is earned |
| Design (`design.md`) | Widgets via the reuse ladder: reuse, extend (optional param), create (feature-local or shared) |
| Contract | One data source per backend resource; one DTO per distinct JSON object shape; request DTOs for bodies |
| Brief data needs | Entities shaped for the UI and logic (not a copy of the DTO); one mapper per DTO→entity (and entity→request DTO) |
| Endpoints grouped by resource | One repository contract + impl per resource/aggregate, never one per screen |
| Navigation in/out | Route definitions, arguments, and the **change at the entry point** (an existing file) |

## Step 2 — Map every value end to end

Fill the **value trace** table: screen value → entity field → DTO field → conversion. This
table forces three decisions:
- every displayed value has a source;
- every nullable DTO field gets a default or an explicit nullable entity field;
- every conversion is decided: dates, money, enums and unlocalized text.

Each row without a source becomes a gap.

## Step 3 — Plan the tests

For each class, list its test file and its cases, tagged with the acceptance criteria
(`AC-n`) they cover. Use `../forge-tests/references/test-matrix.md` for what each kind of
class must test. Add the E2E flow: entry routine, steps, checkpoints and data preconditions.
Every AC must appear at least once. An AC with no test is listed as uncovered, with the reason.

## Step 4 — Write `blueprint.md`

Use the format in `references/blueprint-template.md`. Size it to the feature: a one-screen
feature fits in ~120 lines. List files in implementation order: domain → data → presentation
→ DI/routes → l10n → tests.

## Step 5 — Gate 2

- **Interactive.** Present the file tree, the class table and the open decisions (for example,
  "use case for transfer validation: yes/no?"). Wait for approval or changes, then record the
  decision with today's date.
- **Unattended.** Continue unless a blocking gap appeared. Record every judgement call under
  **Assumptions**.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| One repository per screen | One per backend resource/aggregate | Screens change; resources are stable |
| Entity = DTO with another name | Entity shaped for the UI/logic; mapper absorbs differences | A backend change should only touch DTO + mapper |
| A use case per repository method | Use case only when earned (`forge-architecture`) | Pass-through classes add files, not value |
| Abstract data-source interfaces "for testing" | Concrete classes (mocktail mocks them) | Speculative generality |
| One state class with `isLoading`, `hasError`, `data` flags | Sealed states per independently-loading region | Invalid combinations become unrepresentable |
| Creating a widget that the catalog already has | Reuse ladder: exact → extend with optional param → create | Duplicates drift apart |
| Skipping the entry-point change | List the existing file and the exact change | The flow is unreachable otherwise |
| Test plan "add tests" | Per class: file + cases + AC ids | Coverage is checked against it |

## Finish

- Write `blueprint.md`. Update `state.json` with `phase: blueprint` and the file count by layer.
- Report:
  - number of files to create and to modify, by layer;
  - decisions taken;
  - ACs without tests (should be none);
  - gaps that remain open.
