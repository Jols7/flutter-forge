# API contract — Forge Demo API

Source format: `postman-v2.1` · Endpoints: 5
Variables referenced (names only; values live in environments): `access_token`, `base_url`, `demo_password`

## POST `auth/login` — Login
folder: Auth · auth: noauth (inherited) · headers: Content-Type
> Exchanges credentials for an access token.
Request body (json) → test/fixtures/auth/login_request.json:
  root: object
    email: string
    password: string
Response 200 "OK" → test/fixtures/auth/login_200.json:
  root: object
    access_token: string
    expires_in: int
    user: object
      id: string
      name: string
Response 401 "Invalid credentials" → test/fixtures/auth/login_401.json:
  root: object
    code: string
    message: string

## GET `accounts` — List accounts
folder: Accounts · auth: bearer (inherited)
> Accounts owned by the authenticated user.
Response 200 "OK" → test/fixtures/accounts/list_accounts_200.json:
  root: object
    data: list<object>
      id: string
      alias: string?
      number_masked: string
      currency: string
      balance: num  [int and double seen]
      type: string

## GET `accounts/{accountId}/transactions` — List transactions
folder: Accounts · auth: bearer (inherited)
> Paginated movements of one account, newest first.
Path params: accountId
Query: page=1, size=20
Response 200 "OK", "Empty" → test/fixtures/accounts/list_transactions_200.json, test/fixtures/accounts/list_transactions_200_empty.json:
  root: object
    data: list<object>
      id: string
      description: string?
      amount: num  [int and double seen]
      currency: string
      booked_at: string (date-time)
      category: string?
    next_page: int?
Response 404 "Not found" → test/fixtures/accounts/list_transactions_404.json:
  root: object
    code: string
    message: string

## GET `transfers/preview` — Preview transfer
folder: Transfers · auth: bearer (inherited)
Query: from=acc_1, to=acc_2, amount=500
Response 200 "OK" → test/fixtures/transfers/preview_transfer_200.json:
  root: object
    fee: int
    exchange_rate: double
    amount_received: double
    total_debited: int

## POST `transfers` — Create transfer
folder: Transfers · auth: bearer (inherited) · headers: Content-Type, Idempotency-Key
Request body (json) → test/fixtures/transfers/create_transfer_request.json:
  root: object
    from_account_id: string
    to_account_id: string
    amount: int
    concept: string
Response 201 "Created" → test/fixtures/transfers/create_transfer_201.json:
  root: object
    id: string
    status: string
    reference: string
    created_at: string (date-time)
Response 422 "Validation error" → test/fixtures/transfers/create_transfer_422.json:
  root: object
    code: string
    message: string
    errors: object
      amount: list<string>
Response 409 "Insufficient funds" → test/fixtures/transfers/create_transfer_409.json:
  root: object
    code: string
    message: string

## Contract gaps
- GET accounts: no error example (4xx/5xx shape unknown)
- GET transfers/preview: no error example (4xx/5xx shape unknown)
