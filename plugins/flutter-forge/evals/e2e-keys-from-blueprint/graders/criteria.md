---
type: llm
weight: 2
---

The answer follows the test-key convention:
- Finders come from the `TransferKeys` constants (`$(TransferKeys.amount)`, `$(TransferKeys.item(id))`), not invented symbols like `$(#transfer_amount)`.
- For "Cancelar" it does **not** edit production code: it falls back to the next finder (screen type, ARB text, icon) and reports the missing key (element, screen, suggested constant) so forge-presentation adds it.
- It says the E2E phase leaves `lib/` untouched, and it declines the shortcut of adding the key in the page.
