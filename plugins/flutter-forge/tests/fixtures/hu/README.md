# Story fixtures (hu-v1 and earlier stories)

`hu-to-brief.md` is an instruction, not a script. These fixtures pin down the story formats that
forge-requirements must read. `tests/test_hu_template.py` checks their structure, using a small
reference reader that applies the rules of `hu-to-brief.md` → "Reading a story".

| Fixture | Format | Expected reading |
|---|---|---|
| `legacy-flat.md` | Template before hu-v1: `Platform: App (mobile)`, flat §5/§6, no `Template` field | Applies (Platform names the app); §5 and §6 are read whole |
| `hu-v1-multisurface.md` | hu-v1, `Surfaces: api · web · mobile`, `### web` + `### mobile` in §5/§6 | Applies (Surfaces contains mobile); §5 and §6 yield **only** the `### mobile` block, with no `WEB-ONLY` text |

## Manual checklist for a forge-requirements run on these fixtures

Use it when changing `hu-to-brief.md` or `hu-template.md`. It costs one interactive run per
fixture and needs no eval.

- [ ] `legacy-flat.md`:
  - [ ] the brief has the transfer screens from §5;
  - [ ] the `Platform` field doesn't trigger a "not for this app" stop;
  - [ ] the `[TBD]` limits become gaps.
- [ ] `hu-v1-multisurface.md`:
  - [ ] the brief's Screens table has `Pagos` and nothing marked `WEB-ONLY`;
  - [ ] the design list has node `20:5` only;
  - [ ] `NFR-1`, `Epic`, `Points` and `Depends on` produce no brief items.
- [ ] A story with `Surfaces: api · web` produces a "not for this app" report and no brief.
