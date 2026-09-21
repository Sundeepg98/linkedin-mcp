# WHAT PLAYWRIGHT QUOTES: the parked question, measured offline

Subject: section 7 of `2026-09-21-what-the-browser-said.md`, which parked ONE
case as needing the operator's authorisation for a live-LinkedIn run -- the
case where the BROWSER ITSELF quotes page content in its own error message.

Ruling in force: `ERROR-MESSAGE-RULED-AT-THE-RAISE`.

---

## 0. THE ANSWER, FIRST

**THE LIVE ACCOUNT WAS NEVER NEEDED, AND THE PARKED QUESTION WAS A TECHNICAL
UNKNOWN WEARING A PERMISSION COSTUME.** Playwright does not know what site it
is looking at. Every string in this document was raised against a planted
local page in an ephemeral chromium this process started and stopped. Nothing
navigated to linkedin.com, nothing attached to the operator's Chrome on 9224,
nothing touched the persistent profile.

**AND THE LEAD WAS RIGHT, TWICE OVER.** A strict mode violation enumerates
every matched element with its FULL OUTER HTML -- id, class, every attribute
value and its text -- and then appends an `aka get_by_text("<the element's
text>")` suggestion that quotes the text a second time. A sanitiser that
scrubs paths does nothing to it: measured, `scrub()` removed **0 characters**
from such a message.

**BUT STRICT MODE IS NOT THE WIDEST CHANNEL, AND THE WIDEST ONE IS NOT ABOUT
PAGE TEXT AT ALL.** A failing `page.request.get` renders its own call log into
`str(exc)`, and that call log **enumerates every request header, including
`cookie:`**. This package makes exactly one such request -- the identity call
in `auth.py::check_auth` -- and interpolates `str(exc)` straight into a field
it returns to the caller. Driven end to end below: the session cookie's value
lands in `$.reason` of `linkedin_auth_status`, and in the log line beside it.
`auth._cookie_records` states in its own docstring that those values are
*"Never logged, never persisted, never returned"*. All three clauses are false
on that path.

Section 7 asked whether to take a trade blind or spend a live run. **Neither.
The trade was measurable offline, the answer is not the one the trade assumed,
and the remedy is not at the envelope.**

| section 7 said | measured |
|---|---|
| *"No needle this package controls travels that path, so no offline instrument can measure it"* | **false.** The needle does not have to be the package's. It has to be the PAGE'S, and a planted page supplies one. 64 cases driven, 0 failed declarations |
| *"the only reading anyone has ... says those interpolate the address we requested"* | **CORROBORATED BY DRIVING**, including through a real 302 to a site-chosen address (section 3). The source-reading was right |
| *"The only remedy is type-only at `_error`"* | **false.** The provenance IS knowable at the raise for every class found here, which is what the ruling already says. Section 6 gives the three shapes |
| the residue is *"a trade rather than a question of fact"* | it was a question of fact. It took a `set_content` call and a loopback socket |

---

## 1. WHAT WAS DRIVEN, AND THE EVIDENCE THAT NO LIVE PAGE WAS INVOLVED

Instrument: `scripts/_probe_what_playwright_quotes.py`. Playwright **1.63.0**,
chromium reporting `HeadlessChrome/153.0.8010.12`, launched with
`chromium.launch(headless=True)` -- an ephemeral profile, never
`launch_persistent_context`, never `config.CHROME_PROFILE`, never a CDP attach.
The context and browser are closed in a `finally`.

Two page sources, both local:

* `page.set_content(<a planted document>)` for everything DOM-shaped.
* a `http.server.ThreadingHTTPServer` on `127.0.0.1:0` that this process starts
  and shuts down, for everything navigation-shaped. It exists because ONE
  question needs an address the SITE chose rather than one we asked for, and a
  302 is the only honest way to produce one.

Every planted value is an obviously synthetic token (`ZQTEXTZQ`, `ZQATTRZQ`,
`ZQCOOKIEZQ`, ...). **No measurement in this wave produced a real string**, so
there is nothing withheld from this document.

### 1.1 THE AXIS, WHICH IS THE RULING'S AXIS AND NOT A CONVENIENT ONE

Every sentinel is tagged by PROVENANCE before it is planted, because
`ERROR-MESSAGE-RULED-AT-THE-RAISE` turns on whether **a value the PAGE chose**
entered the exception, and no other axis answers that:

* `PAGE_CHOSEN` -- element text, an attribute value, an id, a class, the
  document title, an option label, an input value, an href, a JSON body, a
  redirect landing, a cookie value.
* `OURS` -- a selector string, a requested address, a header we set.

A case whose only hits are `OURS` is reported as `OURS_ONLY`, never as an echo
and never as silence, because the two behave differently under composition:
**an `OURS` echo becomes a `PAGE_CHOSEN` echo the moment the composing
expression reads from the page.** Section 5.2 settles whether it does here.

---

## 2. THE ECHOES -- 32 cases, each proven by CALLING

Every row below raised, and the named PAGE_CHOSEN classes were found inside
`str(exc)`.

| api | exception type | page-chosen classes echoed |
|---|---|---|
| `Locator.text_content` | `Error` | attr, class, id, text |
| `Locator.inner_text` | `Error` | attr, class, id, text |
| `Locator.inner_html` | `Error` | attr, class, id, text |
| `Locator.get_attribute` | `Error` | attr, class, id, text |
| `Locator.is_visible` | `Error` | attr, class, id, text |
| `Locator.wait_for` | `Error` | attr, class, id, text |
| `Locator.element_handle` | `Error` | attr, class, id, text |
| `Locator.evaluate` | `Error` | attr, class, id, text |
| `Locator.bounding_box` | `Error` | attr, class, id, text |
| `Locator.click` | `Error` | attr, class, id, text |
| `Locator.fill` | `Error` | attr, class, id, text |
| `page.get_by_text(..).text_content` | `Error` | attr, class, id, text |
| `Locator.filter(has_text=..).text_content` | `Error` | attr, class, id, text |
| `Page.text_content(sel, strict=True)` | `Error` | attr, class, id, text |
| `Page.wait_for_selector(sel, strict=True)` | `Error` | attr, class, id, text |
| `Locator.wait_for(state="visible")` on a hidden node | `TimeoutError` | the hidden node's outer HTML |
| `Page.wait_for_selector(state="visible")`, NOT strict | `TimeoutError` | the hidden node's outer HTML |
| `Locator.click` intercepted by an overlay | `TimeoutError` | the INTERCEPTING node's outer HTML, and the target's href |
| `Page.click(sel)` on a 3-element selector | `TimeoutError` | the first match's outer HTML, and the overlay's |
| `Page.evaluate` whose JS throws naming what it read | `Error` | text, title |
| `Page.evaluate`, `JSON.parse` over page text that is not JSON | `Error` | text |
| `Page.evaluate` with a page value passed back as an arg | `Error` | text |
| `page.request.get`, connect error, context holding a cookie | `Error` | **the cookie value** |
| `page.request.get`, timeout, context holding a cookie | `TimeoutError` | **the cookie value**, the landing |
| `expect(..).to_have_text` | `AssertionError` | attr, class, id, text |
| `expect(..).to_have_attribute` | `AssertionError` | attr, class, id, text |
| `int(<page text>)` | `ValueError` | text |
| `float(<page text>)` | `ValueError` | text |
| `[].index(<page text>)` | `ValueError` | text |
| `set().remove(<page text>)` | `KeyError` | text |
| `{}[<page text>]` | `KeyError` | text |
| `datetime.strptime(<page text>, ..)` | `ValueError` | text |

### 2.1 THE THREE MECHANISMS, WHICH ARE NOT ONE MECHANISM

A count of echoing methods is the wrong unit -- they are echoing for three
independent reasons, and closing one leaves the other two open.

**(a) THE STRICT MODE ENUMERATION.** Raised by every `Locator` method when the
locator matches 2 or more. Verbatim, against the planted page:

```
Locator.text_content: Error: strict mode violation: locator(".card") resolved to 3 elements:
    1) <div id="ZQIDZQ-1" class="card ZQCLASSZQ" data-probe="ZQATTRZQ-1">...ZQTEXTZQ-alpha...</div> aka get_by_text("ZQTEXTZQ-alpha")
    2) <div id="ZQIDZQ-2" class="card ZQCLASSZQ" data-probe="ZQATTRZQ-2">...ZQTEXTZQ-beta...</div> aka get_by_text("ZQTEXTZQ-beta")
    3) <div id="ZQIDZQ-3" class="card ZQCLASSZQ" data-probe="ZQATTRZQ-3">...ZQTEXTZQ-gamma...</div> aka get_by_text("ZQTEXTZQ-gamma")

Call log:
  - waiting for locator(".card")
```

Note what the `aka` suffix is: Playwright helpfully suggests a BETTER LOCATOR,
and the better locator it suggests is built out of the element's own text. It
quotes the page twice per element for the user's benefit.

**(b) THE ACTIONABILITY CALL LOG, WHICH NEEDS NO STRICT VIOLATION AT ALL.**
Any action or wait that has to retry prints what the locator resolved to:

```
Page.wait_for_selector: Timeout 900ms exceeded.
Call log:
  - waiting for locator("#hiddenone") to be visible
    9 x locator resolved to hidden <div class="gone" id="hiddenone" data-probe="ZQHIDDENZQ">ZQHIDDENZQ-text</div>
```

and, on a click, the outer HTML of whatever got in the way:

```
      - <div id="cover" data-probe="ZQOVERLAYZQ">ZQOVERLAYZQ-text</div> intercepts pointer events
```

**This is the one that matters most for this package**, because it fires on a
`wait_for(state="visible")` against a SINGLE element -- no multi-match needed,
and `.first` does not help.

**(c) THE REQUEST HEADER DUMP.** `APIRequestContext` renders the whole request:

```
APIRequestContext.get: connect ECONNREFUSED 127.0.0.1:53681
Call log:
  - GET http://127.0.0.1:53681/identity
    - user-agent: Mozilla/5.0 (...) HeadlessChrome/153.0.8010.12 ...
    - accept: */*
    - accept-encoding: gzip,deflate,br
    - cookie: li_at=ZQCOOKIEZQ-val
```

Measured on both branches: connect error and timeout. Section 7 follows it
into this package.

---

## 3. PROVEN SILENT -- 25 cases, and WHY each is silent

A silence has a cause, and the causes are not interchangeable. Eleven of these
are silent because they **never raise**, which is a different fact from
declining to quote, and the table says which is which.

| api | outcome | why it carries nothing |
|---|---|---|
| `Page.text_content(sel)` | did not raise | NOT STRICT: takes the first of 3 |
| `Page.inner_text(sel)` | did not raise | NOT STRICT |
| `Page.get_attribute(sel, name)` | did not raise | NOT STRICT |
| `Page.wait_for_selector(sel)` | did not raise | NOT STRICT by default |
| `Locator.first.text_content` | did not raise | qualified: cannot violate strict |
| `Locator.last.text_content` | did not raise | qualified |
| `Locator.nth(0).text_content` | did not raise | qualified |
| `Locator.count` | did not raise | set-wide |
| `Locator.all_text_contents` | did not raise | set-wide |
| `Locator.all_inner_texts` | did not raise | set-wide |
| `Locator.evaluate_all` | did not raise | set-wide |
| `Locator.text_content`, literal selector, no match | `TimeoutError` | the call log quotes the SELECTOR only, and this one is a literal |
| `Locator.nth(9).text_content` | `TimeoutError` | nothing resolved, so nothing to describe |
| `Page.wait_for_function` | `TimeoutError` | quotes our expression, not the page |
| `Page.wait_for_url` | `TimeoutError` | quotes the PATTERN; does NOT print the current url |
| `Page.wait_for_load_state` | did not raise | -- |
| `Page.set_content` | `TimeoutError` | **the case section 7 already had, re-driven and confirmed** |
| `Page.evaluate`, TypeError on a missing node | `Error` | V8 names the operation, not the document |
| `Page.evaluate`, syntax error | `Error` | quotes our script's shape, not page content |
| `Page.evaluate`, `JSON.parse` of STRUCTURALLY bad page JSON | `Error` | reports a POSITION -- see 4.1 |
| `APIResponse.json()` over a page-chosen body | `JSONDecodeError` | Python's decoder reports a position |
| `expect(..).to_have_count` | `AssertionError` | the actual value is an integer |
| `[].remove(<page text>)` | `ValueError` | does not quote -- see 4.2 |
| `set().discard(<page text>)` | did not raise | -- |
| `json.loads(<page text>)` | `JSONDecodeError` | does not quote |

### 3.1 OURS_ONLY -- 7 cases where only a value WE composed came back

| api | what came back |
|---|---|
| `Locator.text_content`, selector carrying a token | **the selector, verbatim** |
| `Locator` with `:has-text('<token>')`, no match | **the needle, verbatim** |
| `Page.goto`, nothing listening | the address we ASKED FOR |
| `Page.goto`, 302 to a site-chosen address that then dies | the address we ASKED FOR |
| `Page.goto`, 302 to a site-chosen address that hangs | the address we ASKED FOR |
| `Page.goto`, malformed url | the address we ASKED FOR |
| `page.request.get`, nothing listening | the address we ASKED FOR |

**THE NAVIGATION ROWS CARRY THEIR OWN POSITIVE CONTROL.** "The landing is not
quoted" is worth nothing unless the landing was VISITED, so the loopback
server records every path the browser asked for and the verdict engine FAILS
the row as `VACUOUS` if the redirect target is not among them. Recorded:

```
nav.redirect_then_reset   -> server saw: ['/ZQREQZQ/redirect-me',   '/ZQLANDZQ-landing/page']
nav.redirect_then_timeout -> server saw: ['/ZQREQZQ/redirect-slow', '/ZQLANDZQ-landing/slow']
```

The landing was reached in both, and the error still named the requested
address. **The `$.url` wave's source-reading is now corroborated by driving**,
on both the net-error and the timeout branch.

---

## 4. THE NEAR-MISS TRAPS, ALL FOUND BY CALLING AND NONE BY READING

The brief warned that members of one apparent family behave differently. Four
were found here, and **three of them would have been got wrong by reasoning
from the name**.

### 4.1 ONE FUNCTION, TWO BRANCHES, OPPOSITE ANSWERS

`JSON.parse` inside `page.evaluate`, over page text, in the same V8:

```
structural badness  -> SyntaxError: Expected ':' after property name in JSON at position 10 (line 1 column 11)
not-JSON-at-all     -> SyntaxError: Unexpected token 'Z', "ZQTEXTZQ-alpha" is not valid JSON
```

The first quotes nothing. The second quotes the input. **I declared this case
ECHO, drove only the structural branch, and the probe convicted me** -- the
verdict engine's first genuine red was against my own prediction. The fix was
to drive BOTH branches, which is how the quoting one was found at all.

### 4.2 THE STDLIB FAMILY, RE-DRIVEN RATHER THAN CITED

| call | quotes its input |
|---|---|
| `int(s)` / `float(s)` | YES |
| `[].index(s)` | YES |
| `[].remove(s)` | **NO** |
| `set().remove(s)` | YES |
| `set().discard(s)` | does not raise |
| `{}[s]` | YES |
| `datetime.strptime(s, fmt)` | YES |
| `json.loads(s)` | **NO** |

Re-measured rather than quoted from the memory that records it, because a
recorded behaviour is a reading with a timestamp.

### 4.3 `Page.click(sel)` IS NOT STRICT; `Locator.click()` IS

The same verb, one letter of receiver apart. `page.click(".card")` against 3
matches printed `resolved to 3 elements. Proceeding with the first one:
<outer HTML>` and picked one. `page.locator(".card").click()` raised. Every
`Page`-level selector method takes `strict=False` by default; every `Locator`
method is strict always. **A census built on method names alone would have put
these in the same bucket.**

### 4.4 THE FIXTURE BUGS THIS PROBE HAD, BOTH OF WHICH MANUFACTURED SILENCE

Recorded because both produced a clean-looking negative that was not one.

1. **A failed `goto` blew the page away and three later cases ran against a
   blank document**, recording `expect(..).to_have_text` as SILENT with
   `Actual value: None / element(s) not found`. It is in fact one of the
   loudest echoes in the corpus -- `Actual value:`, the resolved element's
   outer HTML, AND an aria snapshot. The repair is `_replant()` before every
   case.
2. **A routed redirect never fired.** The first navigation fixture pointed at a
   reserved-TLD host behind `context.route`; the redirect hop was not routed
   and came back `ERR_NAME_NOT_RESOLVED`, so the row asserted something about a
   landing that was never visited. The repair is the loopback server plus the
   VACUOUS check in 3.1, which now fails that shape on purpose.

**A proven-silent claim built on a page that was not there is a fixture bug
wearing a measurement's clothes**, and both of mine were exactly that.

---

## 5. THE CROSS-REFERENCE: which of these can this package actually raise

Instrument: `scripts/_census_strict_mode_call_sites.py` (AST, stdlib only,
`--selftest` with 27 inline cases). Slice report:
`_audit/_slice-strict-call-sites.md`. Machine-readable:
`scripts/_census_strict_mode_call_sites.json`.

**METHOD.** Every `Call` whose func is an `Attribute` naming one of 37 strict
`Locator` methods (or `wait_for_selector`) is a candidate. The receiver is
resolved by walking the enclosing function body and tracking simple `Name`
bindings to locator-valued expressions, including multi-hop aliases, `for`
targets bound from `.all()` / `element_handles()`, and lexical shadowing. A
chain ending in `.first` / `.last` / `.nth(...)` is IMMUNE; a `Page`-level
selector call without `strict=True` is IMMUNE; `strict=True` is VULNERABLE.
**An unresolvable receiver is `UNRESOLVED` and is folded into neither bucket.**

| verdict | count |
|---|---:|
| VULNERABLE | 6 |
| IMMUNE | 74 |
| UNRESOLVED | 5 |
| total candidates | 85 |

IMMUNE by reason: `.first` 27, `.nth(...)` 19, page-level-non-strict 28,
`.last` 0, `.all()` element 0. The last two are measured zero, not assumed.

**INDEPENDENT CROSS-CHECK.** I ran a deliberately different method of my own
before reading the slice -- render the receiver with `ast.unparse` and decide
on the rendered text, with no name resolution -- which finds 83 candidates and
over-reports by construction. It named the SAME SIX. Two methods, one answer.

### 5.1 THE SIX, REVIEWED BY READING THEM -- AND 0 OF 6 ARE REACHABLE TODAY

The classifier is correctly conservative: it does not model runtime guards. I
do, because the question is whether a leak is LIVE.

| site | shape | verdict |
|---|---|---|
| `dom.py::read_apply_modal` x3 `get_attribute`, x1 `is_visible` | preceded by `count = int(await submit.count())` with `if count != 1: return`; and every await is inside `try/except Exception` that substitutes `None`/`False` | **unreachable, and swallowed even if reached** |
| `dom.py::read_radio_label_binding` `control.get_attribute("id")` | preceded by `found = int(await control.count())` with `if found != 1: return`; **NOT inside a try** | unreachable while the guard holds; **would escape if it did not** |
| `dom.py::read_radio_label_binding` `labels.get_attribute("for")` | preceded by `matching = int(await labels.count())` with `if matching != 1: return`; **NOT inside a try** | same |

**SO THE STRICT-MODE CHANNEL IS CLOSED IN THIS PACKAGE TODAY, BY A GUARD
RATHER THAN BY A QUALIFIER.** That distinction is the finding, not a
footnote: `count()` and `get_attribute()` are TWO SEPARATE ROUND TRIPS to a
page this server does not control, and LinkedIn renders asynchronously. A
second matching node appearing between the two turns the guard into a race,
and the two unwrapped sites then raise a strict mode violation which
propagates to the tool body's `except Exception as exc: return _error(exc)`
and is published. It is narrow. It is not impossible, and `.first` would cost
nothing at either site.

The 5 UNRESOLVED are all name collisions with the strict-method vocabulary and
none is a locator: `dict.clear()` x3, `asyncio.wait_for(...)`,
`page.keyboard.press(...)`.

### 5.2 THE SELECTOR CHANNEL: 73 interpolated sites, 0 page-derived

Because a timeout echoes the selector verbatim (3.1), a selector composed from
a page value is its own echo path. The slice enumerated 73 sites building a
selector from a non-literal (72 `.locator(...)`, 1 `wait_for_selector`; shapes:
53 a bare name, 11 a builder call, 6 concatenation, 2 f-string, 1 subscript).
The slice was told not to judge provenance; I did, by resolving each
interpolated name inside its enclosing function:

    module constant or pure local     66
    from a CALLER PARAMETER            5
    flagged as page-derived candidate  2   <- both false positives, read below

The two flagged are in `dom.py::read_typeahead_options`: one iterates the
module constant `TYPEAHEAD_OPTION_SELECTORS`, the other uses
`out["selector"]`, which is `typeahead_option_selector(needle)` over the
function's own `needle` parameter. My heuristic flagged them only because
`out` is assigned from an `await` elsewhere in the same function.

**NO SELECTOR IN THIS PACKAGE IS BUILT FROM A VALUE READ OFF THE PAGE.** The
conditional class is therefore not live, and the selector echo is class 2
(`OURS`), publishable under the ruling.

### 5.3 THE CHANNEL THE CENSUS CANNOT SEE

2.1(b) fires on `wait_for(state="visible")` against a SINGLE element. It is
not a strict-mode site, so it is in the census's IMMUNE column and is still an
echo. `linkedin_server` contains 4 `.wait_for(` and 1 `.wait_for_selector(`.
**A census of strict-mode sites is not a census of echo sites**, and this
document should not be read as if it were. The instrument for the wider sweep
is not built; it is named in section 10.

---

## 6. WHAT REACHES THE ENVELOPE

Instrument: `scripts/_probe_playwright_error_reaches_the_envelope.py`. It
catches a REAL strict mode violation from the browser -- the exception object
is not constructed by the probe -- and hands it to the shipped
`server._error`.

    PATH 1  BARE      Playwright exception -> server._error   PUBLISHED
    PATH 2  WRAPPED   ExtractionFailedError(...) from exc      NOT published
    PATH 3  SCRUB     config.scrub over the raw message        0 characters removed

Path 1, verbatim, as `$.message`:

```
  $.error   = 'unexpected'
  $.message = Error: Locator.text_content: Error: strict mode violation: locator(".card") resolved to 2 elements:
                  1) <div class="card" id="ZQIDZQ-1" data-probe="ZQATTRZQ-1">ZQTEXTZQ-alpha</div> aka get_by_text("ZQTEXTZQ-alpha")
                  2) <div class="card" id="ZQIDZQ-2" data-probe="ZQATTRZQ-2">ZQTEXTZQ-beta</div> aka get_by_text("ZQTEXTZQ-beta")

              Call log:
                - waiting for locator(".card")
```

The pipe, measured on this tree:

* `server.py` has **48** `except Exception` handlers that call `_error(exc)`.
  That is every tool body.
* `_error`'s generic branch is
  `{"error": "unexpected", "message": scrub(f"{type(exc).__name__}: {exc}")}`.
* `scrub` is `paths.relativise_known`, which substitutes this server's own
  directories by EXACT match. It has nothing to say about outer HTML.
* Of **124** page-taking readers in `linkedin_server`, **51 contain no `try`
  at all**, so a library exception raised inside them reaches the tool body
  raw.

**PATH 2 IS THE EXISTING DEFENCE AND IT WORKS.** A reader that catches and
raises `ExtractionFailedError(...) from exc` publishes only the package's own
sentence; the Playwright text survives on `__cause__`, which `_error` never
reads. That is worth stating plainly because it is the cheapest available
repair shape and this package already uses it in 73 of 124 readers.

---

## 7. THE LIVE ONE: a session cookie in a published field

Red proof: `scripts/_probe_the_auth_reason_publishes_a_cookie.py`. It catches a
REAL `APIRequestContext` failure from a real browser whose context holds a
synthetic cookie, then calls the REAL `auth.check_auth` with a planted page
whose `request.get` raises that specimen.

`auth.py::check_auth`:

```python
    except Exception as exc:
        logger.info("auth check request failed: %s: %s", type(exc).__name__, exc)
        result = {
            ...
            "reason": (
                f"the auth request could not be completed ({type(exc).__name__}: "
                f"{exc}). This is not a verdict either way."
            ),
        }
```

`server.py::linkedin_auth_status` returns that dict unchanged. It does not pass
through `_error`. It does not pass through `scrub`.

Driven result, with a synthetic cookie value:

```
  $.authenticated          = None
  $.session_cookie_present = True
  $.reason carries the cookie value: True

  $.reason, verbatim:
    | the auth request could not be completed (Error: APIRequestContext.get: connect ECONNREFUSED 127.0.0.1:53681
    | Call log:
    |   - GET http://127.0.0.1:53681/identity
    |     - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... HeadlessChrome/153.0.8010.12 ...
    |     - accept: */*
    |     - accept-encoding: gzip,deflate,br
    |     - cookie: li_at=ZQCOOKIEZQ-val
    | ). This is not a verdict either way.
```

and the `logger.info` line above it prints the same thing.

**WHY THIS IS THE SHARPEST FORM OF THE FINDING.** `auth._cookie_records`
documents an invariant:

> Read the raw cookie jar. Never logged, never persisted, never returned.
> Values stay inside this module. Only derived facts -- a name, a presence, an
> expiry timestamp -- ever reach a tool result.

The invariant is about what THIS MODULE does with the jar, and it is true of
every line in it. The value leaves anyway, because a library the module hands
the cookie to writes it back out in its own error text. **An invariant scoped
to a module's own statements cannot see a channel that runs through a
dependency**, which is the same shape as `landing.py`'s finding one rule up:
a scrubber that knows paths cannot clean a name.

**REACHABILITY.** Both branches were driven: connect error and timeout. The
identity call runs on every `linkedin_auth_status`, every login wait poll, and
the session-store arm. Any transport failure takes this branch.

**I DID NOT REPAIR IT.** Six waves are live and `auth.py` is not mine to edit
mid-flight; the repair is also a contract decision about a documented
tri-state `reason`, which `tests/test_auth.py` asserts on in at least six
places. What is on disk is the reproduction, so whoever owns it can act on a
measurement rather than a claim. The shape is already in this package:
`press.disclose` renders the exception TYPE and drops the text, for exactly
this reason.

---

## 8. THE CONTROLS, EACH SHOWN FAILING

### 8.1 The verdict engine convicts -- 4 ways, no browser

`scripts/_check_the_playwright_quote_probe_can_fail.py`, over the committed
baseline:

```
CONTROL A  declaration flipped to SILENT
  strict.text_content  declared=SILENT observed=ECHO
  why: declared SILENT, observed ECHO
CONTROL B  a real echo replaced by a sentinel-free message
  strict.inner_text  declared=ECHO observed=SILENT
  why: declared ECHO, observed SILENT
CONTROL C  navigation rows with no proof the landing was visited
  nav.redirect_then_reset  declared=OURS_ONLY observed=OURS_ONLY
  why: VACUOUS: the redirect target was never requested, so this row proves
       nothing about a landing; server saw nothing
CONTROL D  a case declared to raise that did not raise
  strict.get_attribute  declared=ECHO observed=SILENT
  why: declared to raise, did not raise; declared ECHO, observed SILENT
CONTROL E  the untouched baseline
  64 rows, 0 failures
```

Control C is the one worth keeping: it convicts a row that LOOKS right
(`declared=OURS_ONLY observed=OURS_ONLY`) on the ground that its evidence is
missing. That is the exact failure my own first navigation fixture had.

### 8.2 The DRIVEN probe convicts, not only the replayed engine

Controls A-D judge recorded rows. Run live against the browser with two
declarations inverted:

```
FLIPPED strict.text_content: declared ECHO -> SILENT
FLIPPED timeout.hidden_wait_visible: declared ECHO -> SILENT
strict.text_content          SILENT  ECHO  FAIL   attr,cls,eid,text
                             ^^ declared SILENT, observed ECHO
timeout.hidden_wait_visible  SILENT  ECHO  FAIL   hidden
LIVE_FLIP_EXIT=1
```

### 8.3 The census convicts

`scripts/_census_strict_mode_call_sites.py --selftest` runs 27 cases over an
inline fixture manufactured in the file. Green at 27/27; the slice report's
CONTROL section carries its red, produced by inverting one expectation.

### 8.4 The one control that convicted its author

`evaluate.json_parse_page_text` was DECLARED `ECHO` from my own reasoning about
V8 and came back `SILENT`. The probe exited 1. Section 4.1 is the result of
chasing that red instead of editing the declaration to match.

### 8.5 A GUARD THIS WAVE DID NOT WRITE CONVICTED THIS WAVE

Worth recording because it is the strongest control in the document and I did
not author it. The first version of section 7 quoted the planted cookie line
with a longer synthetic value -- the same name, and a trailing
`-session-value` where the committed version ends `-val`, which put the whole
`name=value` pair at 30 characters. `scripts/staged_identity_shapes.py`, the
incremental half of
`tests/test_no_committed_identity.py::test_no_tracked_file_carries_a_real_identifier`,
refused the commit:

```
REFUSED: a corpus-wide guard is RED on this change, answered by its incremental half.
      REFUSED: a file this commit would write carries an UNDECLARED identifier shape.
        _audit/2026-09-21-what-playwright-quotes.md:180  [credential]  li..ue <30 chars>
      A SHAPE MATCH MEANS UNDECLARED, NOT REAL. The repair is either to change the
      content or to declare the plant in DECLARED_PLANTS ... and a declaration
      permanently widens what the guard tolerates for that file, so prefer changing
      the content.
```

**I took its advice rather than its escape hatch.** The plant was shortened at
the source -- `scripts/_probe_the_auth_reason_publishes_a_cookie.py` now builds
a value short enough that the `<name>=<value>` pair is under the shape's
length -- the probe was re-run, and the document quotes the new output. No
entry was added to `DECLARED_PLANTS`, because a declaration would blunt that
guard for this file permanently, and the guard cannot tell my plant from the
real thing. That is the correct behaviour for it and the wrong thing to spend.

Note also what this proves about section 7: **the repository already owns a
detector for the shape that leaks there.** It watches tracked FILES. It does
not watch `$.reason`.

### 8.6 TWO MORE GUARDS CONVICTED THE PROBE, AND BOTH WERE ANSWERED BY DECLARING

`tests/test_probe_navigation_budget.py` and
`tests/test_probe_interaction_budget.py` both went red on
`scripts/_probe_what_playwright_quotes.py` the moment it was staged:

```
FAILED test_no_new_probe_navigates_without_a_guard_or_a_declaration
    _probe_what_playwright_quotes.py:307  312  317  320  608
FAILED test_every_gated_probe_interaction_is_declared
    _probe_what_playwright_quotes.py:177  fill  lambda: cards.fill("x", timeout=T)),
```

Both are correct and both were answered the way the guards prescribe, with an
argument rather than a suppression:

* **The `fill`** is declared in `DECLARED`. It cannot type anything: the
  locator matches three divs, so `Locator.fill` raises a strict mode
  violation before any input is dispatched, which is the only reason the line
  exists.
* **The five `page.goto` calls** are declared in `KNOWN_UNGUARDED`. Four go to
  a loopback server this probe starts and stops; the fifth is a deliberately
  malformed string. `BROWSER.goto` was not an option -- it takes the profile
  lock, which would put this probe on the operator's signed-in Chrome, the one
  thing its brief forbids -- and `assert_read_url` would have meant asking the
  LinkedIn read allowlist to bless `127.0.0.1`.

**THE SECOND ONE COST A TRIPWIRE, AND THAT IS RECORDED HERE BECAUSE IT SHOULD
COST SOMETHING.** `KNOWN_UNGUARDED` was empty, and
`test_the_record_is_empty_and_that_is_a_claim_rather_than_an_absence` asserts
that emptiness directly so it reads as a claim rather than a vacuous loop. Its
own docstring prescribes the resolution: *"it gets recorded and this assertion
gets a named exception with its ruling, not a quiet bump."* That is what was
done -- a `NAMED_EXCEPTIONS` set holding exactly one entry, with the ruling
written above it -- plus a second assertion that a named exception may not
outlive the record it excepts.

**CONTROL, because an amended tripwire is a tripwire somebody might have
blunted.** A bogus, unargued entry was planted in `KNOWN_UNGUARDED`:

```
planted a bogus entry
3 failed, 6 passed in 13.28s
... restored ...
9 passed in 12.92s
```

Three assertions convict an unknown entry, not one. The amendment narrowed the
claim by exactly one named file and left everything else armed.

### 8.7 A check this wave did NOT ship

I did not add a pytest guard asserting that every locator call site is
qualified. It would be RED at HEAD on the six in 5.1, and a red test on a
shared tree with six live waves is a merge hazard, not a guard. The census plus
its committed JSON is the shippable form: it is re-runnable, it has a shown
failure, and a future site moves its number.

---

## 9. WHERE THIS LEAVES THE RULING

`ERROR-MESSAGE-RULED-AT-THE-RAISE` **survives intact, and its central sentence
is strengthened rather than weakened.** The discriminator really is whether a
value the page chose entered the exception's arguments, and really is unknowable
at the envelope: `_error` holds a `playwright._impl._errors.Error` whose text
is page payload, and a `playwright._impl._errors.Error` whose text is a
timeout, and cannot tell them apart.

What this measurement changes is the SUPPORTING CLAIM in class 2. Section 3.2
of the predecessor reasoned that a library's exception text is publishable, in
part because *"the one thing anybody has measured points away from the
hazard"* -- the two navigation templates. That reading is confirmed (3.1). But
navigation is not the whole library, and the classes nobody had measured --
strict mode, the actionability call log, the request header dump -- are class 3
payload inside a class 2 exception. **The two classes are not distinguished by
the exception's author. They are distinguished by which Playwright API raised
it, which is knowable at the call site and nowhere downstream.**

So the class-2 verdict wants one clause added, and it is a clause the ruling
already implies:

> A library's exception text is publishable **where the raising call is one
> whose message cannot carry page payload**. Where it can -- any `Locator`
> method, any wait with an actionability log, any `request` call -- the
> enforcement point is the call site, which is what "at the raise" means for a
> raise nobody here writes.

Three enforcement shapes, all already in this package, none at the envelope:

1. **QUALIFY** the locator (`.first` / `.nth`) so the strict raise is
   structurally impossible. Costs nothing at the two sites in 5.1.
2. **WRAP** at the reader, `raise ExtractionFailedError(...) from exc`.
   Measured clean in section 6; 73 of 124 readers already do it.
3. **TYPE-ONLY AT THE CATCH THAT KNOWS**, the `press.disclose` shape. This is
   the right one for `auth.py::check_auth`, because there the payload is not
   page text but the session.

**AND THE SECTION 7 TRADE IS OFF THE TABLE.** It proposed type-only at
`_error`, which would delete every diagnosis in the package to close a channel
that is better closed at three named sites. The predecessor declined it on
reasoning; it can now be declined on measurement.

---

## 10. RESIDUAL -- what genuinely needs a live page, and what merely is not built

**NAMED PRECISELY, per the brief, and deliberately short. Almost nothing here
needs the account.**

### 10.1 NEEDS A LIVE LINKEDIN PAGE -- one item, and it is not about Playwright

**Whether LinkedIn's DOM can actually present two matches to the three
count-gated locators in 5.1, and on what timescale.** The strict-mode channel
in this package is closed by a `count()` guard across two round trips. Whether
that guard can lose the race is a question about LinkedIn's render behaviour,
not about Playwright, and no planted page can answer it -- a planted page
mutates when I tell it to. **I stopped here rather than reaching for it.**

It is also not worth a live run as things stand: the remedy (`.first` at two
sites) costs less than the measurement, and does not depend on its outcome.

### 10.2 DOES NOT NEED A LIVE PAGE, JUST NOT BUILT HERE

* **The echo census is narrower than the echo surface** (5.3). The census
  covers strict-mode sites. The actionability-call-log channel fires on
  single-element waits, and this package has 4 `.wait_for(` and 1
  `.wait_for_selector(`. Enumerating and classifying those is a planted-page
  job, and one an implementer could take.
* **`Locator.aria_snapshot` and the aria snapshot inside `expect` failures**
  were seen echoing in passing (4.4). `expect` has 0 call sites here, so this
  is a leak no call site can produce -- recorded as such, not chased.
* **Other Playwright surfaces this package does not use** -- `expect_download`,
  `expect_popup`, `frame_locator`, `route`, `new_cdp_session` -- were confirmed
  at 0 call sites and not driven. If any is adopted, it is unmeasured.
* **The repair in section 7.** It is a one-site change plus whatever
  `tests/test_auth.py` asserts. It needs an owner, not an operator.

### 10.3 NOT A RESIDUAL, A DECISION SOMEBODY SHOULD MAKE

The `logger.info` in `check_auth` writes the same cookie to the log file. A
published field and a log file are different disclosure surfaces with
different rulings, and this document does not decide the second one.

---

## 11. ANYTHING CONTRADICTING THE BRIEF

| the brief said | disk says |
|---|---|
| *"a library exception carries page payload verbatim ... a sanitiser that scrubs paths does nothing to it"* | **CONFIRMED, exactly.** `scrub` removed 0 characters from a strict-mode message |
| the case to test hardest is strict mode violation | strict mode is real and is the loudest single message, but it is **closed in this package today** by count guards (5.1). The channel that is OPEN is the request header dump (7), which the brief did not anticipate and which carries the session rather than a name |
| *"which Playwright Python API errors can carry page-derived content"* -- the question as an API-level one | the unit is not the API. **It is the MECHANISM** (2.1): three of them, and one fires on a single element where `.first` is no defence |
| *"a `Locator` that is `.first`-qualified ... cannot violate strict mode"* | confirmed by driving (`qualified.first`, `.last`, `.nth(0)` all silent). But qualification defends against ONE of the three mechanisms |
| implied: a page-level verb is the same as its locator verb | **no.** `Page.click(sel)` is not strict, `Locator.click()` is (4.3) |

---

## 12. FILES

| path | what |
|---|---|
| `scripts/_probe_what_playwright_quotes.py` | NEW. The driven probe: 64 declared cases, planted page plus loopback server, verdict engine, `--json` / `--replay` / `--flip` |
| `scripts/_probe_what_playwright_quotes.json` | NEW. The committed baseline: 64 rows, ECHO 32, OURS_ONLY 7, SILENT 25, 0 failed declarations |
| `scripts/_check_the_playwright_quote_probe_can_fail.py` | NEW. The control: four convictions and one clean replay, no browser |
| `scripts/_probe_playwright_error_reaches_the_envelope.py` | NEW. A real strict-mode exception handed to the shipped `server._error`; three paths compared |
| `scripts/_probe_the_auth_reason_publishes_a_cookie.py` | NEW. The red proof for section 7. Exits 0 while the leak reproduces, 1 once it is closed |
| `scripts/_census_strict_mode_call_sites.py` | NEW, slice instrument. AST census, stdlib only, 27-case `--selftest` |
| `scripts/_census_strict_mode_call_sites.json` | NEW, slice artifact. 85 candidates, 6 / 74 / 5 |
| `_audit/_slice-strict-call-sites.md` | NEW, slice report, with its selftest shown red and green |
| `_audit/2026-09-21-what-playwright-quotes.md` | this document |
| `_audit/INDEX.md`, `_audit/RULINGS.md` | DERIVED, regenerated with `--write`, never hand-merged. 219 documents, 37 rulings, both `--check` green |
| `tests/test_probe_interaction_budget.py` | one `DECLARED` entry for the probe's `fill` (8.6) |
| `tests/test_probe_navigation_budget.py` | one `KNOWN_UNGUARDED` entry, plus the `NAMED_EXCEPTIONS` amendment its own docstring prescribes, plus an assertion that a named exception may not outlive its record (8.6) |

**NOTHING UNDER `linkedin_server/` WAS EDITED BY THIS WAVE.** The findings in
5.1 and 7 are reproductions, not repairs, and each names the shape of its
repair and who has to decide it.

**THE THREE `tests/` EDITS ARE DECLARATIONS, NOT LOGIC**, and each was made
because a guard demanded one by name. No guard was weakened: the interaction
budget gained one argued entry, the navigation budget gained one argued entry
and one narrowed-by-exactly-one claim, and the control in 8.6 shows all three
of that file's assertions still convicting an entry nobody argued. No
`DECLARED_PLANTS` entry was added anywhere, and nothing was committed with
`--no-verify`.
