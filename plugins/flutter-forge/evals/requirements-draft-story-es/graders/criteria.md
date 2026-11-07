---
type: llm
weight: 2
---

The response follows the flutter-forge requirements workflow:
- It drafts a user story with an "As / I want / so that" statement and acceptance criteria in Given/When/Then form with ids (AC-1, AC-2…), including the 10-peso minimum with its exact error behavior.
- It lists screen states for the transfer screen (at least loading, error with retry, validation, success) and treats the fee preview as its own region.
- It does NOT invent business numbers that were not given (maximum amount, fee value, daily limit): those appear as [TBD]/gaps or questions.
- It ends with a single grouped list of questions/gaps (at most about five), marking which are blocking.
- It is written in Spanish.
