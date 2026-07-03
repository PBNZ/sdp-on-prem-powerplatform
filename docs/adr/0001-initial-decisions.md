# ADR-0001: Initial decisions — scaffold, type, and hand-authored connectors

- **Status:** accepted
- **Date:** 2026-07-04

## Context

New repo for Power Platform custom connectors for ServiceDesk Plus On-Premises, scaffolded to
the RepoKit standard (`/new-repo`, type `power-platform-connectors`, visibility `private` =
Core tier, author Peter Braun, licence Apache-2.0 on publication).

RepoKit's `power-platform-connectors` type template assumes connectors are **generated from a
committed Postman collection** (Dockerfile + `generate.mjs` pipeline). The PRD for this project
explicitly rejects that approach: the official SDP Postman collection is ~9 MB (over the 1 MB
import cap), mostly example payloads, and models the API as raw requests rather than clean
actions.

## Decision

- Scaffold Core-tier RepoKit base files as standard.
- **Omit the Postman-generation pipeline** (`Dockerfile`, `scripts/generate.mjs`,
  `connectors.config.json`, `.postman/`, `source/`) from the type overlay; keep the
  `connectors/` output layout.
- Connector definitions are **hand-authored OpenAPI 2.0**, one folder per connector
  (`apiDefinition.swagger.json`, `apiProperties.json`, `README.md`), per PRD §9.
- Add project-required files beyond the RepoKit set: `CHECKPOINT.md`, `LESSONS.md`,
  `templates/` (Execute-Query SQL), `docs/test-evidence/`.
- Split into ~4 domain connectors (Service Desk / Assets+CMDB v3 / CMDB v1 legacy / Query)
  rather than one monolith, to stay under the 1 MB / 256-operation caps.
- API keys are secured connection parameters, never committed in definitions. Demo instance is
  read-only; writes only against a disposable Dockerized SDP.

## Consequences

- No auto-regeneration from upstream Postman changes — intentional; definitions track
  live-verified behaviour instead. Upstream drift is handled by editing definitions.
- A repo-kit gap is surfaced upstream: the `power-platform-connectors` type has no
  hand-authored variant (GitHub issue to be filed against `pbnz/repo-kit`).

## Addendum (2026-07-04): a small generator for the repetitive ops

Every SDP operation shares the same shape (authtoken header, single `input_data` envelope,
`response_status`/`list_info` handling). Hand-copying ~40 near-identical operation blocks per
connector is error-prone, so `tools/gen_swagger.py` stamps the boilerplate from a **hand-curated
operation table** (endpoints/verbs/examples authored from live probes + the sibling MCP
inventory). This is explicitly **not** the forbidden Postman conversion — the input is a small
reviewable Python spec, not the 9 MB collection, and the **generated JSON remains the committed,
reviewed artifact**. Trade-off accepted: a build step (`python tools/gen_swagger.py`) is needed
to regenerate, versus editing JSON directly. The Phase 0 skeleton (hand-written, 9/9 verified)
is the pattern the generator reproduces.
