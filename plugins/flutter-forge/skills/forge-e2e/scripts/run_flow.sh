#!/usr/bin/env bash
# Run one Patrol (or integration_test) flow test, print only the flow report, and stop hung runs.
#
# Usage:
#   run_flow.sh --test <path|all> [--flavor <flavor id>] [--device <id>] [--timeout <s>]
#               [--env <credentials json>] [--forbid "prod,appProd"] [--runner patrol|integration_test]
#               [--dir <e2e dir>] [-- <extra args passed to patrol/flutter test>]
# Exit: 0 green · 1 failures · 2 timeout · 3 usage error / refused
set -u

EXTRA=()
TEST="" FLAVOR="" DEVICE="" TIMEOUT=900 ENV_FILE="" FORBID="prod" RUNNER="patrol" E2E_DIR="patrol_test"

usage() { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 3; }

while [ $# -gt 0 ]; do
  case "$1" in
    --test) TEST="${2:-}"; shift 2 ;;
    --flavor) FLAVOR="${2:-}"; shift 2 ;;
    --device) DEVICE="${2:-}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-}"; shift 2 ;;
    --env) ENV_FILE="${2:-}"; shift 2 ;;
    --forbid) FORBID="${2:-}"; shift 2 ;;
    --runner) RUNNER="${2:-}"; shift 2 ;;
    --dir) E2E_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    --) shift; EXTRA=("$@"); break ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

if [ -z "$TEST" ]; then echo "--test is required" >&2; usage; fi
case "$TIMEOUT" in ''|*[!0-9]*) echo "--timeout must be seconds" >&2; exit 3 ;; esac

# Refuse forbidden flavors: exact id match, or the id ends with a forbidden name (appProd ← prod).
flavor_lc=$(printf '%s' "$FLAVOR" | tr '[:upper:]' '[:lower:]')
IFS=',' read -r -a forbidden <<< "$FORBID"
for f in "${forbidden[@]}"; do
  f_lc=$(printf '%s' "$f" | tr '[:upper:]' '[:lower:]' | tr -d ' ')
  [ -z "$f_lc" ] && continue
  case "$flavor_lc" in
    "$f_lc"|*"$f_lc") echo "REFUSED: flavor '$FLAVOR' is forbidden for E2E ($FORBID)" >&2; exit 3 ;;
  esac
done

if [ "$TEST" != "all" ] && [ ! -f "$TEST" ]; then echo "Test file not found: $TEST" >&2; exit 3; fi
if [ -n "$ENV_FILE" ] && [ ! -f "$ENV_FILE" ]; then
  echo "Credentials file not found: $ENV_FILE — create it from the committed example (the agent never writes it)." >&2
  exit 3
fi

cmd=()
if [ "$RUNNER" = "patrol" ]; then
  PATROL_BIN=$(command -v patrol || true)
  [ -z "$PATROL_BIN" ] && [ -x "$HOME/.pub-cache/bin/patrol" ] && PATROL_BIN="$HOME/.pub-cache/bin/patrol"
  [ -z "$PATROL_BIN" ] && { echo "patrol CLI not found: dart pub global activate patrol_cli" >&2; exit 3; }
  cmd=("$PATROL_BIN" test --show-flutter-logs)
  [ -n "$FLAVOR" ] && cmd+=(--flavor "$FLAVOR")
  [ "$TEST" != "all" ] && cmd+=(--target "$TEST")
  [ -n "$DEVICE" ] && cmd+=(--device "$DEVICE")
elif [ "$RUNNER" = "integration_test" ]; then
  FLUTTER_BIN=${FLUTTER_BIN:-flutter}
  target="$TEST"; [ "$TEST" = "all" ] && target="$E2E_DIR"
  cmd=("$FLUTTER_BIN" test "$target")
  [ -n "$FLAVOR" ] && cmd+=(--flavor "$FLAVOR")
  [ -n "$DEVICE" ] && cmd+=(-d "$DEVICE")
else
  echo "--runner must be patrol or integration_test" >&2; exit 3
fi
[ -n "$ENV_FILE" ] && cmd+=("--dart-define-from-file=$ENV_FILE")
[ "${#EXTRA[@]}" -gt 0 ] && cmd+=("${EXTRA[@]}")

LOG="${TMPDIR:-/tmp}/forge-e2e-$(date +%Y%m%d-%H%M%S)-$$.log"
echo "Running: ${cmd[*]}"
echo "Log: $LOG"

"${cmd[@]}" > "$LOG" 2>&1 &
PID=$!

stop_run() {
  kill "$PID" 2>/dev/null
  sleep 2
  kill -9 "$PID" 2>/dev/null
  pkill -P "$PID" 2>/dev/null || true
}
trap 'stop_run; exit 3' INT TERM

elapsed=0
summary_seen=0
status=""
while kill -0 "$PID" 2>/dev/null; do
  if grep -Eq 'Test summary|All tests passed|Some tests failed|tests? (passed|failed)' "$LOG" 2>/dev/null; then
    summary_seen=$((summary_seen + 1))
    # give the tool a few seconds to exit on its own, then stop it (Patrol may hang on iOS)
    if [ "$summary_seen" -ge 5 ]; then stop_run; break; fi
  fi
  if [ "$elapsed" -ge "$TIMEOUT" ]; then status="timeout"; stop_run; break; fi
  sleep 2
  elapsed=$((elapsed + 2))
done
wait "$PID" 2>/dev/null
code=$?

echo "----- flow report -----"
CLEAN="$LOG.clean"
sed -E $'s/\x1b\\[[0-9;]*[A-Za-z]//g' "$LOG" > "$CLEAN"
grep -E '\[FLOW |\[APP_ERROR\]|Successful: |Failed: |All tests passed|Some tests failed|EXCEPTION CAUGHT' "$CLEAN" | sed -E 's/^.*(\[FLOW |\[APP_ERROR\])/\1/' || true
echo "-----------------------"
echo "Full log: $LOG"

if [ "$status" = "timeout" ]; then echo "RESULT: TIMEOUT after ${TIMEOUT}s"; exit 2; fi
if grep -Eq '\[FLOW [^]]*\] (FAIL|ABORTED|END [0-9]+ failure)|Some tests failed|Failed: [1-9]' "$CLEAN"; then
  echo "RESULT: FAILURES"; exit 1
fi
if grep -Eq '\[FLOW [^]]*\] END OK|All tests passed|Successful: [1-9]' "$CLEAN"; then
  echo "RESULT: GREEN"; exit 0
fi
echo "RESULT: UNKNOWN (process exit $code) — read the full log"
if [ "$code" -eq 0 ]; then exit 0; else exit 1; fi
