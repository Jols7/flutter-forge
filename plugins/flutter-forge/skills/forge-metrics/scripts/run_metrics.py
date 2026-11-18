#!/usr/bin/env python3
"""Cost, time and outcome of a finished flutter-forge run, from Claude Code's local transcripts.

Usage:
  run_metrics.py --root PROJECT --slug SLUG [--include ID ...] [--exclude ID ...]
                 [--review-hours H] [--write] [--format text|json]
  run_metrics.py --root PROJECT --session ID [ID ...] [--id NAME] [--write]
  run_metrics.py --root PROJECT --list
  run_metrics.py --root PROJECT --summary

Sessions are linked to a run by the run folder they touched. Totals come from the `cost-state`
record Claude Code writes when a session closes, so no price table is needed; a session without
one has an unknown cost and the result is marked incomplete. Phase costs split those official
totals with relative weights.

The transcript holds code and conversation. This script keeps counters, model names, forge skill
names and timestamps only, and never copies text. The transcript format is not a public contract:
anything unrecognized is skipped and reported. Read-only except for `--write`, which writes under
PROJECT/.flutter-forge/metrics/. No network, Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import glob
import json
import os
import re
import statistics
import sys
import tempfile
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCHEMA = 1
IDLE_CAP_SECONDS = 180
ADJACENT_MARGIN_SECONDS = 600
MIN_SAMPLE = 5
# Relative to one input token. They only split an official total between phases.
WEIGHTS = {"input": 1.0, "output": 5.0, "cache_read": 0.05, "cache_1h": 2.0, "cache_5m": 1.25}
PHASE_BY_SKILL = {
    "forge-profile": "profile",
    "forge-requirements": "requirements",
    "forge-figma": "design",
    "forge-api-contract": "contract",
    "forge-blueprint": "blueprint",
    "forge-data-layer": "data",
    "forge-presentation": "presentation",
    "forge-l10n": "l10n",
    "forge-tests": "tests",
    "forge-e2e": "e2e",
    "forge-audit": "review",
    "forge-security": "review",
    "forge-deliver": "orchestration",
    "forge-health": "health",
}
REVIEW_PHASES = {"review", "audit", "security", "fix", "report"}
NOT_A_PROMPT = ("<task-notification", "<local-command", "<system-reminder", "<bash-")
COMMAND_NAME = re.compile(r"<command-name>/?(?:flutter-forge:)?(forge-[a-z0-9-]+)</command-name>")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
MEASURING = (".claude/projects", "run_metrics.py")
PATH_KEYS = ("file_path", "path", "notebook_path", "command")


def parse_ts(value: Any) -> Optional[dt.datetime]:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def iso(value: Optional[dt.datetime]) -> Optional[str]:
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if value else None


def number(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def projects_dir_for(root: str) -> str:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(base, "projects", re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(root)))


def read_rows(path: str) -> Iterable[Dict]:
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    yield row
    except OSError:
        return


def skill_name(raw: Any) -> Optional[str]:
    if not isinstance(raw, str):
        return None
    plugin, _, name = raw.rpartition(":")
    if plugin not in ("", "flutter-forge") or not name.startswith("forge-"):
        return None
    return name


def call_tokens(usage: Dict) -> Dict[str, float]:
    written = number(usage.get("cache_creation_input_tokens"))
    detail = usage.get("cache_creation") if isinstance(usage.get("cache_creation"), dict) else {}
    five = number(detail.get("ephemeral_5m_input_tokens"))
    hour = number(detail.get("ephemeral_1h_input_tokens"))
    if not five and not hour:
        hour = written
    return {
        "input": number(usage.get("input_tokens")),
        "output": number(usage.get("output_tokens")),
        "cache_read": number(usage.get("cache_read_input_tokens")),
        "cache_1h": hour,
        "cache_5m": five,
    }


def new_session(path: str) -> Dict:
    return {
        "id": os.path.basename(path)[:-len(".jsonl")],
        "calls": {},
        "markers": [],
        "stamps": [],
        "tool_seconds": 0.0,
        "question_seconds": 0.0,
        "waiting_seconds": 0.0,
        "prompts": 0,
        "commands": [],
        "cost_state": None,
        "linked_text": [],
        "measuring": False,
    }


def scan_assistant(session: Dict, row: Dict, when: Optional[dt.datetime], is_sub: bool, pending: Dict) -> None:
    message = row.get("message")
    if not isinstance(message, dict):
        return
    usage, model = message.get("usage"), message.get("model")
    if isinstance(usage, dict) and when and isinstance(model, str) and not model.startswith("<"):
        key = message.get("id") or row.get("uuid") or len(session["calls"])
        session["calls"][key] = {"at": when, "model": model, "tokens": call_tokens(usage), "subagent": is_sub}
    content = message.get("content")
    for block in content if isinstance(content, list) else []:
        if not (isinstance(block, dict) and block.get("type") == "tool_use"):
            continue
        name, data = block.get("name"), block.get("input")
        data = data if isinstance(data, dict) else {}
        if not is_sub and when:
            pending[block.get("id")] = (name, when)
        for key in PATH_KEYS:
            if isinstance(data.get(key), str):
                session["linked_text"].append(data[key])
        command = data.get("command")
        if isinstance(command, str) and any(token in command for token in MEASURING):
            session["measuring"] = True
        if not when:
            continue
        if name == "Skill":
            skill = skill_name(data.get("skill"))
            if skill:
                session["markers"].append((when, skill))
        elif name in ("Agent", "Task") and str(data.get("subagent_type", "")).endswith("flutter-reviewer"):
            session["markers"].append((when, "forge-audit"))


def scan_user(session: Dict, row: Dict, when: Optional[dt.datetime], pending: Dict, last_reply: Optional[dt.datetime]) -> None:
    content = (row.get("message") or {}).get("content") if isinstance(row.get("message"), dict) else None
    texts: List[str] = [content] if isinstance(content, str) else []
    has_result = False
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            texts.append(block["text"])
        elif block.get("type") == "tool_result":
            has_result = True
            started = pending.pop(block.get("tool_use_id"), None)
            if started and when:
                seconds = max(0.0, (when - started[1]).total_seconds())
                if started[0] == "AskUserQuestion":
                    session["question_seconds"] += seconds
                elif started[0] not in ("Agent", "Task"):
                    session["tool_seconds"] += seconds
    if has_result or row.get("isMeta") or row.get("isSidechain") or not when or not texts:
        return
    for text in texts:
        for match in COMMAND_NAME.finditer(text):
            session["markers"].append((when, match.group(1)))
    if texts[0].lstrip().startswith(NOT_A_PROMPT):
        return
    session["prompts"] += 1
    if last_reply:
        session["waiting_seconds"] += max(0.0, (when - last_reply).total_seconds())


def load_session(path: str) -> Dict:
    session = new_session(path)
    pending: Dict[Any, Tuple[Any, dt.datetime]] = {}
    last_reply: Optional[dt.datetime] = None
    for file_path in [path] + sorted(glob.glob(os.path.join(path[:-len(".jsonl")], "subagents", "*.jsonl"))):
        is_sub = file_path != path
        for row in read_rows(file_path):
            kind = row.get("type")
            when = parse_ts(row.get("timestamp"))
            if when:
                session["stamps"].append(when)
            if kind == "cost-state" and not is_sub:
                session["cost_state"] = row
            elif kind == "assistant":
                scan_assistant(session, row, when, is_sub, pending)
                if not is_sub and when:
                    last_reply = when
            elif kind == "user" and not is_sub:
                scan_user(session, row, when, pending, last_reply)
    session["stamps"].sort()
    session["markers"].sort(key=lambda item: item[0])
    return session


def load_sessions(projects_dir: str) -> List[Dict]:
    loaded = [load_session(path) for path in sorted(glob.glob(os.path.join(projects_dir, "*.jsonl")))]
    return sorted([s for s in loaded if s["stamps"]], key=lambda s: s["stamps"][0])


def forge_work(session: Dict) -> List[str]:
    return [name for _, name in session["markers"] if name != "forge-metrics"]


def role_for(session: Dict, slug: str) -> Optional[str]:
    pattern = re.compile(r"\.flutter-forge/runs/" + re.escape(slug) + r"(?![\w.-])")
    if not any(pattern.search(text) for text in session["linked_text"]):
        return None
    if forge_work(session):
        return "core"
    if session["measuring"] or any(name == "forge-metrics" for _, name in session["markers"]):
        return "measurement"
    return "linked"


def matches(session: Dict, prefixes: List[str]) -> bool:
    return any(session["id"].startswith(prefix) for prefix in prefixes)


def session_cost(session: Dict) -> Optional[float]:
    state = session["cost_state"]
    return round(number(state.get("totalCostUSD")), 6) if state else None


def brief_session(session: Dict, role: str) -> Dict:
    return {
        "id": session["id"][:8],
        "role": role,
        "started_at": iso(session["stamps"][0]),
        "ended_at": iso(session["stamps"][-1]),
        "calls": len(session["calls"]),
        "cost_usd": session_cost(session),
        "forge_skills": sorted(set(forge_work(session))),
    }


def select_by_slug(sessions: List[Dict], slug: str, include: List[str], exclude: List[str]) -> Tuple[List[Tuple[Dict, str]], Dict[str, List[Dict]]]:
    chosen: List[Tuple[Dict, str]] = []
    left: Dict[str, List[Dict]] = {"measurement": [], "manual": [], "adjacent": []}
    rest: List[Dict] = []
    for session in sessions:
        role = role_for(session, slug)
        if matches(session, exclude):
            left["manual"].append(brief_session(session, role or "unlinked"))
        elif matches(session, include):
            chosen.append((session, "included"))
        elif role in ("core", "linked"):
            chosen.append((session, role))
        elif role == "measurement":
            left["measurement"].append(brief_session(session, role))
        else:
            rest.append(session)
    if chosen:
        margin = dt.timedelta(seconds=ADJACENT_MARGIN_SECONDS)
        start = min(s["stamps"][0] for s, _ in chosen) - margin
        end = max(s["stamps"][-1] for s, _ in chosen) + margin
        left["adjacent"] = [brief_session(s, "adjacent") for s in rest if s["stamps"][0] <= end and s["stamps"][-1] >= start]
    return chosen, left


def capped_seconds(stamps: List[dt.datetime]) -> float:
    ordered = sorted(stamps)
    return sum(min((b - a).total_seconds(), IDLE_CAP_SECONDS) for a, b in zip(ordered, ordered[1:]))


def weight(tokens: Dict[str, float]) -> float:
    return sum(tokens[key] * WEIGHTS[key] for key in WEIGHTS)


def phase_markers(session: Dict, phase_log: List[Tuple[dt.datetime, str]]) -> List[Tuple[dt.datetime, str]]:
    own = [(when, PHASE_BY_SKILL.get(name, name)) for when, name in session["markers"] if name != "forge-metrics"]
    return sorted(own + phase_log, key=lambda item: item[0])


def official_models(session: Dict) -> Dict[str, Dict]:
    state = session["cost_state"]
    usage = state.get("modelUsage") if state else None
    return {k: v for k, v in usage.items() if isinstance(v, dict)} if isinstance(usage, dict) else {}


def build_phases(chosen: List[Tuple[Dict, str]], phase_log: List[Tuple[dt.datetime, str]]) -> Tuple[List[Dict], float]:
    buckets: Dict[str, Dict] = defaultdict(lambda: {"calls": 0, "cost": 0.0, "context": 0.0, "stamps": defaultdict(list), "first": None})
    unattributed = 0.0
    for session, _ in chosen:
        markers = phase_markers(session, phase_log)
        times = [when for when, _ in markers]
        calls = sorted(session["calls"].values(), key=lambda call: call["at"])
        totals: Dict[str, float] = defaultdict(float)
        for call in calls:
            totals[call["model"]] += weight(call["tokens"])
        models = official_models(session)
        for model, data in models.items():
            if not totals.get(model):
                unattributed += number(data.get("costUSD"))
        for call in calls:
            index = bisect.bisect_left(times, call["at"]) - 1
            phase = markers[index][1] if index >= 0 else "unmarked"
            bucket = buckets[phase]
            tokens = call["tokens"]
            bucket["calls"] += 1
            bucket["context"] += tokens["input"] + tokens["cache_read"] + tokens["cache_1h"] + tokens["cache_5m"]
            bucket["stamps"][session["id"]].append(call["at"])
            bucket["first"] = min(bucket["first"] or call["at"], call["at"])
            model_total = totals[call["model"]]
            if model_total:
                bucket["cost"] += number(models.get(call["model"], {}).get("costUSD")) * weight(tokens) / model_total
    total = sum(b["cost"] for b in buckets.values()) or 1.0
    rows = [{
        "phase": name,
        "calls": b["calls"],
        "cost_usd": round(b["cost"], 4),
        "cost_share": round(b["cost"] / total, 4),
        "active_seconds": round(sum(capped_seconds(s) for s in b["stamps"].values())),
        "avg_context_tokens": round(b["context"] / b["calls"]) if b["calls"] else 0,
        "first_at": iso(b["first"]),
    } for name, b in buckets.items()]
    return sorted(rows, key=lambda row: row["first_at"] or ""), round(unattributed, 6)


def build_models(chosen: List[Tuple[Dict, str]]) -> Dict[str, Dict]:
    fields = {"input": "inputTokens", "output": "outputTokens", "thinking": "thinkingTokens",
              "cache_read": "cacheReadInputTokens", "cache_write": "cacheCreationInputTokens"}
    result: Dict[str, Dict] = defaultdict(lambda: defaultdict(float))
    for session, _ in chosen:
        models = official_models(session)
        for model, data in models.items():
            result[model]["usd"] += number(data.get("costUSD"))
            for field, source in fields.items():
                result[model][field] += number(data.get(source))
        if not models:
            for call in session["calls"].values():
                tokens = call["tokens"]
                row = result[call["model"]]
                row["input"] += tokens["input"]
                row["output"] += tokens["output"]
                row["cache_read"] += tokens["cache_read"]
                row["cache_write"] += tokens["cache_1h"] + tokens["cache_5m"]
    return {m: {k: round(v, 4) if k == "usd" else int(v) for k, v in row.items()} for m, row in sorted(result.items())}


def read_json(path: str) -> Dict:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def read_phase_log(state: Dict) -> List[Tuple[dt.datetime, str]]:
    log = state.get("phase_log")
    entries = []
    for item in log if isinstance(log, list) else []:
        when = parse_ts(item.get("started_at")) if isinstance(item, dict) else None
        if when and when.time() != dt.time(0, 0, 0) and isinstance(item.get("phase"), str):
            entries.append((when, item["phase"]))
    return entries


def build_outcome(state: Dict, result: Dict, active_seconds: float, review_hours: Optional[float], total_cost: Optional[float]) -> Dict:
    criteria = [c for c in result.get("acceptance_criteria") or [] if isinstance(c, dict)]
    tested = sum(1 for c in criteria if c.get("status") == "implemented-tested")
    review = result.get("review") if isinstance(result.get("review"), dict) else {}
    by_status: Dict[str, int] = defaultdict(int)
    for finding in review.get("findings") or []:
        if isinstance(finding, dict):
            by_status[str(finding.get("status", "open"))] += 1
    fixed = by_status.get("fixed", 0)
    decided = fixed + by_status.get("wontfix", 0)
    gates = state.get("gates") if isinstance(state.get("gates"), dict) else {}
    answered = [g for g in gates.values() if isinstance(g, dict) and g.get("status") not in (None, "pending")]
    recorded = [g for g in answered if isinstance(g.get("changed"), bool)]
    retries = state.get("retries") if isinstance(state.get("retries"), dict) else None
    baseline = state.get("baseline_estimate_hours")
    baseline = float(baseline) if isinstance(baseline, (int, float)) and not isinstance(baseline, bool) else None
    savings = None
    if baseline is not None and review_hours is not None:
        savings = round(baseline - active_seconds / 3600 - review_hours, 2)
    return {
        "status": result.get("status") or state.get("status"),
        "acs_total": len(criteria),
        "acs_tested": tested,
        "cost_per_ac_usd": round(total_cost / len(criteria), 2) if criteria and total_cost is not None else None,
        "review_verdict": review.get("verdict"),
        "findings_by_status": dict(by_status),
        "acceptance_rate": round(fixed / decided, 3) if decided else None,
        "gates_answered": len(answered),
        "gates_changed": sum(1 for g in recorded if g["changed"]) if recorded else None,
        "retries": retries,
        "baseline_estimate_hours": baseline,
        "review_hours": review_hours,
        "savings_hours": savings,
    }


def infer_type(state: Dict, chosen: List[Tuple[Dict, str]], slug: Optional[str]) -> str:
    skills = {name for session, _ in chosen for name in forge_work(session)}
    if slug:
        phases = set(state.get("phases") or [])
        return "review" if phases and phases <= REVIEW_PHASES else "deliver"
    if "forge-health" in skills:
        return "health"
    if "forge-deliver" in skills:
        return "deliver"
    if skills and skills <= {"forge-audit", "forge-security"}:
        return "review"
    return "skill"


def build_report(run_id: str, chosen: List[Tuple[Dict, str]], left: Dict[str, List[Dict]], root: str, slug: Optional[str], review_hours: Optional[float]) -> Dict:
    run_dir = os.path.join(root, ".flutter-forge", "runs", slug) if slug else ""
    state = read_json(os.path.join(run_dir, "state.json")) if slug else {}
    result = read_json(os.path.join(run_dir, "result.json")) if slug else {}
    phase_log = read_phase_log(state)
    sessions = [session for session, _ in chosen]
    stamps = [when for session in sessions for when in session["stamps"]]
    missing = [s["id"][:8] for s in sessions if not s["cost_state"]]
    known = [session_cost(s) for s in sessions if s["cost_state"]]
    total = round(sum(known), 4) if known else None
    active = capped_seconds(stamps)
    phases, unattributed = build_phases(chosen, phase_log)
    warnings = []
    if missing:
        warnings.append("no cost-state (session open or closed abnormally): %s; cost is partial" % ", ".join(missing))
    if slug and not phase_log:
        warnings.append("no phase_log in state.json: fix and report are counted inside review")
    if slug and not result:
        warnings.append("result.json missing or unreadable: outcome is partial")
    if left["adjacent"]:
        warnings.append("%d adjacent session(s) not counted; add with --include if they were part of the run" % len(left["adjacent"]))
    api = [number(s["cost_state"].get("totalAPIDuration")) / 1000 for s in sessions if s["cost_state"]]
    return {
        "schema": SCHEMA,
        "id": run_id,
        "slug": slug,
        "run_type": infer_type(state, chosen, slug),
        "generated_at": iso(dt.datetime.now(dt.timezone.utc)),
        "complete": not missing and bool(sessions),
        "warnings": warnings,
        "sessions": [brief_session(session, role) for session, role in chosen],
        "not_counted": left,
        "measurement_cost_usd": round(sum(s["cost_usd"] or 0 for s in left["measurement"]), 4),
        "cost": {"total_usd": total, "source": "cost-state", "unattributed_usd": unattributed, "by_model": build_models(chosen)},
        "time": {
            "started_at": iso(min(stamps)) if stamps else None,
            "ended_at": iso(max(stamps)) if stamps else None,
            "wall_seconds": round((max(stamps) - min(stamps)).total_seconds()) if stamps else 0,
            "active_seconds": round(active),
            "model_seconds": round(sum(api)) if api else None,
            "tool_seconds": round(sum(s["tool_seconds"] for s in sessions)),
            "question_seconds": round(sum(s["question_seconds"] for s in sessions)),
            "waiting_seconds": round(sum(s["waiting_seconds"] for s in sessions)),
        },
        "calls": sum(len(s["calls"]) for s in sessions),
        "prompts": sum(s["prompts"] for s in sessions),
        "phases": phases,
        "outcome": build_outcome(state, result, active, review_hours, total),
    }


def minutes(seconds: Optional[float]) -> str:
    return "n/a" if seconds is None else "%.1f min" % (seconds / 60)


def money(value: Optional[float]) -> str:
    return "n/a" if value is None else "$%.2f" % value


def render(report: Dict) -> str:
    time, cost, outcome = report["time"], report["cost"], report["outcome"]
    lines = ["Run %s · type %s · %s" % (report["id"], report["run_type"], "complete" if report["complete"] else "INCOMPLETE"),
             "Cost %s at API prices (not a bill) · %d calls · %d prompts" % (money(cost["total_usd"]), report["calls"], report["prompts"]),
             "Time: wall %s · active %s · model %s · tools %s · questions %s · waiting %s" % (
                 minutes(time["wall_seconds"]), minutes(time["active_seconds"]), minutes(time["model_seconds"]),
                 minutes(time["tool_seconds"]), minutes(time["question_seconds"]), minutes(time["waiting_seconds"])),
             "", "Models:"]
    for model, row in cost["by_model"].items():
        lines.append("  %-22s %8s  out %d  cache read %d  cache write %d" % (model, money(row.get("usd")), row.get("output", 0), row.get("cache_read", 0), row.get("cache_write", 0)))
    lines += ["", "Phases (estimated split of the official total):"]
    for row in report["phases"]:
        lines.append("  %-14s %7s %5.1f%%  %3d calls  %8s  avg context %dK" % (
            row["phase"], money(row["cost_usd"]), row["cost_share"] * 100, row["calls"], minutes(row["active_seconds"]), row["avg_context_tokens"] / 1000))
    lines += ["", "Sessions counted:"]
    for row in report["sessions"]:
        lines.append("  %s %-8s %s  %3d calls  %s" % (row["id"], row["role"], (row["started_at"] or "")[11:16], row["calls"], money(row["cost_usd"])))
    for group, rows in report["not_counted"].items():
        if rows:
            lines.append("Not counted (%s): %s" % (group, ", ".join("%s %s" % (r["id"], money(r["cost_usd"])) for r in rows)))
    lines += ["", "Outcome: status %s · ACs %d/%d tested · cost per AC %s · verdict %s" % (
        outcome["status"], outcome["acs_tested"], outcome["acs_total"], money(outcome["cost_per_ac_usd"]), outcome["review_verdict"]),
        "Findings %s · acceptance %s · gates answered %d, changed %s · retries %s" % (
            outcome["findings_by_status"] or "{}", outcome["acceptance_rate"], outcome["gates_answered"], outcome["gates_changed"], outcome["retries"]),
        "Savings: %s (baseline %s h, review %s h)" % (
            "%s h" % outcome["savings_hours"] if outcome["savings_hours"] is not None else "not computable",
            outcome["baseline_estimate_hours"], outcome["review_hours"])]
    if report["warnings"]:
        lines += ["", "Warnings:"] + ["  - " + w for w in report["warnings"]]
    return "\n".join(lines)


def atomic_write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    with os.fdopen(handle, "w", encoding="utf-8") as out:
        out.write(text)
    os.replace(temp, path)


def history_row(report: Dict) -> Dict:
    time, outcome = report["time"], report["outcome"]
    return {
        "id": report["id"], "run_type": report["run_type"], "generated_at": report["generated_at"],
        "complete": report["complete"], "cost_usd": report["cost"]["total_usd"],
        "active_minutes": round(time["active_seconds"] / 60, 1),
        "model_minutes": round(time["model_seconds"] / 60, 1) if time["model_seconds"] is not None else None,
        "wall_minutes": round(time["wall_seconds"] / 60, 1), "calls": report["calls"],
        "acs_total": outcome["acs_total"], "acs_tested": outcome["acs_tested"],
        "cost_per_ac_usd": outcome["cost_per_ac_usd"], "findings_by_status": outcome["findings_by_status"],
        "acceptance_rate": outcome["acceptance_rate"], "gates_changed": outcome["gates_changed"],
        "baseline_estimate_hours": outcome["baseline_estimate_hours"],
        "review_hours": outcome["review_hours"], "savings_hours": outcome["savings_hours"],
    }


def read_history(path: str) -> List[Dict]:
    return [row for row in read_rows(path) if row.get("id")]


def write_outputs(root: str, report: Dict) -> str:
    folder = os.path.join(root, ".flutter-forge", "metrics")
    if not os.path.isdir(folder):
        atomic_write(os.path.join(folder, ".gitignore"), "*\n")
    target = os.path.join(folder, report["id"] + ".json")
    atomic_write(target, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    history = os.path.join(folder, "history.jsonl")
    rows = [row for row in read_history(history) if row["id"] != report["id"]] + [history_row(report)]
    atomic_write(history, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    return target


def spread(values: List[float]) -> Optional[Dict]:
    if not values:
        return None
    return {"median": round(statistics.median(values), 2), "min": round(min(values), 2), "max": round(max(values), 2)}


def summarize(root: str) -> Dict:
    rows = read_history(os.path.join(root, ".flutter-forge", "metrics", "history.jsonl"))
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("run_type"))].append(row)
    result = {}
    for run_type, items in sorted(groups.items()):
        complete = [r for r in items if r.get("complete")]
        pick = lambda key, source: [r[key] for r in source if isinstance(r.get(key), (int, float))]
        result[run_type] = {
            "runs": len(items), "complete_runs": len(complete), "enough_data": len(complete) >= MIN_SAMPLE,
            "cost_usd": spread(pick("cost_usd", complete)), "active_minutes": spread(pick("active_minutes", items)),
            "model_minutes": spread(pick("model_minutes", complete)), "cost_per_ac_usd": spread(pick("cost_per_ac_usd", complete)),
            "acceptance_rate": spread(pick("acceptance_rate", items)), "savings_hours": spread(pick("savings_hours", items)),
        }
    return {"min_sample": MIN_SAMPLE, "by_type": result}


def render_summary(summary: Dict) -> str:
    if not summary["by_type"]:
        return "No measured runs yet (.flutter-forge/metrics/history.jsonl is empty or missing)."
    lines = []
    for run_type, row in summary["by_type"].items():
        note = "" if row["enough_data"] else " · fewer than %d complete runs: anecdotal" % summary["min_sample"]
        lines.append("%s: %d runs (%d complete)%s" % (run_type, row["runs"], row["complete_runs"], note))
        for key in ("cost_usd", "active_minutes", "model_minutes", "cost_per_ac_usd", "acceptance_rate", "savings_hours"):
            if row[key]:
                lines.append("  %-16s median %s  range %s to %s" % (key, row[key]["median"], row[key]["min"], row[key]["max"]))
    return "\n".join(lines)


def list_targets(root: str, sessions: List[Dict]) -> Dict:
    runs_dir = os.path.join(root, ".flutter-forge", "runs")
    metrics_dir = os.path.join(root, ".flutter-forge", "metrics")
    runs = []
    for slug in sorted(os.listdir(runs_dir)) if os.path.isdir(runs_dir) else []:
        if os.path.isfile(os.path.join(runs_dir, slug, "state.json")):
            runs.append({"slug": slug, "status": read_json(os.path.join(runs_dir, slug, "state.json")).get("status"),
                         "measured": os.path.isfile(os.path.join(metrics_dir, slug + ".json"))})
    recent = [brief_session(s, "forge") for s in sessions if forge_work(s)][-20:]
    return {"runs": runs, "recent_forge_sessions": recent}


def render_list(data: Dict) -> str:
    lines = ["Runs:"] + ["  %s · %s · %s" % (r["slug"], r["status"], "measured" if r["measured"] else "not measured") for r in data["runs"]]
    lines += ["Recent sessions with forge skills:"]
    lines += ["  %s %s %s %s" % (r["id"], (r["started_at"] or "")[:16], money(r["cost_usd"]), ",".join(r["forge_skills"])) for r in data["recent_forge_sessions"]]
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".")
    parser.add_argument("--projects-dir", help="transcript folder; detected from --root by default")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--slug")
    target.add_argument("--session", nargs="+", metavar="ID")
    target.add_argument("--list", action="store_true")
    target.add_argument("--summary", action="store_true")
    parser.add_argument("--id", help="name for a --session measurement")
    parser.add_argument("--include", nargs="*", default=[], metavar="ID")
    parser.add_argument("--exclude", nargs="*", default=[], metavar="ID")
    parser.add_argument("--review-hours", type=float, help="human review and rework time, in hours")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    for name in (args.slug, args.id):
        if name and not SLUG_RE.match(name):
            parser.error("invalid run name: %s" % name)
    if args.review_hours is not None and args.review_hours < 0:
        parser.error("--review-hours cannot be negative")
    return args


def emit(data: Dict, text: str, fmt: str) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False) if fmt == "json" else text)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    root = os.path.abspath(args.root)
    if args.summary:
        summary = summarize(root)
        emit(summary, render_summary(summary), args.format)
        return 0
    projects_dir = args.projects_dir or projects_dir_for(root)
    if not os.path.isdir(projects_dir):
        reason = "no Claude Code transcripts for this project; pass --projects-dir"
        emit({"available": False, "reason": reason}, "Unavailable: " + reason, args.format)
        return 0
    sessions = load_sessions(projects_dir)
    if args.list:
        data = list_targets(root, sessions)
        emit(data, render_list(data), args.format)
        return 0
    left: Dict[str, List[Dict]] = {"measurement": [], "manual": [], "adjacent": []}
    if args.slug:
        chosen, left = select_by_slug(sessions, args.slug, args.include, args.exclude)
        run_id = args.slug
    else:
        chosen = [(s, "included") for s in sessions if matches(s, args.session)]
        run_id = args.id or "session-" + args.session[0][:8]
    if not chosen:
        reason = "no session matches this run"
        emit({"available": False, "reason": reason, "not_counted": left}, "Unavailable: " + reason, args.format)
        return 0
    report = build_report(run_id, chosen, left, root, args.slug, args.review_hours)
    if args.write:
        report["written_to"] = os.path.relpath(write_outputs(root, report), root)
    emit(report, render(report), args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
