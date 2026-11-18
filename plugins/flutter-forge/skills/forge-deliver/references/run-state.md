# `state.json` (run state)

```json
{
  "schema": 1,
  "slug": "new-transfer",
  "feature": "Nueva transferencia entre cuentas propias",
  "mode": "interactive",
  "phases": ["requirements", "design", "contract", "blueprint", "data", "presentation", "l10n", "tests", "e2e", "review", "fix", "report"],
  "completed": ["requirements", "contract"],
  "next_phase": "blueprint",
  "status": "in-progress",
  "started_at": "2026-11-06T18:20:00Z",
  "updated_at": "2026-11-06T19:05:00Z",
  "baseline_estimate_hours": 16,
  "phase_log": [
    {"phase": "requirements", "started_at": "2026-11-06T18:20:04Z"},
    {"phase": "contract", "started_at": "2026-11-06T18:42:31Z"}
  ],
  "retries": {"tests": 0, "e2e": 0},
  "sources": {
    "story": "docs/stories/HU-12-transfer.md",
    "figma": "https://www.figma.com/design/<file>?node-id=12-345",
    "api": "api/forge_demo.postman_collection.json"
  },
  "gates": {
    "brief": {"status": "approved", "at": "2026-11-06T18:40:12Z", "changed": true, "notes": "G-2 deferred"},
    "blueprint": {"status": "pending"},
    "findings": {"status": "pending"}
  },
  "gaps": {"blocking": 0, "non_blocking": 1},
  "files": {"created": [], "modified": []},
  "mocked_routes": [],
  "tests": {"unit": null, "widget": null, "e2e": null, "coverage": null},
  "review": {"independent": null, "verdict": null, "counts": {}}
}
```

`status` is one of:
- `in-progress`;
- `blocked` (the gate is waiting for answers);
- `failing-tests`;
- `completed`;
- `completed-with-gaps`.

Every phase rewrites the file atomically: write to `state.json.tmp`, then rename it.

## Facts for `forge-metrics`

These optional fields record what cannot be recovered after the run:

- **Timestamps** (`started_at`, `updated_at`, `gates.*.at`, `phase_log[].started_at`) come from
  `date -u +%Y-%m-%dT%H:%M:%SZ`, run at that moment. You have no clock, so never write a time from
  memory or a placeholder such as `00:00:00Z`.
- `phase_log`: append one entry when a phase starts, including a resumed one.
- `gates.*.changed`: `true` when the person's answer changed the brief, the blueprint or the list
  of findings to fix; `false` when they approved it as proposed.
- `retries`: the fix-and-re-run cycles spent on failing unit/widget tests and on E2E.
- `baseline_estimate_hours`: the estimate for doing the work without the agent, given before the
  run. Omit it when nobody gave one; never infer it.
