"""Presets are data that every project copies; a typo in them breaks every audit.

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
SKILLS = os.path.join(os.path.dirname(HERE), "skills")
PRESETS = os.path.join(SKILLS, "forge-architecture", "presets")
CHECK = os.path.join(SKILLS, "forge-audit", "scripts", "check_layers.py")

# Minimal trees that follow each preset's own documentation. Every import below is one the
# preset's reference says is legitimate, so a violation means the preset contradicts its docs.
CLEAN_TREE = {
    "lib/core/error/result.dart": "sealed class Result<T> {}\n",
    "lib/core/constants/app_assets.dart": "abstract final class AppAssets {}\n",
    "lib/core/utils/paginated.dart": "class Paginated<T> {}\n",
    "lib/core/network/api_client.dart": "import '../error/result.dart';\n",
    "lib/features/a/domain/entities/a.dart": "import '../../../../core/error/result.dart';\n",
    "lib/features/a/domain/repositories/a_repository.dart": "import '../entities/a.dart';\n",
    "lib/features/a/data/models/a_dto.dart": "class ADto {}\n",
    "lib/features/a/data/mappers/a_mapper.dart": "import '../models/a_dto.dart';\nimport '../../domain/entities/a.dart';\n",
    "lib/features/a/data/repositories/a_repository_impl.dart":
        "import '../../domain/repositories/a_repository.dart';\nimport '../mappers/a_mapper.dart';\n"
        "import '../../../../core/network/api_client.dart';\n",
    "lib/features/a/presentation/state/a_cubit.dart":
        "import '../../domain/repositories/a_repository.dart';\nimport '../../../../core/constants/app_assets.dart';\n",
    "lib/features/a/presentation/pages/a_page.dart": "import '../state/a_cubit.dart';\n",
    "lib/features/a/di/a_module.dart": "import '../data/repositories/a_repository_impl.dart';\n",
    "lib/core/di/injection.dart": "import '../../features/a/di/a_module.dart';\n",
    "lib/core/router/app_router.dart": "import '../../features/a/presentation/pages/a_page.dart';\n",
    "lib/main.dart": "import 'core/di/injection.dart';\n",
}

LAYERED_TREE = {
    "lib/core/error/result.dart": "sealed class Result<T> {}\n",
    "lib/core/network/dio_client.dart": "import '../error/result.dart';\n",
    "lib/models/a.dart": "class A {}\n",
    "lib/data/dtos/a_dto.dart": "import '../../models/a.dart';\n",
    "lib/data/api/a_api.dart": "import '../dtos/a_dto.dart';\nimport '../../core/network/dio_client.dart';\n",
    "lib/data/repositories/a_repository.dart": "import '../api/a_api.dart';\nimport '../dtos/a_dto.dart';\nimport '../../models/a.dart';\n",
    "lib/features/a/a_controller.dart": "import '../../data/repositories/a_repository.dart';\n",
    "lib/features/a/a_screen.dart": "import 'a_controller.dart';\n",
    "lib/core/di/injection.dart": "import '../../data/repositories/a_repository.dart';\n",
}


def load(name):
    with open(os.path.join(PRESETS, name + ".layers.json"), encoding="utf-8") as fh:
        return json.load(fh)


class PresetShapeTest(unittest.TestCase):
    def test_every_may_import_names_an_existing_layer(self):
        for name in ("clean", "layered"):
            data = load(name)
            layers = set(data["layers"])
            for layer, spec in data["layers"].items():
                for target in spec["may_import"]:
                    self.assertTrue(target == "*" or target in layers, "%s: %s imports unknown layer %s" % (name, layer, target))
            for target in data.get("cross_feature", {}).get("allowed_layers", []):
                self.assertIn(target, layers, "%s: cross_feature names unknown layer %s" % (name, target))

    def test_every_layer_has_paths(self):
        for name in ("clean", "layered"):
            for layer, spec in load(name)["layers"].items():
                self.assertTrue(spec["paths"], "%s: layer %s has no paths" % (name, layer))

    def test_service_locator_layer_is_closed_to_ui_and_data(self):
        for name, ui in (("clean", ["presentation", "data", "domain"]), ("layered", ["presentation", "api", "repositories", "models"])):
            data = load(name)
            self.assertIn("composition_di", data["layers"])
            for layer in ui:
                self.assertNotIn("composition_di", data["layers"][layer]["may_import"], "%s/%s" % (name, layer))
                self.assertNotIn("*", data["layers"][layer]["may_import"])


class PresetAgainstOwnDocsTest(unittest.TestCase):
    def check(self, preset, tree):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        for rel, text in dict(tree, **{"pubspec.yaml": "name: demo\n"}).items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        out = subprocess.run([sys.executable, CHECK, "--root", tmp, "--rules", os.path.join(PRESETS, preset + ".layers.json"),
                              "--format", "json"], capture_output=True, text=True)
        return json.loads(out.stdout)

    def test_clean_tree_documented_in_preset_clean_has_no_violations(self):
        report = self.check("clean", CLEAN_TREE)
        self.assertEqual(report["violations"], [], report["violations"])
        self.assertEqual(report["unclassified"], [])

    def test_layered_tree_documented_in_preset_layered_has_no_violations(self):
        report = self.check("layered", LAYERED_TREE)
        self.assertEqual(report["violations"], [], report["violations"])
        self.assertEqual(report["unclassified"], [])


if __name__ == "__main__":
    unittest.main()
