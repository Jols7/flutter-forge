#!/usr/bin/env python3
"""Check Dart imports against flutter-forge layer rules (layers.json).

Usage:
  check_layers.py --rules RULES.json [--root PROJECT] [--files F ...] [--changed-from REF]
                  [--format text|json] [--summary] [--no-fail]

  --files / --changed-from limit the *reported* violations to those files (new or
  changed code); the whole tree is still classified. Exit 1 when violations are
  reported (unless --no-fail). Read-only, no network, Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
from collections import Counter
from typing import Dict, List, Optional, Pattern

IMPORT_RE = re.compile(r"""^\s*(import|export)\s+['"]([^'"]+)['"]""", re.M)


def glob_to_regex(glob: str) -> Pattern[str]:
    out, i = "", 0
    while i < len(glob):
        c = glob[i]
        if c == "*":
            while i + 1 < len(glob) and glob[i + 1] == "*":
                i += 1
            out += ".*"
        elif c == "?":
            out += "[^/]"
        else:
            out += re.escape(c)
        i += 1
    return re.compile("^" + out + "$")


class Rules:
    def __init__(self, data: Dict) -> None:
        self.source_root = data.get("source_root", "lib").rstrip("/")
        self.features_root = (data.get("features_root") or "").rstrip("/")
        self.ignore = [glob_to_regex(g) for g in data.get("ignore", [])]
        self.layers = []
        for name, spec in data["layers"].items():
            self.layers.append({
                "name": name,
                "paths": [glob_to_regex(p) for p in spec.get("paths", [])],
                "may_import": set(spec.get("may_import", [])),
                "forbidden": spec.get("forbidden_imports", []),
                "allowed": spec.get("allowed_imports", []),
            })
        self.by_name = {layer["name"]: layer for layer in self.layers}
        self.cross_allowed = set((data.get("cross_feature") or {}).get("allowed_layers", []))
        self.barrels = data.get("barrels", {})

    def ignored(self, path: str) -> bool:
        return any(rx.match(path) for rx in self.ignore)

    def classify(self, path: str) -> Optional[str]:
        if path in self.barrels:
            return self.barrels[path]
        for layer in self.layers:
            if any(rx.match(path) for rx in layer["paths"]):
                return layer["name"]
        return None

    def feature_of(self, path: str) -> Optional[str]:
        if not self.features_root or not path.startswith(self.features_root + "/"):
            return None
        rest = path[len(self.features_root) + 1:]
        return rest.split("/", 1)[0] if "/" in rest else None


def read_package(root: str) -> Optional[str]:
    try:
        with open(os.path.join(root, "pubspec.yaml"), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^name:\s*([A-Za-z0-9_]+)", line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def dart_files(root: str, source_root: str) -> List[str]:
    files = []
    base = os.path.join(root, source_root)
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.endswith(".dart"):
                files.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return sorted(files)


def resolve(uri: str, importer: str, package: Optional[str]) -> Optional[str]:
    if uri.startswith("dart:"):
        return None
    if uri.startswith("package:"):
        pkg, _, rest = uri[len("package:"):].partition("/")
        return "lib/" + rest if pkg == package else None
    return posixpath.normpath(posixpath.join(posixpath.dirname(importer), uri))


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def changed_files(root: str, ref: str) -> List[str]:
    out = subprocess.run(["git", "-C", root, "diff", "--name-only", ref, "--"], capture_output=True, text=True, check=False)
    untracked = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, check=False)
    names = set(out.stdout.split()) | set(untracked.stdout.split())
    return sorted(n for n in names if n.endswith(".dart"))


def check(root: str, rules: Rules, package: Optional[str]) -> Dict:
    files = [f for f in dart_files(root, rules.source_root) if not rules.ignored(f)]
    violations: List[Dict] = []
    unclassified: List[str] = []
    layer_counts: Counter = Counter()
    for path in files:
        layer_name = rules.classify(path)
        if layer_name is None:
            unclassified.append(path)
            continue
        layer_counts[layer_name] += 1
        layer = rules.by_name[layer_name]
        try:
            with open(os.path.join(root, path), encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        for match in IMPORT_RE.finditer(text):
            uri = match.group(2)
            line = line_of(text, match.start())
            base = {"file": path, "line": line, "import": uri, "from_layer": layer_name}
            if not uri.startswith("dart:") and _forbidden(uri, layer):
                violations.append(dict(base, kind="forbidden-import", to_layer=None,
                                       message="'%s' layer must not import %s" % (layer_name, uri)))
                continue
            target = resolve(uri, path, package)
            if target is None or rules.ignored(target):
                continue
            target_layer = rules.classify(target)
            if target_layer is None:
                continue
            if "*" not in layer["may_import"] and target_layer not in layer["may_import"]:
                violations.append(dict(base, kind="layer", to_layer=target_layer,
                                       message="%s → %s is not allowed (may import: %s)" % (layer_name, target_layer, ", ".join(sorted(layer["may_import"])))))
                continue
            src_feature, dst_feature = rules.feature_of(path), rules.feature_of(target)
            if ("*" not in layer["may_import"] and src_feature and dst_feature and src_feature != dst_feature
                    and target_layer not in rules.cross_allowed):
                violations.append(dict(base, kind="cross-feature", to_layer=target_layer,
                                       message="feature '%s' imports %s of feature '%s' (only %s may cross features)" % (
                                           src_feature, target_layer, dst_feature, ", ".join(sorted(rules.cross_allowed)) or "nothing")))
    return {"files": len(files), "layers": dict(layer_counts), "unclassified": unclassified, "violations": violations}


def _forbidden(uri: str, layer: Dict) -> bool:
    if any(uri == a or (a.endswith("/") and uri.startswith(a)) for a in layer["allowed"]):
        return False
    return any(uri.startswith(prefix) for prefix in layer["forbidden"])


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rules", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--files", nargs="*", default=None)
    parser.add_argument("--changed-from")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    rules_path = args.rules if os.path.isabs(args.rules) or os.path.exists(args.rules) else os.path.join(root, args.rules)
    with open(rules_path, encoding="utf-8") as fh:
        rules = Rules(json.load(fh))
    report = check(root, rules, read_package(root))

    scope = None
    if args.files is not None:
        scope = {f.replace(os.sep, "/") for f in args.files}
    if args.changed_from:
        scope = (scope or set()) | set(changed_files(root, args.changed_from))
    all_violations = report["violations"]
    reported = [v for v in all_violations if scope is None or v["file"] in scope]
    report["reported"] = reported
    report["preexisting"] = len(all_violations) - len(reported)
    if scope is not None:
        report["unclassified"] = [f for f in report["unclassified"] if f in scope]

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print("Layer check: %d files · %s" % (report["files"], ", ".join("%s=%d" % kv for kv in sorted(report["layers"].items()))))
        if report["unclassified"]:
            print("Unclassified (%d): %s%s" % (len(report["unclassified"]), ", ".join(report["unclassified"][:10]), " …" if len(report["unclassified"]) > 10 else ""))
        if args.summary:
            kinds = Counter(v["kind"] for v in reported)
            pairs = Counter("%s → %s" % (v["from_layer"], v["to_layer"] or v["import"].split("/")[0]) for v in reported)
            top = Counter(v["file"] for v in reported).most_common(10)
            print("Violations reported: %d (pre-existing outside scope: %d)" % (len(reported), report["preexisting"]))
            for kind, n in kinds.most_common():
                print("  %-17s %d" % (kind, n))
            for pair, n in pairs.most_common(10):
                print("  %-40s %d" % (pair, n))
            for f, n in top:
                print("  %4d  %s" % (n, f))
        else:
            for v in reported:
                print("%s:%d  [%s] %s" % (v["file"], v["line"], v["kind"], v["message"]))
            print("Violations: %d%s" % (len(reported), " (+%d pre-existing outside scope)" % report["preexisting"] if report["preexisting"] else ""))
    return 1 if reported and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
