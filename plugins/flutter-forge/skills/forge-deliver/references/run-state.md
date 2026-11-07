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
  "sources": {
    "story": "docs/stories/HU-12-transfer.md",
    "figma": "https://www.figma.com/design/<file>?node-id=12-345",
    "api": "api/forge_demo.postman_collection.json"
  },
  "gates": {
    "brief": {"status": "approved", "at": "2026-11-06T18:40:00Z", "notes": "G-2 deferred"},
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
