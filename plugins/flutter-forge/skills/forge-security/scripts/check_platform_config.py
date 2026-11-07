#!/usr/bin/env python3
"""Check Android/iOS platform configuration of a Flutter app against MASVS-oriented rules.

Usage: check_platform_config.py [--root PROJECT] [--format text|json] [--no-fail]

Checks AndroidManifest(s), network security config, Gradle release settings,
iOS Info.plist (ATS, URL schemes, permission strings) and release build scripts.
Read-only, no network, Python 3.9+ stdlib. Exit 1 on high/critical findings.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import plistlib
import re
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
DANGEROUS_PERMISSIONS = {
    "READ_CONTACTS", "WRITE_CONTACTS", "READ_SMS", "RECEIVE_SMS", "SEND_SMS", "READ_CALL_LOG", "READ_PHONE_STATE",
    "ACCESS_FINE_LOCATION", "ACCESS_BACKGROUND_LOCATION", "RECORD_AUDIO", "CAMERA", "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE", "MANAGE_EXTERNAL_STORAGE", "READ_MEDIA_IMAGES", "SYSTEM_ALERT_WINDOW", "QUERY_ALL_PACKAGES",
    "REQUEST_INSTALL_PACKAGES", "BODY_SENSORS",
}


def finding(findings: List[Dict], severity: str, area: str, file: str, message: str, masvs: str, fix: str) -> None:
    findings.append({"severity": severity, "area": area, "file": file, "message": message, "masvs": masvs, "fix": fix})


def block(text: str, opener: str) -> str:
    """Body of the first `{ … }` block whose header matches `opener` (brace-balanced)."""
    m = re.search(opener, text)
    if not m:
        return ""
    depth, start = 1, m.end()
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
    return text[start:]


def check_android(root: str, findings: List[Dict]) -> None:
    manifest = os.path.join(root, "android/app/src/main/AndroidManifest.xml")
    if not os.path.exists(manifest):
        return
    rel = os.path.relpath(manifest, root)
    try:
        tree = ET.parse(manifest)
    except ET.ParseError as e:
        finding(findings, "medium", "android", rel, "Manifest could not be parsed: %s" % e, "-", "Fix the XML")
        return
    app = tree.getroot().find("application")
    if app is not None:
        attr = lambda n: app.get(ANDROID_NS + n)
        if attr("usesCleartextTraffic") == "true":
            finding(findings, "high", "android", rel, "android:usesCleartextTraffic=\"true\" allows HTTP traffic", "MASVS-NETWORK-1",
                    "Remove it (default false since API 28) or scope cleartext to debug hosts via a debug-only network_security_config")
        if attr("allowBackup") != "false":
            finding(findings, "medium", "android", rel, "android:allowBackup is not false: app data (incl. prefs) can be extracted via backup", "MASVS-STORAGE-2",
                    "Set android:allowBackup=\"false\" (and dataExtractionRules/fullBackupContent excluding sensitive files)")
        if attr("debuggable") == "true":
            finding(findings, "critical", "android", rel, "android:debuggable=\"true\" hardcoded in the main manifest", "MASVS-RESILIENCE-4",
                    "Remove it; Gradle sets debuggable per build type")
        nsc = attr("networkSecurityConfig")
        if nsc:
            name = nsc.split("/")[-1]
            path = os.path.join(root, "android/app/src/main/res/xml", name + ".xml")
            if os.path.exists(path):
                text = open(path, encoding="utf-8").read()
                if re.search(r'cleartextTrafficPermitted="true"', text) and "<base-config" in text:
                    finding(findings, "high", "android", os.path.relpath(path, root), "Network security config permits cleartext in base-config", "MASVS-NETWORK-1",
                            "Permit cleartext only in <domain-config> for local debug hosts, in a debug source set")
                if "<certificates src=\"user\"" in text and "debug-overrides" not in text:
                    finding(findings, "high", "android", os.path.relpath(path, root), "User-installed CAs trusted outside debug-overrides", "MASVS-NETWORK-1",
                            "Trust user CAs only inside <debug-overrides>")
        for tag in ("activity", "service", "receiver", "provider"):
            for comp in app.findall(tag):
                exported = comp.get(ANDROID_NS + "exported")
                has_filter = comp.find("intent-filter") is not None
                name = comp.get(ANDROID_NS + "name", "?")
                if exported == "true" and not comp.get(ANDROID_NS + "permission") and tag != "activity":
                    finding(findings, "high", "android", rel, "%s %s is exported without a permission" % (tag, name), "MASVS-PLATFORM-1",
                            "Set android:exported=\"false\" or protect it with a signature permission")
                if tag == "activity" and has_filter:
                    for data in comp.iter("data"):
                        scheme = data.get(ANDROID_NS + "scheme")
                        if scheme and scheme not in ("http", "https"):
                            finding(findings, "medium", "android", rel, "Custom URL scheme '%s://' on %s: any app can register it" % (scheme, name), "MASVS-PLATFORM-1",
                                    "Prefer verified App Links (https + autoVerify); validate every deep-link parameter in the router")
    permissions = {p.get(ANDROID_NS + "name", "").split(".")[-1] for p in tree.getroot().findall("uses-permission")}
    risky = sorted(permissions & DANGEROUS_PERMISSIONS)
    if risky:
        finding(findings, "low", "android", rel, "Sensitive permissions requested: %s" % ", ".join(risky), "MASVS-PRIVACY-1",
                "Confirm each one is required by a feature and requested at use time with rationale")

    for gradle in glob.glob(os.path.join(root, "android/app/build.gradle*")):
        text = open(gradle, encoding="utf-8").read()
        relg = os.path.relpath(gradle, root)
        build_types = block(text, r"buildTypes\s*\{")
        body = block(build_types or "", r"(?:getByName\(\s*[\"']release[\"']\s*\)|\brelease)\s*\{") or ""
        release = bool(body)
        if release and re.search(r"signingConfig\s*=?\s*signingConfigs\.(getByName\(\"debug\"\)|debug)", body):
            finding(findings, "high", "android", relg, "Release build is signed with the debug key", "MASVS-CODE-1",
                    "Use a release signingConfig fed from CI secrets (never committed keystores/passwords)")
        if release and not re.search(r"(minifyEnabled|isMinifyEnabled)\s*=?\s*true", body):
            finding(findings, "low", "android", relg, "R8 minification not enabled for release", "MASVS-RESILIENCE-3",
                    "Enable isMinifyEnabled/isShrinkResources with proguard rules (Flutter Dart code is protected via --obfuscate)")
        if re.search(r"(?<![\"'])\b(storePassword|keyPassword)\b\s*=?\s*['\"][^'\"$\n]{4,}['\"]", text):
            finding(findings, "critical", "android", relg, "Keystore password hardcoded in Gradle", "MASVS-CODE-1",
                    "Read it from key.properties (gitignored) or CI environment variables")


def check_ios(root: str, findings: List[Dict]) -> None:
    for plist_path in glob.glob(os.path.join(root, "ios/Runner/Info*.plist")):
        rel = os.path.relpath(plist_path, root)
        try:
            with open(plist_path, "rb") as fh:
                plist = plistlib.load(fh)
        except Exception as e:  # noqa: BLE001 - malformed plist is itself a finding
            finding(findings, "medium", "ios", rel, "Info.plist could not be parsed: %s" % e, "-", "Fix the plist")
            continue
        ats = plist.get("NSAppTransportSecurity") or {}
        if ats.get("NSAllowsArbitraryLoads"):
            finding(findings, "high", "ios", rel, "NSAllowsArbitraryLoads=true disables App Transport Security", "MASVS-NETWORK-1",
                    "Remove it; add narrowly scoped NSExceptionDomains only for hosts that truly need it")
        for domain, cfg in (ats.get("NSExceptionDomains") or {}).items():
            if isinstance(cfg, dict) and cfg.get("NSExceptionAllowsInsecureHTTPLoads"):
                finding(findings, "medium", "ios", rel, "Insecure HTTP allowed for %s" % domain, "MASVS-NETWORK-1",
                        "Use HTTPS for this host or restrict the exception to debug builds")
        for url_type in plist.get("CFBundleURLTypes") or []:
            for scheme in url_type.get("CFBundleURLSchemes") or []:
                if not str(scheme).startswith(("com.googleusercontent", "fb")):
                    finding(findings, "medium", "ios", rel, "Custom URL scheme '%s://': any app can claim it" % scheme, "MASVS-PLATFORM-1",
                            "Prefer Universal Links; validate every deep-link parameter in the router")
        if plist.get("UIFileSharingEnabled") or plist.get("LSSupportsOpeningDocumentsInPlace"):
            finding(findings, "medium", "ios", rel, "Documents folder exposed via file sharing", "MASVS-STORAGE-2",
                    "Disable unless the feature needs it; never store sensitive files in Documents")
        for key, value in plist.items():
            if key.endswith("UsageDescription") and (not value or len(str(value).strip()) < 10):
                finding(findings, "low", "ios", rel, "%s is empty or too vague" % key, "MASVS-PRIVACY-1",
                        "Explain concretely why the permission is needed (App Review also rejects vague strings)")


def check_build_scripts(root: str, findings: List[Dict]) -> None:
    candidates = glob.glob(os.path.join(root, ".github/workflows/*.y*ml")) + glob.glob(os.path.join(root, "codemagic.y*ml")) + \
        glob.glob(os.path.join(root, "fastlane/Fastfile")) + glob.glob(os.path.join(root, "scripts/*.sh")) + \
        glob.glob(os.path.join(root, "bitrise.y*ml"))
    release_cmds = []
    for path in candidates:
        text = open(path, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r"flutter\s+build\s+(apk|appbundle|ipa|ios)[^\n]*", text):
            release_cmds.append((os.path.relpath(path, root), m.group(0)))
    for path, cmd in release_cmds:
        if "--obfuscate" not in cmd or "--split-debug-info" not in cmd:
            finding(findings, "low", "build", path, "Release build without --obfuscate --split-debug-info: `%s`" % cmd.strip()[:80], "MASVS-RESILIENCE-3",
                    "Add --obfuscate --split-debug-info=build/symbols and upload symbols to the crash reporter")
    if not release_cmds:
        finding(findings, "info", "build", "-", "No CI release build script found to verify obfuscation", "MASVS-RESILIENCE-3",
                "Document the release command with --obfuscate --split-debug-info")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.root)
    findings: List[Dict] = []
    check_android(root, findings)
    check_ios(root, findings)
    check_build_scripts(root, findings)
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: order[f["severity"]])
    if args.format == "json":
        print(json.dumps({"findings": findings}, indent=2))
    else:
        for f in findings:
            print("%-8s %-7s %s — %s [%s]\n         fix: %s" % (f["severity"], f["area"], f["file"], f["message"], f["masvs"], f["fix"]))
        print("Platform config: %d finding(s)" % len(findings))
    return 1 if any(f["severity"] in ("critical", "high") for f in findings) and not args.no_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
