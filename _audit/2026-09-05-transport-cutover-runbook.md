# Cutover runbook: LinkedIn MCP from stdio to HTTP + CDP attach

Written 2026-09-05. Everything marked MEASURED was run on this machine and the
result is quoted. Everything marked UNMEASURED could not be checked without
changing the operator's live configuration and is left for the supervised
cutover.

## What this buys, in one line

Under stdio the MCP client owns the server process, so loading changed code
needs the operator to type `/mcp`. Claude Code reconnects a dropped **HTTP**
server by itself, so after this cutover the reload is `restart_server.ps1` in a
shell and he never has to be present for it.

## What it would cost if only the first half were done

A long-lived HTTP server in the default LAUNCH mode would hold the persistent
Chrome profile lock for as long as it runs -- strictly worse than stdio, where
the server at least dies with the session. So the browser stops being the
server's: Chrome is started separately and the server attaches to it over CDP.
`start_server.ps1` sets `LINKEDIN_CDP_ATTACH=1` and refuses to start when no
browser is there to attach to.

---

## THE ONE-WAY DOOR -- read before step 1

`_state/chrome-profile` is currently stamped **151.0.7922.34**, which is
exactly playwright's chromium. The operator's real Chrome is **152.0.7977.77**.
Both MEASURED today.

The moment real Chrome opens that profile it migrates and re-stamps it to 152.
Attach mode is then fine forever. But falling back to the LAUNCH path puts
playwright's chromium 151 in front of a profile from the future, and
`browser.py` records what that did on 2026-08-25: Chrome moved the profile
aside, started clean, and the operator signed in over and over. That is the
whole reason `session_store.restore_into_context` exists.

**So the rollback is a restored copy, and the copy must be taken first.**
`start_chrome.ps1` warns about this before it starts anything (MEASURED --
the warning fires and names both versions), but it does not take the copy
itself; a silent multi-hundred-megabyte duplication is not something a "start
the browser" command should do behind your back.

The zero-risk alternative, if you would rather not depend on a restore: point
`-ProfileDir` at a NEW directory and sign in to LinkedIn by hand once inside
that window. `_state/chrome-profile` is then never touched by real Chrome and
rollback is instant and lossless. It costs one sign-in.

---

## Cutover

**Every command below runs from the repo root** -- the `mcp-servers/linkedin`
directory inside the job-hunting project, the one holding `linkedin.py`. `cd`
there once and the relative paths in this document all resolve.

The paths here are deliberately relative rather than absolute. This file is a
STANDING INSTRUCTION -- whoever opens it next reads it as the thing to type --
and an absolute path off this machine names the account it lives under, which
`test_no_committed_identity` is right to refuse. It also rots the moment the
tree moves.

### 0. Copy the profile

```powershell
Copy-Item -Recurse -Force ".\_state\chrome-profile" ".\_state\chrome-profile.pre-http-20260905"
```

### 1. Stop every stdio LinkedIn server FIRST

This ordering is the point: the stdio server holds `_state/chrome-profile.lock`
whenever its browser is up, and starting Chrome on a locked profile puts two
processes on one Chromium user-data-dir, which is how the session gets lost.

There were THREE live stdio servers when this was written -- one per Claude
Code session, each spawning its own process. All of them must go.

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -like 'python*.exe' -and $_.CommandLine -match 'linkedin\.py' -and $_.CommandLine -notmatch '--http' } |
  ForEach-Object { "stopping pid=$($_.ProcessId)"; Stop-Process -Id $_.ProcessId -Force }
```

Then confirm the lock is gone. If it is still there naming a live PID, that PID
is a server you missed:

```powershell
Test-Path ".\_state\chrome-profile.lock"   # must be False
```

`start_chrome.ps1` refuses rather than proceeding if it is not (MEASURED -- the
refusal names the holding PID).

### 2. Start Chrome

```powershell
.\scripts\start_chrome.ps1
```

Expect `"outcome": "started"` plus the version-skew warning from the section
above. Run it twice if you like -- the second run reports `"outcome": "found"`
and starts nothing (MEASURED, same PID both times).

This is a real Chrome window on the LinkedIn profile. **Leave it open.** It is
now the browser every tool call goes through, and it must outlive every server
restart.

### 3. Start the server

```powershell
.\scripts\start_server.ps1 -EnableWrites
```

`-EnableWrites` is required to match what the current stdio entry does -- the
live `.mcp.json` sets `LINKEDIN_ENABLE_WRITES=1`, and this script will not turn
writes on unless asked. Expect `"outcome": "started"` and `"url":
"http://127.0.0.1:8322/mcp"`.

### 4. Change the config -- THIS IS THE SWITCH

The file is the job-hunting project's `.mcp.json`, two levels above this repo
(`..\..\.mcp.json` from the repo root). Copy it first -- **that copy, not this
document, is the authoritative rollback**, because it is the entry byte for
byte rather than a transcription of it:

```powershell
Copy-Item "..\..\.mcp.json" "..\..\.mcp.json.pre-http-20260905"
```

**Before** -- the entry you are replacing has this shape. The two paths are
absolute and are written here as `<REPO>` only so this file does not publish
the machine's directory layout; the real values are in the copy you just took.

```json
    "linkedin": {
      "type": "stdio",
      "command": "<REPO>\\venv\\Scripts\\python.exe",
      "args": [
        "-u",
        "<REPO>\\linkedin.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LINKEDIN_ENABLE_WRITES": "1"
      }
    }
```

**After:**

```json
    "linkedin": {
      "type": "http",
      "url": "http://127.0.0.1:8322/mcp"
    }
```

That is the same shape the `naukri` entry two blocks above already uses, on the
adjacent port.

### 5. `/mcp` once

The last one. From here on, `restart_server.ps1` is the reload.

### 6. Confirm

```powershell
.\venv\Scripts\python.exe .\scripts\mcp_probe.py --url http://127.0.0.1:8322/mcp --call linkedin_cdp_status
```

Expect `"active_browser_mode": "attach"` and `"reachable": true`. Then call
`linkedin_auth_status` through the MCP client itself to confirm the session in
the attached browser is his signed-in one.

---

## The restart command

From the repo root:

```powershell
.\scripts\restart_server.ps1 -EnableWrites
```

* Safe to run repeatedly -- MEASURED, twice back to back, 13s then 11s, exactly
  three server processes and one listener after each, no orphans.
* Does not touch Chrome -- MEASURED, the three Chrome PIDs were identical
  before and after every restart.
* Refuses to start a server when the browser is gone rather than starting one
  that would fail every call (MEASURED).

`stop_server.ps1` and `start_server.ps1` can be run separately; `restart` is
just the two composed.

---

## Rollback

1. `.\scripts\stop_server.ps1`
2. Quit the attach Chrome. **By profile path, never image-wide** -- an
   image-wide `taskkill /IM chrome.exe` has reached the operator's own browser
   on this machine before:

   ```powershell
   $needle = [regex]::Escape((Resolve-Path ".\_state\chrome-profile").Path)
   Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
     Where-Object { $_.CommandLine -match $needle } |
     ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
   ```

   Resolving the path at run time rather than pasting it is not only a
   disclosure fix: a hand-typed needle that does not match what Chrome was
   actually given silently selects NOTHING, and a kill loop that matches
   nothing looks exactly like a kill loop that worked.

3. **Restore the profile copy** -- this is the step that exists because of the
   one-way door:

   ```powershell
   Remove-Item -Recurse -Force ".\_state\chrome-profile"
   Copy-Item -Recurse -Force ".\_state\chrome-profile.pre-http-20260905" ".\_state\chrome-profile"
   ```

4. Restore `.mcp.json` from the copy taken in step 4 of the cutover:

   ```powershell
   Copy-Item -Force "..\..\.mcp.json.pre-http-20260905" "..\..\.mcp.json"
   ```

   Restore the file, do not retype the entry. The shape is quoted in step 4
   with its two absolute paths elided, so this document alone cannot
   reconstruct it -- which is the point of taking the copy.

5. `/mcp`.

Nothing in the code needs reverting: `linkedin.py` still runs stdio when
`--http` is absent, which is the whole reason the flag was added rather than
the transport swapped.

---

## Optional: close the write surface

stdio could be driven by exactly one thing, the parent that spawned it. A
loopback port can be driven by anything running as this user, and writes are
enabled -- so anything on this machine could post, message or invite as him.

The server supports a bearer token:

```powershell
.\scripts\restart_server.ps1 -EnableWrites -Token "<32+ random chars>"
```

and the config entry gains a header:

```json
    "linkedin": {
      "type": "http",
      "url": "http://127.0.0.1:8322/mcp",
      "headers": { "Authorization": "Bearer <the same token>" }
    }
```

MEASURED at the server: no token and a wrong token both get 401 and never reach
the app; the right token serves. UNMEASURED: whether Claude Code sends the
`headers` field on an http entry -- it is documented, but testing it needs his
live config. **So cut over without the token first**, confirm the plain HTTP
entry works, and add the token as a second, separately-verified step. A token
the client does not send locks him out of his own server.

The token is written into `_state\run-http-server.cmd` by the launcher. That
directory is gitignored and already holds the live Chrome profile, so the token
is the smaller secret of the two sitting there.

---

## Files

| path | what |
|---|---|
| `linkedin.py` | `--http` added; no argument still means stdio, unchanged |
| `linkedin_server/transport.py` | the HTTP transport and the bearer gate |
| `scripts/start_chrome.ps1` | idempotent Chrome starter, refuses on a live profile lock |
| `scripts/start_server.ps1` | starts the server in HTTP + attach, confirms by speaking MCP |
| `scripts/stop_server.ps1` | stops the server, never a browser |
| `scripts/restart_server.ps1` | the reload command |
| `scripts/mcp_probe.py` | stdlib-only MCP client, used by the scripts and by hand |
| `scripts/_probe_attach_continuity.py` | measures that a new server reaches the old browser |
| `tests/test_transport.py` | 19 tests, mutation-checked |
