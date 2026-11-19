# Code comments policy

Base rule: **the code says *what*; a comment says *why*.** Comments are in English. Before
writing a comment, try to **rename or extract** first. A good name removes most comments.

**Sources:** *Effective Dart: Documentation* (dart.dev/effective-dart/documentation, verified
2026-11-19) for `///`, the one-sentence summary, the blank line and `[references]`. The Flutter
style guide is also followed in spirit but **not yet verified** against its text (BIT-011).

**Why English:** identifiers, the Dart/Flutter ecosystem, dartdoc output and the plugin's own
rules are in English, so mixed-language code is avoided and any contributor can read it. A
project overlay may choose otherwise (see Adopt mode).

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

## Writing a `///` comment

1. One-sentence summary, user-centric, ending in a period. A fragment is fine.
2. A blank `///` line, then detail only if needed (guarantees, failures, units).
3. Link identifiers with `[Name]` or `[Class.member]`; do not repeat the signature.
4. Write it for public API: domain contracts, entities, use cases and shared widgets.

| Layer | ✅ Good | ❌ Bad |
|---|---|---|
| Domain | `/// Loads the account's transactions, newest first.`<br>`///`<br>`/// Fails with [NetworkFailure] offline. Amounts are in cents (UTC dates).` | `/// Gets transactions.` |
| Shared widget | `/// A card summarising one account's balance.`<br>`///`<br>`/// Use in lists; for a single hero balance use [BalanceHeader].` | `/// AccountCard widget` |
| Data | `// amount is num: the backend sends 12 and 12.5 (contract §3.2)` | `// the amount` |
| Presentation | `// HU-12 §5: skeleton only after 250 ms (no flicker)` | `// show the loading spinner` |

`///` is checked by `check_comments.py` in `domain/` and, with `--shared-widgets`, in
`paths.shared_widgets`. To require it everywhere, enable the analyzer lint
`public_member_api_docs` (profile: `quality.public_member_api_docs: true`).

## Adopt mode

In existing projects, don't rewrite existing comments to this policy. Apply it to new and
changed code only. When the project's overlay sets a different rule (e.g. Spanish comments),
the overlay wins.
