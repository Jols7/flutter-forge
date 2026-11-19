#!/usr/bin/env python3
"""Mechanical checks for layouts that break on small phones, large text or other devices.

Usage: check_responsive.py [--root PROJECT] [--files F ...] [--changed-from REF] [--profile PROFILE.yaml]
                           [--mode new|adopt|improve|migrate] [--max-fixed-width N]
                           [--format text|json] [--no-fail]

Static, regex-based, no Dart parser: it finds the patterns that overflowed in a real app
(BIT-013 phase 0), not every possible layout bug. Rendering at several sizes and text scales
(forge-tests, `widget-tests.md` § Responsive matrix) is what proves a screen; this script points
at the lines to look at first. Single source of the rules: forge-presentation `responsive.md`.

  row-text-no-flex   a Row has an Expanded/Flexible child and also a Text (or a Column holding a
                     Text) that is NOT flexible: the bare child cannot shrink and overflows with long
                     text, large numbers or text scale 1.5+                         [finding; warn in adopt/improve]
  row-texts-no-flex  a Row of two or more bare Texts with no Expanded/Flexible/Wrap/FittedBox  [warn]
  fixed-width        SizedBox/Container `width:` literal >= max_fixed_width (default 240 dp):
                     likely a width copied from the design frame                    [warn]
  fixed-height-text  SizedBox/Container with a literal `height:` >= 16 that holds a Text: it clips
                     at large text scale (use a minimum height)                     [warn]
  list-not-builder   ListView(children: [... .map / for ...]): build lazily, and think of adaptive
                     columns on tablets                                             [warn]
  media-query-of     MediaQuery.of(context): use sizeOf/paddingOf/textScalerOf     [warn]
  form-no-scroll     a page with TextField/TextFormField and no scrollable ancestor in the file
                     (the keyboard covers the form)                                 [warn]

Threshold: `--max-fixed-width` or `quality.max_fixed_width` in the profile. Scope: files under
presentation/, pages/, widgets/, screens/ or state/ (generated code skipped), like
check_presentation.py. Read-only, no network, Python 3.9+ stdlib. Exit 1 only when a [finding]
exists (unless --no-fail).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, Iterator, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_presentation as base  # noqa: E402  (strip, dart_files, changed_files, scope regexes)

DEFAULT_FIXED_WIDTH = 240
FLEX = ("Expanded", "Flexible", "Spacer", "Wrap", "FittedBox")
ROW = re.compile(r"\bRow\(")
FIXED_WIDTH = re.compile(r"\b(?:SizedBox|Container)\(\s*(?:[^()]*?,\s*)?width:\s*(\d+(?:\.\d+)?)\b")
FIXED_HEIGHT_CALL = re.compile(r"\b(?:SizedBox|Container)\(")
HEIGHT = re.compile(r"\bheight:\s*(\d+(?:\.\d+)?)\b")
LISTVIEW = re.compile(r"\bListView\(")
MEDIA_OF = re.compile(r"\bMediaQuery\.of\(")
TEXT_FIELD = re.compile(r"\bText(?:Form)?Field\(")
SCROLL = re.compile(r"\b(?:SingleChildScrollView|ListView|CustomScrollView|Scrollable|NestedScrollView)\b")
HEAD = re.compile(r"^(?:const\s+)?([A-Za-z_]\w*)(?:\.\w+)?\s*\(")


def balanced(text: str, open_index: int, pair: str = "()") -> int:
    """Index just past the bracket that closes `text[open_index]` (strings are already blanked)."""
    opener, closer = pair
    depth = 0
    for i in range(open_index, len(text)):
        if text[i] == opener:
            depth += 1
        elif text[i] == closer:
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def split_top(text: str) -> Iterator[Tuple[int, str]]:
    """Top-level comma separated elements of a list body, with their offset in `text`."""
    depth, start = 0, 0
    for i, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            if text[start:i].strip():
                yield start, text[start:i]
            start = i + 1
    if text[start:].strip():
        yield start, text[start:]


def children_of(call_text: str) -> Optional[Tuple[int, str]]:
    """(offset, body) of the `children: [ ... ]` list of a widget call, when it has one."""
    m = re.search(r"\bchildren:\s*(?:<\w+>)?\[", call_text)
    if not m:
        return None
    open_index = m.end() - 1
    end = balanced(call_text, open_index, "[]")
    return open_index + 1, call_text[open_index + 1:end - 1]


def head(element: str) -> str:
    m = HEAD.match(element.strip())
    return m.group(1) if m else ""


def holds_text(element: str) -> bool:
    return bool(re.search(r"\bText(?:\.rich)?\(", element))


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_text(path: str, raw: str, cfg: Dict[str, object]) -> List[Dict]:
    clean = base.strip(raw)
    out: List[Dict] = []
    legacy = cfg.get("mode") in ("adopt", "improve")

    def add(kind: str, index: int, severity: str, message: str) -> None:
        out.append({"file": path, "line": line_of(clean, index), "kind": kind, "severity": severity, "message": message})

    for m in ROW.finditer(clean):
        call = clean[m.start():balanced(clean, m.end() - 1)]
        parsed = children_of(call)
        if not parsed:
            continue
        offset, body = parsed
        elements = [(o, e) for o, e in split_top(body) if head(e) or e.strip().startswith(("for", "if", "..."))]
        heads = [(o, e, head(e)) for o, e in elements]
        has_flex = any(h in FLEX for _, _, h in heads)
        bare = [(o, e) for o, e, h in heads if (h == "Text" or (h == "Column" and holds_text(e)))]
        if has_flex and bare:
            o, _ = bare[0]
            add("row-text-no-flex", m.start() + offset + o + (len(body[o:]) - len(body[o:].lstrip())), "warn" if legacy else "finding",
                "Text next to an Expanded/Flexible in a Row is not flexible: wrap it in Flexible (maxLines, or FittedBox(scaleDown) for money)")
        elif not has_flex and len(bare) >= 2:
            o, _ = bare[0]
            add("row-texts-no-flex", m.start() + offset + o, "warn",
                "Row of bare Texts: make the label Expanded and the value Flexible, or use Wrap")

    for m in FIXED_WIDTH.finditer(clean):
        if float(m.group(1)) >= cfg["max_fixed_width"]:
            add("fixed-width", m.start(), "warn",
                "fixed width %s dp (>= %s): constrain by the parent or use a fraction of the available width" % (m.group(1), cfg["max_fixed_width"]))
    for m in FIXED_HEIGHT_CALL.finditer(clean):
        call = clean[m.start():balanced(clean, m.end() - 1)]
        h = HEIGHT.search(call)
        if h and float(h.group(1)) >= 16 and holds_text(call) and "minHeight" not in call:
            add("fixed-height-text", m.start(), "warn", "fixed height %s dp around a Text clips at large text scale: use a minimum height" % h.group(1))
    for m in LISTVIEW.finditer(clean):
        call = clean[m.start():balanced(clean, m.end() - 1)]
        if re.search(r"\bchildren:", call) and re.search(r"\.map\(|\bfor\s*\(", call):
            add("list-not-builder", m.start(), "warn", "ListView(children: …) builds every item: use ListView.builder (and adaptive columns on tablets)")
    for m in MEDIA_OF.finditer(clean):
        add("media-query-of", m.start(), "warn", "MediaQuery.of(context) rebuilds on every change: use sizeOf / paddingOf / textScalerOf")
    if re.search(r"/(pages|screens)/", "/" + path):
        field = TEXT_FIELD.search(clean)
        if field and not SCROLL.search(clean):
            add("form-no-scroll", field.start(), "warn", "form without a scrollable in this file: the keyboard can cover it")
    return out


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".")
    p.add_argument("--files", nargs="*")
    p.add_argument("--changed-from")
    p.add_argument("--profile")
    p.add_argument("--mode", choices=["new", "adopt", "improve", "migrate"])
    p.add_argument("--max-fixed-width", type=int)
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--no-fail", action="store_true")
    a = p.parse_args(argv)
    root = os.path.abspath(a.root)
    prof = base.read_profile(a.profile)
    cfg: Dict[str, object] = {"mode": a.mode or prof.get("mode") or "new", "max_fixed_width": DEFAULT_FIXED_WIDTH}
    if a.profile and os.path.exists(a.profile):
        with open(a.profile, encoding="utf-8") as fh:
            m = re.search(r"^\s*max_fixed_width:\s*(\d+)", fh.read(), re.M)
        if m:
            cfg["max_fixed_width"] = int(m.group(1))
    if a.max_fixed_width is not None:
        cfg["max_fixed_width"] = a.max_fixed_width
    if a.changed_from:
        files = sorted(set(base.changed_files(root, a.changed_from)) | {f.replace(os.sep, "/") for f in (a.files or [])})
    else:
        files = [f.replace(os.sep, "/") for f in a.files] if a.files else base.dart_files(root)
    files = [f for f in files if f.endswith(".dart") and not base.GENERATED.search("/" + f)
             and base.IN_SCOPE.search("/" + f) and not f.startswith("test/")]
    findings: List[Dict] = []
    for f in files:
        try:
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                findings += check_text(f, fh.read(), cfg)
        except (OSError, UnicodeDecodeError):
            continue
    if a.format == "json":
        print(json.dumps({"files": len(files), "thresholds": cfg, "findings": findings}, indent=2))
    else:
        for f in findings:
            print("%s:%d  [%s/%s] %s" % (f["file"], f["line"], f["severity"], f["kind"], f["message"]))
        print("Responsive check: %d file(s), %d finding(s)" % (len(files), len(findings)))
    return 1 if any(f["severity"] == "finding" for f in findings) and not a.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
