#!/usr/bin/env python3
"""Structural lint of a forge-figma `design.md`, so the agent does not re-read its own output.

Usage: lint_design.py DESIGN_MD [--root PROJECT] [--refs-dir DIR] [--format text|json] [--no-fail]

Checks the contract of `references/design-template.md` mechanically. It does not judge whether
the design was read correctly, only whether the file is complete and consistent.

  missing-section     a required section is absent (Tokens, Components, Screens, Measures,
                      Responsive behavior, References)                              [error]
  gap-undefined       a `D-n` cited in Tokens/Components/Measures has no row in Gaps                [error]
  gap-duplicate       the same gap id has two rows                                  [error]
  gap-unused          a Gaps row is cited nowhere else                              [warn]
  decision-invalid    a Components decision is not reuse / extend / create          [error]
  path-missing        a reuse/extend row cites a `lib/...` path that does not exist
                      (needs --root)                                                [error]
  node-missing        a screen heading carries no node id                           [warn]
  measures-empty      the Measures or Responsive behavior section has no table row  [error]
  ref-missing         a capture listed in References does not exist next to the
                      design.md (or in --refs-dir)                                  [error]
  no-captures         References lists no capture at all                            [error]
  hex-outside-tokens  a #rrggbb literal outside Tokens/Gaps/References             [warn]

Section names accept the English headings of the template and their Spanish forms. Read-only,
stdlib only (Python 3.9+). Exit 1 when an error exists (unless --no-fail). The summary counts
(`gaps`, `reuse`, `extend`, `create`, `inferred`, `to_confirm`) feed `state.json`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional

SECTIONS = {
    "tokens": ["tokens"],
    "gaps": ["gaps", "design gaps", "gaps de diseño", "gaps de diseno"],
    "components": ["components", "componentes"],
    "screens": ["screens", "pantallas", "pantalla"],
    "measures": ["measures", "medidas"],
    "responsive": ["responsive behavior", "responsive", "comportamiento responsivo"],
    "references": ["references", "referencias", "captures", "capturas"],
}
REQUIRED = ["tokens", "components", "screens", "measures", "responsive", "references"]
DECISIONS = ("reuse", "extend", "create")
GAP_REF = re.compile(r"\b(D-\d+)\b")
GAP_ROW = re.compile(r"^\**(D-\d+)\**$")
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
NODE = re.compile(r"\b\d+[:-]\d+\b")
PATH = re.compile(r"`(lib/[^`\s]+\.dart)`")
IMAGE = re.compile(r"[\w./-]+\.(?:png|jpg|jpeg|webp)", re.I)


def norm(heading: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[`*_]", "", heading)).strip().lower()


def split_sections(text: str) -> Dict[str, str]:
    """`## Heading` blocks (and everything beneath, including `###`) keyed by canonical name."""
    parts = re.split(r"^##\s+(?!#)(.+)$", text, flags=re.M)
    sections: Dict[str, str] = {}
    for i in range(1, len(parts), 2):
        name = norm(parts[i])
        for canon, aliases in SECTIONS.items():
            if any(name == a or name.startswith(a + " ") or name.startswith(a + "(") for a in aliases):
                sections[canon] = sections.get(canon, "") + parts[i + 1]
                break
        else:
            sections["_other"] = sections.get("_other", "") + parts[i + 1]
    # Measures normally live as `#### Measures` under each screen
    inner = re.findall(r"^#{3,4}\s+(?:Measures|Medidas)\b.*?(?=^#{1,4}\s|\Z)", sections.get("screens", ""), flags=re.M | re.S)
    if inner:
        sections["measures"] = sections.get("measures", "") + "\n".join(inner)
    return sections


def table_rows(block: str) -> List[List[str]]:
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|?", s):
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else rows  # drop the header row


def lint(path: str, root: Optional[str], refs_dir: Optional[str]) -> dict:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    findings: List[dict] = []

    def add(rule: str, severity: str, message: str) -> None:
        findings.append({"rule": rule, "severity": severity, "message": message})

    if not re.search(r"^\s*Figma:", text, re.M):
        add("missing-section", "error", "no `Figma:` header line (file, frame, read date, calls)")
    sections = split_sections(text)
    for name in REQUIRED:
        if name not in sections:
            add("missing-section", "error", "section `%s` is missing" % name)

    gap_rows = [r[0].strip("*") for r in table_rows(sections.get("gaps", "")) if r and GAP_ROW.match(r[0].strip())]
    seen = set()
    for gid in gap_rows:
        if gid in seen:
            add("gap-duplicate", "error", "gap %s has more than one row" % gid)
        seen.add(gid)
    cited = set(m.upper() for m in GAP_REF.findall("\n".join(sections.get(k, "") for k in ("tokens", "components", "measures"))))
    for gid in sorted(cited - seen):
        add("gap-undefined", "error", "gap %s is cited but has no row in Gaps" % gid)
    for gid in sorted(seen - cited):
        add("gap-unused", "warn", "gap %s is defined but cited nowhere" % gid)

    counts = {"reuse": 0, "extend": 0, "create": 0}
    for row in table_rows(sections.get("components", "")):
        if len(row) < 3:
            continue
        decision = re.sub(r"[*_`]", "", row[1]).strip().lower()
        kind = next((d for d in DECISIONS if decision.startswith(d)), None)
        if not kind:
            add("decision-invalid", "error", "component `%s`: decision `%s` is not reuse/extend/create" % (row[0], row[1]))
            continue
        counts[kind] += 1
        if root and kind in ("reuse", "extend"):
            for rel in PATH.findall(" ".join(row[2:])):
                if not os.path.exists(os.path.join(root, rel)):
                    add("path-missing", "error", "component `%s`: %s does not exist" % (row[0], rel))

    screens = sections.get("screens", "")
    for heading in re.findall(r"^###\s+(?!#)(.+)$", screens, flags=re.M):
        if re.match(r"\s*(states?|estados?|measures|medidas|responsive)", heading, re.I):
            continue
        if not NODE.search(heading) and "node" not in heading.lower():
            add("node-missing", "warn", "screen heading `%s` has no node id" % heading.strip())
    for key in ("measures", "responsive"):
        block = sections.get(key, "")
        if key in sections and not table_rows(block):
            add("measures-empty", "error", "section `%s` has no table row" % key)

    refs = sections.get("references", "")
    images = sorted(set(IMAGE.findall(refs)))
    if "references" in sections and not images:
        add("no-captures", "error", "References lists no capture (png/jpg/webp)")
    base = refs_dir or os.path.dirname(os.path.abspath(path))
    for image in images:
        if not os.path.exists(os.path.join(base, image)) and not os.path.exists(os.path.join(refs_dir or base, os.path.basename(image))):
            add("ref-missing", "error", "capture %s not found under %s" % (image, base))

    outside = "\n".join(v for k, v in sections.items() if k not in ("tokens", "gaps", "references"))
    stray = sorted(set(HEX.findall(outside)))
    if stray:
        add("hex-outside-tokens", "warn", "hex literals outside Tokens/Gaps: %s" % ", ".join(stray[:6]))

    summary = {"gaps": len(seen), **counts, "inferred": len(re.findall(r"\[inferid[oa]\]", text, re.I)),
               "to_confirm": len(re.findall(r"\[por confirmar\]|\[to confirm\]", text, re.I)),
               "captures": len(images)}
    return {"file": path, "summary": summary, "findings": findings}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Lint a forge-figma design.md")
    ap.add_argument("design")
    ap.add_argument("--root")
    ap.add_argument("--refs-dir")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--no-fail", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.design):
        print("not a file: %s" % args.design, file=sys.stderr)
        return 2
    report = lint(args.design, os.path.abspath(args.root) if args.root else None, args.refs_dir)
    errors = [f for f in report["findings"] if f["severity"] == "error"]
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for f in report["findings"]:
            print("%-5s %-18s %s" % (f["severity"].upper(), f["rule"], f["message"]))
        s = report["summary"]
        print("summary: gaps %d · reuse %d · extend %d · create %d · captures %d · inferred %d · to-confirm %d · %d error(s)"
              % (s["gaps"], s["reuse"], s["extend"], s["create"], s["captures"], s["inferred"], s["to_confirm"], len(errors)))
    return 1 if errors and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main())
