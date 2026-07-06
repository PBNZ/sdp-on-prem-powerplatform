# Contributing to sdp-on-prem-powerplatform

Thanks for the interest — and first, expectations: this is a **vibe-coded personal alpha**
maintained in spare time (see the README warning). Issues are welcome and genuinely useful,
especially live-verification reports from real SDP builds. PRs are welcome too, but reviews
may take a while, and the project's direction follows the maintainer's own use case.

## The most useful contributions right now

- **Verification reports.** "Operation X returns Y on SDP build Z" — with the build number and
  a redacted request/response — is gold, because behaviour varies by build (see `LESSONS.md`).
- **Bug reports** against the definitions (wrong path, wrong parameter shape, an operation
  Power Platform rejects on import).
- **SQL template fixes** for other builds' physical schema names (`templates/`).

## Ground rules for changes

- The three V3 connector definitions are **generated**: edit the operation tables in
  `tools/gen_swagger.py`, run `python tools/gen_swagger.py`, and commit the regenerated JSON
  (the committed JSON is the reviewed artifact). Only `sdp-cmdb-v1` is hand-edited directly.
- Definitions must stay **valid Swagger 2.0** and under Power Platform's 1 MB import cap:
  `npx @apidevtools/swagger-cli validate connectors/<name>/apiDefinition.swagger.json`
  (CI runs the same check).
- **Never commit an API key** — not even a truncated one — and never add write-operation tests
  against ManageEngine's shared public demo. Write-testing happens only on a disposable
  instance (see `docs/deploy-sdp-wsl2.md`).
- [Conventional Commits](https://www.conventionalcommits.org/); one concern per PR; add
  user-visible changes to `CHANGELOG.md` under `## [Unreleased]`.
- Notable decisions get an ADR in `docs/adr/` (copy `0000-template.md`).

## Where things live

Start with the map in [`AGENTS.md`](AGENTS.md). Short version: connector definitions in
`connectors/<name>/`, SQL templates in `templates/`, live-capture evidence in
`docs/test-evidence/`, decisions in `docs/adr/`.
