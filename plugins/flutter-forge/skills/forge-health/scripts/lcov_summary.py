#!/usr/bin/env python3
"""Line coverage per file from an existing coverage/lcov.info, joined with git churn.

Usage: lcov_summary.py [--root PROJECT] [--lcov PATH] [--since-days 90] [--top 15] [--format json|text]

Never runs tests. Without an lcov file it says so and prints the command that creates one.
Dart files under lib/ that the report does not mention count as 0% covered (`flutter test
--coverage` only lists files a test imported). Read-only, no network, Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import git_churn  # noqa: E402

GENERATED = git_churn.GENERATED
HOT_COVERAGE = 0.5


def parse_lcov(text: str) -> Dict[str, Dict[str, int]]:
    files: Dict[str, Dict[str, int]] = {}
    current: Optional[str] = None
    for line in text.splitlines():
        if line.startswith("SF:"):
            current = line[3:].strip().replace(os.sep, "/")
            files.setdefault(current, {"lf": 0, "lh": 0})
        elif line.startswith("LF:") and current:
            files[current]["lf"] = int(line[3:] or 0)
        elif line.startswith("LH:") and current:
            files[current]["lh"] = int(line[3:] or 0)
        elif line.startswith("end_of_record"):
            current = None
    return files


def lib_files(root: str) -> List[str]:
    found = []
    base = os.path.join(root, "lib")
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if name.endswith(".dart") and not GENERATED.search(rel):
                found.append(rel)
    return sorted(found)


def normalize(path: str, root: str) -> str:
    path = path.replace(os.sep, "/")
    prefix = root.replace(os.sep, "/").rstrip("/") + "/"
    if path.startswith(prefix):
        path = path[len(prefix):]
    while path.startswith("./"):
        path = path[2:]
    return path


def coverage(root: str, lcov_path: Optional[str] = None, churn_by_file: Optional[Dict[str, int]] = None,
             top: int = 15) -> Dict:
    path = lcov_path or os.path.join(root, "coverage", "lcov.info")
    if not os.path.exists(path):
        return {"available": False, "reason": "coverage/lcov.info not found",
                "hint": "run `flutter test --coverage` (it is not run automatically)"}
    try:
        with open(path, encoding="utf-8") as fh:
            raw = parse_lcov(fh.read())
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return {"available": False, "reason": "lcov unreadable: %s" % exc}

    measured = {normalize(p, root): v for p, v in raw.items() if not GENERATED.search(p)}
    per_file: Dict[str, float] = {}
    lines_total = lines_hit = 0
    for rel in lib_files(root):
        v = measured.get(rel)
        if v is None:
            per_file[rel] = 0.0
            continue
        lines_total += v["lf"]
        lines_hit += v["lh"]
        per_file[rel] = (v["lh"] / v["lf"]) if v["lf"] else 1.0
    unlisted = [f for f in per_file if f not in measured]

    hotspots = []
    for rel, commits in (churn_by_file or {}).items():
        cov = per_file.get(rel)
        if cov is None or cov >= HOT_COVERAGE:
            continue
        hotspots.append({"file": rel, "commits": commits, "coverage": round(cov, 2),
                         "score": round(commits * (1 - cov), 2), "in_lcov": rel in measured})
    hotspots.sort(key=lambda h: (-h["score"], h["file"]))
    return {
        "available": True, "path": os.path.relpath(path, root),
        "line_coverage": round(lines_hit / lines_total, 3) if lines_total else None,
        "files_in_lib": len(per_file), "files_not_in_lcov": len(unlisted),
        "hotspots_untested": hotspots[:top], "hotspot_count": len(hotspots),
        "by_file": {k: round(v, 3) for k, v in per_file.items()},
    }


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--lcov")
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args(argv)
    ch = git_churn.churn(args.root, args.since_days, args.top)
    report = coverage(args.root, args.lcov, ch.get("by_file") if ch.get("available") else None, args.top)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif not report["available"]:
        print("Coverage: not available — %s. %s" % (report["reason"], report.get("hint", "")))
    else:
        print("Coverage: %s lines · %d lib files (%d absent from lcov)" % (
            "%.1f%%" % (report["line_coverage"] * 100) if report["line_coverage"] is not None else "n/a",
            report["files_in_lib"], report["files_not_in_lcov"]))
        for h in report["hotspots_untested"]:
            print("  %3d commits  %3d%%  %s" % (h["commits"], h["coverage"] * 100, h["file"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
