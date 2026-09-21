# THE DICT-LITERAL EXCLUSION: LIFTED, AND A TWIN IS WHY

**Subject.** `_audit/2026-09-21-what-the-browser-said.md` section 2.3 priced a
residual -- the message census's dict-literal exclusion, which puts
`server._error`'s own two renderings outside the guard -- and closed it with
**"NOT DONE HERE, AND THE MEASUREMENT IS WHY."** This document does it, and
re-measures everything rather than inheriting it.

**Tree.** Worktree branch `worktree-agent-ac7a6fb3d2bdc9e3c`, parent HEAD
`f729a2a`. Subject digest `1035304ce819` over 46 modules, stable across the
run. Every number below is from this box on this snapshot.

**CORRECTS:** `_audit/2026-09-21-what-the-browser-said.md` -- section 2.3 prices the lift against the wrong denominator and misnames one of its four new EXCEPTION_TEXT sub-expressions. `+124 sites` costs the consuming baseline nothing, because that guard admits only SHORTLISTED sub-expressions; exactly ONE committed baseline imports the walk, not two; the real cost is 18 baseline rows of which 13 are verdicted from the code and 5 need adjudication across 3 functions. `server.py::_error` is NOT one of the four new EXCEPTION_TEXT sub-expressions at the variant that produces that `+124` -- the fourth is `server.py::_badge_refusal`, which the same section separately and correctly calls a classifier artefact. And its premise that widening would bring `_error` inside the landing guard is false: that guard is scoped to the address shortlist and `_error`'s three expressions name no address. Its absolute figures (310 / 557 / 19) are NOT corrected -- they reproduce exactly on the tree that measured them, see section 2.1.

---

## 0. THE ANSWER, FIRST

**THE EXCLUSION IS LIFTED.** Not because the delta was large -- a delta is not
a finding -- but because of one pair of sites:

    shape.parse_person_card       out["profile"] = f"https://www.linkedin.com/in/{slug}"
    shape.parse_connection_card   return {..., "profile": f"https://www.linkedin.com/in/{slug}", ...}

**The same expression. The same key. The same eight-line source comment saying
it is a deliberate publication.** The first has carried a written verdict in
`tests/landing_interpolation_baseline.json` since that file existed. The second
was invisible to every guard in the repository, and the only difference between
them is which side of an `=` the dict literal sits on.

    A COVERAGE BOUNDARY THAT FOLLOWS SYNTAX RATHER THAN SEMANTICS IS NOT A
    SCOPE DECISION. IT IS AN ACCIDENT WITH A DOCSTRING.

The price, measured against the denominator that actually matters:

| | before | after |
|---|---:|---:|
| census sites | 311 | 480 |
| census sub-expressions | 558 | 792 |
| census shortlisted sites | 19 | 37 |
| **committed baseline rows** | **19** | **37** |
| baseline rows needing a HUMAN verdict | -- | **5**, across **3** functions |
| baseline rows verdicted from the code | -- | 13 |
| baseline rows CHANGED or VANISHED | -- | **0** |
| `stated rows` in `_audit/_census/` | 704 | 704 |
| walk wall clock over the package | 22.1s | **4.6s** |

The walk got 4.8x FASTER while getting 54% wider, because widening it exposed a
cost that was always there and that nobody had profiled (section 6).

---

## 1. WHERE THE EXCLUSION LIVES, IN CODE

### 1.1 WHICH INSTRUMENT, BECAUSE THE BRIEF NAMED THREE AND MEANT ONE

The brief said to start from `scripts/_census_page_coercions.py`,
`scripts/_census_reader_guard_subjects.py` and the `_audit/INSTRUMENTS.md`
entry documenting a walk that covers *"argument, dict literal, subscript
assignment"*. All three are the wrong file, and saying so is part of the job --
`kind-before-resolution`: decide what a token IS before resolving it.

| candidate | what it actually is | carries the exclusion? |
|---|---|---|
| `scripts/_census_message_interpolations.py` | the message-interpolation census. Declares the exclusion twice, in its own module docstring and in section 9 of its generated report | **YES. This is the one.** |
| `scripts/_census_page_coercions.py` | the page-coercion census. IMPORTED by the above as the shared page-controlled analyser | **NO -- the opposite.** `_can_be_page_string` has an explicit `isinstance(expr, ast.Dict)` branch that descends into dict values. The sibling analyser already looked inside dicts |
| `scripts/_census_reader_guard_subjects.py` | 75 lines, a read-only slice that imports `discover_readers` and compares it against the reader baseline | **NO.** Not a walk at all |
| the `_audit/INSTRUMENTS.md` entry the brief pointed at by LINE NUMBER, which resolves to section 3.3 `DECLARE-THE-ANSWER-NOT-THE-CURRENT-STATE` (cited by name here, because that register is append-ordered and a line number in it rots within the day) | the CONTROL for `tests/test_the_source_url_split_was_never_ruled.py`, under section 3.3 `DECLARE-THE-ANSWER-NOT-THE-CURRENT-STATE` -- *"all three spellings of the field read (keyword argument, dict literal, subscript assignment)"* | **NO.** It is a control asserting that a DIFFERENT instrument reads one field in three spellings. That instrument never had this gap; the message census did |

The residual named the right file. The brief's three starting points did not,
and one of them (`_census_page_coercions.py`) is evidence AGAINST the exclusion
being a considered design choice: the analyser the census imports had already
made the other decision.

### 1.2 IT IS THREE CONDITIONS, NOT ONE, AND EACH IS SUFFICIENT ALONE

This is the load-bearing finding of section 1, and it is why the residual's
"lift the exclusion" was never a line. In `scripts/_census_message_interpolations.py`,
as it stood at `f729a2a`:

**MECHANISM 1 -- NO ENTRY POINT.** `_Walker` defined `visit_ExceptHandler`,
`visit_FunctionDef`, `visit_AsyncFunctionDef`, `visit_Raise`, `visit_Call`,
`visit_Assign` and `visit_AnnAssign`. There was **no `visit_Return` and no
`visit_Dict`**. A dict literal was traversed by `ast.NodeVisitor.generic_visit`
and never offered to a recorder.

**MECHANISM 2 -- THE TARGET-SHAPE GATE.** `_Walker._record_field` opens:

    if not any(isinstance(t, (ast.Subscript, ast.Attribute)) for t in targets):
        return

`server._error`'s FIRST rendering is `out: dict[str, Any] = {...}`. That is an
`ast.AnnAssign` whose target is an `ast.Name`, so it reached `visit_AnnAssign`
and was dropped on that one line.

**MECHANISM 3 -- THE STRING DECOMPOSER REFUSES A DICT.** `_decompose` handles
`JoinedStr`, `Call`, `BinOp` and `IfExp` and ends `return None`. There is no
`ast.Dict` branch, so `interpolations(<a dict literal>)` is `None`. Measured
rather than read:

    >>> C.interpolations(ast.parse('{"a": f"x{y}"}', mode='eval').body)
    None

**EACH ONE DROPS THE CONSTRUCT ON ITS OWN**, so repairing any one in isolation
changes nothing and produces a measurement that looks like the construct being
absent. That is demonstrated, not asserted -- see section 5.3, where a widening
that lifts mechanisms 1 and 3 for `return` statements only still cannot see
`_error`'s first rendering.

---

## 2. THE MEASUREMENT, BOTH WAYS, WITH THE SET DIFFERENCE

### 2.1 THE SHIPPED WALK AT HEAD -- AND WHY IT IS 311, NOT THE 310 ON RECORD

    python scripts/_census_message_interpolations.py --json    # at f729a2a

    sites 311   sub-expressions 558   shortlisted sites 19
      UNCLASSIFIED                    174
      TYPE_ONLY                       118
      SERVER_CONSTRUCTED               96
      EXCEPTION_TEXT:arbitrary         89
      PAGE_OR_SITE_DERIVED             70
      CALLER_SUPPLIED                  10
      EXCEPTION_TEXT:package_raised     1

Section 2.3 of the predecessor states **310 sites, 557 sub-expressions, 19
SHORTLISTED**, with `PAGE_OR_SITE_DERIVED 69`. Six of the seven buckets agree
exactly. The disagreement is one site and one `PAGE_OR_SITE_DERIVED`
sub-expression, and it is not an error in either measurement.

Driving the SAME shipped walk over the package as committed at each revision:

    6c24426  sites 310  sub-expressions 557  shortlisted 19   <- the predecessor's own tree
    f729a2a  sites 311  sub-expressions 558  shortlisted 19   <- the merge it produced

**The predecessor's figures reproduce EXACTLY on the tree it measured.** The
merge `f729a2a` took a second parent, and the master line carried `b73783a`
*"fix(dom): the filter pill's navigation finding now refuses"*. The set
difference, keyed on `(module, function, kind, target, message)` because
`A-LINE-NUMBER-IS-NOT-AN-ANCHOR-IN-A-LIVE-TREE` -- a line-keyed diff called 60
rows new when one was:

    ADDED    dom.py :: activate_messaging_filter
             RAISE WriteAttemptError
             f"the {wanted!r} filter pill moved the browser to a different address ..."
    REMOVED  (nothing)

**This is `relayed-measurements-go-stale` in its mildest form and it is worth
one line in a future brief:** a census total quoted from a pre-merge tree is a
reading with a timestamp, and the timestamp is the thing the reader cannot see.
Both numbers are right. Neither is current unless its revision is stated.

### 2.2 FOUR WIDENINGS, NOT ONE, BECAUSE "WIDER" IS TWO DECISIONS

"Lift the exclusion" underdetermines the instrument. Two independent axes:

    SCOPE   return-only   a dict literal that IS the value of a `return`
            all-dicts     every `ast.Dict` literal, wherever it sits

    KEYS    every-key     every string key -- which is what reusing the shipped
                          `_record_field` unmodified actually does, since its
                          FIELD branch fires for ANY Subscript target and only
                          its PASSTHROUGH branch consults `_is_message_field`
            message-key   only keys in the shipped `MESSAGE_KEYS`

All four, over the one snapshot, against the shipped 311 / 558 / 19:

| variant | sites | sub-expr | shortlisted | delta sites | delta sub-expr | delta shortlisted |
|---|---:|---:|---:|---:|---:|---:|
| SHIPPED | 311 | 558 | 19 | -- | -- | -- |
| return-only / every-key | 435 | 739 | 23 | **+124** | **+181** | **+4** |
| return-only / message-key | 424 | 721 | 22 | +113 | +163 | +3 |
| all-dicts / every-key | 480 | 792 | 37 | +169 | +234 | +18 |
| all-dicts / message-key | 446 | 745 | 22 | +135 | +187 | +3 |

**`return-only / every-key` reproduces the predecessor's `+124 / +181 / +4`
and its `EXCEPTION_TEXT +4` exactly.** Its variant is therefore identified,
not guessed: it subclassed the walker with a `visit_Return` and handed every
string key to `_record_field`.

### 2.3 THE SET DIFFERENCE AT THE SHORTLIST, WHICH IS THE ONLY PLACE IT COSTS

| variant | added shortlisted sites |
|---|---|
| return-only / every-key | `shape.parse_connection_card` `returned['profile']` (`slug`); `shape.apply_route` `returned['why']` x3 (`raw_href`) |
| return-only / message-key | `shape.apply_route` x3 only -- the twin drops out, because `profile` is not a `MESSAGE_KEYS` key |
| all-dicts / every-key | the four above, plus `writes._direction` `returned['what_that_means']` (`observation.state_url`), plus **13** `server.py` `<module>`-scope entries, each `f"{BASE_URL}/..."`, from TWO route tables -- `CENSUS_SURFACES` (10) and `PROFILE_DETAIL_URLS` (3) |
| all-dicts / message-key | `shape.apply_route` x3 only |

### 2.4 THE FOUR NEW `EXCEPTION_TEXT` SUB-EXPRESSIONS ARE NOT THE FOUR ON RECORD

Section 2.3 of the predecessor names them as *"`server.py::_error`,
`server.py::linkedin_premium_job_collection`, `preflight.py::report` and
`cdp_bridge.py::probe`"*. Measured at the variant that produces its own
`+4`:

    return-only / every-key, EXCEPTION_TEXT sub-expressions added: 4
      cdp_bridge.py  probe                            returned['reason']   EXCEPTION_TEXT:arbitrary   exc
      preflight.py   report                           returned['message']  EXCEPTION_TEXT:arbitrary   exc
      server.py      _badge_refusal                   returned['error']    EXCEPTION_TEXT:undecided   error
      server.py      linkedin_premium_job_collection  returned['message']  EXCEPTION_TEXT:arbitrary   str(exc)

**`server.py::_error` is not among them.** It IS added by that variant, as one
row -- `PASSTHROUGH returned['message'] = scrub(f"{type(exc).__name__}: {exc}")`
-- bucketed `PAGE_OR_SITE_DERIVED`, because `scrub` is not in `STRINGIFIERS` so
the classifier never unwraps to the exception and `type(exc).__name__` matches
the hazard token `name`. The fourth slot is `server.py::_badge_refusal`, the
row the same document separately and correctly calls *"a classifier artefact,
not a site"*. Five items were listed for four slots and the one that dropped
out is the one the section is named after.

`_error`'s FIRST rendering reaches `EXCEPTION_TEXT` only under `all-dicts`,
where the count is 8 rather than 4:

    all-dicts, added: server.py _error returned['error']   EXCEPTION_TEXT:undecided  exc.kind
                      server.py _error returned['message'] UNCLASSIFIED              scrub(str(exc))

---

## 3. THE KEEP-OR-LIFT VERDICT

### 3.1 THE PRICE WAS QUOTED IN THE WRONG DENOMINATOR

The residual prices the lift as *"+124 sites on a shared walk that two
committed baselines import, plus 4 rows needing rulings on one of them ... a
wave and not a line."* Two of those three clauses do not survive measurement.

**ONE committed baseline imports this walk, not two.** A content search for
`_census_message_interpolations` across the worktree returns, excluding the
census itself and prose: `tests/test_no_message_publishes_a_landing.py` (a
dynamic path load, because `scripts/` has no `__init__.py`) and nothing else
under `tests/` or `scripts/`. `tests/tool_envelope_baseline.json` and
`tests/reader_leak_baseline.json` belong to DRIVEN guards that discover their
own subjects and never touch this walk.

**THE SITE COUNT IS NOT WHAT THAT BASELINE COSTS.** `subject_sites` admits a
sub-expression only when `field["shortlist"]` is true:

    for field in row["fields"]:
        if not field.get("shortlist"):
            continue

So `+124 sites` costs the baseline **nothing**. What costs it is
`+N shortlisted`, and `verdict_for` decides two of the five verdicts FROM THE
CODE before any ruled table is consulted -- `site["sanitiser"]` gives
`WITHHELD`, `site["bucket"] == "SERVER_CONSTRUCTED"` gives `SERVER_CONSTRUCTED`.
Running the guard's own `measure()` with each walk substituted:

| variant | live keys | appeared | vanished | changed | UNRULED (needing adjudication) | distinct functions |
|---|---:|---:|---:|---:|---:|---:|
| SHIPPED | 19 | 0 | 0 | 0 | 0 | -- |
| return-only / every-key | 23 | 4 | 0 | 0 | 4 | 2 |
| return-only / message-key | 22 | 3 | 0 | 0 | 3 | 1 |
| all-dicts / every-key | 37 | 18 | 0 | 0 | **5** | **3** |
| all-dicts / message-key | 22 | 3 | 0 | 0 | 3 | 1 |

**The full lift costs five adjudications across three functions.** The other
thirteen are verdicted from their bucket with no human in the loop. That is a
line, not a wave, and the difference between the two estimates is entirely
which denominator was counted.

### 3.2 THE RESIDUAL'S OWN PREMISE DOES NOT SURVIVE EITHER, AND IT MATTERS

Section 2.3 argues the exclusion puts `_error` *"outside its own census, and
therefore outside `test_no_message_publishes_a_landing`'s subject set too."*
The first clause is true. **The inference is false, and lifting the exclusion
does not repair it.**

That guard's subject rule is `SHORTLIST_TOKENS` -- `url`, `landed`, `final_url`,
`href`, `slug`, `redirect` -- matched against an expression's source text.
`_error`'s three expressions are `exc.kind`, `scrub(str(exc))` and
`scrub(f"{type(exc).__name__}: {exc}")`. **None contains an address token, so
`_error` does not enter that guard's subject set at any widening.** Measured:
with the exclusion fully lifted the baseline gains 18 keys and **not one of
them is in `_error`**.

So the lift is right, but not for the reason the residual gives. Had it been
taken on that reasoning, it would have shipped and `_error` would still have
been ungoverned by the guard the argument was about -- which is exactly the
class of half-repair `_audit/INDEX.md` exists to make visible.

### 3.3 WHAT DOES GOVERN `_error`, AND WHETHER A PAGE VALUE CAN REACH IT

`_error` has two renderings and both were outside the census:

    the LinkedInReaderError branch
        out: dict[str, Any] = {"error": exc.kind, "message": scrub(str(exc))}
    the fall-through branch
        return {"error": "unexpected", "message": scrub(f"{type(exc).__name__}: {exc}")}

**CAN A VALUE THE PAGE CHOSE REACH EITHER?** Yes, and the ruling already says
how: `ERROR-MESSAGE-RULED-AT-THE-RAISE` -- the discriminator is not the
exception's author but whether a page-chosen value entered the exception's
ARGUMENTS, knowable at the raise and unknowable at the envelope. `int("<a
label>")` raises a stdlib `ValueError` quoting its input verbatim, and the
`quoting-callees` slice proved by CALLING them that 14 of 26 stdlib callables
echo their refused input, `int` among them. `config.scrub` substitutes this
server's own filesystem paths and nothing else, so it does not touch such a
value.

**IS IT GOVERNED? YES -- BY A DRIVEN GUARD, NOT BY THIS CENSUS.**
`tests/test_tool_envelopes_emit_no_page_string.py` drives tool bodies with a
page that answers in plants and asks what came OUT of the envelope, which is
precisely `_error`'s return value. Its baseline, measured:

    tests/tool_envelope_baseline.json   49 tools
      not_driven:never read the page    27
      clean                             17
      returns_text                       5

    tests/reader_leak_baseline.json    119 readers
      clean                             58
      returns_text                      40
      not_driven                        21

**22 of 49 tool bodies and 98 of 119 readers are actually driven.** That is
real coverage and it is the right instrument for this question, because a
static walk cannot answer provenance at the envelope. The 27 `not_driven`
tools are the honest hole and they are already on record as a later wave's
work. **Widening this census does not shrink that hole by one tool**, and any
future brief proposing it as the remedy for `_error` should be answered with
this section rather than re-deriving it.

### 3.4 SO WHY LIFT AT ALL -- THE TWIN, AND ONLY THE TWIN

Strip out the reason that failed and one reason is left standing, and it is
sufficient on its own. `shape.parse_person_card` and
`shape.parse_connection_card` publish **the same address expression under the
same key**; the first is ruled `PUBLISHED_BY_CONTRACT` in the committed
baseline and the second was invisible. Widening the census does not make the
second a leak -- it makes it a ROW, with the same verdict its twin already has,
written down where a future reader can disagree with it.

    A CENSUS THAT COVERS ONE OF TWO IDENTICAL PUBLICATIONS IS NOT REPORTING
    A SMALLER NUMBER. IT IS REPORTING A NUMBER ABOUT PYTHON SYNTAX.

And the same widening surfaces `writes._direction` and `shape.apply_route`,
which are real sites with real verdicts owed (section 4).

### 3.5 THE VARIANT CHOSEN, AND WHY NOT THE SMALLER ONES

**SHIPPED: `all-dicts / every-key`.** Reasons, in order of weight:

1. **`message-key` WOULD HAVE MISSED THE TWIN.** `profile` is not in
   `MESSAGE_KEYS`, so both `message-key` variants drop
   `parse_connection_card` -- the single row that convicts the exclusion. A
   widening that cannot see its own justification is not the right widening.
2. **`every-key` IS NOT A NEW POLICY; IT IS THE EXISTING ONE.** The shipped
   `_record_field` already fires its FIELD branch for ANY subscript key and
   scopes only its PASSTHROUGH branch to `_is_message_field`. Handing every
   string key to it reproduces exactly what the walk already did for the
   subscript spelling. Scoping dict keys more tightly than subscript keys
   would have re-created the twin problem one level down.
3. **THE PUBLICATION POINT IS THE KEY, NOT THE STATEMENT.** `return-only` is a
   rule about which statement the literal sits in, which is the same kind of
   syntactic accident being repaired -- and it demonstrably leaves `_error`'s
   first rendering out.
4. **THE 13 ROUTE-TABLE ROWS ARE NOT NOISE, THEY ARE FREE.** They are
   `f"{BASE_URL}/..."` entries of two module-level tables in `server.py` --
   `CENSUS_SURFACES` (10) and `PROFILE_DETAIL_URLS` (3).
   `verdict_for` classifies them `SERVER_CONSTRUCTED` from the bucket with no
   ruling written. They are addresses this package assembled from its own
   constant, correctly labelled, at zero adjudication cost -- and the shipped
   walk would already have recorded every one of them had those tables been
   written as subscript assignments.

**MECHANISMS 2 AND 3 ARE NOT LIFTED.** The dict path does not go through the
target-shape gate or through `_decompose`, so both keep doing their real work
for every non-dict value: a local `x = f"..."` still does not become a site,
and a bare literal is still not a built message.

---

## 4. THE ROWS, ADJUDICATED

### 4.1 THE FIVE THAT NEEDED A HUMAN

All five are ruled `PUBLISHED_BY_CONTRACT`, each with its reason written into
`PUBLISHED_BY_CONTRACT_SITES` in `tests/test_no_message_publishes_a_landing.py`.
`verdict_for` keys that table by `module:function`, so three entries cover the
five rows.

| row | verdict | why, in one line |
|---|---|---|
| `shape.py:parse_connection_card:slug` | PUBLISHED_BY_CONTRACT | the twin of `parse_person_card`, already ruled the same way for the same expression under the same key; its own source comment declares it *"A BROWSER LINK, NOT A NAVIGABLE ADDRESS"* |
| `shape.py:apply_route:raw_href` x3 | PUBLISHED_BY_CONTRACT | the function's contract IS to name where an application would be sent; it publishes `destination` and `destination_host` as declared fields, and on refusal it names the href it could not classify -- the repository's standing refusal doctrine |
| `writes.py:_direction:observation.state_url` | PUBLISHED_BY_CONTRACT | the SAME dict literal publishes the value verbatim one key earlier as `read_from_url`; withholding it in the sentence beside the field would withhold nothing |

**THE `apply_route` RULING IS THE ONE TO ARGUE WITH, AND THE ASYMMETRY IS
RECORDED RATHER THAN HIDDEN.** Three sites, one table key:

    branch                          destination     why quotes raw_href
    identified (linkedin_apply)     raw_href        yes  <- the field republishes it
    refusal: href does not match    None            yes  <- the field does not
    refusal: not a safety wrapper   None            yes  <- the field does not

On one branch the value is republished as a first-class field and
`PUBLISHED_BY_CONTRACT` is exact. On the other two it is in the message only,
and the justification is the refusal doctrine rather than a sibling field. The
guard's `module:function` granularity cannot express that split. Convicting
them instead would convict a contract for obeying a standing rule -- the exact
error `_audit/2026-09-21-what-the-browser-said.md` section 5.2a records against
a leak rule built from envelope shape rather than provenance. Reach is
confirmed, not assumed: `server.py::linkedin_job_detail` assigns the whole dict
to `out["apply_path"]`, and `writes.py::_read_apply_route` returns `why` into a
write gate's refusal.

### 4.1a PER-ROW MOVEMENT, ALL 18, NOT A COUNT

Every key that entered `tests/landing_interpolation_baseline.json`, with the
verdict it carries and how that verdict was reached. **Nothing left the
baseline and nothing already in it changed verdict** -- `vanished 0`,
`changed 0`, asserted by the guard's own `compare()`.

| key | verdict | decided by |
|---|---|---|
| `server.py:<module>:BASE_URL` | SERVER_CONSTRUCTED | the bucket, in code |
| `server.py:<module>:BASE_URL#2` .. `#13` (12 more) | SERVER_CONSTRUCTED | the bucket, in code |
| `shape.py:apply_route:raw_href` | PUBLISHED_BY_CONTRACT | RULED, this wave |
| `shape.py:apply_route:raw_href#2` | PUBLISHED_BY_CONTRACT | RULED, this wave |
| `shape.py:apply_route:raw_href#3` | PUBLISHED_BY_CONTRACT | RULED, this wave |
| `shape.py:parse_connection_card:slug` | PUBLISHED_BY_CONTRACT | RULED, this wave |
| `writes.py:_direction:observation.state_url` | PUBLISHED_BY_CONTRACT | RULED, this wave |

The 19 pre-existing keys are unchanged, by key and by verdict: 7 `ASKED_FOR`,
5 `WITHHELD`, 4 `SERVER_CONSTRUCTED`, 2 `PUBLISHED_BY_CONTRACT`, 1
`NAMES_NO_ADDRESS`.

### 4.2 THE THIRTEEN THAT DID NOT

`server.py:<module>:BASE_URL` x13 -- two module-level route tables,
`CENSUS_SURFACES` (10 entries) and `PROFILE_DETAIL_URLS` (3), each entry a
literal route such as `f"{BASE_URL}/in/me/details/experience/"`. Bucket
`SERVER_CONSTRUCTED`, so `verdict_for` decides them from the code before any
table is read. **No ruling was written for these and none should be**: the
guard's own design puts measured verdicts ahead of ruled ones precisely so a
ruling cannot quietly override what the source says.

### 4.3 THE CENSUS STATE INVARIANT -- 704, BEFORE AND AFTER

`_audit/_census/*.md` is the CAPABILITY census and is a different instrument
from the message-interpolation census this wave widened. The brief conflated
them; the residual did not (it says *"+4 rows needing verdicts in
`tests/landing_interpolation_baseline.json`"*). **This wave touches no
capability row**, so the invariant must hold unchanged -- which is a
prediction, and it was checked rather than assumed, before and after.

    python scripts/count_census_states.py     # BEFORE, at f729a2a

    jobs.md                 stated rows 150      profile.md   stated rows 203
    messaging-and-content.md stated rows 142     network.md   stated rows 209
    TOTAL  stated rows 704
      GAP 275   EXCLUDED-RULED 285   COVERED-PROVEN 52   COVERED-UNFIRED 19
      COVERED-CANNOT-DELIVER 19   MEASURED-ABSENT 7   CP 20   CU 4   XR 23

    python scripts/count_census_states.py     # AFTER

    TOTAL, all four slices
      COVERED-CANNOT-DELIVER       19
      COVERED-PROVEN               52
      COVERED-UNFIRED              19
      CP                           20
      CU                            4
      EXCLUDED-RULED              285
      GAP                         275
      MEASURED-ABSENT               7
      XR                           23
      stated rows                 704

**IDENTICAL, state by state.** The prediction held; it was still checked.

---

## 5. THE CONTROLS, SHOWN FAILING

`scripts/_check_the_dict_literal_walk_can_fail.py`, three arms, each driven red
on a mutation and green on its removal in one process. Wall clock 1.6s.

### 5.1 GREEN, ON THE TREE AS SHIPPED

    BEFORE THE MUTATIONS -- every arm must HOLD
      HELD         arm 1: the walk sees both renderings
      HELD         arm 2: the constant pre-skip is inert
            compared 2257 located nodes (10 carrying multi-byte text) over 8 of 46
            package modules IN FULL, plus a synthetic edge-case module.
            DID NOT RUN over 38 module(s): __init__.py, __main__.py, anchors.py,
            auth.py, browser.py, buildinfo.py, cdp_bridge.py, collections_page.py,
            company_page.py, company_root.py, config.py, cookie_jar.py, dom.py,
            events.py, feed.py, group_page.py, groups.py, groups_page.py,
            item_addresses.py, job_collections.py, jobfilter.py, landing.py,
            menus.py, newsletters.py, notify_cost.py, page_plugin.py, preflight.py,
            premium.py, press.py, profile_version.py, readonly.py,
            recommendations.py, search_results.py, server.py, session_store.py,
            shape.py, uploads.py, writes.py
      HELD         arm 3: _segment == ast.get_source_segment

### 5.2 RED, ONE MUTATION PER ARM -- VERBATIM

    MUTATION 1 -- the two dict entry points are removed (the walk as it stood
    before 2026-09-21)
      FAILED       arm 1
            the walk cannot see rendering_one, rendering_two

    MUTATION 2 -- the pre-skip is widened to swallow an f-string
      FAILED       arm 2
            the pre-skip is NOT behaviour-preserving: 1 row(s) with it, 2 without

    MUTATION 3 -- _segment loses its first character
      FAILED       arm 3
            errors.py: disagreement at line 1 on Expr

    OK: all three arms held on the tree and all three fired on their mutation.

### 5.3 THE MUTATION THAT PROVED "THREE MECHANISMS, NOT ONE"

Run against the measurement harness before the lift shipped, and the reason
section 1.2 is a finding rather than a reading. The widened walk was narrowed
to `return-only` -- mechanisms 1 and 3 lifted for `return` statements,
mechanism 2 untouched:

    MUTATION 3 -- the widened walk is run at scope `return-only`, which cannot
    reach `rendering_one`'s ANNASSIGN dict.
      shipped walk sees : negative_log, negative_raise, negative_subscript
      widened walk sees : negative_log, negative_raise, negative_subscript, rendering_two
      the two renderings, per the widened walk : NOT SEEN -- the widening failed

    FAIL: THE WIDENING DOES NOT WORK: the widened walk still cannot see rendering_one

**A partial lift is indistinguishable from a working one unless the control
holds both renderings.** The predecessor's variant is exactly this partial lift.

### 5.4 A CONTROL OF MINE THAT COULD NOT FAIL, AND HOW IT WAS CAUGHT

The first run of the baseline-cost harness reported **19 live keys and zero
appeared for all four widened variants** -- five different walks, one answer.
That is the signature this whole wave is about, in my own instrument.

`measure(None)` routes through `package_sites()`, which memoises on
`_PACKAGE_SITES`, so every substituted walk after the first read the first
one's answer. Fixed by clearing the cache per run; the corrected numbers are
the table in section 3.1. Recorded because a harness that answers identically
for four different inputs is not a null result, it is a broken instrument, and
the only thing that caught it was the delta disagreeing with a measurement
taken a different way ten minutes earlier.

### 5.5 THE GUARD ITSELF, RED ON THE FIVE NEW ROWS BEFORE THEY WERE RULED

A ruling is only worth writing if the guard would have gone red without it, so
the three table entries this wave added were removed IN PROCESS -- nothing on
disk edited -- and the guard's own test functions called directly, so the text
below is the real `AssertionError` and not a paraphrase.

    WITH the three rulings this wave added:
       37 site(s), 0 UNRULED

    WITHOUT them -- the state the lift arrived in:
       37 site(s), 5 UNRULED

    FAILED test_every_address_naming_site_has_a_verdict[shape.py:apply_route:raw_href]
       AssertionError: shape.py:apply_route:raw_href interpolates an address and has
       no verdict. Either route it through landing.withheld(), or record WHY it is
       safe in ASKED_FOR_SITES / PUBLISHED_BY_CONTRACT_SITES / NAMES_NO_ADDRESS_SITES
       in test_no_message_publishes_a_landing.py. There is no verdict meaning 'this
       one is allowed to publish a landing'.
    FAILED test_every_address_naming_site_has_a_verdict[shape.py:apply_route:raw_href#2]
    FAILED test_every_address_naming_site_has_a_verdict[shape.py:apply_route:raw_href#3]
    FAILED test_every_address_naming_site_has_a_verdict[shape.py:parse_connection_card:slug]
    FAILED test_every_address_naming_site_has_a_verdict[writes.py:_direction:observation.state_url]

    FAILED test_the_subject_set_has_not_silently_changed
       AssertionError: site verdict(s) changed: shape.py:apply_route:raw_href#2:
       PUBLISHED_BY_CONTRACT -> UNRULED; shape.py:apply_route:raw_href#3:
       PUBLISHED_BY_CONTRACT -> UNRULED; ...

Five rows, five reds, each naming its own site rather than a count -- and the
subject-set guard firing a second time from the other direction. **`UNRULED` is
a failure in this guard and not a bucket**, so the lift could not have shipped
with the rows unadjudicated even if somebody had wanted it to.

### 5.5a A SHIPPED GUARD WENT RED ON THIS DOCUMENT, AND IT WAS RIGHT

The first full impact-gate run refused:

    REFUSED: a test this change can reach is RED.
        FAILED tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged
        1 failed, 2015 passed in 1139.07s (0:18:59)

**This document corrects the one it was commissioned from, and had said so only
in prose.** That guard exists because a correction can name what it corrects
while the corrected document cannot name its corrector, so every reader
starting at the claim reaches the wrong file. It was right, and the fix is the
one it names: a `CORRECTS:` marker here and a matching `CORRECTED BY:`
back-pointer written into `_audit/2026-09-21-what-the-browser-said.md`
section 6.2.

Two further reds came out of writing those markers, and both are worth the
line:

    FAILED test_every_marker_names_one_document_and_carries_a_reason
      2026-09-21-the-dict-literal-exclusion.md:13 carries no reason after the
      citation; a marker must say in one line what the correction was

-- markdown-wrapped markers are not markers. The reason must sit on the same
physical line as the citation, and both were rewritten as single lines.

    FAILED test_every_candidate_pair_is_declared_or_triaged
      2026-09-21-the-dict-literal-exclusion.md:58 cites INSTRUMENTS.md with
      correction vocabulary within 2 line(s)

-- section 1.1 says the `_audit/INSTRUMENTS.md` entry the brief pointed at
describes a different instrument. **That entry is TRUE and is not corrected**;
what was corrected is the brief, and a brief is not a document in this corpus.
Filed as a `NOT_A_CORRECTION` entry with that reason and with what would make
it wrong, because declaring a pair there would stamp a `CORRECTED BY:` marker
on a register entry nobody found fault with.

    13 passed in 25.87s

### 5.6 THE GUARD, GREEN ON THE NEW BASELINE

    python -m pytest tests/test_no_message_publishes_a_landing.py -q
    44 passed in 25.26s

Including `test_the_subject_set_has_not_silently_changed` (appeared / vanished
/ changed all empty), `test_every_address_naming_site_has_a_verdict`
(parametrised over all 37, `UNRULED` is a failure and none is), and
`test_the_baseline_cannot_record_a_leak`.

---

## 6. THE COST THAT WAS ALWAYS THERE, FOUND BY WIDENING

Widening the walk took it from **22.1s to 59s** over the package. The first
explanation written down was that the package's dict literals are mostly
constant tables. **That explanation was wrong, and it was written into a source
comment before it was checked.** cProfile over `server.py` alone:

    16.384 seconds total
      605 calls  _source
      605 calls  ast.get_source_segment
      302 calls  ast._splitlines_no_ff      11.994s tottime   13.147s cumtime

`ast.get_source_segment` re-splits its entire `source` argument on every call.
`server.py` is half a megabyte. **That was 12 of 16 seconds and it predates
this wave entirely** -- the narrow walk paid it too, at half the call count.

Repaired by caching the split per module text and slicing locally
(`_lines_of`, `_segment`). A reimplementation of a stdlib function is a
liability unless it is proven equal, so it was proven twice:

    ONE-TIME, WHOLE PACKAGE   65672 located nodes compared against
                              ast.get_source_segment, 0 disagreements
    IN THE CONTROL, arm 3     2257 nodes over 8 modules IN FULL, plus a
                              synthetic module carrying multi-byte characters

The whole-package sweep is the stronger evidence and takes about five minutes,
because the stdlib side is the very function whose cost this removed. The
control keeps the fast version so it stays runnable, and adds the case the
package itself cannot supply: this repository is strict-ASCII, so **no real
module can exercise a multi-byte slice**, which is exactly what a byte-offset
extractor breaks on. Ten multi-byte segments compared there; the arm refuses to
pass on fewer than four.

    shipped walk, before this wave   22.1s
    widened walk, cache absent       59.0s
    widened walk, as shipped          4.6s      <- 4.8x faster than the narrow walk

The constant pre-skip was kept -- it is behaviour-preserving and arm 2 proves
it -- but the comment claiming it was the speedup is corrected in place, with
the profile that refuted it, so the next reader does not inherit the wrong
cause.

---

## 7. EVERY NUMBER, RE-DERIVABLE

    python scripts/_census_message_interpolations.py --json     # 480 / 792 / 37
    python scripts/_check_the_dict_literal_walk_can_fail.py     # 3 arms, 3 mutations
    python scripts/_check_the_dict_literal_walk_can_fail.py --narrow
    python -m pytest tests/test_no_message_publishes_a_landing.py -q
    python -m tests.test_no_message_publishes_a_landing --write-baseline
    python scripts/count_census_states.py

**THE BEFORE IS RE-DERIVABLE WITHOUT A CHECKOUT.** `--narrow` removes the two
dict entry points from the current walk and prints both sides, so the
counterfactual survives in the tree rather than only in this document:

    subject digest 1035304ce819 over 46 modules

                                        sites  sub-exprs  shortlisted
    WITH the dict entry points            480        792           37
    WITHOUT them (pre-2026-09-21)         311        558           19
    THE EXCLUSION'S COST                 +169       +234          +18

    SITES THE EXCLUSION HID THAT REACH THE ADDRESS SHORTLIST: 18
       server.py   <module>                returned['experience'] ... x13, all BASE_URL
       shape.py    parse_connection_card   returned['profile']          ['slug']
       shape.py    apply_route             returned['why']              ['raw_href'] x3
       writes.py   _direction              returned['what_that_means']  ['observation.state_url']

**The narrowed walk reproduces 311 / 558 / 19 exactly**, which is the
independent check that this lift is purely additive: no pre-existing row moved
bucket, changed expression or disappeared.

Baseline verdict distribution, before and after:

| verdict | before | after |
|---|---:|---:|
| SERVER_CONSTRUCTED | 4 | 17 |
| ASKED_FOR | 7 | 7 |
| PUBLISHED_BY_CONTRACT | 2 | 7 |
| WITHHELD | 5 | 5 |
| NAMES_NO_ADDRESS | 1 | 1 |
| **total** | **19** | **37** |

### 7.1 THE IMPACT GATE, AND WHAT IT SAYS IT DID NOT RUN

Run on the staged tree immediately before the commit:

    python scripts/impact_gate.py

    impact-gate: 10 changed path(s) -> 44 SELECTED + 15 corpus-wide = 44 test file(s).

      PASS over the 44 file(s) above (2277 tests) -- AND OVER NOTHING ELSE.

      NOT CHECKED: 164 of 208 test files (78.8% of the suite by file).
      The corpus-wide guards DID run, so the identity, credential and page-text
      sweeps cover the whole tree. Everything else above is unexamined.
      That is roughly 3817 of 6094 tests unrun (62.6%), against a suite count
      taken 2026-09-20 at 970a276.
      Wall clock: 673.3s.
      THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
      certifier; a green gate here is not a reason to shrink that matrix.

**READ THE SECOND HALF, NOT THE FIRST.** 62.6% of the suite did not run. What
DID run is everything the analyser could couple to these ten paths plus the
fifteen corpus-wide guards, and the identity gate separately reported
`10 staged file(s) against 218 spellings; 0 hits`.

**AND THE FIRST RUN OF THIS GATE REFUSED**, on
`test_a_correction_is_findable_from_the_claim` -- section 5.5a. That is the
gate doing its job on this document rather than on the code, and it is the
reason this section quotes the THIRD run.

**WHAT IS NOT COVERED BY THAT RUN:** this subsection itself, and the two
sentences added to section 8 after it. They are prose in this file and nothing
else. The four doc-facing guards were re-run over the final text afterwards --
`test_a_correction_is_findable_from_the_claim`,
`test_the_audit_index_is_derived`, `test_the_rulings_register_is_derived` and
`test_the_register_numbers_are_unique` -- and the two derived views were
regenerated with their build scripts and re-checked. Said out loud because a
gate may not claim more than it ran, and that includes when the thing it did
not run is the paragraph describing it.

---

## 8. WHERE THIS DISAGREES WITH WHAT IT WAS HANDED

| the record said | disk says |
|---|---|
| census at HEAD: 310 sites / 557 sub-expressions | **311 / 558 at `f729a2a`.** 310 / 557 is exact at `6c24426`, the tree that measured it; the merge brought one `RAISE` in `dom.activate_messaging_filter` from `b73783a`. Both right, neither current without its revision |
| *"a shared walk that two committed baselines import"* | **one.** `tests/test_no_message_publishes_a_landing.py` and nothing else under `tests/` or `scripts/`. The envelope and reader baselines belong to driven guards that discover their own subjects |
| *"+4 rows needing rulings"*, priced against +124 sites, *"a wave and not a line"* | **+124 sites costs that baseline nothing** -- it admits only shortlisted sub-expressions. The full lift costs **18 baseline rows, of which 13 are verdicted from the code and 5 need adjudication across 3 functions** |
| the four new `EXCEPTION_TEXT` sub-expressions include `server.py::_error` | **it does not,** at the variant producing that `+4`. The fourth is `server.py::_badge_refusal` -- the row the same section separately calls a classifier artefact. `_error` enters that variant as one `PASSTHROUGH` bucketed `PAGE_OR_SITE_DERIVED`, and reaches `EXCEPTION_TEXT` only under `all-dicts` |
| `_error` is outside the census *"and therefore outside `test_no_message_publishes_a_landing`'s subject set too"* | **true, and lifting the exclusion does not change it.** That guard is scoped to `SHORTLIST_TOKENS`; `_error`'s three expressions name no address. With the exclusion fully lifted the baseline gains 18 keys and none is in `_error`. The lift is right for a different reason |
| the brief: start from `_census_page_coercions.py` / `_census_reader_guard_subjects.py` / the INSTRUMENTS entry on *"argument, dict literal, subscript assignment"* | **none of the three.** The exclusion is in `_census_message_interpolations.py`. `_census_page_coercions.py` has an explicit `ast.Dict` branch and never had this gap; the INSTRUMENTS line describes a control on `tests/test_the_source_url_split_was_never_ruled.py` |
| the brief: *"`stated rows` must total 704 after your change"* | **704, unchanged** -- and the instruction conflates two censuses. `_audit/_census/*.md` is the CAPABILITY census; the rows this residual owes verdicts to live in `tests/landing_interpolation_baseline.json`. Checked both ways anyway |

**AND ONE AGAINST MYSELF.** My baseline-cost harness returned the same answer
for four different walks and I nearly wrote that down as "the lift costs
nothing." It was a memoised cache, recorded in 5.4. Separately, I wrote a
performance claim into a source comment before profiling it; the profile
refuted it and the comment now carries its own refutation (section 6). And I
wrote that the thirteen `BASE_URL` rows came from ONE module-level table;
they come from TWO, `CENSUS_SURFACES` (10) and `PROFILE_DETAIL_URLS` (3),
found by opening the file rather than by trusting a plausible sentence I had
just typed. Three self-corrections in one wave, all of them from running or
reading the thing rather than from re-reading the claim.

---

## 9. RESIDUAL

**R1. `shape.apply_route`'s three sites carry one verdict and disagree about
its ground.** On the identified branch `destination` republishes `raw_href`;
on the two refusal branches it is `None` and the justification is the refusal
doctrine alone. `verdict_for` keys `PUBLISHED_BY_CONTRACT_SITES` by
`module:function`, so this guard cannot express the split, and a future repair
that withheld the href on the two refusal branches would NOT show as a verdict
change. Whoever owns `shape.py` should decide whether the refusal branches want
`landing.withheld`; my judgement is that they do not, because a refusal that
cannot name the href it rejected cannot be acted on. Written here rather than
folded into the table so the disagreement survives.

**R2. The ordinal hazard did not bite and is still live.** Baseline keys are
`module:function:expr[:60]` with a `#n` ordinal, and **10 of 37 keys carry
one**, in 3 groups. If a widening ever inserts a site that sorts BEFORE an
existing same-base site, every later ordinal shifts and the verdicts
re-attribute silently -- `compare()` would report one `appeared` and nothing
else. Measured today: `vanished 0`, `changed 0` for all four variants, and
every ordinal group is verdict-uniform, so no misattribution is possible right
now. That is a property of today's data, not of the key scheme.

**R3. 27 of 49 tool bodies are `not_driven`.** Unchanged by this wave and
unchangeable by any static widening. It is the real remaining hole around
`_error` and it needs `PlantedPage` to grow a `context` and a `request`, which
is ordinary work needing no ruling.

**R4. What the census still does not count**, now that the dict literal is off
the list: a built string `return`ed on its own outside a dict; a string passed
to `print`; a message assembled across a function boundary by a helper; an
f-string reached only through `str.join`. Unmeasured, and named so the next
reader does not have to find out by being surprised.

**R5. Arm 3 of the control covers 8 of 46 modules.** It prints the 38 it did
not run, and it cannot cheaply cover them because the stdlib side of the
comparison is the function whose cost this wave removed. The synthetic
edge-case module covers the shapes those 38 could not supply anyway
(multi-byte, multi-line, mid-line start, nested f-string), which is why the
trade was taken -- but it is a trade, and a segment bug that needs a
construct unique to one large module would survive it.

**R6. `server._error`'s two renderings are now COUNTED and still UNRULED as a
publication question.** The census sees them; no guard rules on whether
`scrub(str(exc))` may carry a third party's exception text, because that is the
open trade in section 7 of `_audit/2026-09-21-what-the-browser-said.md` and it
belongs to the operator, not to this wave. Nothing here makes that decision
harder or easier; it only makes both renderings visible to the instrument that
will have to measure it.

**R7. `_audit/INSTRUMENTS.md` carries 16 non-ASCII characters at HEAD**, in
section 2-era prose well above section 52, in a repository whose rule is
strict ASCII. Find them with a codepoint scan rather than a line number -- that
register is append-ordered and its line numbers rot within the day. Confirmed
present at `f729a2a` before this wave touched the file
and deliberately NOT repaired here: it is another section's text, the file is
append-contended by several waves, and an in-place edit far from my own append
is exactly the kind of change that loses somebody's work. Named so it is a
known quantity rather than a surprise for whoever next runs an encoding check.
