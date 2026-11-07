# HU-01 · Transferencia entre cuentas propias

> Sample input for a `forge-deliver` run. Written in the default template; some values are
> intentionally left as `[TBD]` so the run has to surface them as gaps.

| Field | Value |
|---|---|
| Module / epic | Movimientos de dinero |
| Platform | App (mobile) |
| Priority | must |
| Status | Draft — pending approval |
| Design | none yet |

## 1. Story and purpose
**As** a customer with two or more accounts, **I want** to move money between my own accounts,
**so that** I can fund my savings without leaving the app.

Objective: reduce support requests about internal transfers.

INVEST check: Independent ✓ · Negotiable ✓ · Valuable ✓ · Estimable ✓ · Small ✓ · Testable ✓

## 2. Use cases
- **Happy path:** 1. On "Mis cuentas", open an account. 2. Tap "Transferir". 3. Pick the destination
  account. 4. Type the amount; a preview shows fee, exchange rate (if currencies differ) and the
  amount received. 5. Confirm. 6. A receipt with the reference is shown.
- **Alternative paths:** destination in another currency → preview shows the exchange rate.
- **Contingencies:** no connection · session expired · insufficient funds · validation error.

## 3. Business rules and validations
| # | Rule | Value | Source | Message shown |
|---|---|---|---|---|
| R-1 | Minimum amount | 10.00 in the origin currency | Business | "Ingresa un monto mayor a $10.00" |
| R-2 | Maximum per transfer | [TBD] | Business | [TBD] |
| R-3 | Origin and destination must differ | — | Business | (destination list excludes the origin) |
| R-4 | Amount cannot exceed the available balance | balance of origin | Backend (409 INSUFFICIENT_FUNDS) | "Saldo insuficiente" |

Permissions and roles: account owner only.
Traceability: backend issues a receipt reference; the app shows it.

## 4. Acceptance criteria
- **AC-1** — Given I am on an account's movements, when I tap "Transferir", then the transfer form opens with that account as origin.
- **AC-2** — Given the form, when I type an amount below 10.00, then the amount field shows "Ingresa un monto mayor a $10.00" and "Confirmar" is disabled.
- **AC-3** — Given a valid amount and destination, when I stop typing for 300 ms, then a preview shows fee, amount received and total debited.
- **AC-4** — Given a valid form, when I confirm and the backend accepts it, then a receipt with the reference is shown.
- **AC-5 (edge)** — Given the backend answers INSUFFICIENT_FUNDS, then the amount field shows "Saldo insuficiente" and the form keeps my input.
- **AC-6 (edge)** — Given I tap "Confirmar" twice quickly, then only one transfer is created.

## 5. Screens, navigation and states
| Screen | Entry from | Exit to | States |
|---|---|---|---|
| Nueva transferencia | Movimientos → "Transferir" (only if the user has ≥ 2 accounts) | Comprobante (receipt) | loading accounts · validation · preview loading/ready/error(retry) · submitting · error |
| Comprobante | after success | back to Movimientos (refreshed) | success |

- Live validation: amount, on every keystroke.
- Blocking vs interactive: only the preview card reacts to the network; inputs stay interactive.
- Premature exit: no confirmation dialog.
- Non-functional: no loading flicker (show the preview skeleton only after 250 ms).

## 6. Design references
None yet — use the shared widgets and the theme.

## 7. Data and integration (to be confirmed by backend)
| Shown / sent | Needed from | Known endpoint |
|---|---|---|
| Own accounts | backend | GET accounts |
| Preview | backend | GET transfers/preview |
| Create | backend | POST transfers (Idempotency-Key) |

## 8. Security and privacy
- Sensitive data: financial → account numbers always masked ("•••• 4821").
- Never logged: amounts with account ids, idempotency keys.
- Re-authentication before confirming: [TBD — biometrics required?]
- Limits and retries: preview retry unlimited; submit is never retried automatically.
- Screenshots: blocked on the receipt screen ([TBD — confirm with compliance]).

## 9. Out of scope
- Transfers to third parties; scheduled transfers.

## 10. Open questions
- [ ] Q-1 Maximum amount per transfer (R-2)?
- [ ] Q-2 Is biometric re-authentication required before confirming?
