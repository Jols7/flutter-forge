"""Tests for forge-metrics' run_metrics.py, on synthetic transcripts.

Run: python3 -m unittest discover -s plugins/flutter-forge/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "skills", "forge-metrics", "scripts")
sys.path.insert(0, SCRIPTS)
import run_metrics  # noqa: E402

SLUG = "new-transfer"
RUN_PATH = ".flutter-forge/runs/%s/brief.md" % SLUG
CANARY = "CONVERSATION-CANARY"
OPUS, SONNET = "model-large", "model-small"


def at(minute: int, second: int = 0) -> str:
    return "2026-01-10T%02d:%02d:%02dZ" % (10 + minute // 60, minute % 60, second)


def call(minute, msg_id, model=OPUS, output=100, read=1000, tools=()):
    return {"type": "assistant", "timestamp": at(minute), "message": {
        "id": msg_id, "model": model, "content": list(tools),
        "usage": {"input_tokens": 10, "output_tokens": output, "cache_read_input_tokens": read,
                  "cache_creation_input_tokens": 50,
                  "cache_creation": {"ephemeral_1h_input_tokens": 50, "ephemeral_5m_input_tokens": 0}}}}


def tool(name, tool_id="t1", **data):
    return {"type": "tool_use", "id": tool_id, "name": name, "input": data}


def result(minute, tool_id="t1"):
    return {"type": "user", "timestamp": at(minute), "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_id, "content": CANARY}]}}


def prompt(minute, text=CANARY):
    return {"type": "user", "timestamp": at(minute), "message": {"content": text}}


def cost(usd_by_model, api_ms=60000):
    return {"type": "cost-state", "totalCostUSD": sum(usd_by_model.values()), "totalAPIDuration": api_ms,
            "modelUsage": {m: {"costUSD": usd, "inputTokens": 10, "outputTokens": 100, "thinkingTokens": 5,
                               "cacheReadInputTokens": 1000, "cacheCreationInputTokens": 50}
                           for m, usd in usd_by_model.items()}}


class RunMetricsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root = os.path.join(self.tmp, "app")
        self.projects = os.path.join(self.tmp, "projects")
        self.run_dir = os.path.join(self.root, ".flutter-forge", "runs", SLUG)
        os.makedirs(self.run_dir)
        os.makedirs(self.projects)
        self.session("aaaa1111", [
            prompt(0),
            call(1, "a1", tools=[tool("Skill", skill="flutter-forge:forge-requirements")]),
            call(2, "a2", tools=[tool("Write", "t2", file_path="/app/" + RUN_PATH, content=CANARY)]),
            result(3, "t2"),
            call(4, "a3", output=300, tools=[tool("Skill", "t3", skill="flutter-forge:forge-tests")]),
            call(5, "a4", output=300, tools=[tool("AskUserQuestion", "t4", question=CANARY)]),
            result(7, "t4"),
            call(8, "a4b", output=300),
            prompt(10),
            call(11, "a5", output=300),
            cost({OPUS: 3.0, "model-aux": 0.01}),
        ], subagent=[call(9, "s1", model=SONNET, output=50)], extra_cost={SONNET: 0.5})
        self.session("bbbb2222", [
            call(20, "b1", tools=[tool("Bash", command="python3 x.py %s" % RUN_PATH)]),
            result(21), cost({OPUS: 1.0}),
        ])
        self.session("cccc3333", [
            call(22, "c1", tools=[tool("Bash", command="grep x ~/.claude/projects/y %s" % RUN_PATH)]),
            cost({OPUS: 2.0}),
        ])
        self.session("dddd4444", [call(25, "d1"), cost({OPUS: 0.25})])
        self.session("eeee5555", [call(180, "e1"), cost({OPUS: 9.0})])
        self.write_run({"phases": ["requirements", "tests"], "status": "completed",
                        "gates": {"brief": {"status": "approved", "changed": True},
                                  "blueprint": {"status": "approved", "changed": False},
                                  "findings": {"status": "pending"}},
                        "retries": {"tests": 2}, "baseline_estimate_hours": 10},
                       {"status": "completed",
                        "acceptance_criteria": [{"id": "AC-1", "status": "implemented-tested"},
                                                {"id": "AC-2", "status": "pending"}],
                        "review": {"verdict": "pass", "findings": [{"status": "fixed"}, {"status": "fixed"},
                                                                   {"status": "wontfix"}, {"status": "deferred"}]}})

    def session(self, sid, rows, subagent=None, extra_cost=None):
        if extra_cost:
            state = rows[-1]
            state["totalCostUSD"] += sum(extra_cost.values())
            state["modelUsage"].update(cost(extra_cost)["modelUsage"])
        path = os.path.join(self.projects, sid + "-0000.jsonl")
        with open(path, "w", encoding="utf-8") as out:
            out.write("not json\n")
            for row in rows:
                out.write(json.dumps(row) + "\n")
        if subagent:
            folder = os.path.join(path[:-6], "subagents")
            os.makedirs(folder)
            with open(os.path.join(folder, "agent-1.jsonl"), "w", encoding="utf-8") as out:
                for row in subagent:
                    out.write(json.dumps(row) + "\n")

    def write_run(self, state, result_data=None):
        with open(os.path.join(self.run_dir, "state.json"), "w", encoding="utf-8") as out:
            json.dump(state, out)
        if result_data is not None:
            with open(os.path.join(self.run_dir, "result.json"), "w", encoding="utf-8") as out:
                json.dump(result_data, out)

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_metrics.main(["--root", self.root, "--projects-dir", self.projects, *args])
        self.assertEqual(code, 0)
        return out.getvalue()

    def report(self, *args):
        return json.loads(self.run_cli("--slug", SLUG, "--format", "json", *args))

    def test_links_sessions_by_evidence(self):
        data = self.report()
        self.assertEqual([(s["id"], s["role"]) for s in data["sessions"]],
                         [("aaaa1111", "core"), ("bbbb2222", "linked")])
        self.assertEqual([s["id"] for s in data["not_counted"]["measurement"]], ["cccc3333"])
        self.assertEqual([s["id"] for s in data["not_counted"]["adjacent"]], ["dddd4444"])
        self.assertEqual(data["measurement_cost_usd"], 2.0)

    def test_total_is_official_and_include_exclude_work(self):
        self.assertAlmostEqual(self.report()["cost"]["total_usd"], 4.51)
        self.assertAlmostEqual(self.report("--include", "dddd")["cost"]["total_usd"], 4.76)
        self.assertAlmostEqual(self.report("--exclude", "bbbb")["cost"]["total_usd"], 3.51)

    def test_phases_split_the_official_cost(self):
        data = self.report()
        phases = {p["phase"]: p for p in data["phases"]}
        self.assertEqual(set(phases), {"unmarked", "requirements", "tests"})
        self.assertGreater(phases["tests"]["cost_usd"], phases["requirements"]["cost_usd"])
        self.assertEqual(data["cost"]["unattributed_usd"], 0.01)
        attributed = sum(p["cost_usd"] for p in data["phases"]) + data["cost"]["unattributed_usd"]
        self.assertAlmostEqual(attributed, data["cost"]["total_usd"], places=2)

    def test_time_split(self):
        time = self.report()["time"]
        self.assertEqual(time["question_seconds"], 120)
        self.assertEqual(time["tool_seconds"], 120)
        self.assertEqual(time["waiting_seconds"], 120)
        self.assertEqual(time["model_seconds"], 120)
        self.assertEqual(time["wall_seconds"], 21 * 60)
        self.assertLess(time["active_seconds"], time["wall_seconds"])

    def test_outcome_and_savings(self):
        outcome = self.report("--review-hours", "1.5")["outcome"]
        self.assertEqual((outcome["acs_total"], outcome["acs_tested"]), (2, 1))
        self.assertEqual(outcome["findings_by_status"], {"fixed": 2, "wontfix": 1, "deferred": 1})
        self.assertAlmostEqual(outcome["acceptance_rate"], 0.667)
        self.assertEqual((outcome["gates_answered"], outcome["gates_changed"]), (2, 1))
        self.assertEqual(outcome["retries"], {"tests": 2})
        self.assertIsNotNone(outcome["savings_hours"])
        self.assertLess(outcome["savings_hours"], 8.5)
        self.assertIsNone(self.report()["outcome"]["savings_hours"])

    def test_phase_log_adds_real_markers_and_ignores_placeholders(self):
        self.write_run({"phase_log": [{"phase": "fix", "started_at": at(10)},
                                      {"phase": "fake", "started_at": "2026-01-10T00:00:00Z"}]})
        data = self.report()
        names = {p["phase"] for p in data["phases"]}
        self.assertIn("fix", names)
        self.assertNotIn("fake", names)
        self.assertFalse(any("phase_log" in w for w in data["warnings"]))

    def test_missing_cost_state_marks_incomplete(self):
        self.session("ffff6666", [call(21, "f1", tools=[tool("Read", file_path="/x/" + RUN_PATH)])])
        data = self.report()
        self.assertFalse(data["complete"])
        self.assertAlmostEqual(data["cost"]["total_usd"], 4.51)
        self.assertTrue(any("ffff6666" in w for w in data["warnings"]))
        self.assertIn("INCOMPLETE", self.run_cli("--slug", SLUG))

    def test_session_mode_infers_type_from_slash_command(self):
        self.session("gggg7777", [
            prompt(200, "<command-name>/flutter-forge:forge-health</command-name>"),
            call(201, "g1"), cost({OPUS: 0.7})])
        data = json.loads(self.run_cli("--session", "gggg", "--id", "baseline", "--format", "json"))
        self.assertEqual((data["id"], data["run_type"]), ("baseline", "health"))
        self.assertEqual(data["phases"][0]["phase"], "health")

    def test_write_keeps_counters_only_and_upserts_history(self):
        self.run_cli("--slug", SLUG, "--write")
        self.run_cli("--slug", SLUG, "--write", "--review-hours", "1")
        folder = os.path.join(self.root, ".flutter-forge", "metrics")
        with open(os.path.join(folder, ".gitignore"), encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "*\n")
        with open(os.path.join(folder, "history.jsonl"), encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["review_hours"], 1.0)
        for name in (SLUG + ".json", "history.jsonl"):
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn(CANARY, text)
            self.assertNotIn("/app/", text)

    def test_deleted_gitignore_stays_deleted(self):
        self.run_cli("--slug", SLUG, "--write")
        path = os.path.join(self.root, ".flutter-forge", "metrics", ".gitignore")
        os.remove(path)
        self.run_cli("--slug", SLUG, "--write")
        self.assertFalse(os.path.exists(path))

    def test_summary_flags_small_samples(self):
        self.run_cli("--slug", SLUG, "--write")
        summary = json.loads(self.run_cli("--summary", "--format", "json"))
        row = summary["by_type"]["deliver"]
        self.assertEqual(row["cost_usd"]["median"], 4.51)
        self.assertFalse(row["enough_data"])
        self.assertIn("anecdotal", self.run_cli("--summary"))

    def test_list_shows_runs_and_forge_sessions(self):
        data = json.loads(self.run_cli("--list", "--format", "json"))
        self.assertEqual(data["runs"][0]["slug"], SLUG)
        self.assertFalse(data["runs"][0]["measured"])
        self.assertEqual([s["id"] for s in data["recent_forge_sessions"]], ["aaaa1111"])

    def test_degrades_without_transcripts_or_matches(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_metrics.main(["--root", self.root, "--projects-dir", self.root + "/none", "--slug", SLUG])
        self.assertEqual(code, 0)
        self.assertIn("Unavailable", out.getvalue())
        self.assertIn("Unavailable", self.run_cli("--slug", "other-run"))

    def test_rejects_unsafe_names(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            run_metrics.main(["--root", self.root, "--slug", "../../etc"])

    def test_project_folder_encoding(self):
        path = run_metrics.projects_dir_for(self.root)
        self.assertNotIn(".", os.path.basename(path).replace("-", ""))
        self.assertTrue(os.path.basename(path).startswith("-"))


if __name__ == "__main__":
    unittest.main()
