"""Tests for the flutter-forge scripts. Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v"""
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
EXAMPLE = os.path.join(REPO, "example", "forge_demo")
FIXTURES = os.path.join(HERE, "fixtures")


def load(skill: str, script: str):
    path = os.path.join(SKILLS, skill, "scripts", script)
    spec = importlib.util.spec_from_file_location(script[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(skill: str, script: str, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, os.path.join(SKILLS, skill, "scripts", script), *args],
                          capture_output=True, text=True, cwd=cwd)


class PostmanToContractTest(unittest.TestCase):
    mod = load("forge-api-contract", "postman_to_contract.py")
    collection = os.path.join(EXAMPLE, "api", "forge_demo.postman_collection.json")

    def test_v21_lists_all_endpoints_with_relative_paths(self):
        endpoints, info = self.mod.load_source(self.collection)
        self.assertEqual(info["format"], "postman-v2.1")
        paths = {(e["method"], e["path"]) for e in endpoints}
        self.assertIn(("GET", "accounts/{accountId}/transactions"), paths)
        self.assertIn(("POST", "transfers"), paths)

    def test_merges_examples_by_status_marking_nullables(self):
        out = run("forge-api-contract", "postman_to_contract.py", self.collection, "--format", "json", "--filter", "transactions")
        data = json.loads(out.stdout)
        schema = data["endpoints"][0]["response_schemas"]["200"]
        item = schema["fields"]["data"]["items"]["fields"]
        self.assertTrue(item["description"]["nullable"])
        self.assertEqual(item["amount"]["type"], "num")
        self.assertTrue(schema["fields"]["next_page"]["nullable"])

    def test_variables_are_names_only_and_dynamic_vars_hidden(self):
        out = run("forge-api-contract", "postman_to_contract.py", self.collection)
        self.assertIn("`access_token`", out.stdout)
        self.assertNotIn("$guid", out.stdout)

    def test_fixtures_are_redacted_and_do_not_collide(self):
        tmp = tempfile.mkdtemp()
        try:
            run("forge-api-contract", "postman_to_contract.py", self.collection, "--fixtures-dir", tmp, "--out", os.path.join(tmp, "out", "c.md"))
            login = json.load(open(os.path.join(tmp, "auth", "login_200.json")))
            self.assertEqual(login["access_token"], "<redacted>")
            request = json.load(open(os.path.join(tmp, "auth", "login_request.json")))
            self.assertEqual(request["password"], "<redacted>")
            self.assertTrue(os.path.exists(os.path.join(tmp, "accounts", "list_transactions_200_empty.json")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "out", "c.md")))
        finally:
            shutil.rmtree(tmp)

    def test_v3_directory(self):
        endpoints, info = self.mod.load_source(os.path.join(FIXTURES, "v3", "demo api"))
        self.assertEqual(info["format"], "postman-v3-dir")
        by_name = {e["name"]: e for e in endpoints}
        self.assertEqual(by_name["get account"]["path"], "accounts/{id}")
        self.assertEqual(by_name["get account"]["examples"][0]["status"], 200)
        self.assertIn("bearer", by_name["Create payment: v2"]["auth"])

    def test_openapi(self):
        endpoints, _ = self.mod.load_source(os.path.join(FIXTURES, "openapi.json"))
        user = endpoints[0]["examples"][0]["schema"]["fields"]
        self.assertTrue(user["nick"]["nullable"])
        self.assertTrue(user["age"].get("optional"))
        self.assertNotIn("optional", user["id"])

    def test_sensitive_key_detection(self):
        self.assertTrue(self.mod.is_sensitive("accessToken"))
        self.assertTrue(self.mod.is_sensitive("card_number"))
        self.assertFalse(self.mod.is_sensitive("expand"))
        self.assertFalse(self.mod.is_sensitive("company"))


class CheckLayersTest(unittest.TestCase):
    rules = os.path.join(SKILLS, "forge-architecture", "presets", "clean.layers.json")

    def test_example_app_is_clean(self):
        out = run("forge-audit", "check_layers.py", "--root", EXAMPLE, "--rules", self.rules)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("Violations: 0", out.stdout)

    def test_detects_seeded_violations(self):
        tmp = tempfile.mkdtemp()
        try:
            def write(rel, text):
                path = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "w").write(text)
            write("pubspec.yaml", "name: demo\n")
            write("lib/features/a/data/models/a_dto.dart", "class ADto {}\n")
            write("lib/features/a/domain/entities/a.dart", "import 'package:dio/dio.dart';\nclass A {}\n")
            write("lib/features/a/presentation/pages/a_page.dart", "import '../../data/models/a_dto.dart';\n")
            write("lib/features/b/presentation/pages/b_page.dart", "import 'package:demo/features/a/presentation/pages/a_page.dart';\n")
            out = run("forge-audit", "check_layers.py", "--root", tmp, "--rules", self.rules, "--format", "json")
            kinds = sorted(v["kind"] for v in json.loads(out.stdout)["reported"])
            self.assertEqual(kinds, ["cross-feature", "forbidden-import", "layer"])
            self.assertEqual(out.returncode, 1)
            scoped = run("forge-audit", "check_layers.py", "--root", tmp, "--rules", self.rules, "--format", "json",
                         "--files", "lib/features/a/domain/entities/a.dart")
            data = json.loads(scoped.stdout)
            self.assertEqual(len(data["reported"]), 1)
            self.assertEqual(data["preexisting"], 2)
        finally:
            shutil.rmtree(tmp)


    def _tree(self, files):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        files = dict(files, **{"pubspec.yaml": "name: demo\n"})
        for rel, text in files.items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                fh.write(text)
        return tmp

    def test_presentation_cannot_reach_the_service_locator(self):
        tmp = self._tree({
            "lib/core/di/injection.dart": "final getIt = Object();\n",
            "lib/features/a/presentation/pages/a_page.dart": "import '../../../../core/di/injection.dart';\n",
        })
        data = json.loads(run("forge-audit", "check_layers.py", "--root", tmp, "--rules", self.rules, "--format", "json").stdout)
        self.assertEqual([(v["from_layer"], v["to_layer"]) for v in data["reported"]], [("presentation", "composition_di")])

    def test_unclassified_import_target_is_reported_but_not_a_violation(self):
        tmp = self._tree({
            "lib/features/a/domain/entities/a.dart": "import '../../../../odd/thing.dart';\nclass A {}\n",
            "lib/odd/thing.dart": "const x = 1;\n",
        })
        out = run("forge-audit", "check_layers.py", "--root", tmp, "--rules", self.rules, "--format", "json")
        data = json.loads(out.stdout)
        self.assertEqual(out.returncode, 0)
        self.assertEqual([u["target"] for u in data["unclassified_targets"]], ["lib/odd/thing.dart"])
        text = run("forge-audit", "check_layers.py", "--root", tmp, "--rules", self.rules)
        self.assertIn("Imports into unclassified files", text.stdout)


class ScanSecretsTest(unittest.TestCase):
    def test_example_has_no_secrets(self):
        out = run("forge-security", "scan_secrets.py", "--root", EXAMPLE)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_detects_and_masks(self):
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, "lib"))
            secret = "Sup3r#ecretValue!"
            open(os.path.join(tmp, "lib", "a.dart"), "w").write(
                "const _password = '%s';\n"
                "const storageKey = 'access_token';\n"
                "const label = 'Contraseña';\n"
                "final url = 'http://api.example.com/x';\n"
                "void f(String token) { print('token: $token'); }\n" % secret)
            open(os.path.join(tmp, "pubspec.yaml"), "w").write("name: x\nflutter:\n  assets:\n    - .env\n")
            out = run("forge-security", "scan_secrets.py", "--root", tmp, "--format", "json")
            findings = json.loads(out.stdout)["findings"]
            kinds = sorted(f["kind"] for f in findings)
            self.assertEqual(kinds, ["bundled-secret-file", "cleartext-url", "generic-secret-assignment", "sensitive-logging"])
            self.assertNotIn(secret, out.stdout)
            self.assertEqual(out.returncode, 1)
        finally:
            shutil.rmtree(tmp)


class PlatformConfigTest(unittest.TestCase):
    def test_example_release_config_is_hardened(self):
        out = run("forge-security", "check_platform_config.py", "--root", EXAMPLE, "--format", "json")
        severities = {f["severity"] for f in json.loads(out.stdout)["findings"]}
        self.assertFalse(severities & {"critical", "high", "medium"}, out.stdout)

    def test_flags_insecure_manifest_and_gradle(self):
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, "android/app/src/main"))
            open(os.path.join(tmp, "android/app/src/main/AndroidManifest.xml"), "w").write(
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
                '<application android:usesCleartextTraffic="true"><receiver android:name=".R" android:exported="true"/></application></manifest>')
            open(os.path.join(tmp, "android/app/build.gradle"), "w").write(
                'android {\n  signingConfigs { release { storePassword "hunter22" } }\n'
                '  buildTypes {\n    release {\n      signingConfig signingConfigs.debug\n    }\n  }\n}\n')
            out = run("forge-security", "check_platform_config.py", "--root", tmp, "--format", "json")
            messages = " | ".join(f["message"] for f in json.loads(out.stdout)["findings"])
            for expected in ("usesCleartextTraffic", "allowBackup", "exported without a permission", "debug key", "Keystore password"):
                self.assertIn(expected, messages)
        finally:
            shutil.rmtree(tmp)


class DetectProjectTest(unittest.TestCase):
    def test_detects_example_stack(self):
        out = run("forge-profile", "detect_project.py", EXAMPLE)
        report = json.loads(out.stdout)
        self.assertEqual(report["package"], "forge_demo")
        self.assertIn("bloc", report["dependencies"]["state"])
        self.assertEqual(report["dependencies"]["state_primary_in_code"], "bloc")
        self.assertEqual(report["l10n"]["pipeline"], "gen-l10n")
        self.assertEqual(report["structure"]["architecture"]["preset"], "clean")
        self.assertEqual(report["structure"]["feature_root"], "lib/features")
        self.assertEqual(report["naming"]["mapper_method"], "toEntity")
        self.assertEqual(report["needs_decision"], {})

    def test_reports_mapper_name_and_values_the_profile_cannot_express(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        files = {
            "pubspec.yaml": "name: legacy\ndependencies:\n  flutter:\n    sdk: flutter\n  get: ^4.0.0\n  beamer: ^1.0.0\n  dio: ^5.0.0\n",
            "lib/features/a/data/a_dto.dart": "extension on ADto {\n  A toDomain() => A();\n}\nextension on BDto {\n  B toDomain() => B();\n}\n",
            "lib/features/a/a_view.dart": "class AView {}\n",
            "lib/main.dart": "void main() {}\n",
            "lib/x.dart": "class X {}\n",
        }
        for rel, text in files.items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                fh.write(text)
        report = json.loads(run("forge-profile", "detect_project.py", tmp).stdout)
        self.assertEqual(report["naming"]["mapper_method"], "toDomain")
        self.assertEqual(report["needs_decision"]["state"], ["getx"])
        self.assertEqual(report["needs_decision"]["router"], ["beamer"])
        self.assertNotIn("http", report["needs_decision"])


class CheckCommentsTest(unittest.TestCase):
    def test_example_app_follows_the_policy(self):
        out = run("forge-audit", "check_comments.py", "--root", EXAMPLE)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_flags_policy_violations_and_keeps_good_comments(self):
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, "lib/features/a/domain"))
            os.makedirs(os.path.join(tmp, "lib/features/a/presentation"))
            open(os.path.join(tmp, "lib/features/a/domain/repo.dart"), "w").write(
                "abstract interface class ARepository {\n"
                "  Future<int> load();\n"
                "}\n\n"
                "/// Documented on purpose.\n"
                "class Documented {}\n")
            open(os.path.join(tmp, "lib/features/a/presentation/page.dart"), "w").write(
                "// ===== WIDGETS =====\n"
                "// final total = items.length;\n"
                "// setState(() {});\n"
                "// TODO fix later\n"
                "// TODO(#12): remove when the API ships pagination\n"
                "// AC-4 (HU-12): transfers over 50,000 need re-authentication\n"
                "// ignore: avoid_print\n"
                "final pattern = RegExp(r'^\\d+$'); // digits only, no sign\n")
            out = run("forge-audit", "check_comments.py", "--root", tmp, "--format", "json")
            findings = json.loads(out.stdout)["findings"]
            kinds = sorted((f["kind"], f["line"]) for f in findings)
            self.assertEqual(kinds, [
                ("banner", 1),
                ("commented-out-code", 2),
                ("missing-doc", 1),
                ("missing-doc", 2),
                ("todo-without-ref", 4),
            ])
            self.assertEqual(out.returncode, 1)
        finally:
            shutil.rmtree(tmp)


    def _git_app(self):
        """A Flutter app in a monorepo folder (apps/mobile), one commit, then one new file."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        app = os.path.join(tmp, "apps", "mobile")
        files = {
            "lib/old.dart": "// TODO fix later\nclass Old {}\n",
            "lib/domain/model.dart": "class Model {}\n",
        }
        for rel, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(app, rel)), exist_ok=True)
            with open(os.path.join(app, rel), "w") as fh:
                fh.write(text)
        git = ["git", "-C", tmp, "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "init"], check=True)
        with open(os.path.join(app, "lib/new.dart"), "w") as fh:
            fh.write("// TODO later\nclass New {}\n")
        return app

    def test_changed_from_checks_only_new_code_inside_a_monorepo_folder(self):
        app = self._git_app()
        out = run("forge-audit", "check_comments.py", "--root", app, "--changed-from", "HEAD", "--format", "json")
        findings = json.loads(out.stdout)["findings"]
        self.assertEqual([f["file"] for f in findings], ["lib/new.dart"])

    def test_rules_file_says_where_the_domain_is(self):
        app = self._git_app()
        rules = os.path.join(app, "layers.json")
        with open(rules, "w") as fh:
            json.dump({"layers": {"models": {"paths": ["lib/domain/**"], "may_import": []}}}, fh)
        without = json.loads(run("forge-audit", "check_comments.py", "--root", app, "--files", "lib/domain/model.dart", "--format", "json").stdout)
        with_rules = json.loads(run("forge-audit", "check_comments.py", "--root", app, "--rules", rules,
                                    "--files", "lib/domain/model.dart", "--format", "json").stdout)
        self.assertEqual(len(without["findings"]), 1)      # default heuristic also matches /domain/
        self.assertEqual(with_rules["findings"][0]["kind"], "missing-doc")

    def test_shared_widgets_need_docs_only_when_asked(self):
        app = self._git_app()
        os.makedirs(os.path.join(app, "lib/core/widgets"), exist_ok=True)
        with open(os.path.join(app, "lib/core/widgets/badge.dart"), "w") as fh:
            fh.write("class Badge extends StatelessWidget {}\n\n/// Documented.\nclass Chip2 extends StatelessWidget {}\n")
        args = ("--root", app, "--files", "lib/core/widgets/badge.dart", "--format", "json")
        self.assertEqual(json.loads(run("forge-audit", "check_comments.py", *args).stdout)["findings"], [])
        found = json.loads(run("forge-audit", "check_comments.py", *args, "--shared-widgets", "lib/core/widgets").stdout)["findings"]
        self.assertEqual([(f["kind"], f["line"]) for f in found], [("missing-doc", 1)])

    def test_layers_changed_from_is_relative_to_the_app_folder(self):
        app = self._git_app()
        rules = os.path.join(SKILLS, "forge-architecture", "presets", "clean.layers.json")
        with open(os.path.join(app, "pubspec.yaml"), "w") as fh:
            fh.write("name: demo\n")
        os.makedirs(os.path.join(app, "lib/features/a/domain"), exist_ok=True)
        with open(os.path.join(app, "lib/features/a/domain/a.dart"), "w") as fh:
            fh.write("import 'package:dio/dio.dart';\n")
        out = run("forge-audit", "check_layers.py", "--root", app, "--rules", rules, "--changed-from", "HEAD", "--format", "json")
        self.assertEqual([v["file"] for v in json.loads(out.stdout)["reported"]], ["lib/features/a/domain/a.dart"])


class ResultContractTest(unittest.TestCase):
    """The shipped example result must satisfy the shipped schema (needs jsonschema; CI installs it)."""

    def test_example_validates(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema not installed")
        refs = os.path.join(SKILLS, "forge-deliver", "references")
        schema = json.load(open(os.path.join(refs, "result.schema.json")))
        Draft202012Validator.check_schema(schema)
        example = json.load(open(os.path.join(refs, "result.example.json")))
        errors = [e.message for e in Draft202012Validator(schema).iter_errors(example)]
        self.assertEqual(errors, [])
        self.assertTrue(example["why"] and example["review_points"])


class YamlSubsetTest(unittest.TestCase):
    mod = load("forge-api-contract", "postman_to_contract.py")

    def test_block_scalars_lists_and_quotes(self):
        doc = self.mod.load_simple_yaml(
            "a: 'x: y'\nb:\n  - key: k\n    value: \"v\"\n  - plain\nc: |-\n  line1\n  line2\nd: [1, two]\ne: 3\n")
        self.assertEqual(doc["a"], "x: y")
        self.assertEqual(doc["b"], [{"key": "k", "value": "v"}, "plain"])
        self.assertEqual(doc["c"], "line1\nline2")
        self.assertEqual(doc["d"], [1, "two"])
        self.assertEqual(doc["e"], 3)


if __name__ == "__main__":
    unittest.main()
