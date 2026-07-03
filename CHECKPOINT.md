# CHECKPOINT

> Build state for autonomous runs. Keep current: done / in progress / exact next step.

## Done

- Repo scaffolded (RepoKit Core tier, hand-authored variant — see ADR-0001).

## In progress

- Phase 0 walking skeleton: `sdp-service-desk` connector with 3 operations
  (List Requests, Get Request, Create Request).

## Exact next step

Author `connectors/sdp-service-desk/apiDefinition.swagger.json` with the 3 Phase-0 operations,
then validate (Swagger 2.0, < 1 MB, paconn) and live-test List/Get against
`https://demo.servicedeskplus.com` (read-only).

## Phase map (PRD §6)

- [ ] Phase 0 — walking skeleton (3 request ops, proven end-to-end)
- [ ] Phase 1 — full Service Desk connector + admin lookups
- [ ] Phase 2 — Assets & CMDB v3 + CMDB v1 legacy connectors
- [ ] Phase 3 — Query connector (ExecuteQuery + template library)
