# API coverage — what the connectors expose, and what SDP offers

Reference for the question "why isn't *X* in the connectors?". Answer, in short: the scope was
never a recorded decision. This file records what is covered, what is not, and what the API
actually serves, so the next scope call is made on evidence.

- Last updated: 2026-07-22
- Connector operations: **55** across four connectors
- Documented on-prem V3 operations: **206**
- Overlap: **16** — see [Why the overlap looks so small](#why-the-overlap-looks-so-small)

## Which documentation is authoritative

ManageEngine publishes two V3 API doc sets. They are not the same API.

| Doc set | Product | Index |
|---|---|---|
| `sdpop-v3-api` | ServiceDesk Plus **On-Premises** — what this repo targets | [index](https://www.manageengine.com/products/service-desk/sdpop-v3-api/index.html) |
| `sdpod-v3-api` | ServiceDesk Plus **Cloud** | [index](https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html) |

Neither is a complete map of the on-prem API. The on-prem set documents only Requests, Changes,
Projects, Releases, Admin/User and Tasks — it has **no pages at all** for problems, solutions,
assets, CMDB, request worklogs or the admin lookups, yet this repo calls all of those and has
live 2xx evidence for them in [`docs/test-evidence/`](test-evidence/).

## Probing which modules a build actually serves

Because the docs are incomplete, module existence is settled empirically. An unauthenticated `GET`
separates the two cases cleanly:

| Response | Meaning |
|---|---|
| `HTTP 400` + `status_code 401` "AuthToken in the request is invalid" | the route exists |
| `HTTP 404` + `status_code 4007` "Invalid URL" | no such module on this build |

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'Accept: application/vnd.manageengine.sdp.v3+json' \
  https://<your-sdp-host>/api/v3/<module>
```

Read-only and safe against a shared instance. The method self-validates: `requesters` and `groups`
return 404, matching the build variance already recorded in [`LESSONS.md`](../LESSONS.md).

### Result against the public demo (2026-07-22)

Present but **not** in any connector: `tasks`, `projects`, `releases`, `contracts`,
`purchase_orders`, `purchase_requests`, `announcements`, `checklist_templates`, `topics`,
`workstations`, `custom_modules`, `archive_requests`, `list_view_filters`, `request_templates`,
`task_templates`, `service_categories`, `roles`, `worklogs`, `product_types`, `products`,
`change_types`, `closure_codes`, `project_types`, `project_statuses`.

Absent on this build — Cloud-only, correctly excluded: `checklists`, `change_risks`,
`reason_for_changes`, `campus`, `buildings`, `floors`, `rooms`, `leaves`, `unavailability`.

## Gaps against the documented on-prem API

### Whole modules, absent

| Module | Operations missing | Present on demo |
|---|---|---|
| Releases — release, approvals, approval levels, notes, tasks, worklogs | 58 | yes |
| Projects — project, milestones, members, project tasks | 33 | yes |
| Tasks — the standalone General Task module, `/api/v3/tasks` | 12 | yes |

### Partial coverage inside modules already shipped

| Area | Have | Documented | Missing |
|---|---|---|---|
| Requests — core | 8 | 28 | 20 — pickup, assign, merge, summary, tag, trash/restore, and all 9 association ops (problem / project / change) |
| Change approvals + approval levels | 0 | 16 | 16 |
| Change tasks, dependencies, attachments | 0 | 15 | 15 |
| Request tasks | 1 | 14 | 13 — add, edit, get, delete, trigger, close, assign, mark, dependencies, attachments |
| Changes — core | 4 | 14 | 10 — delete, trash/restore, pickup, assign, close, copy, summary, metainfo |
| Users (admin) | 1 | 6 | 5 — add, edit, get, delete, change_as_technician |
| Request drafts | 0 | 4 | 4 |
| Request notes | 2 | 5 | 3 — get, edit, delete |
| Archive requests | 0 | 1 | 1 |

**Attachments have zero coverage anywhere.** Every module documents download / list / delete
attachment operations and no connector exposes one.

### Why the overlap looks so small

Only 16 of the 55 connector operations appear in the on-prem doc set. That is a gap in the
*documentation*, not in the connectors: problems, solutions, assets, CMDB, the 12 admin lookups,
request worklogs and Execute Query are all live-verified here but undocumented upstream.

## Was any of this a deliberate exclusion?

No record exists. Checked: all five ADRs in [`docs/adr/`](adr/), [`LESSONS.md`](../LESSONS.md),
[`CHECKPOINT.md`](../CHECKPOINT.md) and the commit history. The scope traces to a private planning
doc (the PRD, §6) that is not in this repo, and no commit message or ADR states which modules were
considered and dropped.

Tasks are the clearest example: the single task operation, `ListRequestTasks`, sits in the
"request children" group beside notes and worklogs — so tasks appear to have been treated as a
child collection of a request rather than as a module. `README.md` advertising "requests
(+ notes, worklogs, **tasks**, resolution)" reads as broader coverage than one read-only list.

If a scope is chosen deliberately, record it as an ADR and link it here.

## Known defect

`DeleteRequest` is wired to `DELETE /api/v3/requests/{request_id}`, which the
[official Request API page](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/request.html)
documents as **"Delete Request From Trash" — a permanent delete**. The recoverable operation is
`DELETE /api/v3/requests/{request_id}/move_to_trash`. Both the action doc and the operation
description tell the maker it "moves a request to the trash". Tracked as
[issue #3](https://github.com/PBNZ/sdp-on-prem-powerplatform/issues/3); no write operation has
been live-verified, so this has never been exercised.
