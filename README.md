# sdp-on-prem-powerplatform

Microsoft **Power Platform custom connectors** for **ManageEngine ServiceDesk Plus On-Premises**
— hand-authored, lean **OpenAPI 2.0 (Swagger 2.0)** definitions covering the core Service Desk
modules, the CMDB API (v3 and legacy v1), and the Execute Query report API. Import a connector
into Power Automate / Power Apps / Copilot Studio, point it at your internet-published SDP
instance, paste an API key, and use the actions in flows.

> **Status: under construction.** See `CHECKPOINT.md` for the current build state.

## The connector family

| Connector | Covers | Auth |
|---|---|---|
| `sdp-service-desk` | Requests (+ notes, worklogs, resolution, close), changes, problems, solutions, tasks, admin lookups | `authtoken` header |
| `sdp-assets-cmdb-v3` | Assets, CI types, per-type CIs, relationships, metadata, UDF fields (SDP build **15100+** for full CMDB v3) | `authtoken` header |
| `sdp-cmdb-v1` | Legacy XML CMDB API for builds < 15100 (CI ops, relationships) | `TECHNICIAN_KEY` query |
| `sdp-query` | Execute Query — one read-only SQL SELECT replaces many REST GETs | `authtoken` header |

Each connector lives in `connectors/<name>/` as `apiDefinition.swagger.json` +
`apiProperties.json` + a per-connector `README.md` (setup, key generation, caveats).

## Why hand-authored (not the official Postman collection)

Power Platform caps a custom-connector definition at **< 1 MB / 256 operations** and only
imports **OpenAPI 2.0**. The official ~9 MB Postman collection physically cannot be imported and
is mostly example payloads. These definitions are authored from live-verified API behaviour and
contain only the operations that matter, with `x-ms-*` annotations for a clean maker experience.

## Key facts baked into these connectors

- **Auth:** V3 API key goes in the HTTP header `authtoken` (secured connection parameter —
  supplied at connection time, never in the definition). The legacy V1 CMDB API takes the same
  key as a `TECHNICIAN_KEY` query parameter.
- **`input_data` envelope:** SDP requires every parameter wrapped in a single `input_data` JSON
  string (query param on GET, form field on POST/PUT) and rejects anything else.
- **Pagination:** `list_info` — `row_count` (max 100), `start_index`, `has_more_rows`.
- **Responses:** `{ response_status, <module>: [...], list_info }`; success = `status_code` 2000.
  `response_status` can be an object **or** an array depending on build.
- **Networking:** direct HTTPS to your published SDP host (placeholder `host` — edit on import);
  the on-premises data gateway is an optional per-connection choice.

## Repo layout

```
connectors/           one folder per connector (definition + properties + README)
templates/            Execute-Query SQL template library (build-14990 schema)
docs/adr/             architecture decision records
docs/test-evidence/   committed live request/response captures
CHECKPOINT.md         build state — done / in progress / exact next step
LESSONS.md            non-obvious findings
```

See [`AGENTS.md`](AGENTS.md) for the START-HERE map. Follows the
[RepoKit](https://github.com/PBNZ/repo-kit) standard.
