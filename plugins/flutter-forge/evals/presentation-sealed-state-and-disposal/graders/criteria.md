---
type: llm
weight: 2
---

The review applies the forge-presentation rules:
- Flags the bag of booleans (`isLoading`, `hasError`, `error`, `data`) and asks for a sealed state (loading / empty / error / success) with an exhaustive switch in the UI.
- Flags that `emit` runs after an `await` with no `isClosed` check.
- Flags `getIt<…>()` inside the state manager: dependencies come through the constructor.
- Flags `S.current` inside the state manager: it should expose a failure and let the widget map it to text.
- Does **not** raise accessibility or semantics findings (the `a11y` switch is off by default).
