#!/usr/bin/env python3
"""Mechanical checks for presentation code: size, complexity, naming and a few anti-patterns.

Usage: check_presentation.py [--root PROJECT] [--files F ...] [--changed-from REF] [--profile PROFILE.yaml]
                             [--max-build-lines N] [--max-build-complexity N] [--max-file-lines N]
                             [--max-classes N] [--max-depth N] [--ui-helpers allow|forbid] [--mode new|adopt|improve]
                             [--format text|json] [--no-fail]

Thresholds come from flags, else from `quality.*` / `architecture.ui_helpers` in --profile, else
the defaults below (deliberately strict targets; see forge-presentation/references/structure.md).
In `adopt` and `improve` mode (flag or `architecture.mode`) the defaults are the looser LEGACY
numbers (build 120 lines / complexity 10, file 300, depth 20) and build-lines and build-complexity
are warnings, so an existing app is not failed wholesale. Values set in the profile always win.
Scope: files under presentation/, pages/, widgets/, screens/ or state/ (generated code skipped).

  build-lines        build() longer than max_build_lines                          [finding; warn in adopt/improve]
  build-complexity   build() cyclomatic complexity above max_build_complexity     [finding; warn in adopt/improve]
                     APPROXIMATE (regex, no Dart parser): counts if, for, while, case, catch,
                     &&, ||, ?? and ternaries. Prefer DCM's number when quality.dcm is true.
  file-lines         file longer than max_file_lines                              [warn]
  classes-per-file   more than max_classes classes (state/ files and sealed hierarchies exempt) [warn]
  nesting-depth      indentation deeper than max_depth levels (2 spaces each)     [warn]
  file-name          not snake_case, or a pages/ file not ending in _page.dart    [warn]
  ui-helper          private Widget _buildX() when ui_helpers is forbid           [finding]
  hardcoded-style    Color(0x........) or fontFamily: outside a theme folder      [finding]
  locator-in-ui      getIt / GetIt / ServiceLocator inside presentation           [finding]
  navigation-in-state Navigator./context.go/push in a state/ file                 [finding]

Whether the code is well structured is left to the reviewer; this only counts and matches.
Read-only, no network, Python 3.9+ stdlib. Exit 1 only when a [finding] exists (unless --no-fail).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

GENERATED = re.compile(r"(\.g|\.freezed|\.gr|\.config|\.mocks)\.dart$|/generated/|/l10n/")
IN_SCOPE = re.compile(r"/(presentation|pages|widgets|screens|state)/")
DEFAULTS = {"max_build_lines": 50, "max_build_complexity": 5, "max_file_lines": 250,
            "max_classes": 3, "max_depth": 12, "ui_helpers": "allow"}
# adopt/improve: an existing app is measured against looser numbers and its size findings are warnings
LEGACY = {"max_build_lines": 120, "max_build_complexity": 10, "max_file_lines": 300,
          "max_classes": 3, "max_depth": 20}
PROFILE_KEYS = {"max_build_lines": "max_build_lines", "max_build_complexity": "max_build_complexity",
                "max_file_lines": "max_file_lines", "max_classes": "max_classes_per_file",
                "max_depth": "max_widget_depth", "ui_helpers": "ui_helpers"}
BUILD = re.compile(r"\bWidget\s+build\s*\(\s*BuildContext")
BRANCH = re.compile(r"\bif\b|\bfor\b|\bwhile\b|\bcase\b|\bcatch\b|&&|\|\||\?\?|\s\?\s")
CLASS = re.compile(r"^(?:abstract\s+|final\s+|base\s+|sealed\s+|interface\s+)*class\s+\w+", re.M)
SNAKE = re.compile(r"^[a-z][a-z0-9_]*\.dart$")
UI_HELPER = re.compile(r"\bWidget\s+_build\w*\s*\(")
HARDCODED = re.compile(r"\bColor\(\s*0x[0-9A-Fa-f]{6,8}\s*\)|\bfontFamily\s*:")
LOCATOR = re.compile(r"\bgetIt\s*[<(.]|\bGetIt\.(?:I|instance)\b|\bServiceLocator\b")
NAVIGATION = re.compile(r"\bNavigator\.|\bcontext\.(?:go|push|pop)\w*\(")


def strip(text: str) -> str:
    """Blank comments and string contents, keeping line numbers."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", text)
    return re.sub(r'"(?:\\.|[^"\\\n])*"', '""', text)


def read_profile(path: Optional[str]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^\s*mode:\s*(new|adopt|improve|migrate)\b", text, re.M)
    if m:
        out["mode"] = m.group(1)
    for name, key in PROFILE_KEYS.items():
        m = re.search(r"^\s*%s:\s*([\w]+)" % re.escape(key), text, re.M)
        if m:
            out[name] = m.group(1) if name == "ui_helpers" else int(m.group(1)) if m.group(1).isdigit() else DEFAULTS[name]
    return out


def build_methods(clean: str):
    """Yield (start_line, end_line, body) for each build() method."""
    for m in BUILD.finditer(clean):
        brace = clean.find("{", m.end())
        arrow = clean.find("=>", m.end())
        if brace == -1 or (arrow != -1 and arrow < brace):
            end = clean.find(";", m.end())
            end = len(clean) if end == -1 else end
        else:
            depth, i = 0, brace
            while i < len(clean):
                depth += (clean[i] == "{") - (clean[i] == "}")
                i += 1
                if depth == 0:
                    break
            end = i
        yield clean.count("\n", 0, m.start()) + 1, clean.count("\n", 0, end) + 1, clean[m.start():end]


def check_file(root: str, path: str, cfg: Dict[str, object]) -> List[Dict]:
    legacy = cfg.get("mode") in ("adopt", "improve")
    size_severity = "warn" if legacy else "finding"
    try:
        with open(os.path.join(root, path), encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError):
        return []
    clean = strip(raw)
    lines = raw.splitlines()
    out: List[Dict] = []
    name = os.path.basename(path)
    in_state = "/state/" in "/" + path

    def add(kind: str, line: int, severity: str, message: str) -> None:
        out.append({"file": path, "line": line, "kind": kind, "severity": severity, "message": message})

    for start, end, body in build_methods(clean):
        n = end - start + 1
        if n > cfg["max_build_lines"]:
            add("build-lines", start, size_severity, "build() is %d lines (max %d): extract widgets" % (n, cfg["max_build_lines"]))
        cc = 1 + len(BRANCH.findall(body))
        if cc > cfg["max_build_complexity"]:
            add("build-complexity", start, size_severity,
                "build() complexity ~%d (max %d, approximate): move logic into the state or a mapper" % (cc, cfg["max_build_complexity"]))
    if len(lines) > cfg["max_file_lines"]:
        add("file-lines", 1, "warn", "%d lines (max %d): split by section" % (len(lines), cfg["max_file_lines"]))
    classes = len(CLASS.findall(clean))
    if classes > cfg["max_classes"] and not in_state and "sealed class" not in clean:
        add("classes-per-file", 1, "warn", "%d classes (max %d): one public widget per file plus private helpers" % (classes, cfg["max_classes"]))
    for i, line in enumerate(clean.splitlines(), 1):
        if line.strip() and (len(line) - len(line.lstrip(" "))) // 2 > cfg["max_depth"]:
            add("nesting-depth", i, "warn", "indentation deeper than %d levels: extract a widget" % cfg["max_depth"])
            break
    if not SNAKE.match(name) or ("/pages/" in "/" + path and not name.endswith("_page.dart")):
        add("file-name", 1, "warn", "file name should be snake_case and end in _page.dart under pages/")
    if cfg["ui_helpers"] == "forbid":
        for m in UI_HELPER.finditer(clean):
            add("ui-helper", clean.count("\n", 0, m.start()) + 1, "finding", "private _buildX() method: extract a widget (ui_helpers: forbid)")
    if "/theme/" not in "/" + path:
        for m in HARDCODED.finditer(clean):
            add("hardcoded-style", clean.count("\n", 0, m.start()) + 1, "finding", "hex color or fontFamily: use the theme tokens")
    for m in LOCATOR.finditer(clean):
        add("locator-in-ui", clean.count("\n", 0, m.start()) + 1, "finding", "service locator in presentation: inject through the constructor")
    if in_state:
        for m in NAVIGATION.finditer(clean):
            add("navigation-in-state", clean.count("\n", 0, m.start()) + 1, "finding", "navigation inside a state manager: emit a one-shot event instead")
    return out


def changed_files(root: str, ref: str) -> List[str]:
    diff = subprocess.run(["git", "-C", root, "diff", "--name-only", "--relative", ref, "--"], capture_output=True, text=True, check=False)
    new = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, check=False)
    return sorted(n for n in set(diff.stdout.split()) | set(new.stdout.split()) if n.endswith(".dart"))


def dart_files(root: str) -> List[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "lib")):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        out += [os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/") for f in filenames if f.endswith(".dart")]
    return sorted(out)


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".")
    p.add_argument("--files", nargs="*")
    p.add_argument("--changed-from")
    p.add_argument("--profile")
    for k in ("max-build-lines", "max-build-complexity", "max-file-lines", "max-classes", "max-depth"):
        p.add_argument("--" + k, type=int)
    p.add_argument("--mode", choices=["new", "adopt", "improve", "migrate"],
                   help="architecture mode; default from --profile, else new")
    p.add_argument("--ui-helpers", choices=["allow", "forbid"])
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--no-fail", action="store_true")
    a = p.parse_args(argv)
    root = os.path.abspath(a.root)
    prof = read_profile(a.profile)
    mode = a.mode or prof.get("mode") or "new"
    cfg = dict(DEFAULTS)
    if mode in ("adopt", "improve"):
        cfg.update(LEGACY)
    cfg.update({k: v for k, v in prof.items() if k != "mode"})
    cfg["mode"] = mode
    for k in DEFAULTS:
        v = getattr(a, k)
        if v is not None:
            cfg[k] = v
    if a.changed_from:
        files = sorted(set(changed_files(root, a.changed_from)) | {f.replace(os.sep, "/") for f in (a.files or [])})
    else:
        files = [f.replace(os.sep, "/") for f in a.files] if a.files else dart_files(root)
    files = [f for f in files if f.endswith(".dart") and not GENERATED.search("/" + f) and IN_SCOPE.search("/" + f) and not f.startswith("test/")]
    findings: List[Dict] = []
    for f in files:
        findings += check_file(root, f, cfg)
    if a.format == "json":
        print(json.dumps({"files": len(files), "thresholds": cfg, "findings": findings}, indent=2))
    else:
        for f in findings:
            print("%s:%d  [%s/%s] %s" % (f["file"], f["line"], f["severity"], f["kind"], f["message"]))
        print("Presentation check: %d file(s), %d finding(s)" % (len(files), len(findings)))
    return 1 if any(f["severity"] == "finding" for f in findings) and not a.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
