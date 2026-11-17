#!/usr/bin/env python3
"""Change frequency per Dart file from `git log`, for flutter-forge's forge-health.

Usage: git_churn.py [--root PROJECT] [--since-days 90] [--top 15] [--format json|text]

Counts commits, distinct authors and changed lines per file inside PROJECT (paths are relative
to it, so monorepo folders work). Generated files are skipped. Read-only, no network,
Python 3.9+ stdlib. Always exits 0: a missing git history is reported, not raised.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from typing import Dict, List

GENERATED = re.compile(r"(\.g\.dart|\.freezed\.dart|\.gr\.dart|\.mocks\.dart|/generated/)")
SINGLE_OWNER = 0.8


def churn(root: str, since_days: int = 90, top: int = 15) -> Dict:
    cmd = ["git", "-C", root, "log", "--since=%d.days" % since_days, "--numstat", "--no-renames",
           "--format=@@%H|%an", "--relative", "--", "*.dart"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "reason": "git not runnable: %s" % exc}
    if proc.returncode != 0:
        return {"available": False, "reason": "not a git repository or no history (%s)" % proc.stderr.strip()[:120]}

    files: Dict[str, Dict] = {}
    author = None
    commits = set()
    for line in proc.stdout.splitlines():
        if line.startswith("@@"):
            sha, _, author = line[2:].partition("|")
            commits.add(sha)
            continue
        parts = line.split("\t")
        if len(parts) != 3 or author is None:
            continue
        added, deleted, path = parts
        if GENERATED.search(path):
            continue
        entry = files.setdefault(path, {"commits": 0, "added": 0, "deleted": 0, "authors": Counter()})
        entry["commits"] += 1
        entry["authors"][author] += 1
        if added.isdigit():
            entry["added"] += int(added)
        if deleted.isdigit():
            entry["deleted"] += int(deleted)

    rows: List[Dict] = []
    for path, e in files.items():
        owner, owner_n = e["authors"].most_common(1)[0]
        rows.append({"file": path, "commits": e["commits"], "authors": len(e["authors"]),
                     "lines_changed": e["added"] + e["deleted"],
                     "single_owner": e["commits"] >= 3 and owner_n / e["commits"] >= SINGLE_OWNER})
    rows.sort(key=lambda r: (-r["commits"], -r["lines_changed"], r["file"]))
    all_rows = rows
    rows = [r for r in all_rows if r["file"].startswith("lib/")]   # hot lists are production code
    return {
        "available": True, "since_days": since_days, "commits": len(commits),
        "files_touched": len(rows), "authors": len({a for e in files.values() for a in e["authors"]}),
        "top": rows[:top],
        "by_file": {r["file"]: r["commits"] for r in all_rows},
        "single_owner_in_top": sum(1 for r in rows[:top] if r["single_owner"]),
    }


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args(argv)
    report = churn(args.root, args.since_days, args.top)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    elif not report["available"]:
        print("Churn: not available — %s" % report["reason"])
    else:
        print("Churn (last %dd): %d commits, %d files, %d authors" % (
            report["since_days"], report["commits"], report["files_touched"], report["authors"]))
        for r in report["top"]:
            print("  %3d commits  %5d lines  %s%s" % (r["commits"], r["lines_changed"], r["file"],
                                                      "  [single owner]" if r["single_owner"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
