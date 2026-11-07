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
