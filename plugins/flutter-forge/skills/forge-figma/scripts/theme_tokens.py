#!/usr/bin/env python3
"""Theme token map for forge-figma: what each color accessor is worth, and how Figma tokens match it.

Usage: theme_tokens.py [--root PROJECT] [--accessor CLASS] [--files F ...]
                       [--match "Figma/Token Name=#rrggbb[aa]" ...] [--font FAMILY ...]
                       [--format text|json]

Why: matching a Figma token to a theme accessor by name alone hides value differences (a state
layer that is #8D4E2A at 16 % in Figma but `primary` at 16 % in the app) and costs the agent a
read of every color file. This script reads the color class once and answers mechanically.

What it reads (static, regex, no Dart parser, no network, read-only):
  - literal colors:  `static const white = Color(0xFFFFFFFF);`
                     `Color get primary => const Color(0xFFFF7E2B); // Schemes/Primary`
  - delegating getters of the accessor class (`static Color get primary => ThemeManager.colors.primary;`),
    resolved by member name to a literal in another class (one value per flavor class; several
    values are reported as `multiple`);
  - the trailing `// Figma/Token` comment, used as a name hint;
  - `fonts: - family:` in pubspec.yaml.
The accessor class comes from --accessor, else `design.colors` of .flutter-forge/profile.yaml when
it is a class name. A dynamic scheme (`Theme.of(context).colorScheme`, `ColorScheme.fromSeed`) has
no static values: the script says so and only name matches are possible.

--match statuses (Figma hex may carry alpha as RRGGBBAA):
  exact       a member with the camelCased name exists and has the same value
  value-differs  the name exists but the value is different  -> a decision, never silent
  hint        a member whose `// comment` equals the Figma name
  by-value    no name match; members with the same value (several = `tie`)
  overlay     Figma value has alpha: base color compared; says whether an accessor has that base
  gap         nothing matches

Exit 0 always for analysis results; 2 for usage errors. Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

LITERAL = re.compile(
    r"(?:Color\s+get\s+(\w+)\s*=>|(?:static\s+)?(?:const|final)\s+(?:Color\s+)?(\w+)\s*=)\s*"
    r"(?:const\s+)?Color\(\s*0x([0-9A-Fa-f]{8})\s*\)\s*;(?:\s*//\s*(.+?))?\s*$")
DELEGATE = re.compile(r"(?:static\s+)?Color\s+get\s+(\w+)\s*=>\s*[A-Za-z_][\w.]*\.(\w+)\s*;")
CLASS = re.compile(r"^\s*(?:abstract\s+|final\s+|base\s+)*class\s+(\w+)")
IDENT = re.compile(r"^[A-Za-z_]\w*$")
FONT_FAMILY = re.compile(r"^\s*-\s*family:\s*['\"]?([^'\"\n#]+?)['\"]?\s*$", re.M)


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def dart_files(root: str) -> List[str]:
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "lib")):
        dirs[:] = [d for d in dirs if d not in ("generated", ".dart_tool")]
        out.extend(os.path.join(base, f) for f in files if f.endswith(".dart") and not f.endswith(".g.dart"))
    return sorted(out)


def profile_colors(root: str) -> Optional[str]:
    text = read(os.path.join(root, ".flutter-forge", "profile.yaml"))
    m = re.search(r"^\s*colors:\s*([^\s#]+)", text, re.M)
    return m.group(1) if m else None


def camel(token: str) -> str:
    """`Schemes/On Surface Variant` -> `onSurfaceVariant` (last path segment)."""
    last = token.split("/")[-1]
    words = [w for w in re.split(r"[^A-Za-z0-9]+", last) if w]
    if not words:
        return ""
    return words[0][0].lower() + words[0][1:] + "".join(w[0].upper() + w[1:] for w in words[1:])


def parse_hex(value: str) -> Optional[Tuple[str, float]]:
    """`#8d4e2a29` -> ('8D4E2A', 0.16); `#ff7e2b` -> ('FF7E2B', 1.0). Figma lists alpha last."""
    m = re.fullmatch(r"#?([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?", value.strip())
    if not m:
        return None
    alpha = int(m.group(2), 16) / 255 if m.group(2) else 1.0
    return m.group(1).upper(), round(alpha, 2)


def scan(files: List[str]) -> Tuple[Dict[Tuple[str, str], dict], Dict[Tuple[str, str], str]]:
    """(class, member) -> {hex, hint, file, line}  and  (class, member) -> delegated member."""
    literals: Dict[Tuple[str, str], dict] = {}
    delegates: Dict[Tuple[str, str], str] = {}
    for path in files:
        current = ""
        for number, line in enumerate(read(path).splitlines(), 1):
            m = CLASS.match(line)
            if m:
                current = m.group(1)
            lit = LITERAL.search(line)
            if lit:
                name = lit.group(1) or lit.group(2)
                argb = lit.group(3).upper()
                hint = (lit.group(4) or "").strip()
                literals[(current, name)] = {"hex": argb[2:], "alpha": round(int(argb[:2], 16) / 255, 2),
                                             "hint": hint, "file": path, "line": number}
                continue
            dele = DELEGATE.search(line)
            if dele:
                delegates[(current, dele.group(1))] = dele.group(2)
    return literals, delegates


def accessor_tokens(accessor: str, literals: dict, delegates: dict) -> Dict[str, dict]:
    tokens: Dict[str, dict] = {}
    for (cls, name), info in literals.items():
        if cls == accessor:
            tokens[name] = {"values": [info["hex"]], "hint": info["hint"], "source": "%s:%d" % (info["file"], info["line"])}
    for (cls, name), target in delegates.items():
        if cls != accessor or name in tokens:
            continue
        found = [info for (c, n), info in literals.items() if c != accessor and n == target]
        values = sorted({i["hex"] for i in found})
        hint = next((i["hint"] for i in found if i["hint"]), "")
        tokens[name] = {"values": values, "hint": hint,
                        "source": "delegates to `%s` (%d flavor class(es))" % (target, len(found))}
    return tokens


def match(figma: str, hexa: Tuple[str, float], tokens: Dict[str, dict], accessor: str) -> dict:
    base, alpha = hexa
    name = camel(figma)
    result = {"figma": figma, "value": "#%s%s" % (base, "" if alpha == 1.0 else " @%d%%" % round(alpha * 100))}

    def acc(n: str) -> str:
        return "%s.%s" % (accessor, n)

    def has(n: str, val: str) -> bool:
        return val in tokens[n]["values"]

    if alpha < 1.0:
        same_base = sorted(n for n in tokens if has(n, base))
        result.update(status="overlay", candidates=[acc(n) for n in same_base],
                      note=("accessor(s) with the same base color; apply alpha %.2f" % alpha) if same_base else
                           "no accessor has base #%s: an overlay of another color would be a different tint; "
                           "report as a gap with the value and who decides" % base)
        return result
    if name in tokens:
        if has(name, base):
            result.update(status="exact", accessor=acc(name))
        else:
            result.update(status="value-differs", accessor=acc(name),
                          project_values=["#" + v for v in tokens[name]["values"]],
                          note="same name, different value: record it in the gaps table; do not match silently")
        return result
    hinted = sorted(n for n, t in tokens.items() if t["hint"].lower() == figma.lower())
    if hinted:
        n = hinted[0]
        result.update(status="hint" if has(n, base) else "value-differs", accessor=acc(n))
        return result
    by_value = sorted(n for n in tokens if has(n, base))
    if by_value:
        result.update(status="by-value" if len(by_value) == 1 else "tie", candidates=[acc(n) for n in by_value],
                      note="no accessor with that name; pick by context" if len(by_value) > 1 else
                           "equivalent by value only; confirm the meaning matches")
        return result
    result.update(status="gap", note="no accessor with that name or value")
    return result


def fonts(root: str) -> List[str]:
    return sorted({m.strip() for m in FONT_FAMILY.findall(read(os.path.join(root, "pubspec.yaml")))})


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Theme token map for forge-figma")
    ap.add_argument("--root", default=".")
    ap.add_argument("--accessor")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--match", action="append", default=[], metavar="TOKEN=#HEX")
    ap.add_argument("--font", action="append", default=[])
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    accessor = args.accessor or profile_colors(root)
    out: dict = {"accessor": accessor, "dynamic": False, "tokens": {}, "matches": [], "fonts": {}}
    if not accessor or not IDENT.match(accessor):
        out["dynamic"] = True
        out["note"] = ("colors come from `%s` (no color class): values are not static; match by name only "
                       "(camelCased) and confirm in the running app" % (accessor or "the ColorScheme"))
    else:
        files = [os.path.abspath(f) for f in args.files] if args.files else dart_files(root)
        literals, delegates = scan(files)
        out["tokens"] = accessor_tokens(accessor, literals, delegates)
        if not out["tokens"]:
            out["note"] = "class `%s` not found in %d file(s); pass --files or --accessor" % (accessor, len(files))
    for item in args.match:
        if "=" not in item:
            print("--match needs 'Figma/Token=#hex': %s" % item, file=sys.stderr)
            return 2
        figma, _, raw = item.rpartition("=")
        hexa = parse_hex(raw)
        if not hexa:
            print("not a hex color: %s" % raw, file=sys.stderr)
            return 2
        if out["dynamic"]:
            out["matches"].append({"figma": figma, "value": raw, "status": "dynamic",
                                   "accessor": "%s.%s" % (accessor or "colorScheme", camel(figma))})
        else:
            out["matches"].append(match(figma, hexa, out["tokens"], accessor))
    families = fonts(root)
    out["fonts"] = {"project": families, "missing": [f for f in args.font if f not in families]}

    if args.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    if out.get("note"):
        print("NOTE: %s" % out["note"])
    if out["tokens"]:
        print("%s: %d tokens" % (accessor, len(out["tokens"])))
    for m in out["matches"]:
        target = m.get("accessor") or ", ".join(m.get("candidates", [])) or "-"
        print("%-12s %-40s %-12s %s%s" % (m["status"], m["figma"], m["value"], target,
                                          ("  | " + m["note"]) if m.get("note") else ""))
        if m.get("project_values"):
            print("%-12s project value(s): %s" % ("", ", ".join(m["project_values"])))
    if args.font or families:
        print("fonts in pubspec: %s" % (", ".join(families) or "none"))
        for f in out["fonts"]["missing"]:
            print("font-missing %s (not declared in pubspec.yaml)" % f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
