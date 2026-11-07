# Security policy

## Reporting a vulnerability

Please do **not** open a public issue. Use GitHub's private vulnerability reporting instead
(**Security → Report a vulnerability** on the repository). You will get an answer within 7 days.

## What counts

- A skill or script that leaks secrets, for example by printing Postman environment values or
  writing tokens to files or logs.
- A skill that runs untrusted code or downloads files without asking.
- An eval or example that contains real credentials, hosts or personal data.
- Generated code patterns that introduce a vulnerability in the apps that use them.

## Design commitments

- Scripts use the Python standard library only. They never send data over the network and
  never print variable values from Postman environments.
- The agent never writes credentials. Test credentials live in a gitignored file that a person
  creates.
- E2E tests refuse to run against flavors listed in `testing.forbidden_flavors`. The default is
  `prod`.
