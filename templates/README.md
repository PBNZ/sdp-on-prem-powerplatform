# Execute Query SQL templates

Ready-to-run `SELECT` templates for the **SDP – Query** connector's `ExecuteQuery` action.
Paste the SQL into the action's `input_data` as `{"query":"<sql>"}` (the connector wraps it), or
keep it in a flow variable so you can edit it without republishing.

Every template here was **verified to run live** against `https://demo.servicedeskplus.com`
(status_code 2000) on **2026-07-04** — see `../docs/test-evidence/phase3-execute-query.txt`.

| File | Purpose |
|---|---|
| `00-capability-probe.sql` | `SELECT 1 AS test` — run at setup to confirm the API is enabled. |
| `01-recent-requests.sql` | 20 most recent requests with status. |
| `02-request-count-by-status.sql` | Request counts grouped by status. |
| `03-overdue-requests.sql` | Overdue requests. |
| `04-ci-list.sql` | CMDB configuration items. |
| `05-relationship-types.sql` | CMDB relationship type catalogue. |
| `06-assets.sql` | Asset inventory. |
| `07-request-asset-links.sql` | Requests joined to their associated assets. |

## Schema is build-specific — read this before reusing on another instance

These queries use the physical table/column names of **SDP build 14990** (PostgreSQL):
`workorder`, `workorderstates`, `statusdefinition`, `ci`, `relationshiptype`, `resources`,
`workordertoasset`. **Names can change across builds/editions.** If a template errors with an
internal/`4004` error after an upgrade:

1. Confirm the table/column names for your build (regenerate the schema map with
   `pg_dump --schema-only`; see the sibling project's `RUNBOOK.md`).
2. `information_schema` is blocked via the API — to peek at a table's columns, run
   `SELECT * FROM <table> LIMIT 0` and read the result's column headers.

## Rules baked into these templates

- **SELECT only** — DML is rejected server-side.
- **Always alias with `AS`** — result rows are keyed by the column alias.
- **Always `LIMIT`** — avoid pulling large result sets through a flow.
