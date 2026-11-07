---
type: llm
weight: 2
---

The review applies the flutter-forge comments policy ("the code says what; a comment says why"):
- Flags as removable: the decorative banner, the comment that restates the code (`// increment attempts`), the commented-out code (delete it, git keeps it) and the `TODO` without an issue/HU reference (it should be `TODO(#n)` or `TODO(HU-12 …)`).
- Keeps as good: the `AC-4 (HU-12)` business-rule comment with its reference, and the regex/check-digit explanation.
- Flags as missing: a `///` doc comment on the public repository contract `TransfersRepository` / `createTransfer` (what it guarantees and which failures it returns).
- It does not ask to comment every line or private member, and suggests renaming/extracting where that would remove a comment.
