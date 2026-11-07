---
type: llm
weight: 2
---

The answer matches the flutter-forge clean preset:
- Entity and repository contract in `features/payments/domain/`, implementation, DTO, mapper and remote data source in `features/payments/data/`, cubit/state and page in `features/payments/presentation/`.
- Dependency rule: presentation → domain ← data; presentation must not import data (DTOs never cross the repository); domain has no Flutter/Dio/JSON dependencies.
- Repositories return a typed Result (success/failure) instead of throwing strings.
- On the use-case question: it says a pass-through "get payments" use case is NOT needed unless it combines repositories, holds a business rule or is reused (use cases must be earned).
