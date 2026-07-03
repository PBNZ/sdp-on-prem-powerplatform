# AGENTS.md — sdp-on-prem-powerplatform

Microsoft Power Platform custom connectors (hand-authored OpenAPI 2.0) for ManageEngine
ServiceDesk Plus On-Premises — Service Desk modules, CMDB (v3 + legacy v1), and the Execute
Query report API.

Type: `power-platform-connectors` · Tier: Core

This repo follows the **RepoKit** standard. For the conventions and the pre-commit / pre-PR
checklists, use the `repo-standard` skill (RepoKit: `/plugin marketplace add PBNZ/repo-kit`).

## START-HERE map — where things live

| What | Where |
|---|---|
| Agent rules & orientation | `AGENTS.md` (this file; `CLAUDE.md` is a thin import) |
| Decisions & rationale | `docs/adr/` |
| Conventions & checklists | the `repo-standard` skill (RepoKit) |
| Connector definitions | `connectors/<name>/` — `apiDefinition.swagger.json`, `apiProperties.json`, `README.md` |
| Execute-Query SQL templates | `templates/` |
| Test evidence (live request/response captures) | `docs/test-evidence/` |
| Build state / exact resume point | `CHECKPOINT.md` |
| Non-obvious findings (memory file) | `LESSONS.md` |

## Ground rules

- `AGENTS.md` is the canonical agent file; `CLAUDE.md` is a thin `@AGENTS.md` import (Claude Code
  reads `CLAUDE.md`, not `AGENTS.md`).
- Conventional Commits; one concern per PR. Record notable decisions as ADRs in `docs/adr/`.
- Ceremony scales by visibility — this repo is at the **Core** tier.
- Connector definitions are **hand-authored OpenAPI 2.0** (see ADR-0001) — never regenerate them
  from the Postman collection, and never commit an API key into a definition file.
- The public demo (`demo.servicedeskplus.com`) is **read-only** — never create/update/delete
  data on it. Write-testing happens only on a disposable Dockerized SDP instance.
