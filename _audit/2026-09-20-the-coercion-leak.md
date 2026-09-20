# A name can leave the process through an exception

2026-09-20. Base `ba5835d`. Register section 44.

## THE FINDING IN ONE SENTENCE

`int()` writes the value it refused VERBATIM into its own `ValueError`, that
exception escapes the reader, `server._error` renders it through
`config.scrub` -- which substitutes THIS SERVER'S OWN PATHS and nothing else,
because a person's name has no shape to scrub -- so:

> **AN INTEGER-ONLY RETURN VALUE DOES NOT MAKE A FUNCTION INTEGER-ONLY,
> BECAUSE AN EXCEPTION IS NOT A RETURN VALUE.**

Checking a reader's return type is therefore not a check of this property, and
it was checked that way earlier the same day -- on this very surface, by
someone who had just finished proving a shaper name-free. The return type was
correct. It was the wrong question.

---

## 1. WHICH CONSTRUCTORS ARE IN THE CLASS -- MEASURED, NOT ASSUMED

`scripts/_census_page_coercions.py` calls each candidate with a marker and
reports whether the marker survives into `str(exc)`, `repr(exc)` or
`exc.args`. The subject list is a measurement because a census that assumed it
would be wrong in both directions.

| constructor | raises | quotes its input |
|---|---|---|
| `int` | ValueError | **YES** (str, repr, args) |
| `float` | ValueError | **YES** |
| `int(x, 10)` | ValueError | **YES** |
| `datetime.strptime` | ValueError | **YES** |
| `datetime.fromisoformat` | ValueError | **YES** |
| `list.index` | ValueError | **YES** |
| `dict[key]` | KeyError | **YES** (the KEY, not the value) |
| `complex` | ValueError | no |
| `uuid.UUID` | ValueError | no |
| `json.loads` | JSONDecodeError | no |

Seven of ten quote. `complex` and `uuid.UUID` describe the failure without
naming the input, which is the behaviour the repair reproduces.

---

## 2. THE ENUMERATION -- EXACT INTEGERS

Produced by `scripts/_census_page_coercions.py` (AST, not grep) over
`linkedin_server/` at base `ba5835d`.

**273 coercion sites in 31 modules.** By kind: `int` 262, `float` 4,
`.index` 7.

### Why an AST walk and not a text search

`git grep -c` for `int(` and `float(` reports **296 lines**; the AST reports
**273 sites**, and the two disagree in both directions per module. `dom.py`
alone holds **118 textual hits** and the great majority are `parseInt` inside
JAVASCRIPT STRING LITERALS -- in-page script text, which cannot raise a Python
`ValueError`. A grep census would have inflated the denominator with sites that
cannot hold the defect, and missed sites split across lines. The contrast is
printed by the instrument itself rather than asserted here.

### The five buckets

| bucket | sites | what it means |
|---|---:|---|
| `PAGE_DERIVED` | **103** | unguarded, and its input can be a string THE DOCUMENT CHOSE. The hazard set. |
| `GUARDED` | 90 | lexically inside a `try` catching ValueError/TypeError/Exception. |
| `BOUND_ONLY` | 39 | inside a page reader, but coercing a CALLER-SUPPLIED BOUND (`int(max_items)`, `int(timeout_ms)`). |
| `OFF_PAGE` | 39 | unguarded, input is config, env, or a value the server constructed. |
| `LITERAL` | 2 | the argument is a constant. |

`PAGE_DERIVED` spans **6 modules and 35 functions**:

| module | hazard sites |
|---|---:|
| `writes.py` | 44 |
| `dom.py` | 43 |
| `events.py` | 6 |
| `anchors.py` | 4 |
| `collections_page.py` | 3 |
| `server.py` | 3 |

### The distinction that decides the whole census

It is **not** whether a value was awaited.

> `await locator.count()` is awaited and CANNOT be a string -- Playwright
> computes that integer and its type is Playwright's contract, not the
> document's. `await page.evaluate(...)` can be anything the page's JavaScript
> returned, including a name.
>
> **A VALUE IS PAGE-CONTROLLED WHEN THE DOCUMENT CHOOSES IT, NOT WHEN A
> COROUTINE PRODUCED IT.**

A first version of this census ignored that and returned **142** hazard sites
in 7 modules. It convicted `groups_page.read_group_memberships`, whose two
coercions are `int(await anchors.count())`, and six sites in
`events.read_events_home`, which coerces nothing but `.count()` results and
`len()` of text. Those are structurally incapable of carrying a string, and a
census that cries wolf on them is one nobody acts on. Modelling the
source type -- plus `len`/`bool`/`sum` as type-FIXING -- moved the count to
**103 in 6 modules**, and `groups_page.py` left the hazard set entirely.

**The static bucket is a hypothesis.** Measurement is the verdict, and it
acquitted further sites still (section 3).

---

## 3. THE MEASUREMENT -- WHICH SITES ACTUALLY LEAK

`tests/plantedpage.py` supplies a page that answers in strings;
`tests/test_readers_emit_no_page_string.py` discovers every module-level
`async def` in the package taking a `page` and drives it, hunting the plant in
the return value AND in anything raised.

**115 readers discovered.**

| verdict | at base | after repair |
|---|---:|---:|
| `clean` -- driven, carried nothing out | 47 | **55** |
| `returns_text` -- returns page text BY CONTRACT | 33 | **39** |
| `not_driven` -- offline harness could not reach it | 21 | **21** |
| **`leaks` -- carried the plant out through an exception** | **14** | **0** |

**The true total is 16, not 14**, and the extra two were found by a THIRD
false clean in this harness -- see the box below. 14 is what the harness saw on
its first honest run; `dom.read_invitation_surface` and
`writes._read_profile_invitations` were added once it stopped skipping
defaulted parameters.

> ### A DEFAULT IS A BRANCH, AND AN UNTAKEN BRANCH IS NOT A CLEAN ONE
>
> `dom.read_invitation_surface(page, needle=None, ...)` opens with
> `if not wanted: ... return out`. Driven with defaults only it takes that
> early return and **never reaches the three coercions below it**. It reported
> `clean`. It was not measured.
>
> That is the third instance of one disease inside this single wave: a payload
> key nobody supplied, a `dict()` that copied past an override, and a default
> that skipped a branch. All three are the same sentence --
> **a harness only exercises what its author remembered to exercise** -- which
> is the whole argument for a guard that DISCOVERS its subjects rather than
> listing them. The harness now drives each reader twice, once with defaults
> and once with every supportable optional supplied, and takes the worse
> verdict.

### Six readers moved `leaks` to `returns_text`, and that is the right direction

`read_job_insight_panels`, `read_own_activity_items`,
`read_profile_views_insights`, `read_recipient_ids`, `read_search_appearances`,
`read_surface_census` and `_read_dark_mode` used to RAISE on a page that
answers in strings. They now complete, and what they return lands in fields
that carry page text by contract -- `.shape`, `.slug`, `.description`.

**The repair did not create those fields; it made them reachable on an input
that previously crashed.** `read_surface_census` is the documented case: its
own docstring states that `census_redact_rare` is NOT applied there and that
*"A CALLER THAT EMITS THESE RECORDS WITHOUT AGGREGATING THEM MUST APPLY
`census_redact_rare` ITSELF"* -- and records that shipping without it once
printed a member's name. That contract is unchanged by this wave and is the
shapers' subject, not this guard's. It is named here so the behaviour change is
on the record rather than discovered later.

### The two verdicts are different findings and only one is a defect

`dom.read_main_text` returning the page's main text is its entire job;
`read_save_control` returning a control's label is the reading a caller asked
for. Whether those strings may be published is the SHAPERS' question, governed
by `shape.py`, `menus.py` and the redaction tests. Folding them in would paint
33 readers red for working correctly, and the response to a wall of red is to
weaken the guard.

> **RETURNING PAGE TEXT CAN BE A CONTRACT. RAISING A `ValueError` THAT QUOTES
> PAGE TEXT IS NOBODY'S CONTRACT.**

So `leaks` needs no judgement call and has no exemption list to be argued into
-- and an exemption list is how the previous three instances of this class
stayed open.

### The 16

The first twelve plus two were found on the first honest run; the last two only
once the harness stopped skipping defaulted parameters (marked +).

| reader | module |
|---|---|
| `read_anchors` | `anchors.py` |
| `read_collections` | `collections_page.py` |
| `read_file_inputs` | `dom.py` |
| `read_job_insight_panels` | `dom.py` |
| `read_own_activity_items` | `dom.py` |
| `read_profile_views_insights` | `dom.py` |
| `read_recipient_ids` | `dom.py` |
| `read_sdui_actions` | `dom.py` |
| `read_search_appearances` | `dom.py` |
| `read_self_owned_editor_fields` | `dom.py` |
| `read_self_owned_editor_values` | `dom.py` |
| `read_surface_census` | `dom.py` |
| `_editor_value_of` | `writes.py` |
| `_read_dark_mode` | `writes.py` |
| `read_invitation_surface` (+) | `dom.py` |
| `_read_profile_invitations` (+) | `writes.py` |

### `collections_page` DOES leak. The earlier report was wrong.

**CORRECTS:** `_audit/2026-09-20-the-search-admission.md` -- its section 7 states that `collections_page.read_collections` does not leak; it does, on the same path as `anchors.py`, and the survey that cleared it was driving a payload missing `matches`, the one key that reader reads, so the coercion never ran and "not driven" printed as "clean". The `anchors` half of that sentence stands.

Section 7 records `collections_page.read_collections` as NOT leaking. It leaks,
on the same path as `anchors.py`, and the reason the survey said otherwise is
worth more than the correction.

That survey drove the siblings with a hand-written superset payload:

    {"anchors": 1, "counts": [plant], "headings": 1,
     "groupings": [plant], "collections": [plant]}

`read_collections` reads `raw.get("matches")`. **`matches` is not a key in
that payload.** The list came back empty, the comprehension iterated nothing,
the coercion never ran -- and **"not driven" printed as "clean"**.

> A HAND-WRITTEN PAYLOAD CAN ONLY EXERCISE THE KEYS ITS AUTHOR THOUGHT OF.

That is the same defect `tests/leakwalk.py` records having learned twice at the
level of secrets: a guard that is a list of known-bad strings cannot see the
class it guards. Here it is one level up, in the keys. So `PageAnswer` answers
EVERY key, and its key vocabulary is HARVESTED FROM THE PACKAGE SOURCE (470
literals, every `x.get("k")` and `x["k"]` in `linkedin_server/`) rather than
typed out.

### And the harness had the same disease -- measured, in this wave

The first run of the corrected harness reported **4** leaks. The true number
was 14. `dom.py` does `data = dict(data or {})` at fourteen sites, and
`dict()` of a dict SUBCLASS copies the concrete storage without ever calling
the overridden `get`. The key-agnostic double was being flattened back into
whatever keys it literally held, so ten readers were handed a page that
answers every key with a name and reported having seen nothing --
`read_surface_census` returned `controls_read: 0`.

> **PATCHING THE BEHAVIOUR IS NOT PATCHING THE CALL SITE WHEN THE CALL SITE
> COPIES THE VALUE.** The same shape bit twice in one wave: `dict()` copying
> a mapping's storage, and `from ... import` copying a function object (which
> is why `scripts/_check_the_coercion_family_guard_can_fail.py` rebinds the
> helper at every import site and PRINTS HOW MANY bindings it replaced -- a
> plant that reached nothing proves nothing).

Seeding the concrete storage with the harvested vocabulary fixed it. **Ten of
the sixteen leaks were invisible until that was repaired**, which is the
strongest argument in this document for measuring rather than reading.

---

## 4. THE REPAIR

`linkedin_server/coerce.py` -- one home, so the class can be closed instead of
re-fixed per site.

| helper | contract |
|---|---|
| `as_int(value)` | an `int` it was handed, or `None`. **Never raises, never quotes.** Refuses `bool`, since `True` is an `int`. |
| `as_count(value, default=0)` | the drop-in for `int(X or 0)`. Substitutes and **LOGS THE TYPE, NEVER THE VALUE**. |
| `counts_only(values, default=0)` | position-preserving integers plus a refusal COUNT. |
| `scalars_only(raw, names)` | `{name: int}` plus a refusal count; absent and wrong are counted differently. |

Three properties are load-bearing and easy to lose:

1. **A refused entry is SUBSTITUTED, never DROPPED.** Several callers align
   lists positionally against a closed alphabet whose index 0 is the hazard
   class (`member_profile`, `person_result`). Dropping one renames every kind
   behind it -- the silent rename `term_for` refuses to commit by never
   clamping, arriving one function earlier.
2. **In `collections_page` the substitute is `-1`, not `0`.** `-1` is
   `UNMATCHED`. Falling back to `0` would name the heading `domains` --
   asserting a grouping the page never said.
3. **The log names `type(value).__name__` and never `value`.** A log record is
   another way out of the process; the redaction rule that applies to a return
   value applies to it unchanged, and
   `test_as_count_logs_the_type_and_never_the_value` drives the real logger
   and reads `caplog` to prove it.

`search_results._as_int` KEEPS ITS NAME and delegates. It is the plant point of
`scripts/_check_the_shaper_leak_guard_can_fail.py`, which proves that guard can
fail by rebinding it; importing `coerce.as_int` into the callers' bodies would
have silently disarmed the one control showing that guard failing.

`anchors.tally` and `collections_page.tally` were repaired too, though neither
touches a page. Both docstrings claim an address cannot reach them -- true of
the RETURN path only. Handed a string, `int()` would have quoted it straight
back out.

---

## 5. THE GUARD -- AND IT DISCOVERS ITS OWN SUBJECTS

`tests/test_readers_emit_no_page_string.py`.

A guard that NAMES the readers it knows about catches the third instance of a
class and not the fourth, which is the shape of every repair this repository
keeps re-making. So the subject set is discovered by introspection: every
module-level `async def` in `linkedin_server` taking a `page`. **A reader
written tomorrow is in the subject set the moment it is written.**

### It may not claim more than it ran

`not_driven` is a THIRD verdict and never a pass.
`tests/reader_leak_baseline.json` records the verdict for every discovered
reader, and `test_the_driven_set_has_not_silently_shrunk` fails on three
events: a reader that used to be driven no longer is; a new reader appears
unclassified; a known one vanishes. **That file is the half no diff-scoped gate
would select** -- a change to `dom.py` that makes a reader start raising
shrinks coverage silently and nothing in the diff says so.

The baseline REFUSES to record a leaking reader. A file holding
`"x": "leaks"` would become a list of permitted leaks within one commit of
somebody being in a hurry.

### The third path out, which the two verdicts above leave between them

A raise carrying the plant is a LEAK. A return carrying page text is CONTRACT.
Between them sits this, which this package does at **18 sites across 6
modules**:

    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"

If a coercion inside such a `try` refuses a page string, the ValueError never
escapes -- **its message is RETURNED instead**, quoting the name in a field,
and the guard as first written would have called that `returns_text` and
passed it.

> **A NAME THAT LEAVES THROUGH A CAUGHT EXCEPTION HAS STILL LEFT.**

Measured: **22 coercion sites sit inside such a `try`**, and **all 22 are
`int(await ...count())`** -- Playwright integers, which the page cannot turn
into a string. So the hazard is real and **empty BY CONSTRUCTION rather than by
luck**, which is the PAGE-CONTROLLED / PLAYWRIGHT-TYPED distinction of section
2 holding up under a second, independent test it was not designed for.

`plantedpage.carries_a_laundered_exception` closes it anyway, matching on
phrases only a failed coercion produces (*"invalid literal for int()"*) -- no
contract field in this package says those words, so the match is precise rather
than a heuristic. It is checked BEFORE `returns_text`, because a check wired in
the wrong order is a check that does not run, and
`test_a_reader_that_launders_a_coercion_failure_is_called_a_leak` drives a
synthetic reader built with exactly that defect to prove the wiring.

### Shown failing

`scripts/_check_the_coercion_family_guard_can_fail.py` restores the coercion
that actually shipped -- `int()` -- at every binding, and prints the count of
bindings replaced. **A control whose defect is the real previous state is the
strongest kind available**, because nobody has to argue the mutation is
representative.

Result: **11 readers go RED under the plant and GREEN again on its removal**,
including both readers this wave was originally sent to repair. 44 clean
readers are NOT convicted, which is the expected half -- a reader whose values
are already integers cannot leak through a coercion, and the plant demonstrates
that by failing to make it.

It rebinds at every import site and **prints how many bindings it replaced**,
because `from linkedin_server.coerce import as_count` copies the function
object: patching `coerce.as_count` alone would change nothing `dom` ever calls,
and the script would have reported a guard that "cannot fail" when it had never
been handed a defect. A count of zero is a loud failure of the control.

---

## 6. WHAT REMAINS UNREPAIRED, AND WHY

### The static residue, joined to what was measured

The census over the repaired tree reports **219 sites in 29 modules** (from 273
in 31), with the hazard bucket at **52 sites in 4 modules** (from 103 in 6).
**51 hazard sites removed.** Joining each remaining site to the measured
verdict of the reader that holds it:

| the reader holding the site was... | remaining hazard sites |
|---|---:|
| `clean` -- driven, measured not to leak | 19 |
| `returns_text` -- driven, text is contract | 9 |
| **`not_driven` -- NOT MEASURED** | **24** |

So of 52 remaining static sites, **28 are acquitted by measurement and 24 are
genuinely unmeasured.** A static hazard site in a reader that was driven and
did not leak is a coercion the analysis could not prove safe and the
measurement could -- the census doing its job as an over-approximating
superset, exactly as designed.

Per module the residue is `writes.py` 42, `events.py` 6, `server.py` 3,
`dom.py` 1. Two are worth naming:

* `events.read_events_home` (6) is the census's own over-approximation:
  `int(record["rows"])` where `record["rows"]` already holds an `int`, reached
  through a `zip()` the analyser cannot follow. Measured clean.
* `dom.read_reaction_surface` (1) is `int(out["controls"])` where
  `out["controls"]` was set two lines earlier from `int(await
  controls.count())` -- a Playwright integer. Flagged because `out` also holds
  page text elsewhere. Measured, and safe by reading as well.

### Three `dom.py` readers were repaired although measurement had cleared them

`read_comment_surface` measured clean for a reason that is a property of its
CALLER, not of its own line: `read_surface_census` was repaired earlier the
same day, so what reaches `int(census.get("controls_read") or 0)` is already
integers. That is one edit away from not holding, and leaving it is exactly the
"repair the site that bit" pattern this wave exists to break. Repaired.
`read_reaction_surface` was NOT, because its value is a Playwright integer by
construction rather than by a neighbour's good behaviour -- the distinction is
the point.

### The 21 readers this harness cannot drive

They are not claimed as clean.

| reason | readers | why it is left |
|---|---:|---|
| `needs grant: WriteGrant` | 5 | **A POLICY REFUSAL, NOT A CAPABILITY GAP.** A `WriteGrant` is "permission to perform ONE action, on ONE target, ONCE" -- the object between a preview and an irreversible act. Putting a grant constructor in the test tree to reach a few more coercions is not a trade this wave will make, and `writes.perform` is in the discovered set. |
| `raises BrowserUnavailableError` | 9 | auth and navigation readers that need a real browser. Out of scope by instruction: this wave touched no browser and no live surface. |
| `raises WriteAttemptError` | 4 | write-path entry points that refuse before reading. |
| other refusals | 3 | `activate_messaging_filter` validates its argument against a closed set; `read_unfollow_control` raises `ExtractionFailedError`; one needs an `Observation`. |

**The `writes.py` write-path gates are the largest unmeasured block in this
document: 42 of the 52 remaining static hazard sites, 24 of them in readers
this harness could not drive at all.** They are recorded as UNMEASURED rather
than as clean, and the honest statement is that the class is **closed for every
reader this harness can reach and open for the write-path gates it cannot.**

### And they were NOT repaired mechanically, which was a decision

`as_count` is behaviour-identical to `int(X or 0)` for every input the shipped
code handled, so a blanket sweep of all 42 was available and cheap. It was
refused.

> A GATE THAT RAISES ON A MALFORMED PAGE IS FAILING CLOSED, AND "NO LONGER
> RAISES" IS NOT OBVIOUSLY SAFE THERE.

`_send_gate`, `_recipient_gate` and `_typeahead_gate` stand between a preview
and an irreversible act. Converting a raise into a substituted `0` in a gate
nothing in this wave can exercise is a change this wave cannot certify, and an
uncertified edit to a send gate is worse than the leak it would close. They
need the measurement first, and the measurement needs a ruling or a browser.

Driving them needs either a ruling that the harness may mint a grant, or a
live-browser wave. **Neither is a decision this wave should make alone.**

`events.py` (6 sites) and `groups_page.py` are NOT in this list: they were
acquitted by measurement, not left out of it.

---

## 7. INSTRUMENTS

| path | disposable? |
|---|---|
| `linkedin_server/coerce.py` | shipped code |
| `tests/plantedpage.py` | **REGISTER** -- reusable page double |
| `tests/test_readers_emit_no_page_string.py` | **REGISTER** -- the family guard |
| `tests/reader_leak_baseline.json` | **REGISTER** -- the coverage record |
| `scripts/_check_the_coercion_family_guard_can_fail.py` | **REGISTER** -- shows the guard failing |
| `scripts/_census_page_coercions.py` | **REGISTER** -- the enumeration |
| `scripts/_survey_reader_page_api.py` | COMMITTED, **NOT REGISTERED** -- it answered one question (which readers are drivable without a browser) and has no standing job. Kept on disk rather than deleted only because it is cheap to re-run and it is what the drivability split in section 6 is derived from; a future wave that needs that split should re-run it rather than trust the numbers here. |
