#!/usr/bin/env python3
"""Infer a draft layer map (layers.json) from a Flutter repo's real folders, for forge-health.

Usage: infer_layers.py [--root PROJECT] [--write FILE] [--format json|text] [--min-coverage 0.8]

Why: forge-audit's checker needs a layer map. A repo nobody set up rarely matches the presets,
so most files end up "unclassified" and the layer numbers are useless. This script first tests
both presets; when neither fits (under --min-coverage of files classified) it builds a draft
from folder names and file suffixes, then measures how much of the tree the draft covers.

The draft reuses the `layered` preset's import rules and only replaces the `paths`. It is a
proposal: roles come from names, so a folder called `services` or `providers` can be wrong.
Every mapping lists its source (`name` or `suffix`) and the report lists what stays unmapped.

Read-only (writes only to --write), no network, exit 0 always. Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
CHECK_LAYERS = os.path.join(SKILLS, "forge-audit", "scripts", "check_layers.py")
PRESETS = os.path.join(SKILLS, "forge-architecture", "presets")

# Folder name -> layer of the `layered` preset. Deliberately short: ambiguous names
# (services, providers, common, shared, helpers of unknown kind) are left to file suffixes.
ROLE_BY_NAME: Dict[str, str] = {}
for _layer, _names in {
    "presentation": "screens screen pages page ui views view presentation features feature modules",
    "models": "domain models model entities entity",
    "api": "api apis endpoints remote datasources datasource",
    "dtos": "dtos dto mappers",
    "repositories": "repositories repository",
    "composition": "app bootstrap router routes navigation",
    "composition_di": "di injection locator",
    "core_network": "network interceptors http",
    "core_storage": "storage local preferences cache",
    "core_config": "config flavors env environment",
    "core_ui": "widgets theme l10n components design_system",
    "core_constants": "constants",
    "core_utils": "utils util extensions helpers",
    "core_error": "error errors exceptions failures",
}.items():
    for _n in _names.split():
        ROLE_BY_NAME[_n] = _layer

# A subtree under these stays one layer: nested widgets/, models/, utils/ belong to the module.
LOCKED_LAYERS = {"presentation", "models"}
SKIP_DIRS = {"generated", ".dart_tool", "build"}
SUFFIX_ROLES: List[Tuple[str, str]] = [
    (r"_repository(_impl)?\.dart$", "repositories"),
    (r"_(api|endpoint|endpoints|datasource|remote_source)\.dart$", "api"),
    (r"_(dto|request|response)\.dart$", "dtos"),
    (r"_(page|screen|view|widget|bloc|cubit|provider|controller|viewmodel|view_model|notifier)\.dart$", "presentation"),
    (r"_(model|entity)\.dart$", "models"),
]
ROOT_FILE_ROLES: List[Tuple[str, str]] = [
    (r"^lib/main[a-z0-9_]*\.dart$", "composition"),
    (r"^lib/(app|bootstrap)\.dart$", "composition"),
    (r"^lib/firebase_options\.dart$", "core_config"),
]
MAX_EXACT_PER_DIR = 60
MAX_RULES = 400


def load_check_layers():
    spec = importlib.util.spec_from_file_location("check_layers", CHECK_LAYERS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dart_files(root: str) -> List[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "lib")):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name.endswith(".dart") and not re.search(r"\.(g|freezed|gr|config|mocks)\.dart$", name):
                out.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return out


def classify_with(module, rules_data: Dict, files: List[str]) -> Dict:
    rules = module.Rules(rules_data)
    kept = [f for f in files if not rules.ignored(f)]
    hit = [f for f in kept if rules.classify(f)]
    return {"files": len(kept), "classified": len(hit), "ratio": round(len(hit) / len(kept), 3) if kept else 0.0,
            "missing": [f for f in kept if not rules.classify(f)]}


def file_role(path: str) -> Optional[str]:
    for pattern, layer in ROOT_FILE_ROLES:
        if re.match(pattern, path):
            return layer
    for pattern, layer in SUFFIX_ROLES:
        if re.search(pattern, path):
            return layer
    return None


class Node:
    def __init__(self, path: str) -> None:
        self.path = path
        self.dirs: Dict[str, "Node"] = {}
        self.files: List[str] = []
        self.role: Optional[str] = None       # effective role after inheritance
        self.source = "none"                  # name | inherited | none
        self.subtree_roles: set = set()

    def count(self) -> int:
        return len(self.files) + sum(c.count() for c in self.dirs.values())


def build_tree(files: List[str]) -> Node:
    root = Node("lib")
    for path in files:
        node = root
        parts = path.split("/")[1:]
        for part in parts[:-1]:
            node = node.dirs.setdefault(part, Node(node.path + "/" + part))
        node.files.append(path)
    return root


def assign(node: Node, inherited: Optional[str], locked: bool) -> None:
    own = ROLE_BY_NAME.get(os.path.basename(node.path)) if node.path != "lib" else None
    if locked:
        node.role, node.source = inherited, "inherited"
    elif own:
        node.role, node.source = own, "name"
    else:
        node.role, node.source = inherited, "inherited" if inherited else "none"
    child_locked = locked or node.role in LOCKED_LAYERS
    for child in node.dirs.values():
        assign(child, node.role, child_locked)
    node.subtree_roles = {node.role} | set().union(*(c.subtree_roles for c in node.dirs.values())) if node.dirs else {node.role}


def emit(node: Node, rules: List[Tuple[str, str, str, int]]) -> None:
    """Append (glob, layer, source, files). A whole-subtree glob only when the subtree is one role."""
    if node.role and node.subtree_roles == {node.role}:
        rules.append((node.path + "/**", node.role, node.source, node.count()))
        return
    for path in node.files[:MAX_EXACT_PER_DIR] if len(node.files) <= MAX_EXACT_PER_DIR else []:
        layer = node.role if node.source == "name" else (file_role(path) or node.role)
        if layer:
            rules.append((path, layer, "name" if layer == node.role and node.source == "name" else "suffix", 1))
    for child in node.dirs.values():
        emit(child, rules)


def build_rules(preset: Dict, mappings: List[Tuple[str, str, str, int]]) -> Dict:
    data = copy.deepcopy(preset)
    paths: Dict[str, List[str]] = {}
    for glob, layer, _source, _n in mappings:
        paths.setdefault(layer, []).append(glob)
    layers = {}
    for name, spec in data["layers"].items():
        if name in paths:
            spec["paths"] = paths[name]
            layers[name] = spec
    data["layers"] = layers
    data["preset"] = "custom"
    data["description"] = "DRAFT inferred by forge-health from folder names and file suffixes. Review before trusting it."
    presentation = [g for g, layer, _s, _n in mappings if layer == "presentation" and g.endswith("/**")]
    root_dirs = [g[:-3] for g in presentation if g.count("/") == 2]
    data["features_root"] = max(root_dirs, key=lambda d: sum(1 for g, _l, _s, _n in mappings if g.startswith(d + "/")), default=data.get("features_root", ""))
    return data


def infer(root: str, min_coverage: float = 0.8) -> Dict:
    files = dart_files(root)
    if not files:
        return {"status": "insufficient", "reason": "no Dart files under lib/", "files": 0}
    module = load_check_layers()
    presets = {}
    for name in ("clean", "layered"):
        with open(os.path.join(PRESETS, "%s.layers.json" % name), encoding="utf-8") as fh:
            presets[name] = json.load(fh)
    fit = {name: classify_with(module, data, files) for name, data in presets.items()}
    best = max(fit, key=lambda n: fit[n]["ratio"])
    summary = {n: fit[n]["ratio"] for n in fit}
    if fit[best]["ratio"] >= min_coverage:
        return {"status": "preset_fits", "base_preset": best, "preset_coverage": summary, "files": len(files),
                "coverage": fit[best]["ratio"], "unmapped": [], "mappings": [], "rules": None}
    tree = build_tree(files)
    assign(tree, None, False)
    mappings: List[Tuple[str, str, str, int]] = []
    emit(tree, mappings)
    # lib/ root files (main_*.dart, firebase_options.dart) are the only ones left directly under lib
    mappings = mappings[:MAX_RULES]
    rules_data = build_rules(presets["layered"], mappings)
    after = classify_with(module, rules_data, files)
    missing_dirs = Counter(os.path.dirname(f) for f in after["missing"])
    status = "inferred" if after["ratio"] > fit[best]["ratio"] else "no_improvement"
    return {
        "status": status, "base_preset": "layered", "preset_coverage": summary, "files": len(files),
        "coverage": after["ratio"], "mapping_count": len(mappings),
        "mappings": [{"path": g, "layer": l, "source": s, "files": n} for g, l, s, n in mappings if g.endswith("/**")][:40],
        "by_layer": dict(Counter({l: sum(n for _g, ll, _s, n in mappings if ll == l) for l in {m[1] for m in mappings}}).most_common()),
        "by_source": dict(Counter({s: sum(n for _g, _l, ss, n in mappings if ss == s) for s in {m[2] for m in mappings}})),
        "unmapped": [{"dir": d, "files": n} for d, n in missing_dirs.most_common(12)],
        "rules": rules_data if status == "inferred" else None,
        "note": "draft from folder names and file suffixes; ambiguous folders (services, providers, common) stay unmapped unless a suffix decides",
    }


def render_text(result: Dict) -> str:
    lines = ["status: %s · files: %s · coverage: %s" % (result["status"], result.get("files"), result.get("coverage"))]
    if "preset_coverage" in result:
        lines.append("presets classify: %s" % result["preset_coverage"])
    for m in result.get("mappings", [])[:25]:
        lines.append("  %-52s -> %-14s %4d files (%s)" % (m["path"], m["layer"], m["files"], m["source"]))
    if result.get("unmapped"):
        lines.append("unmapped: %s" % ", ".join("%s (%d)" % (u["dir"], u["files"]) for u in result["unmapped"][:8]))
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", help="write the draft layers.json here (only when a draft was inferred)")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--min-coverage", type=float, default=0.8)
    args = parser.parse_args(argv)
    try:
        result = infer(os.path.abspath(args.root), args.min_coverage)
    except Exception as exc:  # never break the caller
        result = {"status": "insufficient", "reason": "collector failed: %s: %s" % (type(exc).__name__, str(exc)[:160])}
    if args.write and result.get("rules"):
        os.makedirs(os.path.dirname(os.path.abspath(args.write)), exist_ok=True)
        with open(args.write, "w", encoding="utf-8") as fh:
            json.dump(result["rules"], fh, indent=2)
    print(json.dumps(result, indent=2) if args.format == "json" else render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
