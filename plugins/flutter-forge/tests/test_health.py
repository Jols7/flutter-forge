"""Tests for forge-health's collectors and snapshot.

Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v
"""
from __future__ import annotations

import importlib.util
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
SKILLS = os.path.join(PLUGIN, "skills")
HEALTH = os.path.join(SKILLS, "forge-health", "scripts")
EXAMPLE = os.path.join(REPO, "example", "forge_demo")
CLEAN = os.path.join(SKILLS, "forge-architecture", "presets", "clean.layers.json")

sys.path.insert(0, HEALTH)
import code_metrics  # noqa: E402
import git_churn  # noqa: E402
import lcov_summary  # noqa: E402


def git(root: str, *args: str) -> None:
    subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                   check=True, capture_output=True)


def write(root: str, rel: str, text: str) -> None:
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


WIDGET = """import 'package:flutter/material.dart';

class BigPage extends StatelessWidget {
  const BigPage({super.key});

  @override
  Widget build(BuildContext context) {
    const brace = '}{ not a block';
    // } a comment brace
    return Column(children: [
      Text('a'), Text('b'), Text('c'),
    ]);
  }
}

class Small extends StatelessWidget {
  @override
  Widget build(BuildContext context) => const Text('x');
}
"""


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        write(self.root, "pubspec.yaml", "name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n  dio: ^5.0.0\n"
              "  loose: any\n  local:\n    path: ../local\ndev_dependencies:\n  mocktail: 1.0.0\n")
        write(self.root, "lib/features/a/domain/entities/a.dart", "class A {}\n")
        write(self.root, "lib/features/a/presentation/pages/a_page.dart",
              "import '../../data/models/a_dto.dart';\n" + WIDGET)
        write(self.root, "lib/features/a/data/models/a_dto.dart", "class ADto {}\n")
        write(self.root, "lib/features/a/data/models/a_dto.g.dart", "// generated\n")
        git(self.root, "init", "-q")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "one")
        for i in range(3):
            write(self.root, "lib/features/a/presentation/pages/a_page.dart",
                  "import '../../data/models/a_dto.dart';\n" + WIDGET + "// edit %d\n" % i)
            write(self.root, "lib/features/a/data/models/a_dto.g.dart", "// generated %d\n" % i)
            git(self.root, "commit", "-qam", "edit %d" % i)


class ChurnTest(ProjectCase):
    def test_counts_commits_and_skips_generated(self):
        report = git_churn.churn(self.root, 90, 5)
        self.assertTrue(report["available"])
        self.assertEqual(report["by_file"]["lib/features/a/presentation/pages/a_page.dart"], 4)
        self.assertFalse(any(".g.dart" in f for f in report["by_file"]))
        self.assertEqual(report["top"][0]["file"], "lib/features/a/presentation/pages/a_page.dart")
        self.assertTrue(report["top"][0]["single_owner"])

    def test_paths_are_relative_inside_a_monorepo_folder(self):
        outer = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outer)
        app = os.path.join(outer, "apps", "mobile")
        write(app, "lib/main.dart", "void main() {}\n")
        git(outer, "init", "-q")
        git(outer, "add", ".")
        git(outer, "commit", "-q", "-m", "x")
        self.assertIn("lib/main.dart", git_churn.churn(app)["by_file"])

    def test_no_git_is_reported_not_raised(self):
        bare = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bare)
        self.assertFalse(git_churn.churn(bare)["available"])


class CoverageTest(ProjectCase):
    def test_missing_lcov_gives_the_command(self):
        report = lcov_summary.coverage(self.root)
        self.assertFalse(report["available"])
        self.assertIn("flutter test --coverage", report["hint"])

    def test_untested_files_count_as_zero_and_hot_ones_rank_first(self):
        write(self.root, "coverage/lcov.info",
              "SF:lib/features/a/domain/entities/a.dart\nLF:4\nLH:4\nend_of_record\n"
              "SF:lib/features/a/presentation/pages/a_page.dart\nLF:10\nLH:2\nend_of_record\n")
        churn = git_churn.churn(self.root)
        report = lcov_summary.coverage(self.root, None, churn["by_file"], 5)
        self.assertEqual(report["files_not_in_lcov"], 1)       # a_dto.dart
        self.assertEqual(report["by_file"]["lib/features/a/data/models/a_dto.dart"], 0.0)
        self.assertEqual(report["hotspots_untested"][0]["file"], "lib/features/a/presentation/pages/a_page.dart")
        self.assertAlmostEqual(report["line_coverage"], 6 / 14, places=3)


class CodeMetricsTest(ProjectCase):
    def test_widget_sizes_ignore_braces_in_strings_and_comments(self):
        code = code_metrics.code_size(self.root, 5)
        big = [w for w in code["largest_widgets"] if w["class"] == "BigPage"][0]
        small = [w for w in code["largest_widgets"] if w["class"] == "Small"][0]
        self.assertEqual(big["lines"], 12)
        self.assertEqual(small["lines"], 4)
        self.assertEqual(code["widget_classes"], 2)

    def test_dependency_kinds(self):
        deps = code_metrics.dependencies(self.root)
        self.assertEqual(deps["constraint_kinds"]["caret"], 1)
        self.assertIn("loose (any)", deps["needs_attention"])
        self.assertIn("local (path)", deps["needs_attention"])
        self.assertFalse(deps["lock_present"])

    def test_outdated_is_off_by_default(self):
        self.assertFalse(code_metrics.metrics(self.root)["dependencies"]["outdated"]["run"])


class LayerMatrixTest(unittest.TestCase):
    def test_matrix_counts_real_edges(self):
        out = subprocess.run([sys.executable, os.path.join(SKILLS, "forge-audit", "scripts", "check_layers.py"),
                              "--rules", CLEAN, "--root", EXAMPLE, "--format", "json", "--no-fail"],
                             capture_output=True, text=True)
        matrix = json.loads(out.stdout)["matrix"]
        self.assertGreater(matrix["presentation -> domain"], 0)
        self.assertNotIn("domain -> data", matrix)


class SnapshotTest(unittest.TestCase):
    script = os.path.join(HEALTH, "health_snapshot.py")

    def run_snapshot(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, self.script, *args], capture_output=True, text=True)

    def test_digest_is_short_and_complete(self):
        out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out_dir)
        proc = self.run_snapshot("--root", EXAMPLE, "--out-dir", out_dir)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLessEqual(len(proc.stdout.splitlines()), 250)
        for heading in ("## Layers", "## Hotspots", "## Tests and coverage", "## Dependencies", "## Security"):
            self.assertIn(heading, proc.stdout)
        self.assertNotIn("collector failed", proc.stdout)
        full = json.load(open(os.path.join(out_dir, "metrics.json")))
        self.assertIn("layers", full)

    def test_no_pubspec_is_a_message_not_a_crash(self):
        empty = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty)
        proc = self.run_snapshot("--root", empty)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("no pubspec.yaml", proc.stdout)

    def test_no_write_leaves_the_project_untouched(self):
        project = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, project)
        shutil.copytree(EXAMPLE, project, dirs_exist_ok=True)
        proc = self.run_snapshot("--root", project, "--no-write")
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(project, ".flutter-forge", "health")))

    def test_section_prints_json_and_secrets_stay_masked(self):
        project = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, project)
        shutil.copytree(EXAMPLE, project, dirs_exist_ok=True)
        secret = "ghp_" + "a1B2c3D4" * 5
        write(project, "lib/leak.dart", "const t = '%s';\n" % secret)
        proc = self.run_snapshot("--root", project, "--no-write")
        self.assertNotIn(secret, proc.stdout)
        self.assertIn("github-token", proc.stdout)
        section = self.run_snapshot("--root", project, "--no-write", "--section", "security")
        self.assertNotIn(secret, section.stdout)
        self.assertGreaterEqual(json.loads(section.stdout)["count"], 1)

    def test_skill_frontmatter_matches_the_design(self):
        text = open(os.path.join(SKILLS, "forge-health", "SKILL.md"), encoding="utf-8").read()
        head = text.split("---")[1]
        for line in ("disable-model-invocation: true", "context: fork", "model: sonnet"):
            self.assertIn(line, head)
        self.assertIn("!`python3", text)
        self.assertLess(len(text.splitlines()), 300)


if __name__ == "__main__":
    unittest.main()
