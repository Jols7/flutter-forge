"""Tests for forge-figma's scripts (theme_tokens.py, lint_design.py) and forge-audit's check_responsive.py.
Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "skills", "forge-figma", "scripts")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tokens_mod = load("theme_tokens")
lint_mod = load("lint_design")
AUDIT_SCRIPTS = os.path.join(os.path.dirname(HERE), "skills", "forge-audit", "scripts")
_spec = importlib.util.spec_from_file_location("check_responsive", os.path.join(AUDIT_SCRIPTS, "check_responsive.py"))
resp_mod = importlib.util.module_from_spec(_spec)
import sys as _sys
_sys.path.insert(0, AUDIT_SCRIPTS)
_spec.loader.exec_module(resp_mod)


def write(root: str, rel: str, text: str) -> str:
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


APP_COLORS = """
import 'package:flutter/painting.dart';
class AppColors {
  static const white = Color(0xFFFFFFFF);
  static Color get primary => ThemeManager.colors.primary;
  static Color get onSurface => ThemeManager.colors.onSurface;
  static Color get outlineVariant => ThemeManager.colors.outlineVariant;
}
"""
BRAND_COLORS = """
class BrandColors extends ColorsTheme {
  @override
  Color get primary => const Color(0xFFFF7E2B); // Schemes/Primary
  @override
  Color get onSurface => const Color(0xFF221A15);
  @override
  Color get outlineVariant => const Color(0xFFD7C2B9);
}
"""


class ThemeTokensTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        write(self.root, "lib/core/app_colors.dart", APP_COLORS)
        write(self.root, "lib/theme/brand_colors.dart", BRAND_COLORS)
        write(self.root, "pubspec.yaml", "flutter:\n  fonts:\n    - family: DMSans\n      fonts:\n        - asset: a.ttf\n")
        files = tokens_mod.dart_files(self.root)
        literals, delegates = tokens_mod.scan(files)
        self.tokens = tokens_mod.accessor_tokens("AppColors", literals, delegates)

    def tearDown(self):
        self.tmp.cleanup()

    def match(self, figma: str, value: str) -> dict:
        return tokens_mod.match(figma, tokens_mod.parse_hex(value), self.tokens, "AppColors")

    def test_literal_and_delegated_members_resolve_to_values(self):
        self.assertEqual(self.tokens["white"]["values"], ["FFFFFF"])
        self.assertEqual(self.tokens["primary"]["values"], ["FF7E2B"])

    def test_exact_by_name_and_value(self):
        result = self.match("Schemes/Primary", "#ff7e2b")
        self.assertEqual((result["status"], result["accessor"]), ("exact", "AppColors.primary"))

    def test_same_name_different_value_is_never_silent(self):
        result = self.match("Schemes/Primary", "#2e6b5e")
        self.assertEqual(result["status"], "value-differs")
        self.assertEqual(result["project_values"], ["#FF7E2B"])

    def test_overlay_with_a_base_nobody_has_is_reported(self):
        result = self.match("State Layers/Primary/Opacity-16", "#8d4e2a29")
        self.assertEqual(result["status"], "overlay")
        self.assertEqual(result["candidates"], [])
        self.assertIn("no accessor has base #8D4E2A", result["note"])

    def test_overlay_with_a_known_base_lists_candidates(self):
        result = self.match("State Layers/Primary/Opacity-16", "#ff7e2b29")
        self.assertEqual(result["candidates"], ["AppColors.primary"])

    def test_value_only_match_is_flagged_and_a_gap_is_a_gap(self):
        self.assertEqual(self.match("Schemes/On Primary", "#ffffff")["status"], "by-value")
        self.assertEqual(self.match("Schemes/Nope", "#123456")["status"], "gap")

    def test_camel_case_and_hex_parsing(self):
        self.assertEqual(tokens_mod.camel("Schemes/On Surface Variant"), "onSurfaceVariant")
        self.assertEqual(tokens_mod.parse_hex("#8d4e2a29"), ("8D4E2A", 0.16))
        self.assertIsNone(tokens_mod.parse_hex("not-a-color"))

    def test_fonts_are_read_from_pubspec(self):
        self.assertEqual(tokens_mod.fonts(self.root), ["DMSans"])

    def test_font_names_compare_without_spaces_or_case(self):
        self.assertEqual(tokens_mod.norm_font("DM Sans"), tokens_mod.norm_font("DMSans"))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            tokens_mod.main(["--root", self.root, "--accessor", "AppColors", "--font", "DM Sans", "--font", "Montserrat"])
        self.assertIn("font-missing Montserrat", out.getvalue())
        self.assertNotIn("font-missing DM Sans", out.getvalue())

    def test_dynamic_scheme_has_no_static_values(self):
        write(self.root, ".flutter-forge/profile.yaml", "design:\n  colors: Theme.of(context).colorScheme\n")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(tokens_mod.main(["--root", self.root, "--match", "Schemes/Primary=#2e6b5e"]), 0)
        self.assertIn("dynamic", out.getvalue())
        self.assertFalse(tokens_mod.IDENT.match(tokens_mod.profile_colors(self.root)))


GOOD_DESIGN = """# Design — Transfer
Figma: file/frame · Read: 2026-11-19 · Mode: feature

## Tokens
| Figma token | Figma value | Flutter | Status |
|---|---|---|---|
| Schemes/Primary | #ff7e2b | AppColors.primary | ✓ |
| State Layers/Primary/Opacity-16 | #8d4e2a @16% | — | **gap D-1** |

## Gaps
| Id | Design value | Nearest | Difference | Decides |
|---|---|---|---|---|
| D-1 | #8d4e2a @16% | primary @16% | warmer tint | team |

## Components
| Figma component | Decision | Widget / path | Notes |
|---|---|---|---|
| Button | reuse | PrimaryButton (`lib/widgets/primary_button.dart`) | |
| Card | create (feature) | features/x/card.dart | |

## Screens
### Transfer (node 12:345) — layout
Column(gap 16)

#### Measures
| Element | Size | Padding | Gap | Radius / border | Alignment | Type role | Color token |
|---|---|---|---|---|---|---|---|
| Card | flexible | 16 | 16 | 16 / 1 | center | — | surfaceContainerLow |

### States
| State | Node | Shows |
|---|---|---|
| loading | 12:410 | skeleton |

## Responsive behavior
| Component | Width rule | When space runs out | Source |
|---|---|---|---|
| Card | fill | grows in height | Figma |

## References
| Screen / state | Node | Capture |
|---|---|---|
| Transfer | 12:345 | `refs/transfer.png` |
"""


class LintDesignTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        write(self.root, "lib/widgets/primary_button.dart", "class PrimaryButton {}")
        write(self.root, "out/refs/transfer.png", "png")

    def tearDown(self):
        self.tmp.cleanup()

    def lint(self, text: str) -> dict:
        path = write(self.root, "out/design.md", text)
        return lint_mod.lint(path, self.root, None)

    def rules(self, report: dict, severity: str = "error") -> set:
        return {f["rule"] for f in report["findings"] if f["severity"] == severity}

    def test_complete_design_has_no_errors_and_counts_its_parts(self):
        report = self.lint(GOOD_DESIGN)
        self.assertEqual(self.rules(report), set())
        self.assertEqual(report["summary"]["gaps"], 1)
        self.assertEqual((report["summary"]["reuse"], report["summary"]["create"]), (1, 1))
        self.assertEqual(report["summary"]["captures"], 1)

    def test_missing_measures_and_responsive_sections_are_errors(self):
        text = GOOD_DESIGN.replace("#### Measures", "#### Notes").replace("## Responsive behavior", "## Other")
        self.assertIn("missing-section", self.rules(self.lint(text)))

    def test_gap_cited_without_a_row_and_duplicate_rows(self):
        self.assertIn("gap-undefined", self.rules(self.lint(GOOD_DESIGN.replace("| D-1 | #8d4e2a @16% | primary @16% | warmer tint | team |\n", ""))))
        dup = GOOD_DESIGN.replace("| D-1 | #8d4e2a @16% | primary @16% | warmer tint | team |\n", "| D-1 | a | b | c | team |\n| D-1 | a | b | c | team |\n")
        self.assertIn("gap-duplicate", self.rules(self.lint(dup)))

    def test_invalid_decision_and_missing_reuse_path(self):
        self.assertIn("decision-invalid", self.rules(self.lint(GOOD_DESIGN.replace("| reuse |", "| maybe |"))))
        self.assertIn("path-missing", self.rules(self.lint(GOOD_DESIGN.replace("lib/widgets/primary_button.dart", "lib/widgets/gone.dart"))))

    def test_captures_are_required_and_must_exist(self):
        self.assertIn("ref-missing", self.rules(self.lint(GOOD_DESIGN.replace("refs/transfer.png", "refs/absent.png"))))
        no_images = GOOD_DESIGN.replace("`refs/transfer.png`", "TBD")
        self.assertIn("no-captures", self.rules(self.lint(no_images)))

    def test_spanish_headings_are_accepted(self):
        text = (GOOD_DESIGN.replace("## Components", "## Componentes").replace("## Screens", "## Pantallas")
                .replace("## Responsive behavior", "## Comportamiento responsivo").replace("## References", "## Referencias")
                .replace("#### Measures", "#### Medidas"))
        self.assertEqual(self.rules(self.lint(text)), set())

    def test_inferred_tags_with_a_reason_and_cells_are_counted(self):
        text = GOOD_DESIGN + "\nNote [inferido: muestreo] and [inferido] and [por confirmar]\n| a | inferido |\n"
        summary = self.lint(text)["summary"]
        self.assertEqual((summary["inferred"], summary["to_confirm"]), (3, 1))

    def test_hex_outside_the_token_tables_only_warns(self):
        report = self.lint(GOOD_DESIGN + "\n## Notes\nUse #123456 here.\n")
        self.assertIn("hex-outside-tokens", self.rules(report, "warn"))
        self.assertEqual(self.rules(report), set())


def kinds(source: str, path: str = "lib/features/x/presentation/widgets/w.dart", mode: str = "new") -> list:
    cfg = {"mode": mode, "max_fixed_width": 240}
    return [(f["kind"], f["severity"]) for f in resp_mod.check_text(path, source, cfg)]


class CheckResponsiveTest(unittest.TestCase):
    def test_bare_text_next_to_expanded_is_a_finding(self):
        src = """class W { Widget build(c) => Row(children: [
            Expanded(child: Text(label)),
            Text(value),
        ]); }"""
        self.assertEqual(kinds(src), [("row-text-no-flex", "finding")])

    def test_column_with_text_next_to_expanded_is_a_finding(self):
        src = """Widget b() => Row(children: [Expanded(child: Column(children: [Text(a)])),
            Column(children: [Text(b), Text(c)])]);"""
        self.assertEqual(kinds(src), [("row-text-no-flex", "finding")])

    def test_flexible_or_fittedbox_value_passes(self):
        src = """Widget b() => Row(children: [
            Expanded(child: Text(label)),
            Flexible(child: FittedBox(child: Text(value))),
        ]);"""
        self.assertEqual(kinds(src), [])

    def test_icon_next_to_expanded_text_passes(self):
        self.assertEqual(kinds("Widget b() => Row(children: [Icon(Icons.add), Expanded(child: Text(t))]);"), [])

    def test_two_bare_texts_without_flex_warn_and_legacy_downgrades_the_finding(self):
        self.assertEqual(kinds("Widget b() => Row(children: [Text(a), Text(b)]);"), [("row-texts-no-flex", "warn")])
        legacy = kinds("Widget b() => Row(children: [Expanded(child: Text(a)), Text(b)]);", mode="improve")
        self.assertEqual(legacy, [("row-text-no-flex", "warn")])

    def test_strings_and_comments_do_not_confuse_the_parser(self):
        src = """Widget b() => Row(children: [Expanded(child: Text('a, ) ] [ Text(')), // Text(x)
            Flexible(child: Text("Row(children: [Text(")))]);"""
        self.assertEqual(kinds(src), [])

    def test_fixed_width_and_height_around_text(self):
        self.assertEqual(kinds("Widget b() => Container(width: 268, height: 1, color: c);"), [("fixed-width", "warn")])
        self.assertEqual(kinds("Widget b() => SizedBox(width: 120, child: Text(t));"), [])
        self.assertEqual(kinds("Widget b() => SizedBox(height: 48, child: Center(child: Text(t)));"), [("fixed-height-text", "warn")])
        self.assertEqual(kinds("Widget b() => SizedBox(height: 8);"), [])

    def test_listview_children_map_media_query_and_form(self):
        self.assertEqual(kinds("Widget b() => ListView(children: items.map((i) => Text(i)).toList());"), [("list-not-builder", "warn")])
        self.assertEqual(kinds("final s = MediaQuery.of(context).size;"), [("media-query-of", "warn")])
        form = "Widget b() => Column(children: [TextField()]);"
        self.assertEqual(kinds(form, "lib/features/x/presentation/pages/p_page.dart"), [("form-no-scroll", "warn")])
        scrolled = "Widget b() => SingleChildScrollView(child: Column(children: [TextField()]));"
        self.assertEqual(kinds(scrolled, "lib/features/x/presentation/pages/p_page.dart"), [])


if __name__ == "__main__":
    unittest.main()
