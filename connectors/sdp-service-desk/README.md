# SDP – Service Desk connector

Power Platform custom connector for ManageEngine ServiceDesk Plus On-Premises. **37 operations**
across requests (list/get/create/update/close/delete + notes, worklogs, tasks, resolution),
changes, problems, solutions, and 12 admin-lookup dropdown sources.

## Files

- `apiDefinition.swagger.json` — the OpenAPI 2.0 definition (import this). **Generated** by
  `tools/gen_swagger.py` from a hand-curated operation table (see ADR-0001); the JSON is the
  committed, reviewable artifact — regenerate with `python tools/gen_swagger.py` after editing
  the spec.
- `apiProperties.json` — connection parameter (the API key) + capabilities (cloud + gateway).

## Operations

| Group | Operations |
|---|---|
| Requests | List, Get, Create, Update, Close, Delete |
| Request children | List/Add Notes, List/Add Worklogs, List Tasks, Get/Add Resolution |
| Changes | List, Get, Create, Update |
| Problems | List, Get, Create, Update |
| Solutions | List, Get, Create, Update |
| Admin lookups (dropdowns) | technicians, requesters (`/users`), categories, statuses, priorities, sites, support groups (`/support_groups`), departments, urgencies, impacts, modes, request types |

**Build note — lookup endpoints:** this connector points *List requesters* at `/users` and
*List support groups* at `/support_groups`, which are the paths verified live on the demo build.
Some SDP builds instead expose `/requesters` and `/groups`. If a lookup 404s on your instance,
edit the operation's path in the definition (or the `endpoint` in `tools/gen_swagger.py` and
regenerate).

## Setup

1. **Generate an API key in SDP.** In ServiceDesk Plus: *Admin → Technicians*, edit a
   technician (ideally a least-privilege integration account), and **Generate API Key** (set a
   validity). Copy the key. It is used as the `authtoken` header.
2. **Import the connector.** Power Automate/Apps → *Custom connectors → New → Import an OpenAPI
   file* → select `apiDefinition.swagger.json`.
3. **Set the host.** Edit the connector's **Host** to your SDP server (e.g.
   `servicedesk.company.com`). The shipped default `sdp.example.com` is a placeholder. HTTPS only.
4. **Create a connection.** Paste the API key when prompted (stored as a secured parameter).

## Operations (Phase 0)

| Operation | Method | Path | Notes |
|---|---|---|---|
| List requests | GET | `/requests` | `input_data` query param carries `list_info` (paging/sort/filter). `row_count` max 100. |
| Get request | GET | `/requests/{request_id}` | Full request detail by ID. |
| Create request | POST | `/requests` | `input_data` form field carries `{"request":{...}}`. Only `subject` is required. |

## The `input_data` envelope

SDP rejects any parameter that isn't wrapped in `input_data` (`Extra parameter(s) not
allowed`). So each operation takes a single **Input Data (JSON)** parameter carrying the JSON
envelope, with a copy-paste example in its description and a sensible default. Friendly typed
parameters (that the connector assembles into `input_data`) are a Phase-1+ enhancement for the
highest-value actions.

- **List:** `{"list_info":{"row_count":10,"start_index":1,"get_total_count":true,"search_criteria":{"field":"status.name","condition":"is","value":"Open"}}}`
- **Create:** `{"request":{"subject":"Printer down","requester":{"email_id":"user@company.com"},"priority":{"name":"High"}}}`

Dates in `search_criteria` use **epoch milliseconds**.

## Auth & networking

- **Auth:** API key in the `authtoken` HTTP header (secured connection parameter — never baked
  into the definition).
- **Networking:** direct HTTPS to your published host by default. The on-premises data gateway
  is available as a per-connection option (declared via `capabilities` in `apiProperties.json`)
  for firewalled installs — no change to the definition.

## Response shape

`{ "response_status": {...|[...]}, "requests"|"request": ..., "list_info": {...} }`. Success is
`response_status.status_code` **2000**. Note `response_status` is an **array** on the public
demo build but an **object** on a local 14990 build — consumers must handle both (the response
schemas leave it untyped for that reason).

## Build caveats

Requests/Changes work across SDP builds. See the top-level README for CMDB v3 (build 15100+) and
Execute Query gating caveats that affect the other connectors.
