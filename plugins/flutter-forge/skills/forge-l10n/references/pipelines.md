# Pipelines

## gen-l10n (Flutter default) — `pipeline: gen-l10n`

1. Run `flutter pub add flutter_localizations --sdk=flutter` and `flutter pub add intl`.
2. Add `flutter: generate: true` to `pubspec.yaml`.
3. Create `l10n.yaml`:
   ```yaml
   arb-dir: lib/l10n
   template-arb-file: app_en.arb
   output-localization-file: app_localizations.dart
   nullable-getter: false
   ```
   On recent Flutter versions, check `flutter gen-l10n --help` for whether to generate into
   the source tree (`synthetic-package: false`, `output-dir`). Follow what the installed SDK
   documents.
4. In `MaterialApp`, set `localizationsDelegates: AppLocalizations.localizationsDelegates` and
   `supportedLocales: AppLocalizations.supportedLocales`.
5. Accessor: `AppLocalizations.of(context)`. Generate with `flutter gen-l10n`; `flutter run`
   also regenerates.

## intl_utils / flutter_intl — `pipeline: intl_utils`

- The config lives in a `flutter_intl:` block in `pubspec.yaml` (`enabled`, `main_locale`,
  `class_name`, default `S`).
- ARB files are `lib/l10n/intl_<locale>.arb`. Generated code goes to `lib/generated/`.
- Generate with `dart run intl_utils:generate`, or through the IDE plugin on save.
- Accessor: `S.of(context)`. `S.current` works without a context, but state managers still
  must not use it in new code (see SKILL anti-patterns).
- Don't add `l10n.yaml` or `flutter gen-l10n` to such a project. Mixing the two pipelines
  creates two sources of truth.

## Migrating intl_utils → gen-l10n

Only when the person explicitly asks for it. Rename the ARB files, add `l10n.yaml`, and replace
`S.of` with `AppLocalizations.of` (a mechanical change). Delete `lib/generated/intl` only after
the build is green. It is a separate change from any feature.
