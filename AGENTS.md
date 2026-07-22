# AGENTS.md — sdp-on-prem-powerplatform

Microsoft Power Platform custom connectors (hand-authored OpenAPI 2.0) for ManageEngine
ServiceDesk Plus On-Premises — Service Desk modules, CMDB (v3 + legacy v1), and the Execute
Query report API.

Type: `power-platform-connectors` · Tier: Core + Public

This repo follows the **RepoKit** standard. For the conventions and the pre-commit / pre-PR
checklists, use the `repo-standard` skill (RepoKit: `/plugin marketplace add PBNZ/repo-kit`).

## START-HERE map — where things live

| What | Where |
|---|---|
| Agent rules & orientation | `AGENTS.md` (this file; [`CLAUDE.md`](CLAUDE.md) is a thin import) |
| Decisions & rationale | [`docs/adr/`](docs/adr/) |
| Conventions & checklists | the `repo-standard` skill (RepoKit) |
| Connector definitions | `connectors/<name>/` — `apiDefinition.swagger.json`, `apiProperties.json`, `README.md` |
| Connector generation — replaces the RepoKit Postman pipeline, omitted per [ADR-0001](docs/adr/0001-initial-decisions.md) | [`tools/gen_swagger.py`](tools/gen_swagger.py), [`tools/gen_action_docs.py`](tools/gen_action_docs.py) |
| CI & compliance checks — [`.github/workflows/validate.yml`](.github/workflows/validate.yml) substitutes for the type overlay's `ci.yml`/`sync.yml` (omitted with the Postman pipeline) | [`.github/workflows/`](.github/workflows/), [`scripts/repokit-check.ps1`](scripts/repokit-check.ps1), [`tools/check_pp_rules.py`](tools/check_pp_rules.py), [`tools/check_action_docs.py`](tools/check_action_docs.py) |
| Tests / live verification | [`tools/live-test.ps1`](tools/live-test.ps1) — live smoke test against a disposable instance; evidence lands in [`docs/test-evidence/`](docs/test-evidence/) |
| Execute-Query SQL templates | [`templates/`](templates/) |
| Test evidence (live request/response captures) | [`docs/test-evidence/`](docs/test-evidence/) |
| Build state / exact resume point | [`CHECKPOINT.md`](CHECKPOINT.md) — at the repo root, a declared variance from RepoKit's default location under `docs/` |
| Non-obvious findings (memory file) | [`LESSONS.md`](LESSONS.md) |

## Ground rules

- `AGENTS.md` is the canonical agent file; `CLAUDE.md` is a thin `@AGENTS.md` import (Claude Code
  reads `CLAUDE.md`, not `AGENTS.md`).
- Conventional Commits; one concern per PR, referencing its driving issue as `Refs #NN` (no
  auto-close keywords). Record notable decisions as ADRs in [`docs/adr/`](docs/adr/).
- Ceremony scales by visibility — this repo is at the **Core + Public** tier (published as a
  clearly-flagged personal alpha; see [ADR-0002](docs/adr/0002-public-personal-alpha.md)).
- Humans + agents sharing an issue board: follow the `repo-standard` skill's
  `standard/agent-collaboration.md` — cards move when state changes, run the session preflight
  before board work, sign agent-authored output.
- Link, don't just name: in docs, issues, and your own chat output to the human, anything they
  might open is a clickable markdown link; code formatting is only for paste-material (the
  `repo-standard` skill's `standard/doc-style.md`, *Links*).
- Identify the author by the GitHub handle `PBNZ`, never a real personal name — in file contents,
  connector `info.contact`, and the commit identity alike (see
  [repo-kit#25](https://github.com/PBNZ/repo-kit/issues/25)). CI fails the build if one reappears.
- Connector definitions are **hand-authored OpenAPI 2.0** (see
  [ADR-0001](docs/adr/0001-initial-decisions.md)) — never regenerate them from the Postman
  collection, and never commit an API key into a definition file.
- The public demo (`demo.servicedeskplus.com`) is **read-only** — never create/update/delete
  data on it. Write-testing happens only on a disposable Dockerized SDP instance.
