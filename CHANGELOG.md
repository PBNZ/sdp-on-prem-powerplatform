# Changelog

All notable changes to sdp-on-prem-powerplatform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `sdp-service-desk` connector — 37 operations across requests (+ notes, worklogs, tasks,
  resolution, close, delete), changes, problems, solutions, and 12 admin-lookup dropdowns.
- `sdp-assets-cmdb-v3` connector — 13 operations: assets, CI types, per-type CIs, `_metadata`,
  association relationships (SDP build 15100+).
- `sdp-cmdb-v1` connector — 4 operations against the legacy XML CMDB API (builds < 15100).
- `sdp-query` connector — Execute Query: one read-only SQL SELECT action.
- `templates/` — 8 live-verified Execute-Query SQL templates (build-14990 schema).
- `tools/gen_swagger.py` (curated-table generator for the V3 connectors) and
  `tools/live-test.ps1` (live smoke test + evidence capture).
- WSL2 deploy/redeploy runbook for a disposable SDP 14990 (`docs/deploy-sdp-wsl2.md`).
- Public-tier governance (ADR-0002): Apache-2.0 `LICENSE`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`, contributor-facing `CONTRIBUTING.md`, issue/PR templates, and a
  definition-validation CI workflow.
- README: prominent vibe-coded-personal-alpha warning (public only so Power Platform can
  import the definitions by URL) plus the four raw import URLs.
- Initial scaffold via RepoKit.

- `tools/check_pp_rules.py` + CI step — enforces the Power Platform x-ms rules that
  swagger-cli can't (internal + default ⇒ required, internal + required ⇒ default).

### Changed

- Git history rewritten before publication to scrub a truncated demo-key prefix from an old
  doc example (ADR-0002) — all pre-publication commit SHAs changed.

### Fixed

- V3 connectors' `Accept` header is now `required: true` — with `required: false` the portal
  wizard refused to save (Swagger Validator rule *PropertyMustBeRequired*: internal parameter
  with a default must be required) and the header would have been silently dropped at runtime.
  This unblocks both file import and import-by-URL for `sdp-service-desk`,
  `sdp-assets-cmdb-v3`, and `sdp-query`.
