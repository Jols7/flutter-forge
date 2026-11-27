"""BIT-012: device selection and prompt-loop guard of forge-e2e. No simulator needed: tools are faked.
Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "skills", "forge-e2e", "scripts")
SELECT = os.path.join(SCRIPTS, "select_device.sh")
RUN = os.path.join(SCRIPTS, "run_flow.sh")


def sim_json(*booted: tuple[str, str]) -> str:
    return json.dumps({"devices": {"iOS-18": [{"udid": u, "name": n, "state": "Booted"} for u, n in booted]}})


class Fakes:
    """A temp dir with fake xcrun/adb/flutter/patrol; each prints the canned text it was given."""

    def __init__(self, test: unittest.TestCase, booted=(), shutdown=(), adb=(), patrol_body=None):
        self.dir = tempfile.mkdtemp(prefix="forge-e2e-fakes-")
        test.addCleanup(lambda: __import__("shutil").rmtree(self.dir, ignore_errors=True))
        allsims = {"devices": {"iOS-18": [{"udid": u, "name": n, "state": "Booted"} for u, n in booted]
                               + [{"udid": u, "name": n, "state": "Shutdown"} for u, n in shutdown]}}
        self._write("xcrun", f"""#!/bin/sh
case "$*" in
  *"devices booted"*) cat <<'J'
{sim_json(*booted)}
J
;;
  *"devices available"*) cat <<'J'
{json.dumps(allsims)}
J
;;
  *boot*) echo "$@" >> "{self.dir}/boot.log"; exit 0 ;;
esac
""")
        self._write("adb", "#!/bin/sh\nprintf 'List of devices attached\\n"
                    + "".join(f"{d}\\tdevice\\n" for d in adb) + "'\n")
        self._write("flutter", "#!/bin/sh\necho '[]'\n")
        if patrol_body is not None:
            self._write("patrol", "#!/bin/sh\n" + patrol_body)

    def _write(self, name: str, body: str) -> None:
        path = os.path.join(self.dir, name)
        with open(path, "w") as f:
            f.write(body)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def env(self) -> dict:
        e = dict(os.environ)
        e.update(XCRUN_BIN=os.path.join(self.dir, "xcrun"), ADB_BIN=os.path.join(self.dir, "adb"),
                 FLUTTER_BIN=os.path.join(self.dir, "flutter"), PATH=self.dir + os.pathsep + e["PATH"],
                 HOME=self.dir, TMPDIR=self.dir)
        return e


def sh(args, env, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout, stdin=subprocess.DEVNULL)


def kv(out: str) -> dict:
    return dict(l.split("=", 1) for l in out.splitlines() if "=" in l)


class SelectDeviceTest(unittest.TestCase):
    def test_zero_devices_exits_4_without_booting(self):
        r = sh([SELECT], Fakes(self).env())
        self.assertEqual(r.returncode, 4)
        self.assertIn("NO_DEVICE", r.stdout)

    def test_one_booted_simulator_is_used(self):
        r = sh([SELECT], Fakes(self, booted=[("UDID-1", "iPhone 16")]).env())
        self.assertEqual(r.returncode, 0)
        self.assertEqual(kv(r.stdout)["DEVICE"], "UDID-1")
        self.assertIn("only booted candidate", kv(r.stdout)["REASON"])

    def test_three_devices_prefers_ios_simulator_and_says_why(self):
        f = Fakes(self, booted=[("UDID-1", "iPhone 16"), ("UDID-2", "iPad")], adb=["emulator-5554"])
        r = sh([SELECT], f.env())
        out = kv(r.stdout)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(out["DEVICE"], "UDID-1")
        self.assertIn("3 booted candidates", out["REASON"])
        self.assertIn("emulator-5554", out["REASON"])

    def test_android_emulator_when_no_simulator(self):
        r = sh([SELECT], Fakes(self, adb=["emulator-5554"]).env())
        self.assertEqual(kv(r.stdout)["DEVICE"], "emulator-5554")

    def test_prefer_wins_over_order(self):
        f = Fakes(self, booted=[("UDID-1", "iPhone 16")], adb=["emulator-5554"])
        r = sh([SELECT, "--prefer", "emulator-5554"], f.env())
        self.assertEqual(kv(r.stdout)["DEVICE"], "emulator-5554")

    def test_prefer_absent_falls_back_and_reports_it(self):
        r = sh([SELECT, "--prefer", "ghost"], Fakes(self, booted=[("UDID-1", "iPhone 16")]).env())
        out = kv(r.stdout)
        self.assertEqual(out["DEVICE"], "UDID-1")
        self.assertIn("'ghost' not found", out["REASON"])

    def test_prefer_shutdown_simulator_is_booted(self):
        f = Fakes(self, shutdown=[("UDID-9", "iPhone 15")])
        r = sh([SELECT, "--prefer", "iPhone 15"], f.env())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(kv(r.stdout)["DEVICE"], "UDID-9")
        self.assertTrue(os.path.exists(os.path.join(f.dir, "boot.log")))

    def test_no_boot_flag_does_not_boot(self):
        f = Fakes(self, shutdown=[("UDID-9", "iPhone 15")])
        r = sh([SELECT, "--prefer", "iPhone 15", "--no-boot"], f.env())
        self.assertEqual(r.returncode, 4)
        self.assertFalse(os.path.exists(os.path.join(f.dir, "boot.log")))


class RunFlowDeviceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forge-e2e-run-")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.test_file = os.path.join(self.tmp, "a_test.dart")
        open(self.test_file, "w").close()

    def test_no_device_never_starts_patrol(self):
        f = Fakes(self, patrol_body=f'echo started > "{self.tmp}/patrol-called"\n')
        r = sh([RUN, "--test", self.test_file], f.env())
        self.assertEqual(r.returncode, 4)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "patrol-called")))

    def test_selected_device_is_always_passed_to_patrol(self):
        f = Fakes(self, booted=[("UDID-1", "iPhone 16")],
                  patrol_body='echo "ARGS: $@"\necho "[FLOW x] END OK"\n')
        r = sh([RUN, "--test", self.test_file], f.env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--device UDID-1", r.stdout)
        self.assertIn("RESULT: GREEN", r.stdout)

    def test_explicit_device_skips_selection(self):
        f = Fakes(self, patrol_body='echo "[FLOW x] END OK"\n')
        r = sh([RUN, "--test", self.test_file, "--device", "mine"], f.env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--device mine", r.stdout)

    def test_repeated_device_prompt_aborts_with_5_quickly(self):
        body = 'while true; do echo "Please choose one (or \\"q\\" to quit): "; sleep 0.2; done\n'
        f = Fakes(self, patrol_body=body)
        r = sh([RUN, "--test", self.test_file, "--device", "x", "--timeout", "60"], f.env(), timeout=30)
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn("DEVICE_PROMPT_LOOP", r.stdout)

    def test_zero_tests_executed_is_not_green(self):
        f = Fakes(self, patrol_body='printf "Test summary:\\nTotal: 0\\nSuccessful: 0\\nFailed: 0\\n"\n')
        r = sh([RUN, "--test", self.test_file, "--device", "x"], f.env())
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("NO_TESTS_RAN", r.stdout)

    def test_patrol_gets_closed_stdin(self):
        f = Fakes(self, patrol_body='if read -r l; then echo "[FLOW x] FAIL got-input"; else echo "[FLOW x] END OK"; fi\n')
        r = sh([RUN, "--test", self.test_file, "--device", "x"], f.env())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
