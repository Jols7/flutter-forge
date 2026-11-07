# Mapping a project onto layer rules

`check_layers.py` classifies each Dart file into a layer by the **first** matching glob in the
order the layers are listed. It then checks the file's imports against that layer's
`may_import` list, its `forbidden_imports` and the `cross_feature` rule.

## Glob semantics

- Paths are relative to the project root and use `/`.
- `*` matches any characters, **including** `/`. `**` is accepted as a synonym.
- The order of the layers matters. Put specific globs first: `lib/features/*/domain/**`
  must come before `lib/features/**`.
- `ignore` globs (generated files) are never classified.
- `features_root` is used to extract the feature name: it is the first path segment after the
  root. Cross-feature rules depend on it.

## Procedure

1. Copy the closest preset: `clean.layers.json` if the project has domain/data/presentation
   splits, otherwise `layered.layers.json`.
2. For every layer, replace `paths` with the project's real folders. Example for an app with
   `lib/screens/<feature>/{pages,provider,widgets}`, `lib/core/services/network/api/endpoints/**`,
   `lib/core/services/network/dtos/**`, `lib/core/services/repositories/**` and
   `lib/domain/**` (models):

   ```json
   "api":          {"paths": ["lib/core/services/network/api/**"], …},
   "dtos":         {"paths": ["lib/core/services/network/dtos/**"], …},
   "repositories": {"paths": ["lib/core/services/repositories/**"], …},
   "models":       {"paths": ["lib/domain/**"], …},
   "presentation": {"paths": ["lib/screens/**"], …},
   "core_ui":      {"paths": ["lib/widgets/**", "lib/flavors/theme/**"], …}
   ```
3. Set `features_root` (`lib/screens` above).
4. Run the checker with `--summary`. Read the top violation kinds:
   - **Many `unclassified` files.** Add the missing folders, often `lib/services/**` →
     `composition` or `lib/core/utils/**`.
   - **One import repeated across the codebase that the team considers fine.** For example a
     `core.dart` barrel imported everywhere. Add a narrow `allowed_imports` entry and note why
     in `description`.
   - **Real violations.** Leave them. In `adopt` mode they become audit findings only for
     *new or changed* files. Pre-existing ones are summarized as debt and never block a run.
5. Barrels: if a project barrel re-exports several layers, imports through it can't be
   classified. Set `"barrels": {"lib/core/core.dart": "core_utils"}` to declare the barrel's
   layer, and note in the overlay that barrels hide layer violations.

## Fields reference

| Field | Meaning |
|---|---|
| `paths` | Globs assigning files to the layer |
| `may_import` | Layer names this layer may import; `"*"` = any |
| `forbidden_imports` | Import prefixes banned in this layer (`package:dio/`) |
| `allowed_imports` | Exceptions to `forbidden_imports` (`package:flutter/foundation.dart`) |
| `cross_feature.allowed_layers` | Layers of *another* feature that may be imported |
| `barrels` | Barrel file → layer it represents |
