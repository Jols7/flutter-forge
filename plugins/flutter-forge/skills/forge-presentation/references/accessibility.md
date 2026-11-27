# Accessibility (only when `a11y: on`)

Single source of truth for semantics in the whole chain. Load this file **only** when the run's
`a11y` is `on` (brief, else `accessibility.default` in the profile). With `off`, no skill requires
or reports any of it. Other skills (`forge-tests`, `forge-audit`, `forge-figma`, blueprint) point
here instead of repeating thresholds.

**How to turn it on:** put `a11y: on` in the brief (`forge-requirements` asks for it from the
story or the requirements), or set `accessibility.default: on` in `.flutter-forge/profile.yaml`.

Test keys for Patrol (`conventions.md` § 9) are **not** accessibility and are emitted regardless of
this switch (BIT-012).

## Thresholds (cite these, do not restate them elsewhere)

| Rule | Value | Source |
|---|---|---|
| Tap target, Android | 48×48 (`androidTapTargetGuideline`) | Flutter docs, Accessibility testing |
| Tap target, iOS | 44×44 (`iOSTapTargetGuideline`) | Flutter docs, Accessibility testing |
| Tap target, WCAG minimum | 24×24 CSS px, level AA | WCAG 2.2 SC 2.5.8 |
| Text resize | usable at 200 % | WCAG 2.2 SC 1.4.4 |
| Contrast | `textContrastGuideline` | `flutter_test` |
| Labeled targets | `labeledTapTargetGuideline` | `flutter_test` |

Verified 2026-11-19 against the Flutter *Accessibility testing* page (48×48, 44×44, the four
guidelines and `ensureSemantics()` in its snippet), WCAG 2.2 (2.5.8, 1.4.4) and the Android
principles page (labels, merged groups, headings, cues other than color). The Apple HIG page could
not be read automatically, so 44 pt rests on the Flutter docs. Re-verify before changing a number.

## Rules

- **Icon-only controls** get a `tooltip:` or `Semantics(label:)`. Decorative images use
  `excludeFromSemantics: true` / `ExcludeSemantics`; meaningful images get `semanticLabel`.
- **Composite tiles** (icon + title + amount) read as one item: `MergeSemantics`.
- **Headings:** `Semantics(header: true)` on section titles.
- **Reading order:** follow visual order; use `sortKey` only when it cannot.
- **Fields and forms:** every field has a visible or semantic label; inline errors sit next to the
  field (`InputDecoration.errorText`).
- **Loading states:** give progress indicators a `semanticsLabel`.
- **Async announcements:** prefer `Semantics(liveRegion: true)`. If you call
  `SemanticsService.announce`, check `MediaQuery.supportsAnnounceOf(context)` first. The API
  changed recently and Android discourages announcements; confirm against the installed Flutter
  version.
- **Amounts and dates** are read in the user's locale (localized formatting, not raw strings).
- **Status is never conveyed by color alone**: pair red/green with a sign or an icon.
- **Text scale:** no fixed heights around text; use `Flexible` or `Wrap`. Test at 2.0.
- **`ListTile`:** `leading`/`trailing` size constraints can clash with 48×48 targets. Put the
  tappable control in its own padded widget instead of enlarging the slot.
- **Server messages:** `ValidationFailure.serverMessage` is shown as-is and may be unlocalized or
  unsuited to a screen reader; prefer a mapped, localized message.
- Labels are localizable text: add them as l10n keys (`forge-l10n`).

## Tests when `on`

- Call `tester.ensureSemantics()` before any `meetsGuideline(...)`; without it the guidelines
  measure nothing.
- Cover `androidTapTargetGuideline`, `iOSTapTargetGuideline`, `labeledTapTargetGuideline`,
  `textContrastGuideline`.
- Text-scale robustness is **not** an accessibility-only test: the responsive matrix always runs it
  (`../../forge-tests/references/widget-tests.md` § Responsive matrix, ADR 0010). With `on`, keep the
  assertion that the content is still visible, not only that no overflow was thrown.
