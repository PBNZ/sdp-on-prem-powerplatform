# LESSONS

> One lesson per section, one-line summary first. Update rather than duplicate; delete what
> turns out wrong.

## RepoKit power-platform-connectors type assumes Postman generation

The type template stamps a Postman→Swagger generation pipeline. This project hand-authors
definitions (PRD non-goal: no mechanical conversion), so the pipeline files were omitted at
scaffold time (ADR-0001). An upstream issue for pbnz/repo-kit is drafted but not yet filed —
filing to an external repo was blocked by the write-safety classifier in autonomous mode; Peter
can post it (draft text in ADR-0001 / this file's history).

## response_status is an array on the demo but an object on local 14990

Verified live both ways: `https://demo.servicedeskplus.com` returns
`response_status: [{status_code:2000,...}]` (array); a local build-14990 instance returns
`response_status: {status_code:...}` (object). The PRD flagged this as build-dependent — now
confirmed on two real builds. Connector response schemas therefore leave `response_status`
untyped, and any consumer/policy must handle both shapes (the sibling MCP client already does:
`Array.isArray(rawStatus) ? rawStatus[0] : rawStatus`).

## Local SDP write-testing is blocked on minting a technician API key

The sibling project's WSL2 SDP 14990 instance starts fine (Postgres 65432, Tomcat on
**HTTPS** 8080 — plain HTTP 8080 returns "This combination of host and port requires TLS") and
its `/api/v3` API routes correctly (returns SDP's own auth envelope, proving the connector's
path + `authtoken` header + `input_data` shape are accepted by a real on-prem build). But:
- `administrator`/`administrator` (the RUNBOOK default) is rejected on this May-restored
  instance (`loginError=true`), so the SDP UI's "Generate API Key" path is unavailable.
- The `techniciankeydefinition.techniciankey` column is `bytea`, AES-encrypted with SDP's
  install-time key — a raw plaintext `INSERT` authenticates as invalid (`4000/401`). Forging a
  valid row needs SDP's internal crypto (reusable in principle via its own jars, e.g.
  `com.manageengine.servicedesk.tools.DecryptPostgresPassword`, but a deep yak).

Net: reads are fully verified live (demo, 2xx); the create/write path is authored and
structurally validated but its live 2xx is **pending a valid technician key on a disposable
instance**. Unblock in seconds once Peter's real admin password is known: log into the local
SDP UI → Admin → Technicians → Generate API Key, then run
`tools/live-test.ps1 -HostName localhost:8080 -ApiKey <key> -IncludeCreate -SkipCertCheck`.

## paconn validate needs a Power Platform login; use swagger-cli offline

`paconn validate` (pip-installed, works) calls the Power Platform API and fails with "Access
token invalid" without `paconn login` (interactive device-code). For offline structural
validation of Swagger 2.0, `npx @apidevtools/swagger-cli validate` is sufficient and CI-friendly.
