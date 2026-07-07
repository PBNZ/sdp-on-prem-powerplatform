# SDP – Query (Execute Query) connector

Power Platform custom connector exposing the ServiceDesk Plus On-Premises **Execute Query**
report API — one read-only SQL `SELECT` action that can replace many REST `GET` calls (JOINs
across modules, custom fields, aggregates). 1 operation. **Generated** by `tools/gen_swagger.py`.

## The one action

| Operation | Method | Path |
|---|---|---|
| Execute query | POST | `/reports/_execute_query` |

Full parameter reference + SQL-in-JSON formatting variations:
[`actions/execute-query.md`](actions/execute-query.md) (the action's **Learn more** link).

Body: `input_data={"query":"SELECT ... AS alias ..."}`. Response:
`{ "response_status": {...}, "execute_query": { "data": [ {row}, ... ] } }` — each row is keyed by
your SQL **column aliases**, so **always alias columns with `AS`**.

## Read-only, admin-scoped, and gated — probe before you rely on it

Verified live against the demo:

- **SELECT only.** `UPDATE`/`DELETE`/`INSERT` are rejected server-side; `information_schema` /
  catalog queries are blocked.
- **POST only.** A `GET` returns `Invalid HTTP method`.
- **Admin permission required** (`Create Query Report`, SDAdmin-scoped), and the endpoint is
  edition/build-gated on some instances.

Because the gate can't be detected from the definition, **probe at setup** with the capability
template `templates/00-capability-probe.sql` (`SELECT 1 AS test`). If it errors, this connector
isn't available on that instance — fall back to the REST connectors.

## Auth

API key in the `authtoken` header (secured connection parameter). Same key as the other V3
connectors, but its technician needs the query-report permission.

## SQL templates & schema fragility

Physical table/column names are **build-specific**. The `templates/` folder (repo root) holds a
starter library keyed to **build 14990**, each template verified to run live:

| Template | Returns |
|---|---|
| `00-capability-probe.sql` | 1 row — setup probe |
| `01-recent-requests.sql` | recent requests + status (workorder ⋈ workorderstates ⋈ statusdefinition) |
| `02-request-count-by-status.sql` | request counts grouped by status |
| `03-overdue-requests.sql` | overdue requests |
| `04-ci-list.sql` | CMDB configuration items (`ci`) |
| `05-relationship-types.sql` | CMDB relationship type catalogue |
| `06-assets.sql` | asset inventory (`resources`) |
| `07-request-asset-links.sql` | requests ⋈ associated assets |

**After an SDP upgrade, physical names can change** — keep your SQL in flow variables / these
template files, not hard-baked, so an admin can fix a query without republishing. Regenerate the
schema map for a new build with `pg_dump --schema-only` against your instance's Postgres.

## Security note

Prefer vetting fixed query templates over exposing a free-form "run any SQL" box to end users.
For an extra layer, point the connection's key at a technician whose DB access is read-only.
