---
name: forge-l10n
description: Add, change or remove user-facing text in a Flutter app through its localization pipeline. It supports Flutter's gen-l10n (AppLocalizations, l10n.yaml) or intl_utils/flutter_intl (S.of(context)), as configured in the profile. It covers ARB keys in every locale, placeholders, ICU plurals and selects, number, currency and date formatting, and moving hardcoded strings into ARB. Use it when the user asks to add or change a text, label, copy, message, translation or error message ("agrega el texto", "cambia el mensaje", "traduce", "mueve los textos a ARB"), when a widget needs new strings, or when forge-deliver adds the blueprint's l10n keys.
---

# forge-l10n

All UI text goes through the project's l10n pipeline. The ARB files are the source, and
generated code is never edited by hand.

## Step 0 — Resolve

1. Read the `l10n` section of `.flutter-forge/profile.yaml`:
   - `pipeline`, `arb_dir`, `template_locale`, `locales`, `accessor` and `generate_command`.
2. If `pipeline` is `none`, ask whether to set up gen-l10n (`references/pipelines.md`) or to
   keep strings inline. Never set up a pipeline silently.
3. List the ARB files. Every locale must receive every key.
4. If `.flutter-forge/overlays/forge-l10n.md` exists, read it; its rules win, for example the
   active locale or key naming rules.

## Step 1 — Keys

- Take the keys from the blueprint, or derive them from the brief's exact copy. The story's
  messages are the source text, and design mock values are **not** strings. Amounts, names
  and dates are data.
- **Naming.** Use lowerCamelCase, named for meaning, prefixed by feature when the word is
  ambiguous: `transferMinAmountError`, not `text3`.
- **Reuse before you add.** Search for the same text first, e.g.
  `grep -n '"Continuar"' <arb_dir>/*.arb`. Shared generic keys (`commonContinue`,
  `errorGeneric`) are not duplicated per feature.
- Write the template locale first. For other locales, translate when you are confident.
  Otherwise mark the value `[TODO-translate] <source text>` and list it in the report. Never
  leave a key missing.

## Step 2 — Messages

Use `references/arb-patterns.md`:
- **Placeholders** with types; never build sentences by concatenation.
- **ICU plurals and selects** instead of `if (count == 1)` in Dart.
- **Money and dates** are formatted in Dart (`NumberFormat.currency`, `DateFormat` with the
  current locale) and passed as `String` placeholders. Use the ARB `format` attribute only
  when the whole project already does.
- Backend codes (`BusinessFailure.code`) map to keys in the widget layer and never come from
  backend text, unless the contract guarantees localized copy.

## Step 3 — Generate and use

```bash
<l10n.generate_command>        # flutter gen-l10n  |  dart run intl_utils:generate
```

Use the profile's `accessor` in widgets: `AppLocalizations.of(context).transferTitle`, or
`S.of(context).transferTitle`. State managers never read l10n; they expose enums or failures.

## Anti-patterns

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| `Text('Transferir')` | `Text(l10n.transferAction)` | All UI text is localized |
| Add the key to one ARB only | Every locale (`[TODO-translate]` if unsure) | Missing keys break generation or fall back silently |
| `l10n.youSent + ' ' + amount` | `"transferSent": "Enviaste {amount}"` | Word order differs between languages |
| Hand-edit generated l10n files | Edit ARB, regenerate | Overwritten on the next run |
| Mix gen-l10n and intl_utils | Use the profile's pipeline only | Two sources of truth |
| `'$count movimientos'` with manual singular | ICU plural | Plural rules belong to the message |
| Currency built inside the ARB (`"${amount} MXN"`) | Format in Dart, pass as String | Locale-aware separators and symbols |
| Strings in state managers (`S.current`) | Enums/failures in state; text in widgets | Testable state; locale changes apply |

## Finish

- Every ARB file is valid JSON (watch for trailing commas) and has the same set of keys.
- Generation succeeds and analyze is clean.
- Report: keys added or changed (and where they are used), keys reused, and pending translations.
