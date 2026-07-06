# Deploy / redeploy ServiceDesk Plus 14990 in WSL2 (for write-testing)

Operational runbook for standing up a **disposable** SDP On-Prem 14990 instance in WSL2 to
live-test the write operations (create/update/close/delete) that can't be run against the shared
public demo. Battle-tested end-to-end on **2026-07-06** (a full redeploy).

> This is the *operational* guide — start, stop, verify, redeploy, mint a key. For the deep
> installer internals (what the `.bin` is, InstallAnywhere, symlink placeholders, the `expect`
> script design), see the companion MCP-Server project's `sdp-14990-schema/RUNBOOK.md`
> (a private repo of the author's — not published; reference-only, do not edit it).

---

## TL;DR

| | |
|---|---|
| WSL distro | `ubuntu-server-lts`, run as **root**: `wsl -d ubuntu-server-lts -u root` |
| Install root (`$SDP`) | `/home/peter/ManageEngine/ServiceDesk` |
| Installer + expect script | `/home/peter/sdp-work/` (`ManageEngine_ServiceDesk_Plus.bin`, `install.exp`) |
| Web UI | **`https://localhost:8080`** — HTTPS ONLY (plain HTTP returns HTTP 400 "requires TLS") |
| First login | `administrator` / `administrator` (works on a **fresh** install) |
| Postgres | `127.0.0.1:65432`, app user `sdpadmin` / `sdpadmin`, db `servicedesk` |
| Start | `cd $SDP/bin && ./startDB.sh && setsid nohup ./run.sh >/tmp/sdp.log 2>&1 </dev/null &` |
| Stop | `cd $SDP/bin && ./shutdown.sh -S` (then `kill -INT <postmaster-pid>` if 65432 lingers) |
| Time to `:8080` up | ~60 s after `run.sh` on a fresh DB |

---

## Why redeploy: the trial expires

SDP's evaluation clock is tied to the **install date**. After ~30 days the instance flips to
*"Your trial period has expired. Application has been switched to the free version"* — which caps
technicians/features and breaks write-testing. **A fresh install to a clean directory resets the
clock** (new `conf/`, new DB, new install date). That is the whole redeploy procedure below.

A fresh install also fixes a second problem: on a *restored/aged* instance the default
`administrator`/`administrator` login can be rejected (unknown admin password), so you can't mint
an API key. **On a fresh install the default admin login works** (verified 2026-07-06), so you can
generate a technician API key in the browser.

---

## Redeploy (reset the trial) — the exact steps

All commands run as root in `ubuntu-server-lts`. Prefix each with
`wsl -d ubuntu-server-lts -u root -- bash -c '<cmd>'`, **or** put multi-line scripts in a file and
run them (see the *WSL2 + PowerShell quoting* note at the bottom — inline heredocs get mangled).

### 1. Stop the old instance and free the ports

```bash
cd /home/peter/ManageEngine/ServiceDesk/bin
./shutdown.sh -S                      # stops Tomcat; usually stops Postgres too
sleep 8
ss -ltn | grep -E ':8080|:65432'      # if 65432 still listed, the postmaster lingered:
#   kill -INT <pid-of pgsql/bin/postgres>   # SIGINT = fast, clean Postgres shutdown
```

### 2. Move the expired install aside (reversible — don't delete yet)

```bash
mv /home/peter/ManageEngine /home/peter/ManageEngine.expired-$(date +%Y%m%d)
```

Keep it until the new instance is verified, then delete to reclaim ~2 GB.

### 3. Verify the installer, then run it fresh

The `.bin` and the working `expect` driver are already staged in `/home/peter/sdp-work/`.

```bash
cd /home/peter/sdp-work
echo "0c003369d49453901b1db8b08b5a1a317d47e01eac394866bd544b823c583944  ManageEngine_ServiceDesk_Plus.bin" | sha256sum -c
./install.exp > install-redeploy-$(date +%Y%m%d).log 2>&1
tail -5 "$(ls -t install-redeploy-*.log | head -1)"   # expect: "Installation Complete"
```

`install.exp` targets `/home/peter/ManageEngine/ServiceDesk`, answers the console prompts
(license Y, no support registration, install-not-as-service, default ports), and quits. ~5 min
(the slow part is `unpack200`-ing ~330 jars). If it ever hangs, the two prompts that historically
tripped it up are the `IS THIS CORRECT? (Y/N)` after the folder choice and
`Enter WebServer Port` (one word, no space) — both already handled in the script.

### 4. Open the WSL path so Postgres can traverse it

WSL home dirs default to `750`; the system `postgres` user needs `o+x` on each path component or
Postgres fails with *Permission denied* on its own data dir.

```bash
chmod o+x /home/peter \
          /home/peter/ManageEngine \
          /home/peter/ManageEngine/ServiceDesk \
          /home/peter/ManageEngine/ServiceDesk/pgsql
```

### 5. Start Postgres, then SDP

```bash
cd /home/peter/ManageEngine/ServiceDesk/bin
./startDB.sh > /tmp/startdb.log 2>&1
sleep 8 && ss -ltn | grep 65432          # Postgres up on 65432

setsid nohup ./run.sh > /tmp/sdp.log 2>&1 < /dev/null &
```

> **Use `setsid nohup … </dev/null &`.** A plain `./run.sh &` gets killed when the `wsl` command
> returns; `setsid nohup` detaches it so Tomcat keeps running after your shell exits.

First boot populates the full schema (2,305 tables) and is listening on `:8080` in ~60 s. Poll:

```bash
for i in $(seq 1 40); do
  ss -ltn | grep -q ':8080' && { echo "up after ~$((i*15))s"; break; }
  sleep 15
done
tail -8 /tmp/sdp.log            # look for "WebService [ STARTED ]"
```

### 6. Verify it's healthy

```bash
curl -s  -o /dev/null -w 'http  %{http_code}\n' http://localhost:8080/          # expect 400 (TLS required)
curl -sk -o /dev/null -w 'https %{http_code}\n' https://localhost:8080/         # expect 200
curl -sk https://localhost:8080/api/v3/requests \
     -H 'Accept: application/vnd.manageengine.sdp.v3+json'                       # expect auth-envelope 4000/401
```

The `4000/401 "AuthToken ... invalid"` envelope is the **success** signal here: it proves the V3
path, the `authtoken` header, and the `input_data` shape are accepted by a real on-prem build — it
just wants a valid key. (Note: this error envelope returns `response_status` as an **object**,
while list successes return an **array** — the shape tracks the response kind, not the build; see
LESSONS.md. Connector schemas leave it untyped for that reason.)

---

## Mint a technician API key (unblocks live write-testing)

The key is **encrypted at rest** — `integrationkeydefinition.integrationkey` is a keystore-encrypted
`schar` column, and auth is served from an in-memory cache — so a direct DB `INSERT` **won't** work
(a plaintext row returns `401 AuthToken invalid`, verified). Generate it through the app. On the
fresh install:

1. Browse to **https://localhost:8080** (accept the self-signed cert) and log in
   `administrator` / `administrator`.
2. **Admin → Technicians →** edit a technician (or make a least-privilege integration account) **→
   Generate API Key**, set a validity, copy it.
   - For the `sdp-query` connector, that technician also needs the **Create Query Report** permission.
3. Run the write smoke-test from this repo (PowerShell, on the Windows host):

   ```powershell
   ./tools/live-test.ps1 -HostName localhost:8080 -ApiKey <key> -IncludeCreate -SkipCertCheck
   ```

   `-IncludeCreate` POSTs a request; evidence lands in `docs/test-evidence/`. **Only ever run
   `-IncludeCreate` against this disposable instance — never the shared public demo.**

### For automated login (reference)

If you ever script the login instead of using a browser, the fresh-install login form uses:
`SDPSESSIONID` session cookie, hidden CSRF field **`sdplogincsrfparam`** (read it from the landing
page and echo it back), and **`AUTHRULE_NAME=RememberMeLoginModule`**, POSTed to `/j_security_check`.
Driving the SPA's *key-generation* endpoints headlessly is fiddly — the browser path above is the
reliable one.

---

## Shut down when done

```bash
cd /home/peter/ManageEngine/ServiceDesk/bin && ./shutdown.sh -S
```

Or stop the whole distro from Windows:
`wsl --terminate ubuntu-server-lts`.

---

## Gotchas (verified)

- **HTTPS only on :8080.** The companion RUNBOOK's `http://localhost:8080` is wrong for this build —
  plain HTTP returns HTTP 400 *"This combination of host and port requires TLS"*. Use `https://`
  and `curl -k` / accept the self-signed cert.
- **Never install on `/mnt/c/*`.** Postgres WAL `fsync` is unreliable over 9P/virtiofs. Install
  under ext4 inside the distro (`/home/...`), as above.
- **`postgres` can't read `/home/<you>` by default** (750) — the `chmod o+x` in step 4 is required.
- **`run.sh` needs `setsid nohup`** or it dies when the launching `wsl` command returns.
- **WSL2 + PowerShell quoting:** running `wsl … bash -lc '…complex…'` from PowerShell mangles
  heredocs, `$(…)`, and `2>/dev/null`. Write multi-line scripts to a file and run the file
  (e.g. `wsl -d ubuntu-server-lts -u root -- bash /mnt/c/…/script.sh`).
- **Redeploy, don't repair, when the trial expires** — a fresh install to a clean dir is the
  supported reset; there's no in-place "extend trial".
