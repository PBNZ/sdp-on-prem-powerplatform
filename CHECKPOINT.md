# CHECKPOINT

> Build state for autonomous runs. Keep current: done / in progress / exact next step.

## Done

- Repo scaffolded (RepoKit Core tier, hand-authored variant — see ADR-0001).
- **Phase 0 walking skeleton** — `sdp-service-desk` connector with 3 operations
  (List Requests, Get Request, Create Request):
  - Valid **Swagger 2.0** (`swagger-cli validate` passes), **8.5 KB** (well under 1 MB), 3 ops.
  - Correct auth (`authtoken` header, secured `securestring` in apiProperties), `input_data`
    envelope modeling (query on GET, formData on POST), static Accept/Content-Type headers.
  - **List + Get 2xx live** against `https://demo.servicedeskplus.com` — evidence in
    `docs/test-evidence/listrequests.txt`, `getrequest.txt`.
  - Reusable `tools/live-test.ps1` (List/Get/Create smoke test + evidence capture).

## In progress

- Phase 0 gate: fresh-context verifier subagent reviewing the connector (running).

## Known gap (see LESSONS.md)

- **Create/write live 2xx is pending a valid technician API key** on a disposable instance. The
  WSL2 SDP 14990 runs and its `/api/v3` API routes correctly (returns SDP's auth envelope), but
  the RUNBOOK-default admin password is rejected on this restored instance and the API-key
  column is AES-encrypted, so no key can be minted headlessly. Unblock: log into local SDP UI →
  Admin → Technicians → Generate API Key, then
  `tools/live-test.ps1 -HostName localhost:8080 -ApiKey <key> -IncludeCreate -SkipCertCheck`.

## Exact next step

Phase 1 — expand `sdp-service-desk`: Requests notes/worklogs/resolution/close/delete, plus
Changes/Problems/Solutions/Tasks list-get-create-update, plus admin-lookup operations
(technicians, requesters, categories, statuses, priorities, sites, groups, departments, modes,
request_types, urgencies, impacts) to power `x-ms-dynamic-values` dropdowns. Transcribe from the
sibling `src/tools/*.ts` inventory. Verify reads live on the demo.

## Phase map (PRD §6)

- [x] Phase 0 — walking skeleton (3 request ops; reads proven live, create authored + pending key)
- [ ] Phase 1 — full Service Desk connector + admin lookups
- [ ] Phase 2 — Assets & CMDB v3 + CMDB v1 legacy connectors
- [ ] Phase 3 — Query connector (ExecuteQuery + template library)
