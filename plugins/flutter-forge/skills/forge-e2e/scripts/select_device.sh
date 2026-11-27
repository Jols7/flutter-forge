#!/usr/bin/env bash
# Pick ONE device for an E2E run, deterministically and without asking anything.
#
# Usage:
#   select_device.sh [--prefer <id|name>] [--no-boot] [--boot-timeout <s>]
# Order: the device the person/profile asked for (--prefer, profile `testing.device`)
#        → a booted iOS simulator → a booted Android emulator.
# Never picks a physical device, desktop or web unless it is named with --prefer.
# If nothing is booted it tries to boot --prefer (a simulator, by UDID or name), then gives up.
# Output (stdout): DEVICE=<id> and REASON=<why>. Exit: 0 chosen · 4 no device available
# Tool binaries can be overridden for tests: FLUTTER_BIN, XCRUN_BIN, ADB_BIN.
set -u

PREFER="" BOOT=1 BOOT_TIMEOUT=120
while [ $# -gt 0 ]; do
  case "$1" in
    --prefer) PREFER="${2:-}"; shift 2 ;;
    --no-boot) BOOT=0; shift ;;
    --boot-timeout) BOOT_TIMEOUT="${2:-120}"; shift 2 ;;
    -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 3 ;;
  esac
done

XCRUN_BIN=${XCRUN_BIN:-xcrun}; ADB_BIN=${ADB_BIN:-adb}; FLUTTER_BIN=${FLUTTER_BIN:-flutter}
export PREFER BOOT BOOT_TIMEOUT XCRUN_BIN

SIM_JSON=$("$XCRUN_BIN" simctl list devices booted --json 2>/dev/null || true)
SIM_ALL=$("$XCRUN_BIN" simctl list devices available --json 2>/dev/null || true)
ADB_OUT=$("$ADB_BIN" devices 2>/dev/null || true)
FL_JSON=$("$FLUTTER_BIN" devices --machine 2>/dev/null || true)
export SIM_JSON SIM_ALL ADB_OUT FL_JSON

exec python3 - <<'PY'
import json, os, re, subprocess, sys

def load(name):
    try:
        return json.loads(os.environ.get(name) or "{}")
    except ValueError:
        return {}

prefer = os.environ.get("PREFER", "").strip()
boot = os.environ.get("BOOT") == "1"
timeout = int(os.environ.get("BOOT_TIMEOUT") or 120)

def sims(data, only_booted):
    out = []
    for devs in (data.get("devices") or {}).values():
        for d in devs:
            if only_booted and d.get("state") != "Booted":
                continue
            out.append({"id": d["udid"], "name": d.get("name", ""), "kind": "ios-simulator"})
    return out

booted_sims = sims(load("SIM_JSON"), True)
all_sims = sims(load("SIM_ALL"), False)
emus = []
for line in (os.environ.get("ADB_OUT") or "").splitlines()[1:]:
    parts = line.split()
    if len(parts) >= 2 and parts[1] == "device" and parts[0].startswith("emulator-"):
        emus.append({"id": parts[0], "name": parts[0], "kind": "android-emulator"})

flutter = []
fl = os.environ.get("FL_JSON") or "[]"
try:
    for d in json.loads(fl):
        flutter.append({"id": d.get("id", ""), "name": d.get("name", ""), "kind": "flutter-device"})
except ValueError:
    pass

def match(pool, wanted):
    w = wanted.lower()
    return next((d for d in pool if d["id"].lower() == w or d["name"].lower() == w), None)

def done(dev, why):
    print(f"DEVICE={dev['id']}")
    print(f"REASON={why}")
    sys.exit(0)

note = ""
if prefer:
    hit = match(booted_sims + emus + flutter, prefer)
    if hit:
        done(hit, f"requested device '{prefer}' ({hit['kind']})")
    target = match(all_sims, prefer)
    if target and boot:
        subprocess.run([os.environ["XCRUN_BIN"], "simctl", "boot", target["id"]], capture_output=True)
        try:
            r = subprocess.run([os.environ["XCRUN_BIN"], "simctl", "bootstatus", target["id"], "-b"],
                               capture_output=True, timeout=timeout)
            if r.returncode == 0:
                done(target, f"requested simulator '{prefer}' was shut down; booted it")
        except subprocess.TimeoutExpired:
            pass
        note = f"requested simulator '{prefer}' did not boot within {timeout}s; "
    else:
        note = f"requested device '{prefer}' not found; "

candidates = booted_sims + emus
if candidates:
    chosen = candidates[0]
    others = [c["id"] for c in candidates[1:]]
    if len(candidates) == 1:
        why = f"{note}only booted candidate ({chosen['kind']} '{chosen['name']}')"
    else:
        why = (f"{note}{len(candidates)} booted candidates; order is requested → iOS simulator → Android emulator, "
               f"so {chosen['kind']} '{chosen['name']}' wins over {', '.join(others)}")
    done(chosen, why)

print(f"{note}no booted iOS simulator or Android emulator found. Boot one "
      "(xcrun simctl boot <udid> / emulator -avd <name>) or set testing.device in the profile.", file=sys.stderr)
print("RESULT: NO_DEVICE")
sys.exit(4)
PY
