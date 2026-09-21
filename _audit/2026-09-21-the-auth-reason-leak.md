# THE AUTH REASON LEAK: a session credential in a published field, and in the log

Subject: `linkedin_server/auth.py::check_auth`, the request-failure handler.

Ruling applied, not re-derived: `ERROR-MESSAGE-RULED-AT-THE-RAISE`.

Predecessor: `_audit/2026-09-21-what-playwright-quotes.md` section 7, which
REPRODUCED this and deliberately did not repair it. Its reproduction was read
and then **re-derived from scratch on this branch** -- none of its scripts
exist here, so nothing below is inherited. Where this wave's measurement
differs from a relayed one, this document says so.

---

## 0. THE ANSWER, FIRST

A failing `page.request.get` does not raise a sentence. **It renders the whole
request into its own exception text, one header per line, and one of those
lines is `cookie:`.** The identity call is the request that carries the
session, so its failure message carries the session credential.

`check_auth` interpolated that text verbatim into a field it RETURNS and a
line it LOGS. Driven end to end against a real chromium with a synthetic
cookie: **six of six channels carried the credential** -- model, log and
exception, on both the connect-error and the timeout branch.

**FIVE EXITS, not the two the brief named.** The brief named the model, the
log and the `require_auth` exception. Following the VALUE rather than the
FIELD found two more: `session_info` copies the reason into
`live_check.why_not` AND to top level, and `login_via_browser` CONCATENATES it
into a different tool's reason. A search for the key `reason` finds the first;
only following the string finds the second.

**AND THE REPOSITORY'S OWN LEAK GUARD WAS ALREADY POINTED AT THIS FUNCTION AND
WAS GREEN.** That is the finding worth keeping, and section 2 is about it.

| | pre-fix | post-fix |
|---|---|---|
| `$.reason` carries the credential | YES, both branches | no |
| the `logger.info` record carries it | YES, both branches | no |
| `AuthUnknownError`'s message carries it | YES, both branches | no |
| `session_info.live_check.why_not` | YES | no |
| `linkedin_login`'s reason | YES | no |
| the reason still names the failure TYPE | yes | yes |
| the reason still prices the wait | no | **yes, new** |
| the log line still fires | yes | yes, 1 record, value-free |

---

## 1. EVERY BRANCH, AND EVERY EXIT, WITH ITS CHANNEL

### 1.1 The branches of `check_auth` that compose a `reason`

Enumerated by reading the function, then pinned in `REASON_BRANCHES` in the
guard so a seventh cannot arrive untested.

| # | branch | what composes the reason | leaked |
|---|---|---|---|
| B1 | `except Exception as exc` around `page.request.get` | `f"...({type(exc).__name__}: {exc})"` | **YES -- THE DEFECT** |
| B2 | 200 with an identity | no reason; returns `authenticated: true` | n/a |
| B3 | 200 with an empty body | a static sentence | no |
| B4 | 401 / 403 | a static sentence, plus a cookie-PRESENCE clause | no |
| B5 | any other status | `f"HTTP {status}"`, an int off `response.status` | no |
| B6 | `_maybe_corroborate`, authwall landing | `landing.withheld(final_url)` | no -- repaired earlier |

B1 is the only branch that renders an exception. B3-B6 were driven with the
planted jar anyway, because the property this wave installs is about the
branch SET, not about the one branch found leaking.

**B6 IS THE PRECEDENT AND IT IS WORTH READING.** `_corroboration_note`'s
docstring already records this exact channel being found the hard way:
*"`reason` above becomes an exception message -- `require_auth` raises
`NotAuthenticatedError(status["reason"])` -- so the authwall landing it quoted
was the `assert_not_authwall` defect reached by a second path."* The channel
was known. B1 was simply never walked down it.

### 1.2 The five exits the string reaches

| # | exit | channel | who can see it |
|---|---|---|---|
| E1 | `server.py::linkedin_auth_status` returns the dict UNCHANGED | **model** | the model. No `_error`, no `scrub` -- this tool does not pass through either |
| E2 | `logger.info(...)` one line above | **log** | whoever reads the log. `logging.getLogger("linkedin")`, a StreamHandler to stderr, `propagate = False` |
| E3 | `require_auth` raises `AuthUnknownError(status["reason"])` (or `NotAuthenticatedError`) | **exception** | every envelope that renders an exception -- in this package the 48 `except Exception: return _error(exc)` tool bodies |
| E4 | `session_info` copies it to `live_check.why_not` AND to a top-level `reason` | **model** | the model, via `linkedin_session_info` -- a SECOND tool and a second field |
| E5 | `login_via_browser` does `"could not determine ...: " + str(last_status.get("reason"))` | **model** | the model, via `linkedin_login` -- a THIRD tool, reached by CONCATENATION |

**E2 IS THE ONE WITH NO ENVELOPE AT ANY POINT.** Sanitisers live at the tool
boundary; a log record goes around them. `coerce.py` states the rule this
violates in its own docstring: *"THE LOG LINE NAMES THE TYPE AND NEVER THE
VALUE ... a log record is another way out of the process."*

**E5 IS THE ONE A FIELD-SHAPED SEARCH MISSES.** It does not return the dict and
does not copy the key; it concatenates the string into a different tool's
reason. Grepping for `"reason"` finds E1 and E4. Only following the value
finds E5.

### 1.3 What the module's own docstring claims

`auth.py::_cookie_records`:

> Read the raw cookie jar. **Never logged, never persisted, never returned.**
> Values stay inside this module.

Two of those three clauses were false on B1. The invariant is true of every
statement in the module -- and the value left anyway, because a library the
module hands the cookie to writes it back out in its own error text. **An
invariant scoped to a module's own statements cannot see a channel that runs
through a dependency.**

---

## 2. WHY THE SHIPPED LEAK GUARD WAS GREEN -- the part worth keeping

`tests/test_auth.py` already calls `leakwalk.assert_no_leak(result,
PLANTED_LI_AT, caplog=caplog)` against `check_auth`. It has done for weeks. It
is a good instrument -- it reads every encoding, every 12-character run, keys
as well as values, and the log. It was green against a build that was leaking
the whole cookie.

Two tests bracket this defect, and **neither is wrong**:

```
test_a_transport_failure_is_unknown_not_signed_out()          # the LEAKING branch
    page = FakePage(cookies={"li_at": "x"},
                    responses=[RuntimeError("connection reset")])
    ...                                                        # no leak assertion,
                                                               # and nothing to find

test_no_cookie_value_ever_reaches_a_tool_result(caplog)        # the PLANTED needle
    page = planted_cookie_page(responses=[me_response()])      # down the SUCCESS branch
    assert_no_leak(result, PLANTED_LI_AT, caplog=caplog)
```

**Three conditions have to coincide before this defect is visible:**

1. a credential-shaped value in the jar,
2. the request-FAILURE branch, and
3. an exception whose text was composed by the LIBRARY rather than the fixture.

The first test had (2) with a one-character jar and a fixture-authored
message. The second had (1) and (3) is irrelevant to it, down a branch that
interpolates no exception at all. **The needle and the branch never met.**

Condition (3) is the one that is easy to lose even after noticing (1) and (2):
crossing the first two tests -- planted jar plus `RuntimeError("connection
reset")` -- **still passes**, because a fixture's exception message carries
nothing. A test author reasonably concludes the path is clean.

So the property installed here is not "check_auth does not leak". It is:

> Every branch of `check_auth` that can compose a `reason` is driven with a
> credential-shaped needle in the jar AND a library-shaped exception on the
> wire.

---

## 3. THE PRE-FIX REPRODUCTION

Instrument: `scripts/_probe_auth_reason_leak.py`. Two stages, because the
premise and the defect are different facts and merging them would let each
assume the other.

**Stage 1 needs the browser and establishes the PREMISE.** An ephemeral
`chromium.launch(headless=True)` -- never `launch_persistent_context`, never
the configured profile, never a CDP attach, closed in a `finally`. There is no
`page.goto` anywhere in the file; the only network verbs are
`page.request.get` at loopback addresses this process owns and shuts down.
Nothing resolved a public name and nothing reached linkedin.com.

**Stage 2 needs no browser and establishes the REACH.** The REAL `check_auth`,
`require_auth` and `session_info` are driven with the REAL specimen stage 1
captured.

The needle is `tests/leakwalk.PLANTED_LI_AT`: credential-LENGTH,
credential-CHARSET, and visibly a plant. **No real credential was read,
written or printed at any point in this wave.** Every quotation below is
printed with the plant located and replaced, which is also how the committed
artifact stores it.

### 3.1 Stage 1 -- what Playwright quotes, verbatim

```
  branch      : connect_refused
  exception   : playwright._impl._errors.Error
  quotes the planted cookie: True
    | APIRequestContext.get: connect ECONNREFUSED 127.0.0.1:57540
    | Call log:
    |   - \u2192 GET http://127.0.0.1:57540/identity
    |     - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... HeadlessChrome/153.0.8010.12 ...
    |     - accept: */*
    |     - accept-encoding: gzip,deflate,br
    |     - cookie: li_at=<PLANTED-CREDENTIAL-WAS-HERE>

  branch      : timeout
  exception   : playwright._impl._errors.TimeoutError
  quotes the planted cookie: True
    | APIRequestContext.get: Timeout 900ms exceeded.
    | Call log:
    |   - \u2192 GET http://127.0.0.1:57539/identity
    |     ... same four header lines ...
    |     - cookie: li_at=<PLANTED-CREDENTIAL-WAS-HERE>
```

Note `\u2192`. Playwright writes its call log with U+2192 RIGHTWARDS ARROW, so
**the string landing in `$.reason` was not even ASCII**, in a repository that
is strict-ASCII everywhere else. That is not a stylistic observation: it is
free evidence that the string was composed outside this repository. It also
killed the first run of this probe outright, on a cp1252 console.

### 3.2 Stage 2 -- where it went

```
  branch                   : connect_refused
  authenticated            : None
  session_cookie_present   : True
  CHANNEL model  ($.reason): leak=True
  CHANNEL log    (logger)  : leak=True  (1 record(s))
  CHANNEL except (AuthUnknownError): leak=True
  $.reason, with the plant located and replaced:
    | the auth request could not be completed (Error: APIRequestContext.get: connect ECONNREFUSED 127.0.0.1:57540
    | Call log:
    |   - \u2192 GET http://127.0.0.1:57540/identity
    |     - user-agent: Mozilla/5.0 ... HeadlessChrome/153.0.8010.12 ...
    |     - accept: */*
    |     - accept-encoding: gzip,deflate,br
    |     - cookie: li_at=<PLANTED-CREDENTIAL-WAS-HERE>
    | ). This is not a verdict either way.

  branch                   : timeout                     [same three channels, all True]

branches driven                          : 2
branches where Playwright quoted the plant: 2
channels leaking                         : model=2 log=2 exception=2
EXPECTED: leak. REPRODUCED.
```

### 3.3 THE PROBE'S OWN LOG DETECTOR WAS BLIND TWICE, AND BOTH TIMES IT SAID "CLEAN"

Recorded because it is the same disease as section 2, in my own instrument,
inside one hour.

The first two versions of the log collector reported
`CHANNEL log: leak=False (0 record(s))` **while four fully-leaking log lines
were going to stderr in the same run.** An absence check over an empty channel
passes perfectly.

1. `logging.getLogger("linkedin_server")` -- the package name. It is a
   SIBLING of the real logger, not an ancestor. Zero records.
2. `logging.getLogger()` -- the root, which is where pytest's `caplog`
   attaches and therefore looks like the safe universal choice. It is not:
   `config.py` sets `logger.propagate = False` deliberately, because this
   server speaks MCP over stdio and a record reaching stdout corrupts the
   transport. Nothing propagates. Zero records.

The correct wiring is `logging.getLogger("linkedin")`.

**I was not the first.** `tests/conftest.py::_caplog_can_hear_the_linkedin_logger`
carries the identical scar, and its docstring prices it: *"the log half of that
guard could not fire at 14 call sites."* The repository had already paid for
this lesson and I walked into it anyway -- which is the argument for the
autouse fixture being autouse.

**What convicted me was not a control I designed.** It was raw stderr from run
1 disagreeing with my own probe's verdict in the same output. Had I captured
stderr, or run the probe quietly first, the blind version would have shipped
saying the log channel was clean.

---

## 4. THE REPAIR, AND WHAT THE REASON NOW SAYS

One site: `linkedin_server/auth.py::check_auth`, the `except` handler.

**Why here and not at the envelope.** `ERROR-MESSAGE-RULED-AT-THE-RAISE`:
what an error string may carry is decided where the value ENTERS the
exception, never where it leaves, because `server._error` holds a
`playwright...Error` whose text is a timeout and one whose text is a
credential and cannot tell them apart. Here it IS knowable -- **this call site
is the one that hands Playwright the cookie** -- so here is where it is
refused. The shape is `press.disclose`'s, which the ruling already names.

The log line takes the same treatment, per `coerce.py`'s stated rule.

**THE FIELD IS NOT DELETED.** A refusal that says nothing is its own defect,
and "the reason is shorter now" is satisfied by removing it. What survives is
everything provably credential-free AND useful:

* the exception **TYPE** -- the diagnosis that separates *LinkedIn did not
  answer inside the ceiling* (`TimeoutError`) from *the request could not be
  made at all* (anything else). Different problems, different remedies. A type
  name is chosen by whoever wrote the class and cannot carry a runtime value.
* the **ceiling**, `API_TIMEOUT_MS` -- this server's own constant, and the one
  number the library's message carried that we can publish safely. **This is
  new; the pre-fix field did not have it.**
* a sentence saying **what was withheld and why**, so a reader does not file
  the terseness as a bug in the field.
* where it was asked is already beside it, in `checked_against`.

Post-fix, verbatim, driven through the REAL captured specimen:

```
  CHANNEL model  ($.reason): leak=False
  CHANNEL log    (logger)  : leak=False  (1 record(s))
  CHANNEL except (AuthUnknownError): leak=False
    | the auth request could not be completed (TimeoutError, within a ceiling of
    | 20000ms). THE LIBRARY'S OWN MESSAGE IS WITHHELD rather than quoted: it
    | renders the entire request, including the cookie header, so it carries the
    | session credential. The type above is the diagnosis -- a TimeoutError means
    | LinkedIn did not answer inside the ceiling, anything else means the request
    | could not be made at all. This is not a verdict either way.

channels leaking : model=0 log=0 exception=0
EXPECTED: clean. CLEAN.
```

`1 record(s)` is load-bearing. **The log channel still speaks** -- it was not
silenced into passing. A guard that went green because the diagnosis vanished
would be the wrong repair, so both the probe and the guard assert the field
and the record are still THERE.

---

## 5. THE GUARD, SHOWN FAILING

`tests/test_auth_reason_withholds_the_request.py`. **No browser**, so it runs
in CI; a guard that does not run is not one.

The specimen is MANUFACTURED in the test file from a template plus
`PLANTED_LI_AT`. It is NOT read from the probe's committed json: a control that
finds its fixture in ambient repo state passes on the box it was written on
and fails in every clone.

It asserts on BOTH sides, because absence alone is satisfied by deletion:

* **absence** -- `leakwalk.assert_no_leak` over the result AND `caplog`, for
  both the session cookie and the csrf cookie, across all 6 branches and all 5
  exits;
* **presence** -- the reason still names the type, still says `not a verdict`,
  still says what it withheld, still prints the ceiling; the field and the log
  record still exist; the reason is ASCII and contains no `Call log:`,
  `user-agent:` or `cookie:`.

Plus two controls that make the rest mean anything:

* `test_the_needle_is_really_in_the_haystack` -- asserts the specimen CARRIES
  the credential before anything asserts it is absent downstream. Without it,
  a broken template would make every assertion in the file pass vacuously.
* `test_every_reason_branch_is_covered` -- pins `REASON_BRANCHES` at 6 by
  count, so a seventh branch must be driven here to be added at all.

### 5.1 RED against pre-fix `auth.py`, GREEN against the repair

Same file, same run, `auth.py` swapped for `git show HEAD:` and put back:

```
--- PRE-FIX auth.py in place ---
FAILED ...::test_no_branch_of_check_auth_publishes_the_credential[request_connect_refused]
FAILED ...::test_no_branch_of_check_auth_publishes_the_credential[request_socket_hangup]
FAILED ...::test_no_branch_of_check_auth_publishes_the_credential[request_timeout]
FAILED ...::test_require_auth_does_not_raise_the_credential[request_connect_refused]
FAILED ...::test_require_auth_does_not_raise_the_credential[request_socket_hangup]
FAILED ...::test_require_auth_does_not_raise_the_credential[request_timeout]
FAILED ...::test_session_info_why_not_does_not_publish_the_credential
FAILED ...::test_login_result_does_not_republish_the_credential
FAILED ...::test_the_reason_still_names_the_exception_type[connect_refused-Error]
FAILED ...::test_the_reason_still_names_the_exception_type[timeout-TimeoutError]
FAILED ...::test_the_reason_is_ascii_and_short_enough_to_read
11 failed, 10 passed in 2.71s

--- with the repair ---
21 passed in 1.90s
```

The discrimination is exact: the **3 exception branches fail on all 3
channels; the 3 response branches (401 / 999 / 200-empty) pass clean** in the
same run. The guard is not firing on everything.

### 5.2 Regression

```
tests/test_auth.py tests/test_auth_lifecycle.py tests/test_leakwalk.py
tests/test_landing.py                                    204 passed in 24.46s

tests/test_probe_navigation_budget.py tests/test_probe_interaction_budget.py
tests/test_no_committed_identity.py tests/test_no_committed_credential.py
tests/test_tool_envelopes_emit_no_page_string.py       1540 passed in 163.10s
```

`tests/test_auth.py::test_a_transport_failure_is_unknown_not_signed_out`
asserts `"not a verdict" in result["reason"]`. The repaired sentence keeps that
phrase deliberately: the contract it pins is real and was not worth breaking to
save four words. **No existing test was edited, weakened or skipped, and no
`DECLARED_PLANTS` entry was added anywhere.** The probe needed no
`KNOWN_UNGUARDED` entry either, because it never navigates.

---

## 6. THE MODULE CENSUS

Instrument: `scripts/_census_auth_exception_renders.py`. AST, stdlib only.
Machine-readable: `scripts/_census_auth_exception_renders.json`.

### 6.1 METHOD, and what it refuses to guess

For every `except ... as N`, it walks the handler body and classifies each
expression by what it renders of `N`:

* **TYPE_ONLY** -- only `type(N).__name__`. A class name is chosen by whoever
  wrote the class; it cannot carry a runtime value.
* **VALUE** -- the object itself, via f-string, `str(N)`, `%s`, or
  concatenation. This invokes `__str__`, which for a library exception is
  composed by code nobody here controls.

**A site rendering BOTH is a VALUE site.** A type render standing next to a
value render defends nothing, and `f"({type(exc).__name__}: {exc})"` is
precisely the defect repaired here. A census that let the type render mask the
value render would have reported B1 clean.

Sinks: **LOG** (any `logger.*`, **in every argument position**), **RETURN**,
**RAISE**, and assignment-into-a-returned-dict.

**THE TRAP THE INSTRUMENT IS BUILT AROUND.** This package logs LAZILY --
`logger.info("failed: %s: %s", type(exc).__name__, exc)`. The credential is in
`args`, never in the format string. **Every real log-channel site in this
module is that shape**, so a scanner that reads only format strings finds zero
and reports it confidently. `--selftest` pins a case of exactly that shape.

Refusals: a bare `except:` binds no name and is counted UNRESOLVED, not folded
into the clean column. Name REBINDING is not modelled, so a rebound name
over-reports -- asserted as a known limit rather than wished away.

**It reports SITES, never LEAKS.** Whether a given exception's `__str__`
carries a credential depends on the library that raised it and is knowable
only by DRIVING it.

### 6.2 The control -- the census shown failing

```
$ ... --selftest                    $ ... --selftest --flip lazy_value_log
  ok   fstring_return                 FLIPPED lazy_value_log: VALUE -> TYPE_ONLY
  ok   lazy_value_log                 FAIL lazy_value_log: renders=VALUE sinks=['LOG']
  ok   multi_hop                      ok   (the other eight)
  ok   subscript_sink
  ok   type_only_log                SELFTEST 8/9
  ok   type_only_return             EXIT=1
  ok   value_raise
  ok   rebound_is_clean
  ok   bare_handler
SELFTEST 9/9
EXIT=0
```

The fixture is manufactured inside the instrument, not found in the repo.

### 6.3 Result on `linkedin_server/auth.py`, post-repair

| line | function | sink | renders |
|---:|---|---|---|
| 115 | `_cookie_records` | RAISE | **VALUE** |
| 148 | `_warm_session_cookies` | LOG | **VALUE** |
| 263 | `_arm_session_store` | LOG | **VALUE** |
| 342 | `check_auth` | LOG | TYPE_ONLY *(was VALUE)* |
| 347 | `check_auth` | RETURN | TYPE_ONLY *(was VALUE)* |
| 480 | `_maybe_corroborate` | LOG | **VALUE** |
| 939 | `session_info_offline` | RETURN | **VALUE** |
| 941 | `session_info_offline` | RETURN | **VALUE** |
| 1401 | `login_via_browser` | RETURN | TYPE_ONLY |

```
  VALUE rows     : 6   <- worth driving
  TYPE_ONLY rows : 3
  unresolved     : 7   (bare `except:`, nothing bound)
```

### 6.4 The one other cookie-touching site, DRIVEN rather than assumed

`_cookie_records` (line 115) wraps `page.context.cookies(...)` and re-raises
with the same VALUE-render shape -- one function above the docstring claiming
the jar is never logged, persisted or returned. The census can see the shape;
only driving it says whether that call quotes what it was reading. Driven,
same probe, same browser:

```
  branch      : cookie_jar_read_on_closed_context
  exception   : playwright._impl._errors.TargetClosedError
  quotes the planted cookie: False
    | BrowserContext.cookies: Target page, context or browser has been closed
```

**MEASURED CLEAN on the branch I could drive, which is a narrower claim than
"clean".** One failure mode of `context.cookies()` was driven; its other
failure modes were not enumerated. Recorded in RESIDUAL rather than closed.

### 6.5 THE INDEPENDENT SECOND METHOD -- and NEITHER census subsumes the other

The delegated slice landed its instrument (though never its report) while this
document was being written: `scripts/_census_auth_exception_interpolation.py`,
an AST census of the same question built to a different design, with its own
manufactured fixture and a `--selftest` of its own. It was reviewed and run
here before being admitted.

**THIS SECTION WAS WRITTEN ONCE AND IS WRONG IN THE FIRST COMMIT OF THIS
DOCUMENT.** It recorded the slice at 6 hits against my 9 and concluded the
stricter instrument simply under-reported. Between that paragraph and the
freeze the child kept working: its selftest went 9/9 to 10/10 and its census
went 6 hits to 7. **A number one agent hands another is a reading with a
timestamp the receiver cannot see**, and I published one without re-taking it.
The corrected reconciliation is below, re-run at 20:35 against the version
actually committed.

Run over the same file: the slice finds **7**, mine finds **9**, and the union
is **10 distinct sites**. The overlap is 6. Each instrument finds rows the
other structurally cannot.

**The 6 both find, line for line:** 115 `_cookie_records` RAISE VALUE,
148 `_warm_session_cookies` LOG VALUE, 263 `_arm_session_store` LOG VALUE,
342 `check_auth` LOG TYPE_ONLY, 361 `check_auth` RETURN TYPE_ONLY,
480 `_maybe_corroborate` LOG VALUE.

**The 3 only MINE finds** -- all confirmed real by reading the source:

| row | returned? | verdict |
|---|---|---|
| `session_info_offline:939` `jar_error = scrub(str(exc))` | **YES** -- `jar_error` lands in `out["credential_source"]` via an f-string, and in `_credential(..., unreadable=jar_error)` | **a real `VALUE` x `RETURN` site** |
| `session_info_offline:941` `jar_error = scrub(f"...{exc}")` | **YES** -- same | **same** |
| `login_via_browser:1401` `stored = {... f"harvest raised {type(exc).__name__}"}` | YES -- via `"session_stored": stored` | real, but `TYPE_ONLY`, so no risk |

*Cause:* the slice's RETURN sink requires the taint to sit inside a dict the
function returns. Here it is assigned to a plain local and the publishing dict
is built **twenty lines later**, so its dataflow stops at the assignment. Mine
marks every assignment `ASSIGN->RETURN?` -- a deliberately cruder sink that
over-reports and forces a human read.

**The 1 only THE SLICE finds, and it is a class mine cannot see at all:**

| row | why mine missed it |
|---|---|
| `check_auth:441` `f"the identity call returned HTTP {status}"` | `status` is `response.status` -- an attribute off a RESPONSE object, not an exception. My census tracks only `except ... as N` names, so this taint class is outside its vocabulary by construction. The slice models it as `T3` |

That row is branch B5, which I had classified by READING as "an int off
`response.status`" and parked in RESIDUAL 7.3 as *"trusted to be an int"*. The
slice is right to flag it: the trust is real but it is an assumption about
Playwright, not a property of this code. The guard drives that branch
(`http_999_unservable`) with the planted jar and it passes clean.

**THE LESSON IS NOT THAT ONE INSTRUMENT WON.** It is that "a census of
exception interpolations" and "a census of tainted values reaching a string"
are different questions that look like one question, and each instrument
answered the one it was built for. *A census that folds its own blind spot
into the clean column is worse than no census* -- so both are committed, both
keep their selftests, and neither is retired. The slice models name rebinding,
which mine does not; mine follows a local into a deferred dict, which the
slice does not.

### 6.6 Disagreement with the coordinator's scan, reconciled

The coordinator's ruling reports **16 candidate sites in `auth.py`** (of 159
across 15 modules), master @ `a46736f`, 20:10. My census reports **9 rows plus
7 unresolved**.

**The numbers are not in conflict; the units differ.** 9 + 7 = 16. The
coordinator counted candidate SITES including bare `except:` handlers; this
census separates the 7 bare handlers into UNRESOLVED because nothing is bound
there to render. **Both counts are right and they agree exactly.** I was told
to trust mine over the coordinator's if they disagreed; they do not.

---

## 7. RESIDUAL -- what is still reachable, named for a successor

### 7.1 Still live in `auth.py`, shape present, not driven

Four VALUE rows remain in this module. None was repaired: the brief scoped this
wave to the `check_auth` defect, and a change made on a shape rather than a
measurement is the thing this repository keeps calling out.

* **`_warm_session_cookies:148` and `_maybe_corroborate:480` (LOG).** Both
  render a `BROWSER.goto` exception. The predecessor measured navigation
  errors quoting the address ASKED FOR (class `OURS`, publishable under
  `ERROR-URL-ASKED-FOR-OR-NOTHING`) -- on the net-error and timeout branches,
  with the landing proven visited. **Relayed, not re-driven here.** Cheap to
  settle with the probe already on disk.
* **`_arm_session_store:263` (LOG).** Renders an exception from
  `SESSION_STORE.save_from_context(context, ...)`, which READS THE CONTEXT'S
  COOKIES. A serialisation failure quoting the object it was writing is the
  hazard. **Not driven. The most credential-adjacent of the four.**
* **`session_info_offline:939,941` (RETURN).** Renders a `cookie_jar` exception
  from the ON-DISK cookie database, and it is RETURNED. It is wrapped in
  `scrub`, which is `paths.relativise_known` -- path substitution by exact
  match. The predecessor measured `scrub` removing **0 characters** from a
  library message. **A sanitiser that knows paths cannot clean a credential**,
  so the wrap is not a defence here. Not driven.

### 7.2 The class, and the two cuts that matter more than the total

From the coordinator's scan, recorded here so a successor starts from a
measurement. **These are candidate sites located by parsing -- "worth driving",
never "leaks".**

```
CANDIDATE SITES: 159 across 15 modules
  by kind: f-string 108, LOG 48, str() 3
  dom.py 87 | auth.py 16 | browser.py 14 | writes.py 9 | cdp_bridge.py 6
  preflight.py 5 | notify_cost.py 4 | session_store.py 4
```

* **The credential subset is not the big one.** `dom.py`'s 87 are
  overwhelmingly extraction errors carrying PAGE TEXT -- a different class,
  partly covered by the shipped page-text guards. Credential risk concentrates
  in the modules that actually hold cookies and tokens: `auth.py`,
  `browser.py`, `cdp_bridge.py`, `session_store.py`.
* **48 sites are the LOG channel, which has no envelope at any point.**
  Sanitisers sit at the tool boundary; logging goes around them. This wave's
  own defect had a log line one row above the returned field, and it was the
  easier of the two to miss.

`scripts/_census_auth_exception_renders.py` takes `--path`, so it runs over
any of those modules unchanged.

### 7.3 What this repair does NOT close

* **The type name is trusted.** `type(exc).__name__` is safe because classes
  are defined by code. A dynamically-built class name (`type(page_text,
  (Exception,), {})`) would defeat it. Nothing in `linkedin_server` does this;
  **this wave's own probe does**, from a controlled name. Recorded for honesty,
  not as a live hazard.
* **`response.status` in B5 is trusted to be an int.** Real Playwright
  guarantees it. A stand-in need not.
* **The guard's specimen is a RECORDED shape.** It pins that *this repository*
  does not republish an exception's text -- which is the durable property, and
  is independent of Playwright's formatting. If Playwright changes its call-log
  format the guard still holds; if it starts rendering a credential somewhere
  new, only re-running the probe would find it. The probe is committed for that
  reason and needs a browser.
* **Other `page.request` failure modes** -- DNS failure, TLS failure, a 3xx
  loop -- were not driven. Two were, and both leaked, so the class is
  established; the enumeration is not.

### 7.4 Process residue

* A delegated slice (`auth-interp-census`) was spawned for this census and
  **had produced no file on disk after ~35 minutes**, measured by
  `find -newermt`, not inferred. I derived the census myself rather than wait
  on a report that might never arrive. Its instrument then landed at 20:25
  while this document was being written; it was reviewed, run, and its result
  reconciled against mine in section 6.5 -- where it turned out to
  under-report the two highest-stakes rows. **Deriving it myself was the right
  call and the duplicate was not waste:** the disagreement between the two
  methods is the only reason the deferred-publication blind spot was found at
  all.
* **THE CHILD WAS STILL WRITING THAT FILE AT FREEZE** -- mtime 20:28:38,
  twenty-one seconds before the check, with the file having grown since its
  selftest passed. Its slice report `_audit/_slice-auth-interp-census.md` had
  not appeared. A mid-write snapshot is not a reviewable artifact, so the
  file's disposition is recorded in section 8 rather than assumed, and the
  cross-check in 6.5 stands on a version that was read and run here.
* No live LinkedIn page was needed for any of this, and none was touched. The
  predecessor's finding holds: **this was a technical question wearing a
  permission costume.**

---

## 8. FILES

| path | what |
|---|---|
| `linkedin_server/auth.py` | **THE REPAIR.** One handler: the log line and the `reason`. +50 / -3 |
| `tests/test_auth_reason_withholds_the_request.py` | **THE GUARD.** 21 assertions, no browser, 6 branches x 5 exits, shown RED (11 failed) against pre-fix |
| `scripts/_probe_auth_reason_leak.py` | The red proof. Two stages, `--expect leak` / `--expect clean`, `--capture` / `--replay` |
| `scripts/_probe_auth_reason_leak.json` | The captured specimens, plant REPLACED by a placeholder -- the artifact carries no credential shape |
| `scripts/_census_auth_exception_renders.py` | The census. `--selftest` 9/9, `--flip` shows it red |
| `scripts/_census_auth_exception_renders.json` | The census result, machine-readable |
| `scripts/_census_auth_exception_interpolation.py` | The delegated slice's INDEPENDENT census -- reviewed and run here, `--selftest` 9/9, models rebinding. **Adopt-committed in a separate commit, credited**, because the child was still writing it at freeze; see 6.5 and 7.4. Its slice report never arrived |
| `_audit/2026-09-21-the-auth-reason-leak.md` | this document |

`_audit/INDEX.md` and `_audit/RULINGS.md` are DERIVED and were regenerated
with their build scripts, never hand-merged.

**NOTHING OUTSIDE `auth.py` WAS EDITED IN `linkedin_server/`.** Nine other
waves are or were live; the four remaining VALUE rows in section 7.1 and the
159-site class in 7.2 are named for a successor rather than taken.
