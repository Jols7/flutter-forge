#!/usr/bin/env python3
"""Scan a Flutter project for hardcoded secrets, bundled env files and sensitive logging.

Usage: scan_secrets.py [--root PROJECT] [--files F ...] [--format text|json] [--no-fail]

Values are always masked in the output. Read-only, no network, Python 3.9+ stdlib.
Exit 1 when findings of severity high/critical exist (unless --no-fail).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, Iterable, List

TEXT_EXT = {".dart", ".yaml", ".yml", ".json", ".xml", ".plist", ".gradle", ".kts", ".properties",
            ".env", ".txt", ".md", ".sh", ".js", ".ts", ".swift", ".kt", ".java", ".m", ".h", ".xcconfig", ".arb"}
SKIP_DIRS = {".git", ".dart_tool", "build", ".idea", ".vscode", "Pods", ".gradle", ".fvm", "node_modules", ".symlinks"}
SKIP_FILES = re.compile(r"(\.g\.dart|\.freezed\.dart|\.lock|pubspec\.lock|Podfile\.lock|\.min\.js)$")

PATTERNS = [
    ("private-key", "critical", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("aws-access-key", "critical", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", "critical", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("slack-token", "critical", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-live-key", "critical", re.compile(r"\b(sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("postman-api-key", "critical", re.compile(r"\bPMAK-[A-Za-z0-9]{24}-[A-Za-z0-9]{34}\b")),
    ("google-api-key", "medium", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("jwt", "high", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("generic-secret-assignment", "high", re.compile(
        r"""(?i)\b([A-Za-z_]*(?:secret|api[_-]?key|apikey|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|private[_-]?key)[A-Za-z_]*)\s*[:=]\s*['"]([^'"\s$]{8,})['"]""")),
]
CLEAR_HTTP = re.compile(r"""['"]http://(?!localhost|127\.0\.0\.1|10\.0\.2\.2|0\.0\.0\.0|schemas\.android\.com|www\.w3\.org|ns\.adobe\.com|apple\.com/DTDs)[^'"\s]+['"]""")
LOG_CALL = re.compile(r"\b(print|debugPrint|log|logger\.\w+|Log\.\w+|developer\.log)\s*\(([^;]*)\)")
SENSITIVE_IN_LOG = re.compile(r"(?i)(token|password|passwd|secret|authorization|cookie|pin\b|cvv|card|otp|session)")
TOKEN_LIKE = re.compile(r"^[\x21-\x7e]{8,}$")          # printable ASCII, no spaces: not UI copy
PLACEHOLDER = re.compile(r"(?i)(example|placeholder|changeme|your[_-]?|xxx+|dummy|fake|test|sample|redacted|<|\$\{|\{\{)")


def mask(value: str) -> str:
    value = value.strip()
    return value[:4] + "…" + "*" * 4 if len(value) > 8 else "****"


def tracked_files(root: str) -> List[str]:
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard"], capture_output=True, text=True, check=True)
        files = [f for f in out.stdout.splitlines() if f]
        if files:
            return files
    except (OSError, subprocess.CalledProcessError):
        pass
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            result.append(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"))
    return result


def candidate(path: str) -> bool:
    parts = path.split("/")
    if any(p in SKIP_DIRS for p in parts) or SKIP_FILES.search(path):
        return False
    base = parts[-1]
    ext = os.path.splitext(base)[1].lower()
    return ext in TEXT_EXT or base.startswith(".env") or base in ("Podfile", "Gemfile", "Fastfile", "Appfile")


def scan_file(root: str, path: str) -> Iterable[Dict]:
    try:
        with open(os.path.join(root, path), encoding="utf-8") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeDecodeError):
        return
    is_dart = path.endswith(".dart")
    in_test = path.startswith(("test/", "integration_test/", "patrol_test/")) or "/test/" in path
    firebase_file = path.endswith(("firebase_options.dart", "google-services.json", "GoogleService-Info.plist")) or "firebase" in path.lower()
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("//", "#")) and "BEGIN" not in stripped:
            continue
        matched_specific = False
        for kind, severity, rx in PATTERNS:
            for m in rx.finditer(line):
                value = m.group(m.lastindex or 0)
                if kind == "generic-secret-assignment":
                    if matched_specific or PLACEHOLDER.search(value) or not TOKEN_LIKE.match(value):
                        continue
                    # identifiers such as storage keys ('access_token') are names, not secrets
                    if not (re.search(r"[\dA-Z]|[^\w.\-]", value) or len(value) >= 24):
                        continue
                else:
                    matched_specific = True
                sev = severity
                message = _message(kind)
                if in_test:
                    sev = "low"
                if kind == "google-api-key" and firebase_file:
                    sev = "low"
                    message = "Firebase client API key (public by design): make sure API-key restrictions and App Check are enabled"
                yield {"file": path, "line": number, "kind": kind, "severity": sev, "evidence": mask(value), "message": message}
        if is_dart and CLEAR_HTTP.search(line) and not in_test:
            yield {"file": path, "line": number, "kind": "cleartext-url", "severity": "high",
                   "evidence": CLEAR_HTTP.search(line).group(0)[:60], "message": "Hardcoded http:// URL: traffic is unencrypted (MASVS-NETWORK-1)"}
        if is_dart and not in_test:
            for m in LOG_CALL.finditer(line):
                if SENSITIVE_IN_LOG.search(m.group(2)):
                    yield {"file": path, "line": number, "kind": "sensitive-logging", "severity": "high",
                           "evidence": m.group(1) + "(…" + SENSITIVE_IN_LOG.search(m.group(2)).group(1) + "…)",
                           "message": "Logging call references sensitive data (MASVS-STORAGE-2 / PRIVACY)"}


def _message(kind: str) -> str:
    return {
        "private-key": "Private key committed in the repository",
        "aws-access-key": "AWS access key id in source",
        "github-token": "GitHub token in source",
        "slack-token": "Slack token in source",
        "stripe-live-key": "Live payment secret key in source",
        "postman-api-key": "Postman API key in source",
        "google-api-key": "Google API key in source: client keys are extractable; restrict it by app signature/bundle id and API (MASVS-CODE)",
        "jwt": "Hardcoded JWT: tokens must never be in source (MASVS-AUTH)",
        "generic-secret-assignment": "Hardcoded secret-like literal: anything shipped in the app is public (MASVS-STORAGE/CODE)",
    }[kind]


def env_bundling(root: str) -> List[Dict]:
    findings = []
    try:
        with open(os.path.join(root, "pubspec.yaml"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return findings
    block = re.search(r"^\s{2}assets:\s*\n((?:\s{4,}-.*\n?)+)", text, re.M)
    if block:
        for m in re.finditer(r"-\s*['\"]?([^'\"\n]+)", block.group(1)):
            asset = m.group(1).strip()
            if re.search(r"(^|/)\.env", asset) or asset.endswith((".env", ".pem", ".p12", ".jks", ".keystore")):
                findings.append({"file": "pubspec.yaml", "line": text[:block.start()].count("\n") + 1, "kind": "bundled-secret-file",
                                 "severity": "high", "evidence": asset,
                                 "message": "File bundled as an asset is readable by anyone who unzips the app: keep only non-secret config there (MASVS-STORAGE-1/CODE)"})
    for name in os.listdir(root):
        if name.startswith(".env") and not name.endswith((".example", ".sample", ".template")):
            ignored = subprocess.run(["git", "-C", root, "check-ignore", "-q", name], capture_output=True).returncode == 0 if os.path.isdir(os.path.join(root, ".git")) else None
            if ignored is False:
                findings.append({"file": name, "line": 0, "kind": "env-not-ignored", "severity": "high", "evidence": name,
                                 "message": "Environment file is not gitignored"})
    return findings


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--files", nargs="*")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    files = args.files if args.files else tracked_files(root)
    findings: List[Dict] = []
    for path in files:
        path = path.replace(os.sep, "/")
        if candidate(path):
            findings.extend(scan_file(root, path))
    findings.extend(env_bundling(root))
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: (order[f["severity"]], f["file"], f["line"]))
    if args.format == "json":
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
    else:
        for f in findings:
            print("%-8s %s:%d  [%s] %s  (%s)" % (f["severity"], f["file"], f["line"], f["kind"], f["message"], f["evidence"]))
        print("Secret scan: %d finding(s)" % len(findings))
    blocking = any(f["severity"] in ("critical", "high") for f in findings)
    return 1 if blocking and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
