# Code comments policy

Base rule: **the code says *what*; a comment says *why*.** Comments are in English. Before
writing a comment, try to **rename or extract** first. A good name removes most comments.

| ✅ Comment | ❌ Don't comment |
|---|---|
| A non-obvious business rule, with its reference: `// AC-4 (HU-12): transfers over 50,000 need re-auth` | What the code already says: `// increment counter`, `// returns the user` |
| A workaround or third-party bug, with a link to the issue | Commented-out code (delete it; git keeps it) |
| A counter-intuitive security or performance decision | Change history or authorship (that is git) |
| Regular expressions, formulas and algorithms | Banners and decorative separators (`// ===== DATA =====`) |
| Public API of packages and domain contracts: `///` dartdoc on repository contracts, entities, use cases and shared widgets | Every private method or trivial getter |
| `TODO(#123): …` or `TODO(HU-12 G-2): …`, always with an issue or gap id | `TODO` / `FIXME` without an owner or reference |
| A link to the ADR when the code follows an architecture decision | Long explanations that belong in an ADR or a doc |

## Where it applies in a feature

| Layer | Expected comments |
|---|---|
| Domain | `///` on repository contracts, entities and use cases: what the method guarantees, its failure cases (`AppFailure` types) and its units (cents, UTC). Rule references `// R-1 (HU-12): …` on validators |
| Data | Why a DTO field is nullable or `num` when the contract is surprising; envelope or pagination quirks of the backend, with the contract reference |
| Presentation | Why a non-functional rule exists (`// HU-12 §5: no loading flicker → show skeleton after 250 ms`); nothing on widget trees |
| Tests | Test names carry the intent (`AC-3: …`), so comments in tests are rare |
| Generated code | Never edited, never commented |

## Adopt mode

In existing projects, don't rewrite existing comments to this policy. Apply it to new and
changed code only. When the project's overlay sets a different rule (e.g. Spanish comments),
the overlay wins.
