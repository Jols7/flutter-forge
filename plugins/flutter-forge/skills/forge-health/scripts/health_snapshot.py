#!/usr/bin/env python3
"""One-shot, token-cheap health snapshot of a Flutter repo for flutter-forge's forge-health.

Usage: health_snapshot.py [--root PROJECT] [--out-dir DIR] [--since-days 90] [--top 10]
                          [--outdated] [--flutter-command CMD] [--rules layers.json]
                          [--depth quick|standard] [--review-files N]
                          [--section NAME] [--no-write]

Runs the existing forge scanners (detect_project, check_layers, scan_secrets,
check_platform_config) plus git_churn, lcov_summary and code_metrics, then:
- writes the full result to DIR/metrics.json (default <root>/.flutter-forge/health/);
- prints a digest of at most ~250 lines, meant to be injected into a skill prompt.
Depth: `standard` (default) also infers a draft layer map when neither a preset nor the repo's own
layers.json fits (layers.draft.json), drafts a profile for repos without one (profile.draft.yaml)
and ranks a review queue of up to 30 files. `quick` skips all three and uses the assumed preset.
`--section churn|coverage|code|dependencies|layers|security|platform|stack|declared|hotspots|inferred_layers|profile_draft|review_queue`
prints just that part of the full result as JSON, for drilling down without reading files.

Never edits the project (it writes only inside --out-dir), never prints secret values, and
always exits 0: a failing collector shows up as "collector failed: <reason>" in the digest.
Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import code_metrics  # noqa: E402
import draft_profile  # noqa: E402
import git_churn  # noqa: E402
import infer_layers  # noqa: E402
import lcov_summary  # noqa: E402

CHECK_LAYERS = os.path.join(SKILLS, "forge-audit", "scripts", "check_layers.py")
DETECT = os.path.join(SKILLS, "forge-profile", "scripts", "detect_project.py")
SCAN_SECRETS = os.path.join(SKILLS, "forge-security", "scripts", "scan_secrets.py")
PLATFORM = os.path.join(SKILLS, "forge-security", "scripts", "check_platform_config.py")
PRESETS = os.path.join(SKILLS, "forge-architecture", "presets")
MAX_DIGEST_LINES = 250
REVIEW_FILES = {"quick": 15, "standard": 30}
DOC_KEYWORDS = ["clean", "layered", "mvvm", "mvc", "bloc", "cubit", "riverpod", "provider", "getx", "mobx",
                "get_it", "injectable", "go_router", "auto_route", "dio", "freezed", "json_serializable"]


def run_json(script: str, *args: str, cwd: Optional[str] = None) -> Dict:
    proc = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, cwd=cwd,
                          check=False, timeout=300)
    if not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip()[:200] or "no output")
    return json.loads(proc.stdout)


def guard(fn: Callable[[], Any]) -> Any:
    try:
        return fn()
    except Exception as exc:  # a collector must never break the whole snapshot
        return {"error": "collector failed: %s: %s" % (type(exc).__name__, str(exc)[:160])}


def read_text(path: str, limit: int = 400) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return "".join(fh.readlines()[:limit])
    except (OSError, UnicodeDecodeError):
        return ""


def load_check_layers():
    spec = importlib.util.spec_from_file_location("check_layers", CHECK_LAYERS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_rules(root: str, stack: Dict, explicit: Optional[str], inferred: Optional[str] = None) -> Dict:
    if explicit:
        return {"path": explicit, "source": "--rules"}
    own = os.path.join(root, ".flutter-forge", "layers.json")
    if os.path.exists(own):
        return {"path": own, "source": ".flutter-forge/layers.json"}
    if inferred:
        return {"path": inferred, "source": "inferred draft (folder names and suffixes; review it)"}
    preset = ((stack.get("structure") or {}).get("architecture") or {}).get("preset")
    preset = preset if preset in ("clean", "layered") else "clean"
    return {"path": os.path.join(PRESETS, "%s.layers.json" % preset), "source": "assumed preset: %s" % preset}


def declared_architecture(root: str) -> Dict:
    profile = {}
    text = read_text(os.path.join(root, ".flutter-forge", "profile.yaml"), 200)
    in_arch = False
    for line in text.splitlines():
        if re.match(r"^architecture:\s*$", line):
            in_arch = True
        elif re.match(r"^\S", line):
            in_arch = False
        elif in_arch:
            m = re.match(r"^\s+(preset|mode|state|di|router):\s*([\w\-]+)", line)
            if m:
                profile[m.group(1)] = m.group(2)
    mentions: List[str] = []
    for doc in ("CLAUDE.md", "README.md", "docs/architecture.md"):
        body = read_text(os.path.join(root, doc)).lower()
        mentions += ["%s:%s" % (doc, k) for k in DOC_KEYWORDS if re.search(r"\b%s\b" % re.escape(k), body)]
    return {"profile": profile or None, "doc_mentions": mentions[:24]}


def drift(declared: Dict, stack: Dict) -> List[str]:
    notes = []
    real_state = (stack.get("dependencies") or {}).get("state_primary_in_code")
    real_preset = ((stack.get("structure") or {}).get("architecture") or {}).get("preset")
    prof = declared.get("profile") or {}
    if prof.get("state") and real_state and prof["state"] != real_state:
        notes.append("profile says state=%s, code uses %s" % (prof["state"], real_state))
    if prof.get("preset") and real_preset and prof["preset"] not in (real_preset, "custom"):
        notes.append("profile says preset=%s, structure looks like %s" % (prof["preset"], real_preset))
    if not prof and declared.get("doc_mentions"):
        notes.append("no profile: declared architecture comes only from docs (%d keyword mentions)" % len(declared["doc_mentions"]))
    if not prof and not declared.get("doc_mentions"):
        notes.append("architecture is undeclared (no profile, no keywords in CLAUDE.md/README)")
    if len((stack.get("dependencies") or {}).get("state") or []) > 1:
        notes.append("several state packages declared: %s" % ", ".join(stack["dependencies"]["state"]))
    return notes


def layers_report(root: str, rules: Dict, churn_by_file: Dict[str, int]) -> Dict:
    raw = run_json(CHECK_LAYERS, "--rules", rules["path"], "--root", root, "--format", "json", "--no-fail")
    module = load_check_layers()
    with open(rules["path"], encoding="utf-8") as fh:
        classifier = module.Rules(json.load(fh))
    per_layer: Dict[str, Dict[str, int]] = {n: {"files": c, "violations": 0, "commits": 0} for n, c in raw["layers"].items()}
    for v in raw["violations"]:
        per_layer.setdefault(v["from_layer"], {"files": 0, "violations": 0, "commits": 0})["violations"] += 1
    for path, commits in churn_by_file.items():
        name = classifier.classify(path)
        if name in per_layer:
            per_layer[name]["commits"] += commits
    files = raw["files"]
    unclassified = len(raw["unclassified"])
    by_pair = Counter("%s -> %s" % (v["from_layer"], v["to_layer"] or v["import"].split("/")[0]) for v in raw["violations"])
    return {
        "rules": rules["source"], "files": files, "unclassified": unclassified,
        "mapping_suspect": files > 0 and unclassified / files > 0.5,
        "violations": len(raw["violations"]), "by_kind": dict(Counter(v["kind"] for v in raw["violations"])),
        "by_pair": dict(by_pair.most_common(8)),
        "top_files": Counter(v["file"] for v in raw["violations"]).most_common(8),
        "violations_by_file": dict(Counter(v["file"] for v in raw["violations"]).most_common(300)),
        "per_layer": per_layer, "matrix": raw["matrix"],
        "blind_spots": dict(Counter(u["target"] for u in raw["unclassified_targets"]).most_common(5)),
        "sample": raw["violations"][:40],
    }


def security_report(root: str) -> Dict:
    secrets = run_json(SCAN_SECRETS, "--root", root, "--format", "json", "--no-fail")
    items = [{"severity": f.get("severity"), "kind": f.get("kind"), "file": f.get("file"), "line": f.get("line")}
             for f in secrets.get("findings", [])]   # values are never copied
    return {"count": len(items), "by_severity": dict(Counter(i["severity"] for i in items)), "findings": items[:60]}


def platform_report(root: str) -> Dict:
    data = run_json(PLATFORM, "--root", root, "--format", "json", "--no-fail")
    items = [{k: f.get(k) for k in ("severity", "area", "file", "message", "masvs")} for f in data.get("findings", [])]
    return {"count": len(items), "by_severity": dict(Counter(i["severity"] for i in items)), "findings": items[:60]}


def build(root: str, args: argparse.Namespace) -> Dict:
    result: Dict[str, Any] = {"root": root}
    result["stack"] = guard(lambda: run_json(DETECT, root))
    stack = result["stack"] if "error" not in result["stack"] else {}
    result["declared"] = declared_architecture(root)
    result["drift"] = drift(result["declared"], stack)
    churn = guard(lambda: git_churn.churn(root, args.since_days, args.top))
    result["churn"] = churn
    by_file = churn.get("by_file", {}) if churn.get("available") else {}
    result["coverage"] = guard(lambda: lcov_summary.coverage(root, None, by_file or None, args.top))
    metrics = guard(lambda: code_metrics.metrics(root, args.top, args.outdated, args.flutter_command))
    result["dependencies"] = metrics.get("dependencies", metrics)
    result["code"] = metrics.get("code", metrics)
    inferred_path = None
    result["profile_present"] = os.path.exists(os.path.join(root, ".flutter-forge", "profile.yaml"))
    if args.depth == "standard":
        inferred_path = standard_layers(root, args, result)
    rules = resolve_rules(root, stack, args.rules, inferred_path)
    result["layers"] = guard(lambda: layers_report(root, rules, by_file))
    if args.depth == "standard" and not result["profile_present"]:
        result["profile_draft"] = guard(lambda: standard_profile(root, args, stack, result.get("inferred_layers", {}), inferred_path))
    result["security"] = guard(lambda: security_report(root))
    result["platform"] = guard(lambda: platform_report(root))
    result["hotspots"] = guard(lambda: hotspots(result, by_file))
    result["review_queue"] = guard(lambda: review_queue(result, by_file, args.review_files or REVIEW_FILES[args.depth]))
    return result


def display_path(root: str, path: str) -> str:
    rel = os.path.relpath(path, root)
    return path if rel.startswith("..") else rel.replace(os.sep, "/")


def standard_layers(root: str, args: argparse.Namespace, result: Dict) -> Optional[str]:
    """Infer a draft layer map when the repo has no layers.json of its own and no --rules."""
    if args.rules or os.path.exists(os.path.join(root, ".flutter-forge", "layers.json")):
        result["inferred_layers"] = {"status": "skipped", "reason": "explicit rules exist"}
        return None
    inferred = guard(lambda: infer_layers.infer(root))
    rules_data = inferred.pop("rules", None) if isinstance(inferred, dict) else None
    result["inferred_layers"] = inferred
    if not rules_data:
        return None
    if args.no_write:
        handle = tempfile.NamedTemporaryFile("w", suffix=".layers.json", delete=False, encoding="utf-8")
        json.dump(rules_data, handle)
        handle.close()
        inferred["path"] = "(not written: --no-write)"
        return handle.name
    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, "layers.draft.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rules_data, fh, indent=2)
    inferred["path"] = display_path(root, path)
    return path


def standard_profile(root: str, args: argparse.Namespace, stack: Dict, inferred: Dict, layers_path: Optional[str]) -> Dict:
    """Draft a profile for a repo without one. Never writes .flutter-forge/profile.yaml."""
    if not stack:
        return {"status": "skipped", "reason": "stack detection failed"}
    shown = inferred.get("path") if inferred.get("path", "").startswith(".") or inferred.get("path") else None
    layers_for_profile = dict(inferred, rules=None)
    text = draft_profile.render(root, stack, layers_for_profile, shown if inferred.get("status") == "inferred" else None)
    info = {"status": "drafted", "lines": len(text.splitlines()), "mode": "unset: human decision"}
    if not args.no_write:
        os.makedirs(args.out_dir, exist_ok=True)
        path = os.path.join(args.out_dir, "profile.draft.yaml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        info["path"] = display_path(root, path)
    else:
        info["path"] = "(not written: --no-write)"
    return info


def review_queue(result: Dict, by_file: Dict[str, int], limit: int) -> Dict:
    """Which files the model should open, best first. Scripts rank; the model confirms."""
    layers = result.get("layers", {})
    viol = layers.get("violations_by_file", {}) if "error" not in layers else {}
    cov = result.get("coverage", {})
    untested = {h["file"] for h in (cov.get("hotspots_untested") or [])} if cov.get("available") else set()
    long_build = {b["file"] for b in (result["code"].get("longest_builds") or []) if b.get("lines", 0) > 80}
    big = {w["file"] for w in (result["code"].get("largest_widgets") or []) if w.get("lines", 0) > 300}
    flagged: Dict[str, List[str]] = {}
    for key in ("security", "platform"):
        sec = result.get(key, {})
        for f in sec.get("findings", []) if "error" not in sec else []:
            if f.get("severity") in ("critical", "high") and f.get("file"):
                flagged.setdefault(f["file"], []).append("%s %s" % (key, f["severity"]))
    files = set(by_file) | set(viol) | untested | long_build | big | set(flagged)
    rows = []
    for f in files:
        if f.endswith((".g.dart", ".freezed.dart", ".gr.dart")) or "/generated/" in f:
            continue
        if not (f.startswith("lib/") or f in flagged):
            continue   # tests and tooling are not review targets unless a scanner flagged them
        reasons: List[str] = list(flagged.get(f, []))
        commits, v = by_file.get(f, 0), viol.get(f, 0)
        score = (100.0 if reasons else 0.0) + commits * (1 + 0.5 * min(v, 10)) + 0.5 * v
        if commits:
            reasons.append("%d commits" % commits)
        if v:
            reasons.append("%d layer violations" % v)
        if f in untested:
            score *= 1.5
            reasons.append("hot and under-tested")
        if f in long_build:
            score *= 1.3
            reasons.append("long build()")
        if f in big:
            score *= 1.2
            reasons.append("large widget")
        if score > 0:
            rows.append({"file": f, "score": round(score, 1), "why": ", ".join(reasons)})
    rows.sort(key=lambda r: -r["score"])
    return {"limit": limit, "candidates": len(rows), "files": rows[:limit],
            "basis": "security(+100) + commits x (1 + 0.5 x violations) x test/size multipliers"}


def hotspots(result: Dict, by_file: Dict[str, int]) -> Dict:
    """Hot files, ranked. With coverage: commits x (1 - coverage). Without: commits x size."""
    cov = result["coverage"]
    if cov.get("available"):
        return {"basis": "commits x (1 - coverage)", "files": cov["hotspots_untested"]}
    sizes = {f["file"]: f["lines"] for f in (result["code"].get("largest_files") or [])}
    rows = sorted(({"file": f, "commits": n, "lines": sizes.get(f)} for f, n in by_file.items() if f.startswith("lib/")),
                  key=lambda r: (-r["commits"], -(r["lines"] or 0)))
    return {"basis": "commits only (no lcov.info; run `flutter test --coverage`)", "files": rows[:10]}


def digest(r: Dict, top: int) -> str:
    out: List[str] = []
    add = out.append
    add("# forge-health snapshot")
    add("Root: %s" % r["root"])
    st = r["stack"]
    if "error" in st:
        add("Stack: %s" % st["error"])
    elif st.get("error") is None and "package" in st:
        d = st.get("dependencies", {})
        arch = (st.get("structure") or {}).get("architecture") or {}
        add("Stack: package=%s state=%s (declared: %s) di=%s router=%s http=%s l10n=%s" % (
            st.get("package"), d.get("state_primary_in_code"), ",".join(d.get("state") or []) or "-",
            ",".join(d.get("di") or []) or "-", ",".join(d.get("router") or []) or "-",
            ",".join(d.get("http") or []) or "-", (st.get("l10n") or {}).get("pipeline")))
        add("Architecture guess: %s (confidence %s) · features: %s · flavors: %s" % (
            arch.get("preset"), arch.get("confidence"), ", ".join((st.get("structure") or {}).get("features") or []) or "-",
            ", ".join((st.get("flavors") or {}).get("names") or []) or "none"))
        if st.get("needs_decision"):
            add("Needs decision (profile cannot express): %s" % st["needs_decision"])
        add("Convention signals: %s" % json.dumps(st.get("conventions_signals", {})))
    il = r.get("inferred_layers")
    if il:
        if il.get("status") == "inferred":
            add("Layer map: INFERRED draft %s (presets classify %s; draft classifies %s of %d files; unmapped: %s)" % (
                il.get("path"), il.get("preset_coverage"), il.get("coverage"), il.get("files"),
                ", ".join("%s (%d)" % (u["dir"], u["files"]) for u in il.get("unmapped", [])[:4]) or "none"))
        elif il.get("status") == "preset_fits":
            add("Layer map: preset `%s` fits (%s of files classified)" % (il.get("base_preset"), il.get("coverage")))
        else:
            add("Layer map: %s (%s)" % (il.get("status"), il.get("reason") or "inference did not improve on the preset"))
    pd = r.get("profile_draft")
    if pd:
        add("Profile: none in repo; draft %s (%s lines, mode: %s)" % (pd.get("path", pd.get("status")), pd.get("lines"), pd.get("mode")))
    dec = r["declared"]
    add("Declared: profile=%s · docs=%s" % (dec["profile"] or "none", ", ".join(dec["doc_mentions"][:8]) or "none"))
    for note in r["drift"]:
        add("DRIFT: %s" % note)

    add("\n## Layers (real imports vs rules)")
    ly = r["layers"]
    if "error" in ly:
        add(ly["error"])
    else:
        add("Rules: %s · files=%d unclassified=%d violations=%d %s" % (
            ly["rules"], ly["files"], ly["unclassified"], ly["violations"], dict(ly["by_kind"])))
        if ly["mapping_suspect"]:
            add("WARNING: more than half the files match no layer; the rules probably do not fit this repo. Map layers before trusting the numbers.")
        add("Layer           files  viol  commits(%dd)" % r["churn"].get("since_days", 90))
        for name, v in sorted(ly["per_layer"].items(), key=lambda kv: (-kv[1]["violations"], -kv[1]["commits"])):
            add("  %-15s %4d  %4d  %6d" % (name, v["files"], v["violations"], v["commits"]))
        add("Top violation pairs: %s" % (dict(list(ly["by_pair"].items())[:5]) or "none"))
        add("Top violating files: %s" % (", ".join("%s×%d" % kv for kv in ly["top_files"][:5]) or "none"))
        if ly["blind_spots"]:
            add("Blind spots (imports into unclassified files): %s" % ly["blind_spots"])
        edges = sorted(ly["matrix"].items(), key=lambda kv: -kv[1])[:12]
        add("Real import edges: %s" % "; ".join("%s=%d" % kv for kv in edges))

    rq = r.get("review_queue")
    if rq and "error" not in rq:
        add("\n## Review queue (open these, in order; %d of %d candidates)" % (len(rq["files"]), rq["candidates"]))
        for row in rq["files"]:
            add("  %6.1f  %s  [%s]" % (row["score"], row["file"], row["why"]))

    add("\n## Hotspots (change frequency)")
    ch = r["churn"]
    if not ch.get("available"):
        add("Churn: %s" % ch.get("reason", ch.get("error")))
    else:
        add("Last %dd: %d commits, %d files, %d authors · single-owner files in top: %d" % (
            ch["since_days"], ch["commits"], ch["files_touched"], ch["authors"], ch["single_owner_in_top"]))
        for row in ch["top"][:top]:
            add("  %3d commits %5d lines  %s%s" % (row["commits"], row["lines_changed"], row["file"], "  [single owner]" if row["single_owner"] else ""))

    add("\n## Tests and coverage")
    cov = r["coverage"]
    if not cov.get("available"):
        add("Coverage: %s. %s" % (cov.get("reason", cov.get("error")), cov.get("hint", "")))
    else:
        pct = "%.1f%%" % (cov["line_coverage"] * 100) if cov["line_coverage"] is not None else "n/a"
        add("Line coverage %s · lib files absent from lcov (counted 0%%): %d/%d · hot files below 50%%: %d" % (
            pct, cov["files_not_in_lcov"], cov["files_in_lib"], cov["hotspot_count"]))
        for h in cov["hotspots_untested"][:top]:
            add("  %3d commits  %3d%% covered  %s" % (h["commits"], h["coverage"] * 100, h["file"]))
    tests = (r["stack"].get("structure") or {}) if "error" not in r["stack"] else {}
    add("Test files: %s · e2e dirs: %s" % (tests.get("test_files"), tests.get("e2e_dirs")))

    add("\n## Code size (performance proxy)")
    cd = r["code"]
    if "error" in cd:
        add(cd["error"])
    else:
        add("%d Dart files, %d lines, %d widget classes · files>300 lines: %d · build()>80 lines: %d" % (
            cd["dart_files"], cd["dart_lines"], cd["widget_classes"], cd["files_over_300"], cd["builds_over_80"]))
        for w in cd["largest_widgets"][:5]:
            add("  widget %4d lines  %s  %s:%d" % (w["lines"], w["class"], w["file"], w["line"]))
        for b in cd["longest_builds"][:5]:
            if b["lines"] > 40:
                add("  build  %4d lines  %s:%d" % (b["lines"], b["file"], b["line"]))

    add("\n## Dependencies")
    dp = r["dependencies"]
    if "error" in dp or not dp.get("available"):
        add(dp.get("error") or dp.get("reason"))
    else:
        add("direct=%d dev=%d overrides=%d · constraints=%s · lock=%s" % (
            dp["direct"], dp["dev"], dp["overrides"], dp["constraint_kinds"], dp["lock"] if dp["lock_present"] else "missing pubspec.lock"))
        if dp["needs_attention"]:
            add("Needs attention (git/path/any/override): %s" % ", ".join(dp["needs_attention"][:12]))
        od = dp.get("outdated", {})
        if od.get("run"):
            add("Outdated: discontinued=%s · major behind=%s · minor/patch behind=%d" % (
                od["discontinued"] or "none", od["major_behind"][:10] or "none", od["minor_or_patch_behind"]))
        else:
            add("Outdated: not run (%s)" % od.get("reason"))

    add("\n## Security scanners (values never shown)")
    for label, key in (("secrets/logging", "security"), ("platform config", "platform")):
        sec = r[key]
        if "error" in sec:
            add("%s: %s" % (label, sec["error"]))
            continue
        add("%s: %d findings %s" % (label, sec["count"], sec["by_severity"]))
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for f in sorted(sec["findings"], key=lambda f: order.get(f.get("severity"), 9))[:6]:
            where = "%s:%s" % (f.get("file"), f.get("line")) if f.get("line") else f.get("file")
            add("  [%s] %s %s" % (f.get("severity"), f.get("kind") or f.get("message"), where))
    add("\nFull data: metrics.json · drill down with --section <churn|coverage|code|dependencies|layers|security|platform|stack|declared|hotspots|inferred_layers|profile_draft|review_queue>")
    if len(out) > MAX_DIGEST_LINES:
        out = out[:MAX_DIGEST_LINES - 1] + ["… digest truncated at %d lines; use --section for the rest" % MAX_DIGEST_LINES]
    return "\n".join(out)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir")
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--outdated", action="store_true")
    parser.add_argument("--flutter-command", default="flutter")
    parser.add_argument("--rules")
    parser.add_argument("--depth", choices=["quick", "standard"], default="standard")
    parser.add_argument("--review-files", type=int, default=0)
    parser.add_argument("--section")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.exists(os.path.join(root, "pubspec.yaml")):
        print("forge-health: no pubspec.yaml in %s. Pass --root <Flutter project folder> (for a monorepo, the app package)." % root)
        return 0
    args.out_dir = args.out_dir or os.path.join(root, ".flutter-forge", "health")
    result = build(root, args)
    if args.section:
        print(json.dumps(result.get(args.section, {"error": "unknown section"}), indent=2))
        return 0
    if not args.no_write:
        out_dir = args.out_dir
        try:
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=2)
        except OSError as exc:
            print("forge-health: could not write metrics.json (%s)" % exc)
    print(digest(result, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
