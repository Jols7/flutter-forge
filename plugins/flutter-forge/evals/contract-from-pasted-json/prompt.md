---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Intégralo en la app (solo diseña el contrato y los DTOs, no escribas archivos). El back me pasó dos respuestas de ejemplo de `GET client/accounts/{id}/movements?page=1`:

```json
{"data":[{"id":"m1","amount":1500,"description":"Pago","booked_at":"2026-10-01T10:00:00Z","tag":"rent"}],"next_page":2}
```

```json
{"data":[{"id":"m2","amount":99.5,"description":null,"booked_at":"2026-10-02T11:30:00Z"}],"next_page":null}
```
