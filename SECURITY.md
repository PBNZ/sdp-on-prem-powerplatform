# Security policy

This is a **personal alpha project** (see the warning at the top of the README). There is no
security team and no response SLA — but reports are genuinely welcome.

## Scope

The repo contains **no runtime code that handles secrets**: it is OpenAPI 2.0 connector
definitions, SQL `SELECT` templates, docs, and two small local tools. The security-relevant
surface is therefore mostly *definitional*:

- API keys are modeled as **secured connection parameters** (`securestring`) and are never
  stored in the definition files or this repo.
- The `sdp-cmdb-v1` connector sends the key as a **query parameter** (a constraint of that
  legacy API) — HTTPS is mandatory there, and the README/connector docs say so.
- The `sdp-query` connector executes SQL `SELECT`s on your SDP database via SDP's own
  Execute Query API. Treat the key you give it accordingly (least privilege, read-only DB
  access where possible).

## Reporting a vulnerability

- Preferred: **GitHub private vulnerability reporting** on this repository
  (*Security → Report a vulnerability*), if enabled.
- Otherwise: open a regular GitHub issue. If the detail is sensitive, say so in the issue
  without the detail, and a private channel will be arranged.

Please do **not** test suspected vulnerabilities against ManageEngine's shared public demo
instance, and never against SDP instances you don't own or have authorization for.

## Supported versions

Only the tip of `main`. There are no release branches and no backports.
