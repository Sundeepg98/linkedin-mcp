# The session store went inert on day 31, and nothing said so

Wave: `auth-lifecycle` follow-up, one closed defect in
`D:\workspace\projects\job-hunting\mcp-servers\linkedin`.
Baseline commit `8f5795e`, 1699 passing.

## The defect

Two rules, each correct on its own, met on day 31 and killed the mechanism
between them.

`linkedin_server/session_store.py:70` sets `MAX_AGE_S = 60*60*24*30`, and
`restore_into_context` refuses any jar older than that -- "the stored session
is Ns old, past the Ns ceiling. Sign in rather than resurrect it." That guard
is right: a jar from a machine state nobody remembers should not be
resurrected into a live browser.

`linkedin_server/auth.py:224-226`, the `_arm_session_store` errand, refused to
harvest over a populated store:

```python
existing = SESSION_STORE.describe()
if existing.get("present") and existing.get("has_session_cookie"):
    return
```

That guard is also right, and its docstring says why: "NEVER OVER A GOOD
STORE. A populated store is left exactly alone. Refreshing it would trade a
known-good jar for a newer one on no evidence that the newer one is better."

Neither rule looked at the other. `_arm` checked `present` and
`has_session_cookie`; it never checked `stale`. So past thirty days a jar was
**simultaneously too old to restore and too present to replace**. The store
sat there reporting nothing wrong -- `describe()` said `present: True`,
`has_session_cookie: True` -- and the one thing it could never do again was
the thing it exists for.

**Severity is bounded and worth stating plainly.** `auth.py` ~line 1235
(`method="login_via_browser"`) calls `save_from_context` with no guard at all,
so an interactive sign-in re-arms the store unconditionally. Nothing was
bricked. The cost of the defect was exactly one sign-in -- which is the single
event this whole module exists to spare him, so it is worth fixing anyway.

Live state at the time of the fix: `_state/session.json` written
2026-08-26 00:41:24 IST, 24 cookies, `li_at` present, `method: check_auth`.
It would have gone inert 2026-09-25.

## RED first

Two tests written against the unmodified code, both failing.

### The defect itself

`tests/test_session_store.py::test_a_jar_too_old_to_restore_is_not_too_good_to_replace`

```
        after = store.describe()
>       assert after["stale"] is False, (
            "a live session did not replace a jar that had gone past the restore "
            "ceiling -- the store is inert and says nothing about it"
        )
E       AssertionError: a live session did not replace a jar that had gone past the restore ceiling -- the store is inert and says nothing about it
E       assert True is False

tests\test_session_store.py:210: AssertionError
```

Note what the test asserts on the way in, because it is the deadlock stated as
two facts rather than one: `store.describe()["stale"] is True` **and**
`restore_into_context(...)["restored"] is False` -- the jar is already refusing
to work -- and then `_arm_session_store` still declines to replace it.

### The margin

`tests/test_session_store.py::test_a_jar_is_replaced_while_it_is_still_good_not_after_it_dies`

```
        after = store.describe()
>       assert after["age_seconds"] < before["age_seconds"], (
            "a jar four fifths of the way to the ceiling was not refreshed, so its "
            "remaining life is whatever is left rather than a full term"
        )
E       AssertionError: a jar four fifths of the way to the ceiling was not refreshed, so its remaining life is whatever is left rather than a full term
E       assert 2073600 < 2073600

tests\test_session_store.py:249: AssertionError
```

```
FAILED tests/test_session_store.py::test_a_jar_too_old_to_restore_is_not_too_good_to_replace
FAILED tests/test_session_store.py::test_a_jar_is_replaced_while_it_is_still_good_not_after_it_dies
2 failed, 31 deselected in 0.23s
```

Both tests age the jar through one shared helper, `age_the_jar`, rather than
each rewriting `saved_at` inline -- staleness is now load-bearing on both the
restore side and the re-arm side, and two tests aging a jar by two routes stop
being about the same clock.

## The ruling on the re-arm margin

**The re-arm threshold is `MAX_AGE_S // 2` = 1296000 s = 15 days, and it is
derived rather than typed.**

The question the lead posed is real: if the skip threshold for RE-ARMING
equalled the refusal threshold for RESTORING, a jar would become eligible for
replacement at the exact moment it stopped working. Two things make that worse
than merely useless:

1. **A re-arm needs a live session to harvest from.** `_arm_session_store` runs
   only in the 200-with-identity branch of `check_auth`. The disaster this
   store exists for -- Chrome running its downgrade migration and discarding
   the profile -- is precisely the event that removes the live session. Waiting
   for expiry means the jar is refreshed only in the window where there is
   nothing left to refresh from.
2. **Nothing else refreshes it.** Between writes the jar's remaining life only
   ever decreases, so at any moment the store's actual value is "whatever term
   is left", not "thirty days".

So the margin must be strictly shorter than `MAX_AGE_S`. The number:

> **Re-arm when the replacement at least DOUBLES the jar's remaining
> restorable life.**

That is exactly `REARM_AFTER_S <= MAX_AGE_S / 2`, and taking the boundary gives
`MAX_AGE_S // 2`. At the moment of replacement the old jar has 15 days left and
the new one has 30.

This is not an arbitrary fraction; it is the number that answers the objection
the original invariant raised. The invariant refused to trade a good jar for a
newer one "on no evidence that the newer one is better." At the half-way mark
there IS evidence, and it is specific: the replacement has identical provenance
-- harvested from a session LinkedIn has just answered 200-with-identity for,
the same evidence class as the jar it replaces -- and strictly more than double
the term. Below half the trade buys less than a doubling and is not worth
touching a working store for. Above half it buys more, at the cost of leaving
less headroom for a machine that goes quiet.

**Guarantee purchased:** after any successful auth check, the store is
restorable for at least 15 more days with no further activity at all.

**Cost:** at most one harvest per 15 days, because a successful re-arm resets
the age to zero. The errand's other standing rule -- "NOT ON EVERY CALL" -- is
untouched.

**One threshold, one clock.** `describe()` already computed the jar's age once
for `stale`; it now publishes `due_for_rearm` off that same `age` rather than
letting the guard compute a second age at the call site. Two age computations
is how a guard and the message it prints drift apart.

**One case decided beyond the literal defect:** an UNDATABLE jar -- `saved_at`
absent or not a number, so `age is None` -- reads as due for re-arm. It is not
`stale` (nothing says it is old), but nothing bounds its remaining life either,
and an unboundable jar is what the re-arm is for. `save_from_context` always
writes a numeric `saved_at`, so this only reaches a hand-edited or
foreign-version file. Replacing it from a confirmed live session also gives it
the timestamp it was missing.

## The diff

```diff
--- a/linkedin_server/session_store.py
+++ b/linkedin_server/session_store.py
@@ -69,6 +69,35 @@
 MAX_AGE_S = 60 * 60 * 24 * 30

+#: Older than this and a saved jar is REPLACED by a live harvest, rather than
+#: left alone as a good store. Derived from MAX_AGE_S, never typed as its own
+#: number, because the whole point is a fixed relationship between the two.
+#: [26 further lines of rationale -- the deadlock, and why HALF specifically]
+REARM_AFTER_S = MAX_AGE_S // 2
+
@@ -149,6 +178,20 @@  (SessionStore.describe)
             "stale": bool(age is not None and age > MAX_AGE_S),
+            # BOTH AGE VERDICTS COME OFF THE SAME `age`, deliberately. [...]
+            # An UNDATABLE jar (`age is None`) reads as due. [...]
+            "due_for_rearm": bool(age is None or age > REARM_AFTER_S),
             "method": data.get("method"),
```

```diff
--- a/linkedin_server/auth.py
+++ b/linkedin_server/auth.py
@@ -217,12 +217,31 @@  (_arm_session_store)
     * **NEVER OVER A GOOD STORE.** [...]
+
+    THAT LAST RULE USED TO READ THE STORE'S AGE WRONG [...] "good" now includes
+    "not near expiry", at ``REARM_AFTER_S`` [...] The staleness verdict is READ
+    from ``describe()`` rather than recomputed here, because a second age
+    computation is how a guard and its ceiling drift apart.
     """
         existing = SESSION_STORE.describe()
-        if existing.get("present") and existing.get("has_session_cookie"):
+        if (
+            existing.get("present")
+            and existing.get("has_session_cookie")
+            and not existing.get("due_for_rearm")
+        ):
             return
```

Full text: `git show 5e5fe7e -- linkedin_server/`. Totals across the three
files: 211 insertions, 2 deletions.

`describe()` has exactly two callers, both internal (`auth.py:239` and
`session_store.py:323`), and no MCP tool surfaces its output -- so the new key
is not a schema change anyone outside this module can see.

## Every new check has been shown failing

Four checks were added. The repo's standing rule is that an instrument enters
only if it has been shown failing, so each was driven at the specific mutation
it exists to catch, with `REARM_AFTER_S` temporarily rewritten and then
restored.

| mutation | what fails | what it proves |
|---|---|---|
| baseline (unfixed `_arm` guard) | `..._too_old_to_restore_is_not_too_good_to_replace`, `..._still_good_not_after_it_dies` | the two reds catch the real defect |
| `REARM_AFTER_S = MAX_AGE_S` | `..._still_good_not_after_it_dies`, `..._margin_is_derived_and_leaves_real_headroom` | the equality case -- re-arming only corpses -- is forbidden |
| `REARM_AFTER_S = 0` | `..._never_overwrites_a_store_that_already_has_a_session`, `..._margin_is_derived...`, `..._well_inside_the_margin_is_still_left_exactly_alone` | the guard gained a threshold; it did not lose the rule |
| restored | 35 passed | |

The margin controls assert RELATIONSHIPS, not the literal 1296000:
`0 < REARM_AFTER_S < MAX_AGE_S` (equality is the defect) and
`MAX_AGE_S - REARM_AFTER_S >= REARM_AFTER_S` (a re-arm at least doubles the
remaining life). A literal would pass for the wrong reasons and would have to
be edited by anyone re-ruling the number, which makes it a speed bump rather
than a check.

`test_a_jar_well_inside_the_margin_is_still_left_exactly_alone` exists because
its sibling cannot do the job: `test_arming_never_overwrites_a_store_that_already_has_a_session`
uses a jar written moments ago, which survives even a one-second margin. The
new one ages the jar to a quarter of the ceiling -- old enough that a collapsed
guard rewrites it, young enough that it must not be.

## Full suite

```
1703 passed in 306.94s (0:05:06)
```

`venv\Scripts\python.exe -m pytest -q` from the repo root. Baseline at
`8f5795e` was 1699; the four new checks account for the difference exactly.
Run against the exact bytes committed (see the line-endings note below).

## `_state/` proof

`session.json` is **byte-for-byte and mtime-for-mtime unchanged**:

| | at wave start | after the work |
|---|---|---|
| mtime | `2026-08-26 00:41:24.087578800 +0530` | `2026-08-26 00:41:24.087578800 +0530` |
| size | 7813 | 7813 |
| contents | 24 cookies, `method: check_auth` | 24 cookies, `method: check_auth` |

```
$ git status --porcelain
 M linkedin_server/auth.py
 M linkedin_server/session_store.py
 M tests/test_session_store.py
?? _audit/2026-08-26-session-store-ttl.md

$ git status --porcelain --ignored -- _state/
!! _state/            # ignored as a whole; no tracked path under it exists
```

The autouse `_never_write_the_real_session_store` fixture in `tests/conftest.py`
redirects both `session_store.SESSION_PATH` and `browser.SESSION_STORE.path` to
`tmp_path` for every test, and every test added here builds its own
`SessionStore(tmp_path / "armed.json")` on top of that.

### The Chrome profile, reported rather than glossed

`_state/chrome-profile/` and `_state/` both moved their directory mtimes during
this wave (to 17:16:12), and `_state/chrome-profile.lock` disappeared. **That is
another actor's browser exiting, not this work.** The profile is intact and no
downgrade migration ran:

- `Last Version` still reads `151.0.7922.34` -- unchanged;
- no `.CHROME_DELETE` directory exists;
- `Default/Network/Cookies` is present, 61440 bytes.

Attribution evidence, in order of strength:

1. `chrome-profile.lock` **already existed** at the wave's first sample, and
   `Last Browser` (17:07:02), `first_party_sets.db` (17:07:03) and
   `BrowserMetrics-spare.pma` (17:07:29) were all written **before this wave's
   first command**. A browser was up before the work started; the 17:15:59 to
   17:16:12 sequence (Crashpad, Variations, Local State, cookie-DB flush, lock
   release) is that process shutting down.
2. Nothing in the suite can open the persistent profile. The only test that
   launches a browser at all, `test_profile_views_fixture.py`, calls
   `pw.chromium.launch(headless=True)` with **no** `user_data_dir` and feeds it
   frozen markup via `page.set_content`. Every other reference to
   `CHROME_PROFILE` in `tests/` is either monkeypatched to a `tmp_path`, read
   as a string for a path-scrubbing assertion, or is
   `test_the_tripwire_would_stop_an_erase_of_the_real_profile` -- which drives
   the real jar path at `_erase` **inside `pytest.raises`** and reaches nothing,
   because the autouse guard raises first.
3. No `chrome.exe` holds the profile now.

Nothing in this wave launched, opened, or wrote to the Chrome profile.

## A trap worth recording: Git Bash `grep -c` lies about line endings

The Python edit scripts read the three source files in text mode, which
converts CRLF to LF, and wrote back with `newline=""`, which does not convert
back. All three files silently became LF in a repo whose working tree is CRLF
(`core.autocrlf=true`, no `.gitattributes`).

**Grepping for a carriage return reported `CRLF=1325` and hid it completely** --
Git Bash's grep reads in text mode, so it counted lines, not carriage returns.
Only a byte-level count found it:

```
$ venv/Scripts/python.exe -c "b=open(f,'rb').read(); print(b.count(b'\r\n'), b.count(b'\n')-b.count(b'\r\n'))"
linkedin_server/auth.py                 CRLF=0      bare-LF=1325
linkedin_server/browser.py  (untouched) CRLF=447    bare-LF=0
```

The commit content would have been correct regardless -- `core.autocrlf=true`
normalizes to LF in the index, which is why `git diff` stayed clean and showed
only the intended hunks. The damage would have been in the working tree: three
LF files among CRLF siblings, flipping back on the next checkout and showing
churn nobody wrote. Restored to CRLF before committing, and the full suite was
re-run on the restored bytes.

**Rule:** verify line endings with a byte count, never with a Git Bash grep for
a carriage return.

## Commit

`5e5fe7e` on `master`. **Not pushed** -- the lead pushes.
