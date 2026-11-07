---
skill: forge-presentation
mode: extend
---

## Rules
- **Feedback states use the shared `EmptyView` / `ErrorView`** from `lib/core/widgets/feedback/`.
  Never build ad-hoc empty or error layouts in a feature.
  ```dart
  TransactionsFailure(:final failure) => ErrorView(
      message: failure.message(l10n),
      retryLabel: l10n.commonRetry,
      onRetry: context.read<TransactionsCubit>().load,
    ),
  ```
  Audit: medium when a feature renders its own empty/error layout. (learned 2026-11-06, source: demo conventions)

- **Load-more failures render `ErrorView(compact: true)` as the last list item**, keeping loaded items visible.
  Audit: medium. (learned 2026-11-06)
