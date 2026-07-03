# SDP – Assets & CMDB (v3) connector

Power Platform custom connector for ManageEngine ServiceDesk Plus On-Premises **assets** and the
**CMDB v3 (JSON) API**. 13 operations. **Generated** by `tools/gen_swagger.py`.

> **Build requirement:** full CMDB v3 requires **SDP build 15100+** (or AssetExplorer 7700+).
> On older builds, use the **SDP – CMDB (v1 legacy)** connector for CI relationships. The public
> demo build is 15100+, so all operations below were verified live there.

## Files

- `apiDefinition.swagger.json` — the OpenAPI 2.0 definition (import this).
- `apiProperties.json` — API key connection parameter + capabilities (cloud + gateway).

## Operations

| Operation | Method | Path | Notes |
|---|---|---|---|
| List CI types | GET | `/ci_types` | Each type has an `api_plural_name` — use it as the **CI Type** value below. |
| List all CIs | GET | `/cmdb` | Every CI across all types. |
| List CIs by type | GET | `/{ci_type}` | `ci_type` = the type's `api_plural_name` (e.g. `cmdb_businessservice`). |
| Create CI | POST | `/{ci_type}` | `input_data` wraps the CI payload; confirm fields via metadata. |
| Get CI | GET | `/{ci_type}/{ci_id}` | Single CI by type + ID. |
| Update CI | PUT | `/{ci_type}/{ci_id}` | V3 updates **by CI ID only** (no criteria-based update). |
| Get CI type metadata | GET | `/{ci_type}/_metadata` | Field/layout metadata. Takes **no** `input_data`. |
| List CI relationships | GET | `/{ci_type}/{ci_id}/assoc_ci_relationships` | Requires build 15100+. |
| Add CI relationship | POST | `/{ci_type}/{ci_id}/assoc_ci_relationships` | Requires build 15100+. |
| List asset modules | GET | `/asset_modules` | Asset type/module hierarchy. |
| List assets | GET | `/assets` | With pagination + search criteria. |
| Get asset | GET | `/assets/{asset_id}` | |
| Update asset | PUT | `/assets/{asset_id}` | `input_data` wraps `{"asset":{...}}`. |

## Workflow — working with CIs

1. **List CI types** → note the `api_plural_name` of the type you want.
2. **List CIs by type**, passing that `api_plural_name` as **CI Type**.
3. **Get/Update CI** with the same **CI Type** plus the CI's numeric ID.
4. For the exact field set of a type, call **Get CI type metadata**.

## Auth & the `input_data` envelope

Same as the Service Desk connector: API key in the `authtoken` header (secured parameter), and
every parameter wrapped in a single **Input Data (JSON)** `input_data` value — a query param on
GET (except `_metadata`, which takes none), a form field on POST/PUT. Success is
`response_status.status_code` 2000 (object or array by build).

## Caveats

- **CI Type is a path segment.** The `/{ci_type}` operations take the type's `api_plural_name`
  as the first path segment. Enter a real plural name (from **List CI types**), e.g.
  `cmdb_businessservice` — not a literal like `assets` or `cmdb` (those have their own
  operations and would hit different semantics).
- **Create/Update CI payloads are type-specific.** The connector models `input_data` as a raw
  JSON envelope; confirm the correct field set for each CI type via **Get CI type metadata**.
  These write ops are authored but were not live write-tested (see repo `LESSONS.md`).
- **CI-type plural names vary per instance.** `cmdb_workstation` exists on some instances and
  not others; always derive names from **List CI types**.
