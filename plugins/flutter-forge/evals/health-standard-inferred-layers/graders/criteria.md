---
type: llm
weight: 2
---

The answer uses the standard-depth evidence the way forge-health defines it. It must show all of these:
- The layer map is described as **inferred** from folder names, with its limits: it is a draft, the
  unmapped folders (`lib/core/services`, `lib/services`, `lib/core`) and the two barrel/locator
  blind spots are named, and the numbers per layer are marked `inferred layer map`, not presented as the team's rules.
- Architecture statements are about what the code does ("real"), compared with what the docs say
  ("declared"): docs mention getx and provider, code uses provider. The drift is named and the choice
  of which one changes is left to the team (a human decision).
- The profile draft is treated as detected values, not as a declaration: the mode stays unset and is
  recommended with evidence, and the answer does not claim to have written `.flutter-forge/profile.yaml`
  or to have run `forge-profile`.
- The files to open come from the review queue, in its order, security items first, and the list stays
  within 30 files. Nothing like "read the whole tree" appears.
- The violation pairs are not turned into findings without reading code: `core_ui -> composition` and
  `presentation -> core_storage` are marked as candidates to confirm, since a barrel such as
  `lib/core/core.dart` can create false positives.
- No secret value is written; the `.env` item is kind + location + rotate.
