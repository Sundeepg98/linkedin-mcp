# linkedin auth-lifecycle slice - 2026-08-23

Slice: reshape `linkedin_session_info` to
`_audit/2026-08-23-auth-contract.md`, add `linkedin_logout(confirm=False)`,
ship no `linkedin_reauth`. Repo `mcp-servers/linkedin` only; no sibling repo
was read, edited or run except the contract and the named control template.

**Code commit: `oldsha06`**
(`feat(session): report the shared auth shape, and add a logout that asks
twice`). NOT PUSHED - the wave lead pushes after review.

---

## 1. Tools and where they live

| tool | file:line | note |
|---|---|---|
| `linkedin_session_info(verify_live=True)` | `linkedin_server/server.py:334` | reshaped, both modes preserved |
| `linkedin_logout(confirm=False)` | `linkedin_server/server.py:416` | new |
| `linkedin_reauth` | - | NOT SHIPPED, per the contract's ruling. `session_info.renewal.why` carries the reason in the payload. |

Supporting implementation:

| symbol | file:line | what it is |
|---|---|---|
| `auth.session_info` | `linkedin_server/auth.py:574` | live path, reshaped |
| `auth.session_info_offline` | `linkedin_server/auth.py:644` | browserless path, reshaped |
| `auth.logout` | `linkedin_server/auth.py:807` | the whole logout, never raises |
| `auth._credential` | `linkedin_server/auth.py:411` | renders `li_at` as the contract's `credential` |
| `auth._supporting` | `linkedin_server/auth.py:469` | renders `JSESSIONID` as `supporting`, role `csrf` |
| `auth._renewal` | `linkedin_server/auth.py:494` | the no-silent-renew block |
| `auth._logout_targets` | `linkedin_server/auth.py:775` | pure path arithmetic; stats nothing |
| `auth._erase` | `linkedin_server/auth.py:791` | the named erase seam a test can trap |
| `profile_lock.live_holder` | `linkedin_server/profile_lock.py:227` | new: PID of a LIVE holder, or None |

Field mapping actually shipped:

| was | is |
|---|---|
| `session_cookie` | `credential` (kind `cookie`, name `li_at`, format `cookie`/`absent`, `expiry_is_authoritative: true`) |
| `csrf_cookie` | `supporting[0]` (name `JSESSIONID`, `role: "csrf"`) |
| `cookie_source` | `credential_source` - prose unchanged, both modes |
| - | `server: "linkedin"` |
| - | `credential.expiry_source` - names the route: live Playwright jar vs on-disk copy |
| - | `renewal {silent_renew_available: false, tool: null, why: ...}` |
| - | `live_check.why_not` on the LIVE path too (it only existed offline before) |

`durability` keeps every field including `measured_here`. Both modes still
work, including the fallback when no browser can be started.

---

## 2. Test counts

| point | count |
|---|---|
| baseline, verified before any edit | **730 passed** (`730 passed in 221.51s`) |
| final, whole suite | **772 passed** (`772 passed in 149.38s`) |

Net +42: 41 in the new `tests/test_auth_lifecycle.py`, 1 in
`tests/test_path_hygiene.py` (the logout preview is the one payload in this
server that is MADE of paths, so it goes through the same relativiser sweep).
Eight existing assertions in `test_auth.py` / `test_session_info_offline.py`
were retargeted at the renamed fields; none was deleted or loosened, and
several gained an assertion (e.g. `expired is None` rather than `False` where
there is no date).

---

## 3. The control, and its measured red

`scripts/presence_is_auth_control.py` - pytest plugin in the house form of
`instahyre/scripts/permissive_scorer_control.py`. It rebuilds this server with
`authenticated` derived from `li_at` being PRESENT in the jar instead of from
the live identity call, patching BOTH `auth.*` and the names `server.py` bound
at import.

    PYTHONPATH=scripts venv/Scripts/python -m pytest \
        tests/test_auth_lifecycle.py tests/test_session_info_offline.py \
        -p presence_is_auth_control

Verbatim, 2026-08-23:

    FAILED tests/test_auth_lifecycle.py::test_the_offline_path_still_answers_null_and_not_false
    FAILED tests/test_auth_lifecycle.py::test_the_browser_failed_path_still_answers_null
    FAILED tests/test_auth_lifecycle.py::test_a_refusal_is_a_false_and_a_shrug_is_a_null
    FAILED tests/test_auth_lifecycle.py::test_why_not_is_present_exactly_when_the_check_did_not_complete
    FAILED tests/test_session_info_offline.py::test_a_perfectly_healthy_cookie_is_still_not_called_authenticated
    FAILED tests/test_session_info_offline.py::test_the_offline_result_says_in_words_that_a_cookie_is_not_a_session
    FAILED tests/test_session_info_offline.py::test_the_reason_the_live_check_could_not_run_travels_with_the_result
    FAILED tests/test_session_info_offline.py::test_an_expired_cookie_is_reported_expired_without_a_browser
    FAILED tests/test_session_info_offline.py::test_both_routes_failing_reports_both_reasons
    FAILED tests/test_session_info_offline.py::test_the_tool_falls_back_to_the_jar_when_no_browser_can_start
    FAILED tests/test_session_info_offline.py::test_verify_live_false_does_not_touch_the_browser_at_all
    FAILED tests/test_session_info_offline.py::test_the_default_does_reach_for_the_browser
    12 failed, 44 passed in 6.38s

The same two files are `56 passed` with the plugin off, so all twelve are real
flips, not collection errors. The asymmetry is the finding:

* `test_the_live_path_does_still_say_true` (the POSITIVE control) stays green.
  A control build that flipped it too would prove nothing about WHERE the
  verdict came from.
* Every `linkedin_logout` test stays green - logout reports no measured
  verdict, so the bug cannot reach it.
* Every SHAPE test stays green (credential / supporting / renewal /
  durability / `expiry_source` on a healthy jar). The permissive build returns
  the right shape with the wrong answer inside it, which is exactly what
  shipped last time and exactly what a shape-only suite would have passed.

`check_auth` is deliberately left unpatched; the reasoning is in the plugin's
docstring.

Instrument controls added alongside (each shown failing at the input it must
catch): `test_the_snapshot_instrument_can_see_a_change`,
`test_the_erase_recorder_fills_on_a_confirmed_call`,
`test_a_stale_lock_from_a_dead_process_does_not_block_forever`,
`test_the_tripwire_would_stop_an_erase_of_the_real_profile`,
`test_that_leak_check_can_actually_fail`,
`test_the_session_recorder_does_fill_on_a_tool_that_uses_a_browser`.

---

## 4. Read-only guards: exactly what changed

**Nothing in `linkedin_server/readonly.py` was touched. Zero-line diff.** The
allowlist, the mutation scanner, the JS token list, the AST evaluate check,
`WRITE_VERBS`, the negator window, `PERMITTED_LAUNCH_FLAGS` and the evasion
import patterns are all byte-identical. `tests/test_readonly.py` and
`tests/test_launch_boundary.py` are byte-identical too.

Two surface expectations were updated, which is the legitimate
adding-a-tool change:

1. `tests/test_server_surface.py` - `"linkedin_logout"` added to
   `EXPECTED_TOOLS`; `assert len(tools) == 12` -> `== 13`; the test renamed
   `test_the_surface_is_exactly_the_twelve_reads` ->
   `..._the_thirteen_tools`. `FORBIDDEN_TOOLS` was NOT touched, and no
   assertion was relaxed.
2. Prose counts: `server.py:1` said "eleven tools" (already stale by one
   before this slice) and `README.md` said "the eleven tools"; both now say
   thirteen.

Three checks the new code had to pass AS WRITTEN, with no exemption:

* `readonly.name_implies_write("linkedin_logout")` is False - `logout` is not
  a write verb and no segment of the name is.
* `readonly.docstring_write_claims` on the `linkedin_logout` description
  returns `[]`. The docstring was written around the verb list (erases,
  throws away, lapses, performs nothing) rather than a waiver being added for
  it. No `# readonly-ok` waiver was added anywhere - the suite still asserts
  waivers exist only in `dom.py` and number at most three.
* `scan_source_for_mutations` over the new `auth.py` and `server.py` code is
  clean; the erase goes through `Path.unlink()`, which is not a Playwright
  mutation call and not on the pattern list.

Honesty disclosure rather than guard weakening: `linkedin_server_info` keeps
`read_only: True` and `writes_available: []` (both are about LINKEDIN, and no
request this server makes changes anything there) and gains a NEW named field
`local_state_writes` naming the local erase. Folding it into `read_only` would
have been the quiet redefinition the contract forbids; hiding it would have
been worse.

---

## 5. Judgement calls the wave lead should check

1. **`authenticated` on a logout that did not clear.** Contract section 2
   prints `"authenticated": false` flat. Section 0 (absolute) says
   `authenticated` is never `false` unless a server said no. The section-2
   false is justified BY the credential being gone, so I ship `false` ONLY on
   a successful clear - with a reason that states the proof - and `null` with
   a reason on the three outcomes where the credential is still sitting there
   (unconfirmed preview, locked profile, failed erase). Saying `false` while
   `li_at` is untouched would be a lie a caller would act on. Named here
   rather than resolved silently.

2. **Logout scope is the cookie jar, not the profile directory.** The
   contract says `scope` must be exact; it does not say how much to take. I
   take `Default/Network/Cookies` plus its `-journal` / `-wal` / `-shm`
   siblings - precisely the files `cookie_jar.py` reads - and leave the
   profile directory standing. Rationale in `auth.LOGOUT_SCOPE`: `li_at` is
   one row of that jar so erasing it ends the session, while erasing the
   whole profile would also take history and preferences nobody offered up.
   If the family wants whole-profile teardown, that is a one-line change to
   `_logout_targets` plus its scope prose.

3. **`live_holder()` added to `profile_lock.py`.** `held_by()` cannot tell a
   live holder from a corpse's lock, and `acquire()` makes that distinction
   only internally while acquiring. A destructive caller needs the answer
   without acquiring. Twenty-one added lines, no existing behaviour touched.

---

## 6. Constraints observed

* `linkedin_notifications` was never called.
* `linkedin_logout` was never run against the real `_state` Chrome profile,
  with or without `confirm`. Every test builds its own temp profile via
  `make_profile`. An autouse tripwire in `tests/test_auth_lifecycle.py`
  (`never_the_real_profile`) wraps `auth._erase` and raises if any test ever
  aims at a path inside the real profile; it has its own control driving it at
  the real jar path, which raises before the real erase runs.
  `tests/test_path_hygiene.py` needed a payload rooted in this checkout to
  exercise the relativiser, and uses
  `_state/chrome-profile-hygiene-probe` - never the real directory.
* No browser was launched at any point; the whole suite runs on fakes plus
  one local headless Chromium over frozen markup that predates this slice.
* Strict ASCII: 0 non-ASCII lines across every `.py` and `.md` in the repo
  (venv, `_state`, `__pycache__` excluded).
* Committed to `master`, no `Co-Authored-By`, no `Claude-Session` line, NOT
  pushed.

---

## 7. Not done, with reasons

* **`linkedin_reauth` - deliberately not shipped.** The contract rules it out
  for this platform with evidence; the reason now lives in the payload at
  `session_info.renewal.why` and in the tool description, so a caller is told
  rather than left to notice a gap.
* **`.github/workflows/ci.yml` prose says "684 tests" in three comments.** It
  was already stale at the 730 baseline (it is prose, not an assertion -
  `scripts/ci_full_run_check.py` derives its counts at runtime and pins
  nothing). Left alone: it is a CI-hygiene item outside this slice and
  another agent may own that file. Flagging it rather than editing it.
* **`README.md` line "tests/ 576 tests"** is stale for the same reason and by
  a larger margin. Same call: flagged, not edited, since a count that has been
  wrong through several waves wants one owner fixing it once.
* **No live end-to-end run of either tool against the real account.** By
  constraint. `linkedin_session_info(verify_live=False)` and
  `linkedin_logout(confirm=False)` were rendered against a temp profile built
  by the test helpers and eyeballed for shape; the live-verdict path is
  covered by fakes only, as the rest of this suite is.

---

# Follow-up pass - 2026-08-23 (wave lead's rulings + `renewal.session_lapses_*`)

Tree verified at `oldsha13`, clean, `origin/master` identical, before any edit.

## Rulings applied

1. **`authenticated: false` only on a proven clear** - already shipped that
   way; now the family rule. No change needed here.
2. **Logout scope stays the cookie jar and its siblings** - kept. No change.
3. **Stale prose counts fixed** - see below. Three things were wrong, not two.

## The addition: `renewal.session_lapses_*`

`linkedin_server/auth.py:494` - `_renewal` now takes the rendered
`credential` block and returns three more keys:

| key | value on linkedin |
|---|---|
| `session_lapses_at` | `credential.expires_at`, ISO8601 `...Z` |
| `session_lapses_in_days` | `credential.expires_in_days`, `round(s/86400, 1)` |
| `session_lapses_source` | names `li_at` and why it governs ALONE |

Both `session_info` (`auth.py:688`) and `session_info_offline`
(`auth.py:785`) now build the credential into a local before the payload and
hand it to `_renewal`, so ONE route produces both dates and they cannot drift
apart. That also means the keys are populated on the browserless path and go
null - never `0`, never `false` - when the jar cannot be read, with the
source carrying the jar's own reason.

The equality with `credential.expires_at` is asserted as a derivation, not a
fixture: `test_the_lapse_date_equals_the_credentials_own_on_this_platform` is
parametrised over +364.2 / +12.5 / -3.0 days, plus a live-path twin.

Rendered on a healthy temp jar:

    "session_lapses_at": "2027-08-22T08:00:52Z",
    "session_lapses_in_days": 364.2,
    "session_lapses_source": "li_at, and it governs ALONE. Because no silent
      renew exists on this platform, nothing can carry the session past the
      date the cookie itself carries, so this is EQUAL to
      credential.expires_at rather than derived from something else..."

...and on an unreadable jar:

    "session_lapses_at": null,
    "session_lapses_in_days": null,
    "session_lapses_source": "li_at governs, and nothing else can: with one
      credential layer and no refresh token there is no other expiry that
      could stand in for it. No date is available here -- no date could be
      read: chrome profile directory does not exist: ..."

The `linkedin_session_info` docstring gained the same explanation, including
that this is the field to compare across servers and `credential.expires_at`
is not.

## Tests

| point | count |
|---|---|
| start of this pass | 772 passed |
| end of this pass | **782 passed** |

Ten added, all in `tests/test_auth_lifecycle.py` section 2b: keys present on
both paths; dates equal to the credential's (parametrised x3 plus a live
twin); the source naming `li_at`, `ALONE`, `no silent renew` and
`credential.expires_at`; an unreadable jar giving nulls with explicit
`is not False` / `!= 0` assertions; a never-signed-in profile giving nulls
with its own different reason; and `silent_renew_available` staying False
whatever the date says, so a date next to it can never read as a promise.

## Control re-measured

The `session_lapses_*` addition is shape, not verdict, so the twelve reds are
unchanged. Verbatim:

    12 failed, 54 passed in 2.21s

(same two files: `66 passed` with the plugin off). Docstring in
`scripts/presence_is_auth_control.py` updated to the re-measured figures and
notes that every `session_lapses_*` assertion stays green under it - correctly,
since the bug it reproduces cannot reach them.

## Stale prose - measured, not adjusted

`README.md`: `576` -> `782` in three places.

`.github/workflows/ci.yml`: the header comment was wrong in THREE ways, not
one. Rather than scaling the numbers I re-measured by running the whole suite
with `PLAYWRIGHT_BROWSERS_PATH` pointed at an empty directory - exactly what a
runner with no binary looks like:

    87 failed, 695 passed in 103.04s

So `684` -> `782` and `77` -> `87` (in both places it appears). The module
list was also stale: the comment named three fixture modules, and there are
now four - `test_job_detail_fixture.py` (10) joined at `oldsha07`, alongside
`test_profile_views_fixture.py` (18), `test_job_search_fixture.py` (27) and
`test_sdui_surfaces_fixture.py` (32). Per-file counts are now written in, and
the comment records that the old figures were stale and how the new ones were
obtained, so the next reader knows which are measured.

The "18 browser tests alongside 25 that need no browser" line in the same
comment was off by one against a 42-test module; corrected to 24.

## Guards, again

`linkedin_server/readonly.py`, `tests/test_readonly.py` and
`tests/test_launch_boundary.py` are still zero-line diffs across BOTH passes.
Nothing in this pass touched a tool name, a docstring claim, the allowlist or
the launch boundary.

## Constraints

`linkedin_notifications` never called. `linkedin_logout` never run against the
real `_state` profile. No browser launched against the real profile - the
browser-absent measurement only pointed `PLAYWRIGHT_BROWSERS_PATH` at an empty
temp directory for one pytest process, which makes `chromium.launch` fail and
touches no profile at all. Strict ASCII across `.py`, `.md` and `.yml`.
