#!/usr/bin/env python3
"""Dependency and widget-size metrics for flutter-forge's forge-health.

Usage: code_metrics.py [--root PROJECT] [--top 10] [--outdated] [--flutter-command "flutter"]
                       [--format json|text]

- Dependencies: pubspec.yaml sections (hosted / any / git / path / sdk) and pubspec.lock counts.
- `--outdated` runs `<flutter-command> pub outdated --json` (needs network and a resolved
  pubspec) with a time limit and reports "not run" when it cannot. Without the flag nothing
  leaves the machine.
- Code size: largest files, largest widget classes and longest `build()` methods. Braces are
  counted outside strings and comments, which is accurate enough for ranking.
Read-only, Python 3.9+ stdlib. Always exits 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lcov_summary import GENERATED, lib_files  # noqa: E402

SECTIONS = ("dependencies", "dev_dependencies", "dependency_overrides")
WIDGET_BASES = ("StatelessWidget", "StatefulWidget", "ConsumerWidget", "ConsumerStatefulWidget", "HookWidget",
                "HookConsumerWidget", "State<", "ConsumerState<")
CLASS_RE = re.compile(r"^(?:abstract\s+|final\s+|base\s+)*class\s+(\w+)(?:<[^>{]*>)?\s+extends\s+([\w<>?, ]+?)(?:\s+(?:with|implements)\b[^{]*)?\s*\{", re.M)
BUILD_RE = re.compile(r"\bWidget\s+build\s*\(\s*BuildContext\b[^)]*\)\s*(?:=>|\{)")
LONG_FILE = 300
LONG_BUILD = 80


def parse_pubspec(text: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {s: {} for s in SECTIONS}
    section: Optional[str] = None
    current: Optional[str] = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key = line.split(":", 1)[0].strip()
            section = key if key in SECTIONS else None
            current = None
        elif section and indent == 2 and ":" in line:
            name, _, value = line.strip().partition(":")
            value = value.strip().strip("'\"")
            current = name
            out[section][name] = value or "?"
        elif section and current and indent >= 4:
            key = line.strip().split(":", 1)[0]
            if key in ("git", "path", "sdk", "hosted"):
                out[section][current] = key
            elif key == "version" and out[section].get(current) == "?":
                out[section][current] = line.split(":", 1)[1].strip().strip("'\"")
    return out


def classify(constraint: str) -> str:
    if constraint in ("git", "path", "sdk", "hosted"):
        return constraint
    if constraint in ("any", "", "?"):
        return "any" if constraint == "any" else "unconstrained"
    if constraint.startswith("^"):
        return "caret"
    return "pinned-or-range"


def parse_lock(text: str) -> Dict[str, int]:
    counts = {"direct main": 0, "direct dev": 0, "transitive": 0, "direct overridden": 0}
    for m in re.finditer(r"^\s+dependency:\s*\"?([a-z ]+)\"?\s*$", text, re.M):
        counts[m.group(1).strip()] = counts.get(m.group(1).strip(), 0) + 1
    return counts


def dependencies(root: str) -> Dict:
    try:
        with open(os.path.join(root, "pubspec.yaml"), encoding="utf-8") as fh:
            spec = parse_pubspec(fh.read())
    except OSError:
        return {"available": False, "reason": "pubspec.yaml not found"}
    kinds: Dict[str, int] = {}
    risky: List[str] = []
    for section, deps in spec.items():
        for name, constraint in deps.items():
            kind = classify(constraint)
            kinds[kind] = kinds.get(kind, 0) + 1
            if kind in ("git", "path", "any", "unconstrained") or section == "dependency_overrides":
                risky.append("%s (%s%s)" % (name, kind, ", override" if section == "dependency_overrides" else ""))
    lock = None
    try:
        with open(os.path.join(root, "pubspec.lock"), encoding="utf-8") as fh:
            lock = parse_lock(fh.read())
    except OSError:
        pass
    return {"available": True, "direct": len(spec["dependencies"]), "dev": len(spec["dev_dependencies"]),
            "overrides": len(spec["dependency_overrides"]), "constraint_kinds": kinds,
            "needs_attention": sorted(risky), "lock": lock,
            "lock_present": lock is not None}


def outdated(root: str, flutter_command: str) -> Dict:
    cmd = shlex.split(flutter_command) + ["pub", "outdated", "--json"]
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=90, check=False)
        data = json.loads(proc.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return {"run": False, "reason": "pub outdated not run (%s)" % type(exc).__name__}
    discontinued, major, minor = [], [], 0
    for pkg in data.get("packages", []):
        cur = (pkg.get("current") or {}).get("version")
        latest = (pkg.get("latest") or {}).get("version")
        if pkg.get("isDiscontinued"):
            discontinued.append(pkg["package"])
        if cur and latest and cur != latest:
            if cur.split(".")[0] != latest.split(".")[0]:
                major.append("%s %s → %s" % (pkg["package"], cur, latest))
            else:
                minor += 1
    return {"run": True, "discontinued": sorted(discontinued), "major_behind": sorted(major),
            "minor_or_patch_behind": minor}


def block_end(text: str, open_idx: int) -> int:
    """Index of the brace that closes the one at open_idx, skipping strings and comments."""
    depth, i, n = 0, open_idx, len(text)
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "//":
            i = text.find("\n", i)
            if i < 0:
                return n
        elif two == "/*":
            i = text.find("*/", i + 2)
            if i < 0:
                return n
            i += 1
        elif c in "'\"":
            quote = text[i:i + 3] if text[i:i + 3] in ("'''", '"""') else c
            j = i + len(quote)
            while j < n and text[j:j + len(quote)] != quote:
                j += 2 if text[j] == "\\" else 1
            i = j + len(quote) - 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


def line_no(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def code_size(root: str, top: int) -> Dict:
    files: List[Tuple[int, str]] = []
    classes: List[Dict] = []
    builds: List[Dict] = []
    widgets = 0
    for rel in lib_files(root):
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        files.append((text.count("\n") + 1, rel))
        for m in CLASS_RE.finditer(text):
            if not any(m.group(2).strip().startswith(b) for b in WIDGET_BASES):
                continue
            widgets += 1
            end = block_end(text, m.end() - 1)
            classes.append({"file": rel, "class": m.group(1), "line": line_no(text, m.start()),
                            "lines": line_no(text, end) - line_no(text, m.start()) + 1})
        for m in BUILD_RE.finditer(text):
            if m.group(0).endswith("{"):
                end = block_end(text, m.end() - 1)
            else:
                end = text.find(";", m.end())
                end = len(text) if end < 0 else end
            builds.append({"file": rel, "line": line_no(text, m.start()),
                           "lines": line_no(text, end) - line_no(text, m.start()) + 1})
    files.sort(reverse=True)
    classes.sort(key=lambda c: -c["lines"])
    builds.sort(key=lambda b: -b["lines"])
    return {
        "dart_files": len(files), "dart_lines": sum(n for n, _ in files), "widget_classes": widgets,
        "files_over_%d" % LONG_FILE: sum(1 for n, _ in files if n > LONG_FILE),
        "builds_over_%d" % LONG_BUILD: sum(1 for b in builds if b["lines"] > LONG_BUILD),
        "largest_files": [{"file": f, "lines": n} for n, f in files[:top]],
        "largest_widgets": classes[:top], "longest_builds": builds[:top],
    }


def metrics(root: str, top: int = 10, with_outdated: bool = False, flutter_command: str = "flutter") -> Dict:
    deps = dependencies(root)
    if deps.get("available") and with_outdated:
        deps["outdated"] = outdated(root, flutter_command)
    elif deps.get("available"):
        deps["outdated"] = {"run": False, "reason": "not requested (--outdated)"}
    return {"dependencies": deps, "code": code_size(root, top)}


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--outdated", action="store_true")
    parser.add_argument("--flutter-command", default="flutter")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args(argv)
    report = metrics(os.path.abspath(args.root), args.top, args.outdated, args.flutter_command)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        code = report["code"]
        print("Code: %d files, %d lines, %d widget classes" % (code["dart_files"], code["dart_lines"], code["widget_classes"]))
        for w in code["largest_widgets"]:
            print("  %4d lines  %s  %s:%d" % (w["lines"], w["class"], w["file"], w["line"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
