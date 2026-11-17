"""Tests for forge-health's standard depth: layer inference, profile draft, review queue.

Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PLUGIN))
HEALTH = os.path.join(PLUGIN, "skills", "forge-health", "scripts")
EXAMPLE = os.path.join(REPO, "example", "forge_demo")
CHECK_LAYERS = os.path.join(PLUGIN, "skills", "forge-audit", "scripts", "check_layers.py")

sys.path.insert(0, HEALTH)
import draft_profile  # noqa: E402
import infer_layers  # noqa: E402


def git(root: str, *args: str) -> None:
    subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                   check=True, capture_output=True)


def write(root: str, rel: str, text: str) -> None:
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class OddLayoutCase(unittest.TestCase):
    """A repo whose folders match neither preset: screens/, domain/, core/services/network/..."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        write(self.root, "pubspec.yaml", "name: odd\ndependencies:\n  flutter:\n    sdk: flutter\n  provider: ^6.0.0\n"
              "  dio: ^5.0.0\n")
        write(self.root, "lib/main.dart", "void main() {}\n")
        write(self.root, "lib/domain/user/user.dart", "class User {}\n")
        write(self.root, "lib/core/services/network/api/user_api.dart", "import '../../../../domain/user/user.dart';\nclass UserApi {}\n")
        write(self.root, "lib/core/services/network/dtos/user_dto.dart", "class UserDto {}\n")
        write(self.root, "lib/core/services/repositories/user_repository.dart", "class UserRepository {}\n")
        write(self.root, "lib/core/utils/format.dart", "String f() => '';\n")
        write(self.root, "lib/screens/home/pages/home_page.dart", "import 'package:flutter/material.dart';\nclass HomePage {}\n")
        write(self.root, "lib/screens/home/provider/home_provider.dart",
              "import 'package:provider/provider.dart';\nclass HomeProvider extends ChangeNotifier {}\n")
        write(self.root, "lib/widgets/card.dart", "class Card2 {}\n")
        write(self.root, "lib/generated/intl/messages.dart", "// generated\n")
        git(self.root, "init", "-q")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "init")
        for i in range(3):
            write(self.root, "lib/screens/home/pages/home_page.dart",
                  "import 'package:flutter/material.dart';\nclass HomePage {}\n// edit %d\n" % i)
            git(self.root, "commit", "-qam", "edit %d" % i)


class InferTest(OddLayoutCase):
    def test_presets_do_not_fit_and_the_draft_does(self):
        result = infer_layers.infer(self.root)
        self.assertEqual(result["status"], "inferred")
        self.assertLess(max(result["preset_coverage"].values()), 0.8)
        self.assertGreaterEqual(result["coverage"], 0.9)
        layers = {m["path"]: m["layer"] for m in result["mappings"]}
        self.assertEqual(layers["lib/screens/**"], "presentation")
        self.assertEqual(layers["lib/domain/**"], "models")
        self.assertEqual(layers["lib/core/services/network/api/**"], "api")
        self.assertEqual(result["rules"]["features_root"], "lib/screens")

    def test_nested_widgets_and_providers_stay_in_the_module(self):
        result = infer_layers.infer(self.root)
        paths = [m["path"] for m in result["mappings"]]
        self.assertNotIn("lib/screens/home/pages/**", paths)   # one rule for the whole module

    def test_generated_code_is_never_mapped_or_counted(self):
        result = infer_layers.infer(self.root)
        self.assertEqual(result["files"], 9)

    def test_the_draft_is_accepted_by_the_checker(self):
        result = infer_layers.infer(self.root)
        path = os.path.join(self.root, "layers.draft.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(result["rules"], fh)
        proc = subprocess.run([sys.executable, CHECK_LAYERS, "--rules", path, "--root", self.root, "--format", "json",
                               "--no-fail"], capture_output=True, text=True)
        report = json.loads(proc.stdout)
        self.assertLessEqual(len(report["unclassified"]), 1)   # lib/main.dart is composition; nothing else is left

    def test_a_repo_that_fits_a_preset_gets_no_draft(self):
        result = infer_layers.infer(EXAMPLE)
        self.assertEqual(result["status"], "preset_fits")
        self.assertIsNone(result["rules"])

    def test_no_dart_files_is_insufficient_not_an_error(self):
        empty = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty)
        self.assertEqual(infer_layers.infer(empty)["status"], "insufficient")


class DraftProfileTest(OddLayoutCase):
    def script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, os.path.join(HEALTH, "draft_profile.py"), "--root", self.root, *args],
                              capture_output=True, text=True)

    def test_mode_is_left_to_a_human_and_detected_values_are_filled(self):
        text = self.script().stdout
        self.assertIn("mode: null", text)
        self.assertIn("HUMAN DECISION", text)
        self.assertIn("state: provider", text)
        self.assertIn("features: lib/screens", text)
        self.assertIn("Not detected", text)

    def test_it_refuses_to_write_a_real_profile(self):
        target = os.path.join(self.root, ".flutter-forge", "profile.yaml")
        proc = self.script("--write", target)
        self.assertIn("refused", proc.stdout)
        self.assertFalse(os.path.exists(target))

    def test_write_goes_to_the_given_path(self):
        target = os.path.join(self.root, ".flutter-forge", "health", "profile.draft.yaml")
        self.script("--write", target)
        self.assertTrue(os.path.exists(target))

    def test_render_marks_the_draft(self):
        stack = {"package": "x", "dependencies": {}, "structure": {"architecture": {}}, "conventions_signals": {}}
        text = draft_profile.render(self.root, stack, {"status": "insufficient"}, None)
        self.assertTrue(text.startswith("# DRAFT profile"))


class StandardSnapshotTest(OddLayoutCase):
    script = os.path.join(HEALTH, "health_snapshot.py")

    def snap(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, self.script, "--root", self.root, *args], capture_output=True, text=True)

    def test_standard_writes_drafts_but_never_a_real_profile(self):
        proc = self.snap()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        health = os.path.join(self.root, ".flutter-forge", "health")
        self.assertTrue(os.path.exists(os.path.join(health, "layers.draft.json")))
        self.assertTrue(os.path.exists(os.path.join(health, "profile.draft.yaml")))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".flutter-forge", "profile.yaml")))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".flutter-forge", "layers.json")))
        self.assertIn("Layer map: INFERRED draft", proc.stdout)
        self.assertIn("## Review queue", proc.stdout)
        self.assertLessEqual(len(proc.stdout.splitlines()), 250)
        self.assertNotIn("collector failed", proc.stdout)

    def test_standard_layers_are_not_mostly_unclassified(self):
        proc = self.snap("--no-write", "--section", "layers")
        layers = json.loads(proc.stdout)
        self.assertFalse(layers["mapping_suspect"])
        self.assertIn("inferred draft", layers["rules"])

    def test_quick_keeps_the_old_behavior(self):
        proc = self.snap("--depth", "quick")
        self.assertIn("assumed preset", proc.stdout)
        self.assertNotIn("INFERRED", proc.stdout)
        queue = json.loads(self.snap("--depth", "quick", "--no-write", "--section", "review_queue").stdout)
        self.assertEqual(queue["limit"], 15)
        health = os.path.join(self.root, ".flutter-forge", "health")
        self.assertFalse(os.path.exists(os.path.join(health, "layers.draft.json")))
        self.assertFalse(os.path.exists(os.path.join(health, "profile.draft.yaml")))

    def test_no_write_leaves_the_project_untouched(self):
        self.snap("--no-write")
        self.assertFalse(os.path.exists(os.path.join(self.root, ".flutter-forge")))

    def test_the_repos_own_layers_json_wins_over_the_draft(self):
        with open(os.path.join(PLUGIN, "skills", "forge-architecture", "presets", "layered.layers.json"), encoding="utf-8") as fh:
            write(self.root, ".flutter-forge/layers.json", fh.read())
        proc = self.snap("--no-write", "--section", "layers")
        self.assertEqual(json.loads(proc.stdout)["rules"], ".flutter-forge/layers.json")

    def test_an_existing_profile_is_not_redrafted(self):
        write(self.root, ".flutter-forge/profile.yaml", "schema: 1\n")
        proc = self.snap("--no-write")
        self.assertNotIn("Profile: none in repo", proc.stdout)

    def test_scanner_findings_head_the_review_queue_and_values_stay_masked(self):
        secret = "ghp_" + "a1B2c3D4" * 5
        write(self.root, "lib/core/utils/leak.dart", "const t = '%s';\n" % secret)
        proc = self.snap("--no-write")
        self.assertNotIn(secret, proc.stdout)
        queue = proc.stdout.split("## Review queue")[1].splitlines()
        self.assertIn("lib/core/utils/leak.dart", queue[1])
        self.assertIn("security", queue[1])

    def test_review_files_limits_the_queue(self):
        proc = self.snap("--no-write", "--review-files", "2", "--section", "review_queue")
        queue = json.loads(proc.stdout)
        self.assertEqual(len(queue["files"]), 2)
        self.assertEqual(queue["files"][0]["file"], "lib/screens/home/pages/home_page.dart")


class SkillTextTest(unittest.TestCase):
    def test_skill_documents_the_standard_depth(self):
        with open(os.path.join(PLUGIN, "skills", "forge-health", "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        for needle in ("Review queue", "layers.draft.json", "profile.draft.yaml", "30 files"):
            self.assertIn(needle, text)
        self.assertLess(len(text.splitlines()), 300)


if __name__ == "__main__":
    unittest.main()
