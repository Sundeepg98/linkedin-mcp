# Slice report: browserless Chrome cookie-jar reader

Date: 2026-08-22
Scope: ONE module + ONE test file. Nothing else in the repo was touched. No
commit, no git command, no full-suite run.

## Files written

- `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\linkedin_server\cookie_jar.py`
  (255 lines, 11417 bytes, pure ASCII -- verified byte by byte)
- `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\tests\test_cookie_jar.py`
  (27 tests, all passing)

Public surface: `read_jar(profile_dir: Path, names: Iterable[str]) -> list[dict[str, Any]]`
plus `CookieJarUnavailableError`, defined in this module and NOT imported from
`errors.py`, as briefed.

## VERIFY: the live profile read

Read once, through the new function, against the operator's real profile at
`_state\chrome-profile`.

Result, verbatim:

    [{'name': 'li_at', 'expires': 1818868357.810868},
     {'name': 'JSESSIONID', 'expires': -1.0}]

`li_at` expiry rendered:

| view | value |
|---|---|
| POSIX seconds | 1818868357.810868 |
| UTC | **2027-08-21** 17:12:37 |
| IST (operator local) | **2027-08-21** 22:42:37 |
| days remaining from 2026-08-22 | 364.5 |

**2027-08-21 on both clocks -- the expected date.** 364.5 days remaining is
consistent with `auth.py`'s own note ("issued 2026-08-21, expiring
2027-08-21"), which is independent corroboration that the epoch conversion is
right rather than merely plausible.

`JSESSIONID` came back `-1.0`, matching `auth.py`'s documented measurement of
that cookie as `is_persistent = 0`.

### Live-file integrity: before / after

File: `_state\chrome-profile\Default\Network\Cookies`

| | before | after |
|---|---|---|
| sha256 | `edd891f2af6557065ec5ed17a791af98bb0af92feaa6250b6d112b3c9c4a131a` | `edd891f2af6557065ec5ed17a791af98bb0af92feaa6250b6d112b3c9c4a131a` |
| size | 57344 | 57344 |
| mtime | 2026-08-22 07:55:46.475531700 +0530 | 2026-08-22 07:55:46.475531700 +0530 |

**All three IDENTICAL.** Both snapshots were taken in the same shell
invocation as the read, to keep the window tight (see the surprise below for
why that mattered).

## Chrome's real cookie table -- exact column names

Read from a temp COPY of the live jar, never the live file. sqlite
`meta.version = 24`; tables are `meta` and `cookies`.

    creation_utc, host_key, top_frame_site_key, name, value,
    encrypted_value, path, expires_utc, is_secure, is_httponly,
    last_access_utc, has_expires, is_persistent, priority, samesite,
    source_scheme, source_port, last_update_utc, source_type,
    has_cross_site_ancestor

All twenty are declared `NOT NULL`. The test fixture reproduces this DDL
exactly, so the tests depend only on column names that really exist.

The two rows that matter, as stored:

| name | host_key | expires_utc | has_expires | is_persistent |
|---|---|---|---|---|
| li_at | `.www.linkedin.com` | 13463341957810868 | 1 | 1 |
| JSESSIONID | `.www.linkedin.com` | 0 | 0 | 0 |

One deviation from the brief's phrasing, worth naming: the brief anticipated a
session cookie might have `expires_utc` NULL. In this schema the column is
`NOT NULL` and Chrome stores **0**, not NULL. `_expires_from_row` handles 0,
NULL and a cleared flag identically (all -> `-1.0`), so the reader is correct
either way, but the stored value is 0.

## The epoch arithmetic, shown

    13463341957810868 us since 1601-01-01
      = 13463341957 s + 810868 us
    13463341957 - 11644473600   (offset = 134774 days * 86400)
      = 1818868357 s since 1970-01-01

The conversion splits into whole seconds and microseconds via `divmod` BEFORE
touching a float, so the result is exact rather than rounded through a
17-significant-digit division.

Three wrong readings the tests explicitly rule out:

| wrong reading | lands on |
|---|---|
| plain Unix microseconds | 2396-08-20 |
| plain Unix seconds | year ~426,000,000 |
| no offset applied | 1601 |

## Constraint compliance

1. **No cookie value is ever fetched.** The query is a module constant naming
   five metadata columns; there is no wildcard select and the sealed blob
   column is never named anywhere in the file. A test scans the source for
   both banned forms; another asserts the query constant contains no `value`
   substring at all.
2. **The live file is never opened.** The jar plus any `-journal` / `-wal` /
   `-shm` sibling is copied to `tempfile.mkdtemp()`, the COPY is opened, and
   the temp dir is removed in a `finally`. A spy on `sqlite3.connect` asserts
   the path it receives is not the jar, is not in the jar's directory, and is
   not under the profile at all -- and that the copy no longer exists after
   the call.
3. **WebKit epoch converted.** Verified against the live jar, above.
4. **Defined exception, never an empty list.** `CookieJarUnavailableError`
   with three distinguishable messages (no profile dir / no jar file / sqlite
   refused), each naming the path tried. A test asserts the missing-dir and
   missing-file messages are not the same string.
5. **Strict ASCII.** Scanned: zero code points above 127 in either file.
6. **House style.** `from __future__ import annotations`, full type hints, a
   docstring that explains why the module exists, following `profile_lock.py`.

## Tests: 27, every guard shown failing

`venv\Scripts\python.exe -m pytest tests/test_cookie_jar.py -q` -> **27 passed**
(0.54s). Only this file was run.

Controls live IN the test file (each drives the same instrument at input it
must reject): the naive Unix-microsecond reading is asserted to be a
different, wrong date; the leak detector is shown rejecting a hand-made record
that carries a session token, both under a `value` key and hidden under an
innocent `note` key; the source scanner is shown rejecting `SELECT *` and a
query naming the sealed column; a non-LinkedIn host is rejected while the same
row on a LinkedIn host is returned; the corrupt-file test is paired with a
control proving raw sqlite really does choke on that file; the journal-copy
assertion is paired with a no-journal control so it tracks the source rather
than a fixed answer.

Beyond the in-file controls, five MUTATIONS were applied to the module
out-of-repo (in the scratchpad, nothing added to the tree) to confirm the
guards are live rather than decorative:

| mutation | tests that failed |
|---|---|
| epoch offset set to 0 (naive read) | 3 |
| host match downgraded to raw `endswith` | 1 |
| expiry flags ignored (session treated as persistent) | 2 |
| query constant selects the value column | 1 |
| `CookieJarUnavailableError` swallowed, `[]` returned | 2 |

**All five caught; 9 distinct test functions shown failing.** No guard was
found that cannot fail.

A further test asserts the jar file is byte-identical, same size and same
mtime_ns after a synthetic read -- the same three-way check run by hand
against the live profile above, but automated so a future edit cannot quietly
start writing to the operator's profile.

Also pinned, without expanding scope: the host match is done on label
boundaries, so `notlinkedin.com` is rejected. A bare `endswith("linkedin.com")`
would have accepted it, and a lookalike site can set a cookie named `li_at`.

## SURPRISES (reported, not worked around)

1. **A live Playwright Chromium is holding the operator's profile right now.**
   `chrome.exe --user-data-dir=...\_state\chrome-profile` at PID 31472, with a
   `network.mojom.NetworkService` utility child and a crashpad handler. This
   is a confound for a before/after hash of the jar -- a live Chrome can flush
   cookies to that file at any moment for reasons unrelated to this slice.
   Both snapshots were therefore taken in a single shell invocation wrapped
   tightly around the one read. They came back identical, so the check is
   clean, but a rerun at a moment when Chrome decides to flush could differ
   through no fault of the reader.
   It also makes the module's case concretely: with that process live, reading
   the expiry through Playwright is not available at all.
2. **No `_state\chrome-profile.lock` exists** even though that Chromium holds
   the profile. Either it was not launched through `profile_lock.acquire()`,
   or the lock was released while the browser stayed up. Outside this slice --
   flagged, not touched.
3. **`_audit/` is not covered by `.gitignore`** (only `_state/` is), so this
   report is a tracked-by-default new file. Flagged, not acted on -- no git
   command was run.
