# Contract sources — commands and rules

## 1. Collection file in the repo

| Kind | How to recognize it | Command |
|---|---|---|
| Postman v2.1 export | `*.postman_collection.json` with `info.schema` …`v2.1.0` | `postman_to_contract.py <file> --list` |
| Postman v3 git-native | `postman/collections/<name>/` with `*.request.yaml` files | `postman_to_contract.py "postman/collections/<name>" --list` |
| Postman API envelope | JSON with top-level `collection` | handled automatically |

v3 YAML is parsed with a built-in subset parser. If a file uses YAML features beyond that
subset (anchors, tags), read those requests directly and fill the contract by hand.

## 2. Postman cloud (CLI or MCP)

The CLI path comes from `api.postman_cli`. It is commonly not on `PATH`, so use the absolute path.

```bash
<postman> whoami                                   # is there a session? If not: ask the person to run `postman login`
<postman> collection list --workspace <workspace-id> --json
<postman> collection get <collection-uid> --json > <scratchpad>/collection.json
python3 <skill>/scripts/postman_to_contract.py <scratchpad>/collection.json --list
```

- Store the workspace id and collection uid (identifiers, not secrets) in the profile under
  `api.sources` so later runs skip discovery.
- Never `environment get`, and never print variable values. Base URLs come from the app's
  configuration (`--dart-define` / flavor config), not from Postman.
- **Postman MCP** (when connected): use its collection and request read tools in the same
  order (find collection → get requests → get saved responses). Write what you get to a
  scratch JSON file and run the script, so the inference is identical. When the MCP server
  needs authentication, tell the person to authorize it. You cannot do it for them.
- When the API has no saved examples, the Postman docs suggest generating them. Suggest that
  to the backend team instead of inventing responses.

## 3. OpenAPI / Swagger

`postman_to_contract.py openapi.json`. The parser understands `$ref` to `components/schemas`,
`required`, `nullable`, `type: [x, null]`, `allOf`/`oneOf`/`anyOf` (fields merged, flagged),
enums and parameters. For Swagger 2.0 or complex YAML, convert to OpenAPI 3 JSON first,
for example with the backend's tooling, or read the relevant paths by hand.

## 4. Pasted endpoints, JSON or cURL

1. Save every pasted response body to a temporary file and run it through the same inference
   by hand: nullability, int/double, dates.
2. For cURL, extract the method, the path (drop the host), query parameters, headers and body.
   **Never copy `Authorization` or cookie values** into any file.
3. Optionally build a local v3 collection with
   `<postman> collection import "<curl>"` when the team wants the requests versioned.

## 5. Mock agreed with backend

Record it in `contract.md`:

```markdown
## POST `transfers` — Create transfer  · status: mock-agreed (backend: <name>, 2026-11-06)
```

Use the JSON from that agreement as the fixture. `forge-data-layer` serves it through the mock
interceptor, and `forge-deliver` lists every mocked route in the final report, so nobody ships
a mock believing that the endpoint exists.
