#!/usr/bin/env python3
"""Draft a `.flutter-forge/profile.yaml` for a repo nobody set up, for forge-health.

Usage: draft_profile.py [--root PROJECT] [--write FILE] [--layers-file PATH] [--stack-json FILE]

Combines what `forge-profile`'s detect_project.py can observe (stack, structure, conventions)
with the layer inference of infer_layers.py, and prints a profile in the schema of
forge-profile/references/profile-schema.md. Every value is *detected*, none is decided.

It is a draft, not a profile:
- `architecture.mode` stays empty: adopt, improve or migrate is a human decision.
- keys the code cannot answer (security level, sensitive data, domain, language) are listed
  under "Not detected" instead of guessed.
- --write is meant for the health output folder; never point it at `.flutter-forge/profile.yaml`
  of a repo you only audit. The script refuses that path.

Read-only otherwise, no network, exit 0 (a failure prints a one-line comment). Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
DETECT = os.path.join(SKILLS, "forge-profile", "scripts", "detect_project.py")
sys.path.insert(0, HERE)
import infer_layers  # noqa: E402

ARCH_FALLBACK = "custom"
NOT_DETECTED = [
    "architecture.mode (adopt | improve | migrate): human decision",
    "security.level and security.sensitive_data: depends on the business",
    "project.domain and project.canonical_feature",
    "requirements.language and l10n.locales beyond the ARB files found",
    "testing.coverage_min: a team target, not an observation",
]


def detect(root: str) -> Dict:
    proc = subprocess.run([sys.executable, DETECT, root], capture_output=True, text=True, check=False, timeout=120)
    if not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip()[:200] or "detect_project produced no output")
    return json.loads(proc.stdout)


def first(values: Optional[List[str]], default: str) -> str:
    return values[0] if values else default


def exists(root: str, rel: Optional[str]) -> bool:
    return bool(rel) and os.path.exists(os.path.join(root, rel))


def find_first(root: str, candidates: List[str]) -> Optional[str]:
    for rel in candidates:
        if exists(root, rel):
            return rel
    return None


def errors_style(signals: Dict) -> str:
    if signals.get("result_type"):
        return "result"
    if signals.get("throws_string"):
        return "legacy"
    return "exceptions"


def render(root: str, stack: Dict, layers: Dict, layers_file: Optional[str]) -> str:
    deps = stack.get("dependencies", {})
    structure = stack.get("structure", {})
    signals = stack.get("conventions_signals", {})
    arch = structure.get("architecture", {})
    layer_status = layers.get("status")
    if layer_status == "preset_fits":
        preset = layers.get("base_preset") or arch.get("preset") or ARCH_FALLBACK
    else:
        preset = ARCH_FALLBACK if layer_status == "inferred" else (arch.get("preset") if arch.get("preset") in ("clean", "layered") else ARCH_FALLBACK)
    state = deps.get("state_primary_in_code") or first(deps.get("state"), "provider")
    di = first(deps.get("di"), "manual")
    if signals.get("get_navigation") and not deps.get("router"):
        router = "navigator"
    else:
        router = first(deps.get("router"), "navigator")
    http = first(deps.get("http"), "dio")
    features_root = None
    if layers.get("rules"):
        features_root = layers["rules"].get("features_root") or None
    features_root = features_root or structure.get("feature_root")
    sdk = stack.get("sdk", {})
    fcmd = sdk.get("command", "flutter")
    flavors = stack.get("flavors", {})
    l10n = stack.get("l10n", {})
    arb = os.path.dirname(l10n["arb_files"][0]) if l10n.get("arb_files") else None
    widgets_dir = find_first(root, ["lib/core/widgets", "lib/widgets", "lib/shared/widgets"])
    core_dir = find_first(root, ["lib/core"])
    mapper = (stack.get("naming") or {}).get("mapper_method")
    codegen = first(deps.get("codegen"), "manual")
    package = stack.get("package") or "unknown"
    e2e = (structure.get("e2e_dirs") or [None])[0]
    testing = deps.get("testing") or []

    out: List[str] = []
    add = out.append
    add("# DRAFT profile written by forge-health. Detected, not decided. NOT valid until `architecture.mode` is chosen.")
    add("# Do not copy this over .flutter-forge/profile.yaml without a person reviewing every line.")
    add("# Layer rules: %s" % (layers_file or ("preset `%s` fits" % preset if layer_status == "preset_fits" else "none inferred")))
    add("# Evidence: architecture guess %s (confidence %s); layer inference %s, coverage %s of files." % (
        arch.get("preset"), arch.get("confidence"), layer_status, layers.get("coverage")))
    add("schema: 1")
    add("")
    add("project:")
    add("  name: %s" % package)
    add("  package: %s" % package)
    add("")
    add("sdk:")
    add("  flutter_command: %s" % fcmd)
    add("  dart_command: %s" % ("fvm dart" if sdk.get("fvm") else "dart"))
    add("")
    add("architecture:")
    add("  preset: %s" % preset)
    add("  mode: null            # HUMAN DECISION: adopt | improve | migrate")
    add("  state: %s%s" % (state, "   # %d state packages declared: %s" % (len(deps["state"]), ", ".join(deps["state"])) if len(deps.get("state") or []) > 1 else ""))
    add("  di: %s" % di)
    add("  router: %s" % router)
    add("  errors: %s" % errors_style(signals))
    add("  use_cases: %s" % ("optional" if arch.get("use_cases") else "none"))
    add("  layers_file: %s" % (layers_file if layers_file else "null"))
    if mapper:
        add("")
        add("naming:")
        add("  mapper_method: %s" % mapper)
    add("")
    add("paths:")
    if features_root:
        add("  features: %s" % features_root)
    if core_dir:
        add("  core: %s" % core_dir)
    if widgets_dir:
        add("  shared_widgets: %s" % widgets_dir)
    add("")
    add("networking:")
    add("  http: %s" % http)
    add("")
    add("serialization:")
    add("  codegen: %s" % codegen)
    if l10n.get("pipeline") and l10n["pipeline"] != "none":
        add("")
        add("l10n:")
        add("  pipeline: %s" % l10n["pipeline"])
        if arb:
            add("  arb_dir: %s" % arb)
    add("")
    add("testing:")
    add("  unit: %s" % ("mockito" if "mockito" in testing and "mocktail" not in testing else "mocktail"))
    add("  e2e: %s" % ("patrol" if "patrol" in testing else ("integration_test" if e2e == "integration_test" else "none")))
    if flavors.get("names"):
        add("")
        add("flavors:")
        add("  names: [%s]" % ", ".join(flavors["names"]))
        if flavors.get("entrypoint_pattern"):
            add("  entrypoint: %s" % flavors["entrypoint_pattern"])
    add("")
    add("security:")
    add("  level: standard       # assumed default; change it if the app handles money or health data")
    add("")
    if stack.get("needs_decision"):
        add("# Values the profile schema cannot express: %s" % json.dumps(stack["needs_decision"]))
    add("# Not detected (ask a human):")
    for item in NOT_DETECTED:
        add("#   - %s" % item)
    return "\n".join(out) + "\n"


def refuse_real_profile(path: str) -> bool:
    norm = os.path.normpath(os.path.abspath(path))
    return norm.endswith(os.path.join(".flutter-forge", "profile.yaml"))


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--write")
    parser.add_argument("--layers-file", help="path of the layers draft to reference (written by infer_layers.py --write)")
    parser.add_argument("--stack-json", help="reuse a detect_project.py JSON instead of running it")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    try:
        if args.stack_json:
            with open(args.stack_json, encoding="utf-8") as fh:
                stack = json.load(fh)
        else:
            stack = detect(root)
        layers = infer_layers.infer(root)
        text = render(root, stack, layers, args.layers_file if layers.get("status") == "inferred" else None)
    except Exception as exc:
        print("# draft_profile failed: %s: %s" % (type(exc).__name__, str(exc)[:160]))
        return 0
    if args.write:
        if refuse_real_profile(args.write):
            print("# refused: --write must not target .flutter-forge/profile.yaml; use the health output folder")
            return 0
        os.makedirs(os.path.dirname(os.path.abspath(args.write)), exist_ok=True)
        with open(args.write, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
