---
type: llm
weight: 2
---

The answer follows the forge-health rules, not a generic cleanup list. It must show all of these.
Items marked "for example" are illustrations of the rule, not separate requirements.
- Security and money items go under "Do now", whatever their change frequency. The leaked token is
  there, handled with "rotate it", and its value is never printed. Rewriting git history is left as a
  human decision. The cleartext transport is in "Do now" or in Quick Wins; either placement is fine as
  long as it is not buried under "later". The order inside "Do now" does not matter.
- The priority is `risk × change frequency ÷ effort` (effort divides). The payment repository and
  `pay_page.dart` rank high because they are hot, risky (money) and untested.
- `lib/core_legacy/old_helpers.dart` (0 commits, ugly, 5 violations) is explicitly left alone or
  scheduled last, with the reason that stable code nobody changes is not worth touching.
- Tests come before refactoring a hot zone: the first step for `pay_page.dart` (310-line `build()`)
  or the payments repository is characterization tests, and a refactor and a feature never share a change.
- Quick Wins (small effort, for example the `any` constraints) are separated from Big Bets
  (large effort, for example splitting `pay_page.dart`), and each Big Bet has a first reversible step.
  The state-manager convergence may be a Big Bet or a human decision, either is acceptable.
- The migration path is incremental, in phases that each end in something shippable. It does not propose a rewrite.
- The mode is not decided silently. The answer treats adopt, improve or migrate as a human decision, recommends one with
  evidence from the digest, and says the analysis is against an assumed preset because there is no profile.
- A "Decisions that need a human" section lists at least: the mode, which state manager wins (bloc versus provider),
  the security items (accepting or fixing, secret rotation), and anything about payment rules. It marks risk levels or
  says why each is a human call.
- It notes the limits: at least that `pub outdated` was not run and that a clean scanner would not prove safety.
  Anything else about what was not measured (coverage, git history) is a bonus.
