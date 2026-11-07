#!/usr/bin/env python3
"""Detect a Flutter project's stack and architecture for flutter-forge.

Usage: detect_project.py [PROJECT_ROOT] [--pretty]

Prints a JSON report to stdout. Read-only: never modifies files, never uses the
network. Python 3.9+ standard library only.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Optional

STATE_PACKAGES = {
    "flutter_bloc": "bloc", "bloc": "bloc", "hydrated_bloc": "bloc",
    "flutter_riverpod": "riverpod", "hooks_riverpod": "riverpod", "riverpod": "riverpod",
    "provider": "provider", "get": "getx", "mobx": "mobx", "flutter_mobx": "mobx",
    "signals": "signals",
}
DI_PACKAGES = {"get_it": "get_it", "injectable": "injectable"}
ROUTER_PACKAGES = {"go_router": "go_router", "auto_route": "auto_route", "beamer": "beamer"}
HTTP_PACKAGES = {"dio": "dio", "http": "http", "chopper": "chopper", "retrofit": "retrofit"}
CODEGEN_PACKAGES = {"freezed_annotation": "freezed", "json_annotation": "json_serializable"}
TEST_PACKAGES = ["mocktail", "mockito", "bloc_test", "patrol", "integration_test", "golden_toolkit", "alchemist"]
FEATURE_ROOT_CANDIDATES = ["lib/features", "lib/feature", "lib/modules", "lib/screens", "lib/presentation/screens", "lib/ui", "lib/pages"]
SKIP_DIRS = {".dart_tool", "build", ".git", "ios", "android", "macos", "windows", "linux", "web", ".fvm", "generated"}


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ""


def parse_pubspec(text: str) -> Dict[str, object]:
    """Minimal pubspec reader: name, top-level sections and their direct keys."""
    result: Dict[str, object] = {"name": None, "sections": {}}
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            key = key.strip()
            current = key
            sections.setdefault(key, [])
            if key == "name":
                result["name"] = value.strip().strip("'\"") or None
            continue
        if current is None:
            continue
        match = re.match(r"^( {2}|\t)([A-Za-z0-9_]+)\s*:", line)
        if match:
            sections[current].append(match.group(2))
    result["sections"] = sections
    return result


def classify(deps: List[str], table: Dict[str, str]) -> List[str]:
    found = []
    for dep in deps:
        if dep in table and table[dep] not in found:
            found.append(table[dep])
    return found


def walk_dart(root: str) -> List[str]:
    files = []
    lib = os.path.join(root, "lib")
    for dirpath, dirnames, filenames in os.walk(lib):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".dart") and not re.search(r"\.(g|freezed|gr|config|mocks)\.dart$", name):
                files.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return sorted(files)


def detect_feature_root(root: str, files: List[str]) -> Optional[str]:
    best, best_count = None, 0
    for candidate in FEATURE_ROOT_CANDIDATES:
        if os.path.isdir(os.path.join(root, candidate)):
            count = sum(1 for f in files if f.startswith(candidate + "/"))
            if count > best_count:
                best, best_count = candidate, count
    return best


def feature_names(root: str, feature_root: Optional[str]) -> List[str]:
    if not feature_root:
        return []
    path = os.path.join(root, feature_root)
    return sorted(d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith("."))


def guess_architecture(files: List[str], feature_root: Optional[str]) -> Dict[str, object]:
    evidence: List[str] = []
    score = Counter()
    layer_dirs = Counter()
    for f in files:
        parts = f.split("/")
        for layer in ("domain", "data", "presentation"):
            if layer in parts:
                layer_dirs[layer] += 1
    if all(layer_dirs[l] for l in ("domain", "data", "presentation")):
        score["clean"] += 3
        evidence.append("domain/, data/ and presentation/ folders present")
    impl = [f for f in files if f.endswith("_repository_impl.dart")]
    contracts = [f for f in files if f.endswith("_repository.dart") and "/domain/" in f]
    concrete = [f for f in files if f.endswith("_repository.dart") and "/domain/" not in f]
    apis = [f for f in files if f.endswith(("_api.dart", "_service.dart"))]
    repo_total = len(impl) + len(concrete)
    if impl and len(impl) >= 0.5 * repo_total:
        score["clean"] += 2
        evidence.append("%d of %d repositories are *_repository_impl.dart" % (len(impl), repo_total))
    if contracts:
        score["clean"] += 1
        evidence.append("%d repository contracts under domain/" % len(contracts))
    if concrete and len(concrete) > len(impl):
        score["layered"] += 3
        evidence.append("%d concrete *_repository.dart vs %d *_impl; %d *_api/_service files" % (len(concrete), len(impl), len(apis)))
    if any("/dtos/" in f or re.search(r"/dto_[a-z0-9_]+\.dart$", f) for f in files):
        evidence.append("DTO files detected")
    if feature_root and feature_root.endswith(("screens", "pages", "ui")):
        score["layered"] += 1
        evidence.append("UI-module feature root: %s" % feature_root)
    usecases = [f for f in files if "/usecases/" in f or "/use_cases/" in f]
    if usecases:
        score["clean"] += 1
        evidence.append("%d use-case files" % len(usecases))
    if not score:
        return {"preset": "unknown", "confidence": "low", "evidence": evidence or ["no recognizable layering"], "use_cases": bool(usecases)}
    preset, top = score.most_common(1)[0]
    total = sum(score.values())
    confidence = "high" if top >= 4 and top / total >= 0.75 else "medium" if top / total >= 0.6 else "low"
    return {"preset": preset, "confidence": confidence, "evidence": evidence, "use_cases": bool(usecases), "scores": dict(score)}


def count_usage(root: str, files: List[str], patterns: Dict[str, str]) -> Dict[str, int]:
    counts = {k: 0 for k in patterns}
    compiled = {k: re.compile(v) for k, v in patterns.items()}
    for f in files:
        text = read(os.path.join(root, f))
        for key, rx in compiled.items():
            if rx.search(text):
                counts[key] += 1
    return counts


def detect_flavors(files: List[str]) -> Dict[str, object]:
    mains = [f for f in files if re.match(r"^lib/main(_[a-z0-9_]+)?\.dart$", f)]
    flavors = []
    pattern = None
    for f in mains:
        m = re.match(r"^lib/main_(?:([a-z0-9]+)_)?([a-z0-9]+)\.dart$", f)
        if m:
            flavors.append(m.group(2))
            pattern = "lib/main_%s{flavor}.dart" % ((m.group(1) + "_") if m.group(1) else "")
    return {"entrypoints": mains, "names": sorted(set(flavors)), "entrypoint_pattern": pattern}


def detect_l10n(root: str, pubspec_text: str, sections: Dict[str, List[str]]) -> Dict[str, object]:
    arbs = []
    for candidate in ("lib/l10n", "lib/src/l10n", "assets/l10n", "lib/core/l10n"):
        path = os.path.join(root, candidate)
        if os.path.isdir(path):
            arbs += [os.path.join(candidate, n) for n in sorted(os.listdir(path)) if n.endswith(".arb")]
    if "flutter_intl" in sections:
        pipeline = "intl_utils"
    elif os.path.exists(os.path.join(root, "l10n.yaml")) or re.search(r"^\s+generate:\s*true", pubspec_text, re.M):
        pipeline = "gen-l10n"
    elif arbs:
        pipeline = "unknown-arb"
    else:
        pipeline = "none"
    return {"pipeline": pipeline, "arb_files": arbs}


def main(argv: List[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    pretty = "--pretty" in argv
    root = os.path.abspath(args[0] if args else ".")
    pubspec_path = os.path.join(root, "pubspec.yaml")
    if not os.path.exists(pubspec_path):
        print(json.dumps({"error": "pubspec.yaml not found", "root": root}))
        return 2
    pubspec_text = read(pubspec_path)
    pubspec = parse_pubspec(pubspec_text)
    sections: Dict[str, List[str]] = pubspec["sections"]  # type: ignore[assignment]
    deps = sections.get("dependencies", [])
    dev_deps = sections.get("dev_dependencies", [])
    files = walk_dart(root)
    feature_root = detect_feature_root(root, files)
    fvmrc = read(os.path.join(root, ".fvmrc"))
    fvm_version = None
    match = re.search(r'"flutter"\s*:\s*"([^"]+)"', fvmrc) or re.search(r"^([0-9][^\s]*)$", fvmrc.strip(), re.M)
    if match:
        fvm_version = match.group(1)
    usage = count_usage(root, files, {
        "service_locator_in_widgets_or_state": r"(GetIt\.I|getIt<|ServiceLocator\.getIt|GetIt\.instance)",
        "manual_bearer_header": r"['\"]Authorization['\"]\s*:\s*['\"]Bearer",
        "throws_string": r"throw\s+['\"]|throw\s+e\.response\?\.data",
        "result_type": r"sealed\s+class\s+Result\b|Either<",
        "change_notifier": r"extends\s+ChangeNotifier",
        "cubit_or_bloc": r"extends\s+(Cubit|Bloc)<",
        "riverpod_notifier": r"extends\s+(_\$\w+|AsyncNotifier|Notifier|StateNotifier)<",
        "navigator_push": r"Navigator\.(push|of\(context\)\.push)",
        "go_router": r"GoRouter\(|context\.(go|push)\(",
        "get_navigation": r"Get\.(to|off|toNamed|offAll)\(",
        "dotenv": r"dotenv\.(env|load)",
        "dart_define": r"String\.fromEnvironment",
    })
    code_state = {
        "bloc": usage["cubit_or_bloc"],
        "riverpod": usage["riverpod_notifier"],
        "provider": usage["change_notifier"],
    }
    primary_state = max(code_state, key=code_state.get) if any(code_state.values()) else None
    report = {
        "root": root,
        "package": pubspec["name"],
        "sdk": {"fvm": bool(fvmrc), "flutter_version": fvm_version, "command": "fvm flutter" if fvmrc else "flutter"},
        "dependencies": {
            "state": classify(deps, STATE_PACKAGES),
            "state_primary_in_code": primary_state,
            "di": classify(deps, DI_PACKAGES),
            "router": classify(deps, ROUTER_PACKAGES),
            "http": classify(deps, HTTP_PACKAGES),
            "codegen": classify(deps, CODEGEN_PACKAGES),
            "secure_storage": "flutter_secure_storage" in deps,
            "dotenv": "flutter_dotenv" in deps,
            "testing": [p for p in TEST_PACKAGES if p in dev_deps or p in deps],
            "lints": [p for p in ("flutter_lints", "very_good_analysis", "lints", "dart_code_metrics", "custom_lint", "riverpod_lint") if p in dev_deps],
        },
        "patrol_config": "patrol" in sections,
        "l10n": detect_l10n(root, pubspec_text, sections),
        "flavors": detect_flavors(files),
        "structure": {
            "dart_files": len(files),
            "feature_root": feature_root,
            "features": feature_names(root, feature_root),
            "architecture": guess_architecture(files, feature_root),
            "has_test_dir": os.path.isdir(os.path.join(root, "test")),
            "test_files": sum(1 for _ in _iter_tests(root)),
            "e2e_dirs": [d for d in ("patrol_test", "integration_test") if os.path.isdir(os.path.join(root, d))],
        },
        "conventions_signals": usage,
        "existing": {
            "flutter_forge": os.path.isdir(os.path.join(root, ".flutter-forge")),
            "claude_md_lines": len(read(os.path.join(root, "CLAUDE.md")).splitlines()) or None,
            "analysis_options": os.path.exists(os.path.join(root, "analysis_options.yaml")),
        },
        "is_new_project": len(files) <= 3,
    }
    print(json.dumps(report, indent=2 if pretty else None, ensure_ascii=False))
    return 0


def _iter_tests(root: str):
    test_dir = os.path.join(root, "test")
    for dirpath, _, filenames in os.walk(test_dir):
        for name in filenames:
            if name.endswith("_test.dart"):
                yield name


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
