# LESSONS

> One lesson per section, one-line summary first. Update rather than duplicate; delete what
> turns out wrong.

## RepoKit power-platform-connectors type assumes Postman generation

The type template stamps a Postman→Swagger generation pipeline. This project hand-authors
definitions (PRD non-goal: no mechanical conversion), so the pipeline files were omitted at
scaffold time (ADR-0001). An upstream issue for pbnz/repo-kit is drafted but not yet filed —
filing to an external repo was blocked by the write-safety classifier in autonomous mode; Peter
can post it (draft text in ADR-0001 / this file's history).

## response_status shape tracks the response kind (list → array, single/error → object), not the build

Earlier versions of this lesson claimed the shape was build-dependent (demo = array, local 14990
= object). The repo's own captures refute that: the demo returns **both** shapes — an array on a
list success (`docs/test-evidence/listrequests.txt`) and an object on single-resource GETs
(`getrequest.txt`, `requests/{id}/resolutions` in `phase1-reads.txt`) — and local 14990 likewise
returns an array on a list success (`listrequests-local14990.txt`) and an object on the
auth-error envelope. Every capture so far fits: list responses → array of status objects;
single-resource and error responses → one status object. Connector response schemas leave
`response_status` untyped, and any consumer/policy must handle both shapes (the companion MCP
project's client already does: `Array.isArray(rawStatus) ? rawStatus[0] : rawStatus`).

## SDP trial expires (~30 days) → redeploy to reset it; fresh install fixes the admin-login blocker

The WSL2 SDP 14990 starts fine (Postgres 65432, Tomcat on **HTTPS** 8080 — plain HTTP 8080 returns
"This combination of host and port requires TLS") and its `/api/v3` routes correctly (returns
SDP's own auth envelope, proving the connector path + `authtoken` header + `input_data` shape are
accepted by a real on-prem build).

The earlier write-test blocker was two-fold, and **both are resolved by a fresh reinstall**:
- SDP's eval clock is install-date-based. The May-14 install aged past ~30 days and flipped to
  *"trial expired → free version"*. There is no in-place extend; a **fresh install to a clean
  dir resets it** (move the old `ManageEngine` dir aside, rerun `install.exp`). Redone 2026-07-06.
- On the *restored/aged* instance, `administrator`/`administrator` was rejected, so the UI's
  "Generate API Key" path was unavailable. **On the fresh install the default admin login works**
  (verified 2026-07-06: `SDPSESSIONID` session cookie, hidden CSRF field `sdplogincsrfparam`,
  `AUTHRULE_NAME=RememberMeLoginModule`, POST `/j_security_check` → authenticated home page).
- The API key is **not** in `techniciankeydefinition` (that AES-`bytea` table is legacy and empty).
  The real store is `integrationkeydefinition.integrationkey`, but it's **encrypted at rest**
  (keystore-keyed `schar` column) and auth is cached in memory — so you **can't** mint one with a DB
  `INSERT`. See the dedicated lesson below; mint via the app (a scripted admin session works
  headlessly on a fresh install).

Net: reads are fully verified live (demo, 2xx); the create/write path is authored + structurally
validated, its live 2xx now **only needs the key generated in the browser** (Admin → Technicians →
Generate API Key) then `tools/live-test.ps1 -HostName localhost:8080 -ApiKey <key> -IncludeCreate
-SkipCertCheck`. Full deploy/redeploy procedure: `docs/deploy-sdp-wsl2.md`.

## SDP API keys: encrypted at rest + cached in memory → mint via the app, not a DB INSERT

Settled by a live insert-then-authenticate test on the fresh 14990 instance. The value you send as
the `authtoken` header is a **36-char GUID**; the DB column `integrationkeydefinition.integrationkey`
(a `citext` **`schar` secure column**) stores only a **reversibly-encrypted 68-byte ciphertext** of
it, keyed to the on-disk keystores (`conf/sdp.keystore`, `conf/manageengine.keystore`,
`conf/key_modifier.conf`, `adssecretkeys`). The plaintext GUID is **nowhere** in the DB.

Two independent facts kill 'just INSERT a key', both verified live:
1. **Encrypted at rest.** Inserting a plaintext GUID into `integrationkey` → the API returns
   `401 AuthToken invalid` (the app decrypts the column and gets garbage), while the real key still
   returns 200. You can't compute the correct ciphertext without SDP's keystore-keyed encryption.
2. **In-memory cache.** Auth is served from an in-memory cache (`INTEGRATION_KEY_DO`), not a
   per-request DB read — 16 auth calls produced zero scans on the table. Even a correctly-encrypted
   row wouldn't be seen until a cache reload/restart.

Own the trail: this note first claimed AES-`bytea`/un-INSERTable (inference from a legacy *empty*
table's name), then *plaintext* (inference from the `citext` type, untested). Both wrong. Only the
insert-then-authenticate test settled it — **encrypted + cached**. Lesson: test the actual auth path,
don't infer key storage from a column type.

**The headless path that works:** mint through the app with a **scripted admin session**. A fresh
install accepts default `administrator`/`administrator` (verified), so a script logs in
(`SDPSESSIONID` + `sdplogincsrfparam` + `AUTHRULE_NAME=RememberMeLoginModule` → POST
`/j_security_check`) and calls SDP's integration-key generation endpoint; the app encrypts + caches
the new key correctly and returns the GUID. That is how to self-provision a key on every rebuild
without a browser. (Alternative, untested: preserve the keystore + restore the existing key row
across rebuilds so the *same* GUID keeps working — hinges on the ciphertext being keystore-portable.)

## Some SDP GET endpoints reject input_data entirely

`GET /requests/{id}/resolutions` and `GET /{ci_type}/_metadata` return 400/4000 if you attach an
`input_data` query param, but 200 without it. They are single-object reads with no list_info.
So the connector must NOT declare an input_data param on these (the generator's plain `op()` /
`get_op(use_input=False)` handles this). Caught twice during evidence capture when a generic
"append input_data" loop broke them.

## Admin-lookup endpoints vary by build: /users vs /requesters, /support_groups vs /groups

On the demo build (15100+), `/requesters` and `/groups` 404; the working paths are `/users` and
`/support_groups`. The MCP client tried the first and fell back to the second at runtime, but a
static Power Platform connector can't fall back — it has one path per operation. Chose the
demo-verified paths and documented the alternative in the connector README. If a lookup 404s on a
customer build, edit the op path (or the endpoint in gen_swagger.py) and regenerate.

## V3 CMDB assoc_ci_relationships works on the demo — it's build 15100+

PRD flagged V3 CMDB as build-15100+-gated. Confirmed the demo build IS 15100+:
`GET /{ci_type}/{ci_id}/assoc_ci_relationships` returns 200/2000. So V3 CMDB (incl.
relationships) is fully live-verifiable on the demo; the V1 legacy connector's relationship path
is the fallback for sub-15100 builds and is superseded on the demo (couldn't be live-verified
there — modeled from the working cmdb-v1-client.ts instead).

## Execute Query: exact live behaviour (build 14990-era demo)

`POST /api/v3/reports/_execute_query`, body `input_data={"query":"SELECT ..."}`. Verified:
SELECT returns `{execute_query:{data:[...]}}` (rows keyed by column AS aliases); `SELECT 1 AS
test` probe works; UPDATE and `information_schema` queries both fail with 4004 "Internal Error";
GET fails with 4021 "Invalid HTTP method". Key tables (build 14990): `workorder`(+`workorderstates`,
`statusdefinition`), `ci`, `resources`(assets), `relationshiptype`, `workordertoasset`.

## paconn validate needs a Power Platform login; use swagger-cli offline

`paconn validate` (pip-installed, works) calls the Power Platform API and fails with "Access
token invalid" without `paconn login` (interactive device-code). For offline structural
validation of Swagger 2.0, `npx @apidevtools/swagger-cli validate` is sufficient and CI-friendly.
