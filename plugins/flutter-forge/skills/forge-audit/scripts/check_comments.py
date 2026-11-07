#!/usr/bin/env python3
"""Check Dart comments against the flutter-forge comments policy.

Usage: check_comments.py [--root PROJECT] [--files F ...] [--format text|json] [--no-fail]

Flags what a script can decide reliably; whether a comment explains *why* is left to the
reviewer (forge-audit checklist §14):
  commented-out-code  consecutive // lines that parse as Dart statements
  todo-without-ref    TODO/FIXME/HACK/XXX without (#123), (HU-12…), (G-2…) or a URL
  banner              decorative separators (// =====, // ----- SECTION -----)
  missing-doc         public declarations in a domain/ folder without a /// doc comment
Read-only, no network, Python 3.9+ stdlib. Exit 1 when findings exist (unless --no-fail).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List

GENERATED = re.compile(r"(\.g|\.freezed|\.gr|\.config|\.mocks)\.dart$|/generated/|/l10n/generated/")
LINE_COMMENT = re.compile(r"^\s*//(?!/)(.*)$")
TOOL_DIRECTIVE = re.compile(r"^\s*(ignore(_for_file)?:|coverage:|dart format|@dart|ignore_for_file)", re.I)
CODE_LIKE = re.compile(
    r"(;\s*$|\{\s*$|^\s*\}|=>|^\s*(final|var|const|return|if|else|for|while|await|import|export|class|void|late|setState|print|debugPrint|throw|try|catch|switch|case)\b|^\s*[\w.$<>\[\]]+\(.*\)\s*[;,]?\s*$|^\s*\w+\s*=\s*[^=])")
PROSE_HINT = re.compile(r"^\s*[A-Z][a-z]+(\s+[a-z]+){3,}")
TODO = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b(.*)")
TODO_REF = re.compile(r"^\s*\(\s*(#\d+|[A-Z][A-Z0-9]*-\d+|G-\d+|https?://)[^)]*\)")
BANNER = re.compile(r"^\s*//+\s*([=\-*#~_/]{4,})|([=\-*#~_]{4,})\s*$")
PUBLIC_DECL = re.compile(r"^(abstract\s+interface\s+class|abstract\s+final\s+class|abstract\s+class|sealed\s+class|final\s+class|base\s+class|interface\s+class|class|enum|mixin|extension\s+type|typedef)\s+([A-Z]\w*)")
INTERFACE_START = re.compile(r"^abstract\s+interface\s+class\s+")
METHOD_SIG = re.compile(r"^  (?!//|@|\)|}|return\b|final\b|const\b)[\w<>?,\s\[\]]+?\s+([a-z]\w*)\s*[(<]")


def dart_files(root: str) -> List[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "lib")):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.endswith(".dart"):
                out.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return sorted(out)


def has_doc(lines: List[str], index: int) -> bool:
    i = index - 1
    while i >= 0 and (lines[i].strip().startswith("@") or not lines[i].strip()):
        if not lines[i].strip():
            return False
        i -= 1
    return i >= 0 and lines[i].strip().startswith("///")


def check_file(root: str, path: str) -> List[Dict]:
    try:
        with open(os.path.join(root, path), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    findings: List[Dict] = []

    def add(kind: str, line: int, message: str) -> None:
        findings.append({"file": path, "line": line, "kind": kind, "message": message})

    # commented-out code: runs of // lines where most lines look like code
    run: List[int] = []

    def flush() -> None:
        if not run:
            return
        texts = [LINE_COMMENT.match(lines[i]).group(1) for i in run]
        code = sum(1 for t in texts if CODE_LIKE.search(t) and not PROSE_HINT.search(t))
        if code >= 1 and code >= len(texts) / 2:
            add("commented-out-code", run[0] + 1, "%d line(s) of commented-out code: delete it (git keeps history)" % len(run))
        run.clear()

    for i, raw in enumerate(lines):
        m = LINE_COMMENT.match(raw)
        if (m and raw.strip().startswith("//") and not TOOL_DIRECTIVE.match(m.group(1))
                and not TODO.search(m.group(1)) and not BANNER.search(raw.strip())):
            run.append(i)
        else:
            flush()
    flush()

    for i, raw in enumerate(lines):
        stripped = raw.strip()
        comment_part = stripped if stripped.startswith("//") else (raw[raw.find("//"):] if "//" in raw and not re.search(r"['\"][^'\"]*//", raw) else "")
        if not comment_part:
            continue
        t = TODO.search(comment_part)
        if t and not TODO_REF.match(t.group(2)):
            add("todo-without-ref", i + 1, "%s without an issue/HU/gap reference: write %s(#123): … or %s(HU-12 G-2): …" % (t.group(1), t.group(1), t.group(1)))
        if stripped.startswith("//") and not stripped.startswith("///") and BANNER.search(stripped):
            add("banner", i + 1, "decorative banner: extract or rename instead of separating sections with comments")

    if "/domain/" in "/" + path:
        in_interface = False
        for i, raw in enumerate(lines):
            decl = PUBLIC_DECL.match(raw)
            if decl:
                in_interface = bool(INTERFACE_START.match(raw))
                if not has_doc(lines, i):
                    add("missing-doc", i + 1, "public domain declaration '%s' has no /// doc comment (what it guarantees, failures, units)" % decl.group(2))
                continue
            if raw.startswith("}"):
                in_interface = False
                continue
            if in_interface:
                sig = METHOD_SIG.match(raw)
                if sig and not has_doc(lines, i):
                    add("missing-doc", i + 1, "contract method '%s' has no /// doc comment" % sig.group(1))
    return findings


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--files", nargs="*")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    files = [f.replace(os.sep, "/") for f in args.files] if args.files else dart_files(root)
    files = [f for f in files if f.endswith(".dart") and not GENERATED.search("/" + f)]
    findings: List[Dict] = []
    for path in files:
        findings.extend(check_file(root, path))
    if args.format == "json":
        print(json.dumps({"files": len(files), "findings": findings}, indent=2))
    else:
        for f in findings:
            print("%s:%d  [%s] %s" % (f["file"], f["line"], f["kind"], f["message"]))
        print("Comment check: %d file(s), %d finding(s)" % (len(files), len(findings)))
    return 1 if findings and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
