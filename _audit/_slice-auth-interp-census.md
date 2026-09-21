# AST census: exception/dependency interpolation in linkedin_server/auth.py

Slice deliverable. Answers one question over `linkedin_server/auth.py`: where
does a value that a DEPENDENCY or the SESSION chose get interpolated into a
string that is then RETURNED, LOGGED, or used as an EXCEPTION's argument?

Instrument: `scripts/_census_auth_exception_interpolation.py` (stdlib only,
`ast`/`json`/`argparse`, Python 3.10+; ran on Python 3.13.14 here).

Command used for the numbers below:

```
python scripts/_census_auth_exception_interpolation.py
```

**auth.py changed under me while building this.** The wave lead's own
concurrent edit to `check_auth`'s exception handler (removing a `{exc}`
render and leaving only `type(exc).__name__`, see the `check_auth` rows
below) landed between my first read of the file and the final run. All
numbers in this report are against the file as it stands at the time of
the final run, not my first read. This is a real, useful cross-check: the
census before that edit reported those two sites as `VALUE`; after it, it
reports them as `TYPE_ONLY`. The walker tracked the repair correctly.

## METHOD

A fresh per-function walker processes each module-level `def` / `async def`
in source order (auth.py has no classes), threading a `name -> TaintInfo`
map forward through the statements it sees.

**What counts as a tainted source (T1/T2/T3), exactly as specified:**

- T1: the bound name of an `except ... as name:` handler.
- T2: a name bound from an `await`ed call whose receiver resolves to
  `page` / `context` / `request` / `response` (e.g. `page.request.get(...)`,
  `page.context.cookies(...)`, `response.text()`), PLUS the one named
  exception the brief itself calls out: `await <anything>.goto(page, ...)`
  taints its result too, regardless of what the receiver is named --
  `BROWSER.goto(page, FEED_URL)` is the literal shape in this file, three
  times.
- T3: a direct attribute read off a name already tainted by T1 or T2
  (`response.status`).

**What counts as a sink (S1/S2/S3):**

- LOG: any `logger.<level>(...)` call, every argument position checked
  (not just the format string -- this file's own log lines are %-style
  lazy calls, so the tainted name is almost always argument 2..n).
- RETURN: a tainted value that lands in a dict-literal value or a
  dict-subscript assignment, where that dict is returned by the SAME
  function -- directly (`return {...}`), via a name (`x = {...}; return x`,
  or `return await helper(..., x, ...)`), or as an inline dict literal
  built straight into the call the function returns
  (`return await helper(..., {...}, ...)`). All three shapes occur in this
  file; see the build note below for the one I missed on the first pass.
- RAISE: an argument (positional or keyword) to the call inside a `raise`
  statement. `raise X(...) from exc` does not itself count `exc` as a hit
  through the `from` clause -- only `X(...)`'s own arguments are scanned.

**What counts as a shape (F1-F4):** an f-string (`JoinedStr`) is F1; a
`%`-BinOp OR lazy logger arguments passed alongside a plain string literal
are F2; `.format()` / `.join()` calls are F3; `+`-concatenation and a bare
`str(tainted)` call are F4. A single hit can carry more than one shape
(e.g. `+` around a `.join()` is F4 and F3 together) and the row reports the
full set.

**Branches are walked, not ignored, and merged conservatively.** Each `if`
branch, each `try` body and each `except` handler, and one pass of a loop
body, is walked from an independent copy of the state as of just before
the branch, then the resulting states are MERGED BY UNION: a name is
tainted after the branch point if ANY path into it left it tainted. A
handler starts from the state as of the START of its `try` (the exception
could have fired before any of the try body's assignments ran) with its
own `except ... as name` binding added on top. A name assigned from a
plain literal, or from any expression this walker does not recognise as
taint-preserving, is dropped from the map from that point on -- "rebound
to clean." This union is deliberately the conservative direction: a
branch that in fact always returns before reaching the code after it
still contributes its state to that union, which can over-flag but cannot
hide a real flow the way an under-approximation would.

**What propagates taint through an assignment**, and nothing else: a bare
tainted Name (direct alias, multi-hop -- `a = exc; b = a` -- chases
correctly, see the CONTROL fixture), a tainted Name's `.attr` (T3), an
explicit `str(tainted)` call, the T1/T2 binding shapes themselves, and
`<list-name>.append(<tainted string-shaped expr>)`. That last one is a
documented EXTENSION beyond the enumerated T1-T3 sources -- see LIMITS for
why it exists and why nothing broader does. ANY OTHER call wrapping a
tainted argument (`scrub(...)`, `landing.withheld(...)`, `.get(...)` on a
dict) is an OPAQUE BOUNDARY: the result is NOT propagated as tainted. See
LIMITS for the two concrete places in this file that decision silences.

**`renders` classifies the interpolation SITE's syntax, not the value's
ultimate origin.** `type(x).__name__` alone is TYPE_ONLY (the brief's own
example of SAFE). A bare tainted Name, `str(tainted)`, or a tainted Name
passed as a lazy `%s` / `.format()` / `.join()` argument is VALUE. A
direct `x.attr` expression written AT the interpolation site is ATTR. A
name that was populated earlier from `response.status` (T3) but is later
interpolated bare as `{status}` is reported VALUE at that use, not ATTR --
the attribute access is not visible at that site; the `source` column
still shows the T3 origin so nothing is hidden. A hit with more than one
rendered part (a TYPE_ONLY part next to a VALUE part in the same
f-string) is headlined by the WORST part present, precedence
VALUE > ATTR > TYPE_ONLY -- **the brief's own instruction that a type
render must never mask a value render** -- and the full set is kept next
to it (e.g. `VALUE (VALUE+TYPE_ONLY)`).

**For the RETURN sink only**, a bare tainted value used as an entire dict
value with no string-building operation at that exact site
(`"http_status": status`, `"failed": failures`) is not counted, unless
the name's own origin was already a rendered string. Reasoning: an HTTP
status code or a raw list object placed into a JSON-shaped result has not
been "interpolated into a string" in the sense the brief asks about --
it is a structured field with no prose-construction step to inspect. LOG
and RAISE get no such exemption: a bare tainted value passed straight as
a logger argument or a raise argument counts every time, because
logging's own substitution (or an exception's own `str()`) is the
rendering step regardless of what the call site additionally wraps it in.

**Build note, said plainly because the brief asks the report to be
honest about how the numbers were made real.** The first working version
of this walker undercounted by one: it recognised a tainted dict handed
to a threaded return call only when the dict had first been bound to a
name (`result = {...}; return await helper(page, result, ...)`), and
missed the same shape built INLINE as a call argument with no
intermediate name (`return await _maybe_corroborate(page, {...}, ...)`).
`check_auth`'s third `_maybe_corroborate` call uses exactly that inline
shape and carries a real hit (`status`, line 441). Caught by running the
instrument against the live file and checking the hit count against a
by-hand read of the function, not by reasoning about the code in the
abstract. Fixed, and a tenth selftest case
(`value_return_inline_dict_threaded_example`) now pins this shape so it
cannot regress silently.

## The full row table -- linkedin_server/auth.py

| line | function | tainted source | renders | sink | shape | source text of the interpolation |
|---|---|---|---|---|---|---|
| 115 | `_cookie_records` | `exc` (T1, `except Exception as exc`) | VALUE (VALUE+TYPE_ONLY) | RAISE | F1 | `BrowserUnavailableError( f"could not read the browser session: {type(exc).__name__}: {exc}" )` |
| 148 | `_warm_session_cookies` | `exc` (T1) | VALUE (VALUE+TYPE_ONLY) | LOG | F2 | `logger.info( "cold-start warm-up navigation failed: %s: %s", type(exc).__name__, exc )` |
| 263 | `_arm_session_store` | `exc` (T1) | VALUE (VALUE+TYPE_ONLY) | LOG | F2 | `logger.debug("session store not armed (%s): %s", type(exc).__name__, exc)` |
| 342 | `check_auth` | `exc` (T1) | TYPE_ONLY | LOG | F2 | `logger.info( "auth check request failed: %s (the library's message is withheld -- it renders the whole request, cookie header included)", type(exc).__name__, )` |
| 361 | `check_auth` | `exc` (T1) | TYPE_ONLY | RETURN | F1 | `'reason': f"the auth request could not be completed ({type(exc).__name__}, within a ceiling of {API_TIMEOUT_MS}ms). THE LIBRARY'S OWN MESSAGE IS WITHHELD rather than quoted: it renders the entire request, including the cookie header, so it carries the session credential. The type above is the diagnosis -- a TimeoutError means LinkedIn did not answer inside the ceiling, anything else means the request could not be made at all. This is not a verdict either way."` |
| 441 | `check_auth` | `status` (T3, `response.status`) | VALUE | RETURN | F1 | `'reason': f"the identity call returned HTTP {status}, which is neither an identity nor a refusal. LinkedIn returns 999 to requests it declines to serve; treat this as unknown, not as signed out."` |
| 480 | `_maybe_corroborate` | `exc` (T1) | VALUE (VALUE+TYPE_ONLY) | LOG | F2 | `logger.info( "corroborating navigation failed: %s: %s", type(exc).__name__, exc )` |

7 hits. 0 unresolved receivers in the real file (the UNRESOLVED bucket is
exercised and proven able to fire -- see CONTROL and the selftest fixture's
`unresolvable_receiver_example` -- it is simply empty here because every
awaited method call in auth.py has a resolvable dotted receiver).

## Totals by (renders x sink)

```
TYPE_ONLY  x LOG     : 1
TYPE_ONLY  x RETURN  : 1
VALUE      x LOG     : 3
VALUE      x RAISE   : 1
VALUE      x RETURN  : 1
```

Reading it: of 7 sites where a T1/T2/T3-sourced value reaches a sink, 5
render the raw VALUE (still carry the exception's or the response's own
text/attribute, not just its type) and 2 render TYPE_ONLY (the two sites
inside `check_auth`'s outer exception handler, which is the one place in
this file that has already been repaired to stop doing that -- see the
note at the top of this report and the docstring at
`linkedin_server/auth.py:314-341`).

## CONTROL -- the selftest shown failing, then restored

The fixture is manufactured inline in the script
(`SELFTEST_FIXTURE`, a triple-quoted string of Python source), never read
from auth.py or from any ambient repo file. It contains ten cases: a
TYPE_ONLY log, a VALUE log via lazy `%s` arguments, a VALUE return via an
f-string in a NAMED dict later threaded through a helper's return, a
second VALUE return via an f-string in an INLINE dict threaded directly
(the shape the build note above describes), a VALUE raise, a
dict-subscript RETURN sink, a two-hop alias (`exc -> first_alias ->
second_alias`) reaching a raise, a rebind-to-clean (a tainted local is
overwritten with a literal before the log call that reads it), and a
deliberately unresolvable receiver (`await get_page().request.get(...)`,
where the receiver is a `Call` result, not a dotted name) sitting next to
an ordinary, independent `exc` log in the same handler -- so the test
also proves the walker does not let "one binding in this handler is
unresolvable" suppress a real, unrelated hit two lines below it.

Baseline, green:

```
$ python scripts/_census_auth_exception_interpolation.py --selftest
PASS: type_only_log_example: exactly one LOG hit, renders TYPE_ONLY
PASS: value_log_lazy_percent_example: one LOG hit, renders VALUE, shape includes F2
PASS: value_return_fstring_dict_example: one RETURN hit, renders VALUE, shape F1
PASS: value_return_inline_dict_threaded_example: one RETURN hit (inline dict, no intermediate name)
PASS: value_raise_example: one RAISE hit, renders VALUE
PASS: dict_subscript_sink_example: one RETURN hit via subscript assignment
PASS: multi_hop_alias_example: one RAISE hit, source names second_alias (2-hop)
PASS: rebound_to_clean_example: NO hit at all (rebind-to-clean must hold)
PASS: unresolvable_receiver_example: one UNRESOLVED receiver (the awaited call)
PASS: unresolvable_receiver_example: the handler's OWN exc log still fires (LOG, VALUE)
SELFTEST 10/10
exit=0
```

Broken on purpose (`--selftest-mutate` inverts the declared verdict for
the first check -- it asserts the TYPE_ONLY-only log renders VALUE, which
the actual, unchanged walker output does not match):

```
$ python scripts/_census_auth_exception_interpolation.py --selftest-mutate
FAIL: type_only_log_example: exactly one LOG hit, renders TYPE_ONLY
PASS: value_log_lazy_percent_example: one LOG hit, renders VALUE, shape includes F2
PASS: value_return_fstring_dict_example: one RETURN hit, renders VALUE, shape F1
PASS: value_return_inline_dict_threaded_example: one RETURN hit (inline dict, no intermediate name)
PASS: value_raise_example: one RAISE hit, renders VALUE
PASS: dict_subscript_sink_example: one RETURN hit via subscript assignment
PASS: multi_hop_alias_example: one RAISE hit, source names second_alias (2-hop)
PASS: rebound_to_clean_example: NO hit at all (rebind-to-clean must hold)
PASS: unresolvable_receiver_example: one UNRESOLVED receiver (the awaited call)
PASS: unresolvable_receiver_example: the handler's OWN exc log still fires (LOG, VALUE)
SELFTEST 9/10
exit=1
```

Restored (no file was edited to do this -- `--selftest-mutate` is a
separate CLI branch in `main()` that calls `run_selftest(mutate=True)`;
the ordinary `--selftest` path is untouched code, so "restoring" is just
calling it again):

```
$ python scripts/_census_auth_exception_interpolation.py --selftest
PASS: type_only_log_example: exactly one LOG hit, renders TYPE_ONLY
[... same nine other PASS lines ...]
SELFTEST 10/10
exit=0
```

## LIMITS -- what this method cannot see, said specifically

**No interprocedural taint.** A parameter is never treated as a source,
and a name bound from a call to a LOCAL function (not literally
`page`/`context`/`request`/`response`, and not the special-cased
`X.goto(page, ...)`) is never tainted, even when that function's own body
provably returns a rendered string built from a T1/T2/T3 value. This is
not a hypothetical gap in this file -- it is the exact shape of
`require_auth` (`linkedin_server/auth.py:1284-1297`), which calls
`status = await check_auth(page)` (not T2 -- `check_auth` is a local
function) and then does
`raise NotAuthenticatedError(status.get("reason") or "...")` /
`raise AuthUnknownError(status.get("reason") or "...")`. Inside
`check_auth`, `status["reason"]` on several branches WAS built from a
tainted value (this table's own rows 361 and 441 are exactly that dict).
`require_auth` is the chokepoint every tool calls to gate access, and
this census says nothing about its two raises, not because they are safe,
but because confirming either way needs a cross-function pass this walker
does not do. A human (or a second, interprocedural instrument) should
read those two lines directly against this table's rows 361/441 rather
than trust a silent "no hit" here as a clearance.

**Opaque calls clear taint, and this file leans on that in two more
places.** `session_info_offline` (`linkedin_server/auth.py:936-941`)
catches an exception into `exc` (T1) and immediately wraps it,
`jar_error = scrub(str(exc))` / `jar_error = scrub(f"{type(exc).__name__}: {exc}")`
-- under this walker's rule, `scrub(...)` is an arbitrary call, not the
bare `str()`/`type().__name__` idioms it recognises, so `jar_error` comes
out CLEAN and neither this assignment nor `jar_error`'s two later uses
(an f-string in `credential_source`, and a bare return field) appear as
hits. `logout` (`linkedin_server/auth.py:1149-1150`) does the same thing
one level deeper: `failures.append(f"{name}: {scrub(f'{type(exc).__name__}: {exc}')}")`
-- the `.append()` extension (below) would ordinarily taint `failures`,
but the tainted content here is wrapped in `scrub(...)` BEFORE it ever
reaches `.append()`, so `failures` comes out clean too, and neither the
append site nor its later `"; ".join(failures)` in the returned `reason`
field is flagged. Both are consistent with this file's own documented
use of `scrub` as a real, deliberate sanitiser (see
`linkedin_server/auth.py:1218-1234`, which narrates the SAME class of
defect being fixed at `assert_not_authwall` via `landing.withheld`, a
second opaque call this walker also declines to look inside for the same
reason). I believe both are correct true-negatives, not missed leaks --
but "opaque call clears taint" is this walker's single largest
judgment call, made once and applied uniformly rather than special-cased
per callee, and it is exactly the kind of call a stricter, allowlist-based
instrument (the file's docstring mentions a `_SANITISERS` list elsewhere
in this codebase, with "a real bar and a documented history of being
abused") would refuse to grant silently. If the wave wants those two
sites re-examined against an explicit allowlist rather than this
walker's blanket rule, that is a one-line change (treat only
`{"scrub", "landing.withheld"}` as taint-clearing by name, and count
every other opaque call as UNRESOLVED-through-a-call the way T2 already
counts an unresolved receiver) -- not built here because the brief's
enumerated shapes do not ask for a sanitiser allowlist, and inventing one
without a ruling would be guessing.

**`**name` dict-spread entries are not walked.** `classify_dict_literal`
skips every `ast.Dict` key that is `None` (Python's AST shape for
`**expr` inside a literal). `check_auth` builds three returned dicts this
way (`{"authenticated": True, **base, **identity}` and its siblings at
lines ~419 and ~437 via `**base`). In this file `base` and `identity`
never carry a STRING-shaped tainted value under this walker's own rules
even where traced by hand (`base`'s only tainted field, `http_status`, is
a bare int per the RETURN string-shape guard above, so it would not have
counted anyway) -- but the gap is structural, not merely unexercised: a
future edit that spreads a dict containing a rendered tainted string
would not be caught.

**No `.get()`/subscript-read propagation.** `status.get("reason")` in
`require_auth`, or any `dict_name["key"]` READ (as opposed to a
dict-literal-value WRITE, which is tracked), is not modeled as
taint-preserving even when `dict_name` is itself tracked. Combined with
the interprocedural gap above, this is why `require_auth`'s two raises
are outside this census's reach twice over.

**No true control-flow precision.** Branch states are merged by
conservative union (see METHOD) rather than a real CFG with
reachability/termination analysis. A branch that always raises or
returns before the merge point still contributes its state to that
merge. This can over-taint relative to a precise analysis; it is not
believed to have produced a false hit in this file (every row in the
table was independently confirmed by reading the function), but it is
an approximation, not a proof.

**The `.append()` extension is narrow on purpose.** Only
`<Name>.append(<tainted-string-shaped-expr>)` is recognised, because
`logout`'s `failures` list is the one and only place in this file that
builds a tainted string by mutating a collection rather than by
rebinding a name. `.extend()`, `+=` on a list, comprehensions that
accumulate into a list, and dict `.update()` are not modeled. This is a
documented extension beyond the T1-T3/S1-S3/F1-F4 enumeration in the
brief, added because a strictly-by-the-letter walker would silently miss
a real, load-bearing pattern in this exact file; it is scoped to exactly
the one shape observed, not generalised to every collection-mutation
method, to avoid guessing at shapes not seen.

**Unresolved receivers are real but, in this file, empty.** The T2
detector correctly refuses to guess when an awaited method call's
receiver is not a simple dotted name (proven by the selftest's
`unresolvable_receiver_example`), and counts each one in a dedicated
bucket rather than defaulting it to clean or tainted. auth.py currently
has zero such sites -- every awaited call in the file is on a plainly
named `page`, `context`, `request`, `response`, or `BROWSER`. This bucket
existing and being empty is a fact about this file today, not a proof
the detector never needs to fire; a future edit that awaits a call
through a more indirect expression would surface there rather than
silently falling into either count.
