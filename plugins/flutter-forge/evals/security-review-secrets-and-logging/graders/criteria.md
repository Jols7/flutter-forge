---
type: llm
weight: 2
---

The security review, mapped to OWASP MASVS categories, reports:
- The live secret key compiled into the app as critical (anything in the binary is extractable; move it to the backend and rotate it).
- Token stored in SharedPreferences instead of secure storage (high; MASVS-STORAGE).
- Logging the token with print (high; never log credentials).
- Cleartext `http://` base URL (high; MASVS-NETWORK).
It does NOT repeat the full secret value in its findings (it may refer to it as "the sk_live key" or mask it). Each finding has a concrete fix.
