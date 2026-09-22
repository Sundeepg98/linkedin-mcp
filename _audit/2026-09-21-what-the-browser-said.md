# WHAT THE BROWSER SAID: `$.message`, adjudicated by PROVENANCE CLASS

Wave `what-the-browser-said`, 2026-09-21, from `75a1983`.

**SUBJECT:** `server._error` builds `{"error": ..., "message": scrub(str(exc))}`.
`config.scrub` substitutes only THIS SERVER'S OWN FILESYSTEM PATHS, so a name
has no shape to scrub. The `$.url` wave measured a needle planted inside the
exception `page.evaluate` raised arriving at `$.message` in all 12 drives, left
it deliberately, and called it *"third-party provenance, 89 sub-expressions
package-wide; needs a ruling, not an edit."*

No browser was opened. No LinkedIn page was loaded. Everything below is
offline, against the committed tree and this repository's registered fakes.

---

## 0. THE ANSWER, FIRST

**THE THREE CLASSES THE BRIEF NAMES ARE NOT THREE CLASSES OF EXCEPTION. TWO OF
THEM ARE THE SAME TYPES CARRYING DIFFERENT PAYLOADS, AND `_error` CANNOT TELL
THEM APART.** `int("<a label from the page>")` raises a *stdlib* `ValueError`
-- a library's exception by author, the page's text by payload. At `_error` the
only facts available are `type(exc)` and `str(exc)`; what the text QUOTES is
not among them.

    THE DISCRIMINATOR IS NOT THE EXCEPTION'S AUTHOR.
    IT IS WHETHER A VALUE THE PAGE CHOSE ENTERED THE EXCEPTION'S ARGUMENTS,
    AND THAT IS KNOWABLE AT THE RAISE AND UNKNOWABLE AT THE ENVELOPE.

So a policy written at `_error` is necessarily uniform across all three
classes, which is exactly the reflexive wrap of a deliberate publication that
the standing fourteen-row ruling forbids. **`_error` is the wrong place, and
that is a reason rather than a preference.**

| class | verdict | enforced where |
|---|---|---|
| **1.** the package's own exception text | **PUBLISHABLE. Already governed, per site.** | `tests/test_no_message_publishes_a_landing.py` + `tests/landing_interpolation_baseline.json` -- 5 verdicts, `UNRULED` is a FAILURE |
| **2.** a library's exception text, no page value in its arguments | **PUBLISHABLE. Type-only here would be a net loss.** | nowhere, and it does not need to be -- section 3.2 |
| **3.** a page value carried inside ANY exception | **FORBIDDEN, AND ALREADY FORBIDDEN.** | `tests/test_readers_emit_no_page_string.py` (119 readers, driven) and, new in this wave, `tests/test_tool_envelopes_emit_no_page_string.py` (49 tools, driven) |

**NOTHING IN THE THREE CLASSES NEEDS THE OPERATOR.** One narrower question
does, and it is section 7: a single paragraph, with what ships meanwhile.

**THE CORPUS HAS ANSWERED THIS QUESTION THREE TIMES IN CODE AND NEVER WRITTEN
IT DOWN AS A RULE.** `coerce.py` answers it at the raise (never build the
exception). `press.disclose` answers it at the catch (render the type, drop
the text). `landing.py` answers it at the interpolation (a closed vocabulary).
Three precedents, one method, and the method is the ruling -- stated once, in
section 3.4, and registered as `ERROR-MESSAGE-RULED-AT-THE-RAISE`.

---

## 1. WHAT THE REGISTER RETURNED, VERBATIM, AND HOW THE NEGATIVE WAS CORROBORATED

Queried five ways before deciding anything. Every query returned the SAME best
match, and it is about a DIFFERENT FIELD:

    venv/Scripts/python scripts/build_rulings_index.py --find \
      "third-party exception text published in the error message field"

    10 registered ruling(s) match 'third-party exception text published in the
    error message field', best first:

      1. ERROR-URL-ASKED-FOR-OR-NOTHING   [2026-09-21]
         RULED  : The error envelope's url field carries the address this
                  server ASKED FOR, or nothing at all. A landing is never
                  published there; where a requested address exists in scope
                  publishing it is REQUIRED rather than merely permitted, and
                  where none exists the key is omitted and the landing is
                  DESCRIBED in the hint. A descriptor never goes into the url
                  field.
         BINDS  : verb -- what ExtractionFailedError.url may carry, per site
         WHERE  : _audit/2026-09-21-the-field-beside-the-message.md
         SECTION: 5. THE RULING, STATED ONCE SO IT CAN BE CITED
         ALIASES: the field beside the message, the twenty sites, ERROR-URL-PER-SITE

The other four phrasings -- *"may the error envelope message carry a string the
page wrote"* (14 matches), *"scrub removes paths only a name has no shape to
scrub"* (28), *"coercion leak int quoting its own refused page input"* (14),
*"provenance of a string this package did not author"* (25) -- returned
`ERROR-URL-ASKED-FOR-OR-NOTHING` first or second and then the general
boundary rulings. **No registered ruling binds `$.message`, and none binds
third-party exception text.**

### 1.1 THE NEGATIVE IS CORROBORATED OUTSIDE THE REGISTER, AND IT IS NOT A CLEAN NEGATIVE

The register's own section 4 says the scan reads `RULED:` and nothing else and
that its recall is poor, naming six signals it never sees. So the corroboration
was run against those signals directly, over `_audit/` and `tests/`:

| signal searched | hits about the message field |
|---|---|
| a heading naming the message field or exception text | 2 -- both `_audit/2026-09-21-the-field-beside-the-message.md` section 4.1, which says it did NOT decide this |
| a bold `RULED`/`THE RULING` line mentioning message / exception / `str(exc)` / scrub | 0 |
| a test pinning what `$.message` may carry | see below |

**AND THE SEARCH FOUND THE THING THE REGISTER COULD NOT: THE MESSAGE FIELD IS
NOT UNRULED.** `tests/test_no_message_publishes_a_landing.py` plus
`tests/landing_interpolation_baseline.json` are a per-site ruling over message
sites, with a five-verdict alphabet -- `WITHHELD`, `SERVER_CONSTRUCTED`,
`ASKED_FOR`, `PUBLISHED_BY_CONTRACT`, `NAMES_NO_ADDRESS` -- and `UNRULED` is a
FAILURE, not a bucket. It is not in the register because it lives as a test
rather than as an audit passage, which is the same reason the `source_url`
split ruling is not registered.

**ITS SCOPE IS THE ANSWER TO HALF THIS WAVE'S QUESTION.** It governs messages
that interpolate an ADDRESS, by a source-text rule over expression names
(`url`, `landed`, `final_url`, `href`, `slug`, `redirect`). `{exc}` matches
none of those, so the third-party exception text is outside it BY
CONSTRUCTION, not by oversight. **Class 1 is governed. The gap is classes 2
and 3.**

That is the best available outcome on the register's own terms -- a standing
per-site ruling found, cited and applied -- and it is why this wave did not
write a second one for class 1.

---

## 2. THE MEASUREMENT AT HEAD -- MINE, NOT RELAYED

### 2.1 THE CHANNEL IS STILL OPEN, RE-RUN RATHER THAN QUOTED

    venv/Scripts/python scripts/_probe_dom_error_url_field.py

    12 readers, verdict "reached" x12
      "url_needle_at":   []              x12   <- the $.url repair HOLDS
      "inner_needle_at": ["$.message"]   x12   <- this wave's subject, OPEN
    plus job_panels_via_read_profile_fields: url_needle_at [], inner_needle_at ["$.message"]

The brief's claim is confirmed on the box rather than inherited.

### 2.2 THE 89, RECONCILED -- AND THE PREDECESSOR'S PRESENTATION ADDS TO 90

    venv/Scripts/python scripts/_census_message_interpolations.py --json

    HEAD sites: 310, sub-expressions 557
      UNCLASSIFIED                    174
      TYPE_ONLY                       118
      SERVER_CONSTRUCTED               96
      EXCEPTION_TEXT:arbitrary         89
      PAGE_OR_SITE_DERIVED             69
      CALLER_SUPPLIED                  10
      EXCEPTION_TEXT:package_raised     1

    EXCEPTION_TEXT by enclosing handler:
      inside 'except Exception'              86
      inside 'except OSError'                 3
      inside 'except ExtractionFailedError'   1

**86 + 3 + 1 = 90, and the bucket is 89.** The fourth line is not part of it:
`except ExtractionFailedError` is `EXCEPTION_TEXT:package_raised`, a DIFFERENT
bucket. So **89 = 86 + 3**, and `_audit/2026-09-21-the-landed-url.md` section
6.5 prints all four under a heading of 89. The brief's "89 sub-expressions, 86
of them under `except Exception`" is correct; the audit's table is what
misleads, and it is pinned here so nobody re-derives it a second time.

Distribution, which narrows the class usefully: **59 of the 89 are in
`dom.py`**, 11 in `browser.py`, 5 in `auth.py`, and 12 modules carry any at all.

### 2.3 THE CENSUS CANNOT SEE THE ENVELOPE IT IS THE DENOMINATOR FOR

`scripts/_census_message_interpolations.py` declares honestly that it does not
count *"strings built into a `dict` LITERAL (`return {"error": f"..."}`)"*.
**`server._error` publishes BOTH of its `message` values exactly that way.**
Measured: the census's 310 sites include `server.py::_error` ONCE, and it is

    module   : server.py
    kind     : PASSTHROUGH
    target   : out["hint"]
    message  : scrub(hint)

-- the hint, assigned to a subscript. **Neither `message` rendering is in the
subject set.** The package's single widest publication point for third-party
exception text is outside its own census, and therefore outside
`test_no_message_publishes_a_landing`'s subject set too, since that guard
imports this walk rather than writing a second one.

**HOW MUCH WOULD CLOSING IT COST? MEASURED, NOT ESTIMATED.** The shipped
`_Walker` was subclassed with a `visit_Return` that reuses the shipped
`_is_message_field` key test and the shipped `_record_field`, and driven
through the shipped `census_sources`:

    SHIPPED WALKER        310 sites, 557 sub-expressions, 19 SHORTLISTED
    PLUS RETURNED DICTS   434 sites, 738 sub-expressions, 23 SHORTLISTED

    DELTA   sites +124   sub-expressions +181   SHORTLISTED sites +4
            EXCEPTION_TEXT sub-expressions +4

The four newly SHORTLISTED sites are all in `shape.py` -- `parse_connection_card`
and `apply_route` x3 -- and each would need its own verdict written into the
committed `landing_interpolation_baseline.json`. The four new EXCEPTION_TEXT
sub-expressions are `server.py::_error`, `server.py::linkedin_premium_job_collection`,
`preflight.py::report` and `cdp_bridge.py::probe`.

**NOT DONE HERE, AND THE MEASUREMENT IS WHY.** +124 sites on a shared walk
that two committed baselines import, plus 4 rows needing rulings on one of
them, is a wave and not a line. What this wave contributes is the number: the
exclusion is no longer "declared in a docstring", it is priced.

One honest artefact of the widened walk, recorded so nobody chases it:
`server.py::_badge_refusal`'s `out["error"]` classifies as
`EXCEPTION_TEXT:undecided` because its PARAMETER is named `error`. It is a
plain string argument, not exception text. A classifier artefact, not a site.

### 2.4 `_error` IS NOT THE ONLY ERROR ENVELOPE, WHICH THE BRIEF AND ITS OWN COMMENT BOTH ASSUME

`_error`'s comment says *"Every tool funnels its failures through here."*
Measured by AST over `server.py`: **49 `mcp.tool` coroutines, 48 of whose
bodies contain `_error(`** (the exception, `linkedin_login_browser`, delegates
to `linkedin_login`, which does). True for UNHANDLED failures.

It is false for at least one HANDLED one. `linkedin_premium_job_collection`
returns

    {"error": "index_out_of_range", "message": str(exc), "collections": [...]}

-- **the package's only `str(exc)` publication with no `scrub` at all.**
`preflight.py::report` is a second envelope outside `_error`, publishing
`unresolvable_message(f"{type(exc).__name__}: {exc}")`.

**The premium one is REPAIRED IN THIS WAVE, and the repair is a DECLARATION
rather than a wrap** -- see section 5.3.

---

## 3. THE PROVENANCE CLASSES, EACH WITH ITS VERDICT AND ITS REASON

### 3.1 CLASS 1 -- THE PACKAGE'S OWN EXCEPTION TEXT. PUBLISHABLE; ALREADY GOVERNED.

**VERDICT: publishable, and no new ruling is written for it, because one
already exists and was found.** `tests/test_no_message_publishes_a_landing.py`
rules every message site that names an address, per site, with five verdicts
and `UNRULED` as a failure. It discovers its subjects through the shipped
census walk, so a message written tomorrow is in the subject set the moment it
is written.

**RESIDUAL, NAMED:** the census's dict-literal exclusion (2.3), which puts
`_error`'s own two renderings outside that guard, priced at +124 sites and +4
ruled rows.

`EXCEPTION_TEXT:package_raised` is **1** sub-expression package-wide, so this
class is also the smallest of the three by a long way.

### 3.2 CLASS 2 -- A LIBRARY'S EXCEPTION TEXT. PUBLISHABLE; TYPE-ONLY WOULD BE A NET LOSS.

**VERDICT: publishable.** Three reasons, in descending strength:

1. **`_error` CANNOT IMPLEMENT ANYTHING ELSE.** Any rule here also applies to
   classes 1 and 3, because the envelope cannot see provenance. A remedy that
   cannot be scoped to its class is not a remedy for that class.
2. **THE MESSAGE IS THE DIAGNOSIS, AND THE ALTERNATIVE DELETES IT.**
   `press.disclose` shows this package knows how to write type-only --
   *"ONLY THE EXCEPTION TYPE. A library's message is composed by code nobody
   here controls and has been measured carrying selectors and urls."* It pays
   that price at a site where the message buys nothing. `_error` is the
   opposite site: its message is the only thing a caller gets.
3. **THE ONE THING ANYBODY HAS MEASURED POINTS AWAY FROM THE HAZARD.** The
   `$.url` wave read Playwright's shipped driver source and found both
   navigation-failure templates interpolate the REQUESTED url, not the
   landing.

**AND I DECLINE TO CERTIFY THE BRIEF'S PREMISE THAT THIS CLASS IS "BOUNDED AND
PREDICTABLE".** It is not established: reason 3 covers two templates out of a
bundle, and a selector error quotes a selector. But the premise does not carry
the verdict -- reason 1 does -- so the verdict survives the premise being
false.

**AND I DECLINE THE PREDECESSOR'S RECOMMENDATION, WITH A REASON IT COULD NOT
HAVE HAD.** `_audit/2026-09-21-the-field-beside-the-message.md` section 4.1
recommends type-only on the twelve `dom.py` reader messages **AS THE NEXT
WAVE**. Measured here, cross-checking `scripts/_probe_dom_error_url_field.py`'s
twelve target functions against `tests/reader_leak_baseline.json`:

    dom.py entries in the reader-leak baseline      57
    of those, named by the $.url probe as its 12    12
    their committed verdicts                        clean 4, returns_text 8
                                                    not_driven 0, leaks 0

**ALL TWELVE ARE INSIDE A DRIVEN GUARD AND ALL TWELVE ARE GREEN.** So the
PAYLOAD class is already held closed for exactly those twelve readers, and the
only thing type-only would additionally buy is protection against Playwright
quoting page content in its own message -- which no needle in this repository
travels, and which the one available reading argues against. **Deleting twelve
real diagnoses to close that is a loss.** The recommendation was correct on the
evidence available when it was written; it is wrong on the evidence available
now, and the difference is the interaction between two guards that no single
wave had looked at together.

### 3.3 CLASS 3 -- A PAGE VALUE INSIDE AN EXCEPTION. FORBIDDEN, AND ALREADY FORBIDDEN.

**VERDICT: forbidden, enforced at the raise, and the enforcement is already
written -- including the sentence that is the ruling.**
`tests/test_readers_emit_no_page_string.py`:

> RETURNING PAGE TEXT CAN BE A CONTRACT. RAISING A `ValueError` THAT QUOTES
> PAGE TEXT IS NOBODY'S CONTRACT.

That is executable, discovers its subjects, and is green at HEAD (208 passed
with its two siblings). `linkedin_server/coerce.py` is the repair it holds in
place.

**BUT IT IS NOT A PACKAGE-WIDE STATEMENT, AND THE GAP IS EXACTLY WHERE THIS
WAVE'S SUBJECT LIVES.** Measured by the `reader-guard-gap` slice
(`_audit/_slice-reader-guard-subjects.md`), three independent ways that agree:

    module-level functions in linkedin_server/     591
      IN-SUBJECT-SET (async def with a `page` param) 119   <- the guard's reach
      async def WITHOUT a `page` param                58
      plain def                                      414

    server.py                                        86
      IN-SUBJECT-SET                                  6
      async def without `page`                       52   <- 49 are mcp.tools
      plain def                                      28   <- `_error` is one

    of server.py's 52 non-page async functions, mcp.tools    49
    of those 49, containing `_error(`                        48

    reader_leak_baseline.json      119 entries
      clean 58 / returns_text 40 / not_driven 21 / leaks 0

**THE 48 TOOL BODIES THAT FUNNEL INTO `_error` ARE OUTSIDE THAT GUARD AND
ALWAYS WILL BE**, because it only ever discovers `async def` functions taking a
page, and `_error` is a plain `def` -- doubly outside. The reader guard's own
docstring names `server._error` as where a laundered exception reaches a
caller. **Nothing was driving it.** That is what this wave built (section 5.1).

### 3.4 THE RULING, STATED ONCE SO IT CAN BE CITED

`CANONICAL-RULING-ID` requires every ruling to have ONE id and every citation
to resolve to a SYMBOL rather than to a re-derived phrase, so this wave's
decision is written here once and registered in `_audit/RULINGS.md` as
`ERROR-MESSAGE-RULED-AT-THE-RAISE`. Every code comment this wave left cites it.

**RULED: what the error envelope's message may carry is decided WHERE THE
VALUE ENTERS THE EXCEPTION, never where it leaves.** The provenance classes
are not classes of exception -- a page value inside a stdlib `ValueError` is
indistinguishable at `server._error` from one that is not -- so no per-class
policy may live at the envelope, and a uniform one there is the reflexive wrap
of a deliberate publication that the standing fourteen-row ruling forbids. The
package's own exception text and a library's own exception text are
PUBLISHABLE: the message is the diagnosis, and deleting it to close a channel
no needle travels is a loss rather than a repair. **A value the PAGE chose is
FORBIDDEN inside any exception, whoever authored the class**, and is enforced
at the site where the value enters -- `coerce.py` at the raise,
`press.disclose` at the catch, `landing.py` at the interpolation -- with the
property held by driving: `tests/test_readers_emit_no_page_string.py` over
119 readers and `tests/test_tool_envelopes_emit_no_page_string.py` over 49
tools.

---

## 4. WHAT I DID NOT DO, AND WHY EACH ONE WAS DELIBERATE

* **`scrub(str(exc))` IS NOT WRAPPED.** Forbidden by the standing per-site
  ruling, and section 0 gives the structural reason it would be wrong even if
  it were allowed.
* **THE MESSAGE IS NOT DELETED.** A diagnostic nobody can read is how a
  package earns a `--no-verify` habit.
* **THE TWELVE `dom.py` MESSAGES ARE NOT MADE TYPE-ONLY.** Section 3.2, with
  the baseline cross-check that settles it.
* **THE CENSUS IS NOT WIDENED.** Section 2.3, with the price.
* **`shape.py` AND `notify_cost.py` ARE NOT EDITED.** Section 6 records a real
  finding in them; they are not this wave's files, and the finding is handed
  over rather than half-fixed.

---

## 5. THE CONTROLS -- FAILING FIRST, THEN PASSING

### 5.1 THE NEW GUARD: `tests/test_tool_envelopes_emit_no_page_string.py`

Drives every `mcp.tool` coroutine in `linkedin_server/server.py` against
`tests/plantedpage.py` -- the registered page double, which answers every page
read with a planted string -- and hunts the plant in the returned envelope.
Four verdicts, the reader guard's vocabulary reused rather than reinvented:
`clean`, `returns_text` (a separate finding, not a failure), `leaks`
(unconditional), `not_driven` (never a pass).

**A DRIVE IS PROVEN, NOT ASSUMED.** A tool dying on its first line returns a
tidy envelope with no plant in it, which looks exactly like a pass, so the page
counts its own reads and a drive with ZERO of them is `not_driven` with that
reason.

At HEAD:

    tools discovered: 49
       clean           17
       returns_text     5
       leaks            0
       not_driven      27

### 5.2 SHOWN FAILING FIRST, ON A NEEDLE THE PAGE SUPPLIED

`scripts/_check_the_tool_envelope_guard_can_fail.py` **imports** the plant from
`scripts/_check_the_coercion_family_guard_can_fail.py` rather than writing a
second copy -- two copies of that walk would drift, and the drift would be
invisible. The plant is not an invented mutation: it is the `int()` coercion
that shipped until 2026-09-20.

    venv/Scripts/python scripts/_check_the_tool_envelope_guard_can_fail.py

    BASELINE: the repaired tree, before anything is planted
      repaired         49 tools -- clean 17, returns_text 5, LEAKS 0, not_driven 27
    PLANTED: the shipped int() coercion, at 6 binding(s)
      planted          49 tools -- clean 15, returns_text 4, LEAKS 3, not_driven 27
          LEAKS  linkedin_job_collections       a coercion-failure message reached the output  at $.message
          LEAKS  linkedin_people_search_shape   a coercion-failure message reached the output  at $.message
          LEAKS  linkedin_search_appearances    a coercion-failure message reached the output  at $.message
    REMOVED: the plant is off, the tree is back
      repaired again   49 tools -- clean 17, returns_text 5, LEAKS 0, not_driven 27

    GUARD FIRED ON THE PLANT: YES (3 leaking)
    GUARD WENT GREEN AGAIN:   YES (0 leaking)
    PASS: the guard can fail, and does so only on the defect.
    exit 0

**THE NEEDLE IS THE PAGE'S.** Nothing in the control puts a string into an
exception by hand -- that would prove the envelope can carry text, which was
never in doubt. `PlantedPage` answers a page read with it, the planted `int()`
quotes whatever it is handed, and the value travels a real tool's real failure
path into `$.message`. **Three of the 48 tool bodies the reader guard cannot
reach, convicted at the exact field this wave was asked about.**

A count of zero replaced bindings is a loud failure of the control rather than
a pass of the guard, and it is printed: 6.

### 5.2a THE GUARD'S FIRST RED WAS ITS OWN BUG, TWICE, AND BOTH ARE RECORDED IN IT

* **My leak rule was too crude and convicted the repository's own contract.**
  The first draft called any envelope with an `error` key a failure envelope,
  and convicted `linkedin_newsletter_subscriptions` for publishing
  `badge_before.saw.shaped_label` in a refusal. A refusal built by
  `_badge_refusal` is a RETURN VALUE that deliberately says what it saw -- the
  standing rule that a refusal naming only what it did NOT match is half a
  measurement -- and the SAME field is on `linkedin_connections`'s success
  path. Narrowed to `_error`'s own CLOSED VOCABULARY of `error` kinds,
  discovered by walking `LinkedInReaderError.__subclasses__()`.
* **MY OWN INSTRUMENT SMUGGLED THE PLANT OUT THROUGH THE POSITION IT REPORTS.**
  `linkedin_search_appearances` returns `view_name_counts` **keyed by the
  name**, so the plant arrived inside a JSON PATH -- and a path is the one
  thing this file prints. Found by running it, not by reviewing it. Path
  segments carrying a page string are now spelled `<key the page chose>`, and
  the hunt was widened to find a plant that arrives ONLY as a key, which a
  value-only walk cannot see.

The second is this wave's own instance of *taint does not survive a container*,
in the instrument written to measure that class.

### 5.3 THE ONE REPAIR IN `server.py`, AND IT IS A DECLARATION

`linkedin_premium_job_collection`'s `{"error": "index_out_of_range", "message":
str(exc), ...}` bypasses `_error` and so inherits nothing from the envelope's
ruling. **It is provably safe today and was undeclared**, which is the state
this repository keeps paying for. `job_collections.collection_url` raises a
`TypeError` naming `type(index)` and never the value, or an `IndexError` built
from an int already proven int one line earlier, a length, and this module's
own constants.

So the repair is the declaration, not a scrubber -- adding one would buy
literally nothing here and would be the reflexive wrap the standing ruling
forbids. The comment names the provenance, the reason, and what would falsify
it (`collection_url` ever rendering its argument). `_error` itself carries a
matching citation.

### 5.4 EVERY NUMBER HERE IS RE-DERIVABLE

    venv/Scripts/python -m pytest tests/test_readers_emit_no_page_string.py \
        tests/test_no_message_publishes_a_landing.py \
        tests/test_the_error_url_is_ruled_per_site.py -q
      -> 208 passed in 46.69s

    venv/Scripts/python -m pytest tests/test_tool_envelopes_emit_no_page_string.py -q
      -> 2 passed in 19.17s

    venv/Scripts/python scripts/_check_the_tool_envelope_guard_can_fail.py
      -> PASS, 6 bindings planted, 3 tools LEAK under the plant, 0 without it

    venv/Scripts/python scripts/_probe_dom_error_url_field.py
      -> 12 reached, $.url clean x12, $.message carrying the needle x12

    venv/Scripts/python scripts/_census_message_interpolations.py
      -> 310 sites, EXCEPTION_TEXT:arbitrary 89 (= 86 + 3)

### 5.5 THE IMPACT GATE, AND WHAT IT SAYS IT DID NOT RUN

Staged first, then run. Its plan line, and the line it prints about its own
reach, both verbatim:

    impact-gate: 12 changed path(s) -> 87 SELECTED + 15 corpus-wide = 87 test file(s).

    NOT CHECKED: 120 of 207 test files (58.0% of the suite by file).
    The corpus-wide guards DID run, so the identity, credential and page-text
    sweeps cover the whole tree. Everything else above is unexamined.
    That is roughly 2091 of 6094 tests unrun (34.3%), against a suite count taken 2026-09-20 at 970a276.
    Wall clock: 793.5s.

87 of 207 files is 42%, under the widening threshold, so **no widening notice
was printed**. The run before this one was RED on five derived-file tests --
`_audit/INDEX.md`, `_audit/RULINGS.md` and the correction register, all of
which this wave had changed the inputs to without regenerating -- and they
are green now.

**AND THE GATE CAUGHT SOMETHING ABOUT ITSELF THAT IS WORTH WRITING DOWN.** Its
second run went red on ONE test, from an edit made to this document AFTER
staging: `tests/test_a_correction_is_findable_from_the_claim.py` reads the
WORKING TREE, while the gate selects its plan from the INDEX. **A staged-diff
gate can run a guard whose subject is the unstaged file**, so "I staged, then
gated" does not mean the gate saw what I staged. Every candidate it raised was
triaged before this commit, and the sequence that makes the claim honest is:
finish the prose, THEN stage, THEN gate -- which is the order this section's
numbers were produced in.

---

## 6. WHAT I LEFT OPEN, AND FOR WHOM

### 6.1 `shape.invitation_badge` STATES A PREMISE THE PACKAGE ELSEWHERE MEASURES FALSE -- for whoever owns `shape.py`

Found by driving, not by reading. `dom.read_invitation_badge`'s docstring says:

> THE LABEL IS SHAPED ON THE WAY OUT ... **so a nav label that one day carries
> a name carries it no further than the page.**

and `shape.invitation_badge`'s says *"what reaches here is a shape"*. The
shaping is real -- `out["label"] = shape.census_shape(...)` -- but `dom.py`
says twice, in its own comments, that **`census_shape` is a CHARACTER AND
LENGTH GATE and not a redactor** (`dom.py` around `read_surface_census`:
*"BE PRECISE ABOUT WHAT `census_shape` BUYS, BECAUSE IT IS NOT WHAT ITS NAME
[SUGGESTS]"*, and *"OVERSTATEMENT"*). A short plain name passes it unchanged.

Driven: the plant passed `census_shape` untouched and was published at
`saw.shaped_label` on **three tools** -- `linkedin_connections`,
`linkedin_newsletter_subscriptions`, `linkedin_notify_cost_precondition` -- on
both the success and the refusal branches.

**NOT A LEAK BY THIS WAVE'S RULING** -- it is `returns_text`, a deliberate
publication on both branches, and wrapping it would break the contract the
refusal rests on. **BUT THE SENTENCE IS FALSE AND IT IS LOAD-BEARING**: it is
the sentence a future reader would cite to conclude the badge path is safe.

**WHY I DID NOT JUST FIX THE DOCSTRING, WHICH WOULD HAVE COST A MINUTE.** The
two honest repairs are incompatible: either correct the claim and keep
publishing the label, or publish the label's SHAPE instead of the label
(`landing.withheld` is the worked precedent, and its alphabet is closed).
**Doing the prose half alone would leave the next reader believing the
question was settled**, which is precisely the defect `_audit/INDEX.md` was
built to make visible -- a claim overtaken, with nothing telling the reader
who arrives at it. It is one decision, it belongs to whoever owns `shape.py`
and `notify_cost.py`, and half of it is worse than none.

### 6.2 THE CENSUS'S DICT-LITERAL EXCLUSION -- for whoever owns `scripts/_census_message_interpolations.py`

Priced in 2.3: +124 sites, +181 sub-expressions, +4 rows needing verdicts in
`tests/landing_interpolation_baseline.json` (all four in `shape.py`), +4
EXCEPTION_TEXT sub-expressions including `_error` itself. A wave, and the
number is now on disk so it does not have to be re-derived.

**CORRECTED BY:** `_audit/2026-09-21-the-dict-literal-exclusion.md` -- the exclusion was LIFTED on 2026-09-21 and this pricing was wrong in three ways. The `+124 sites` costs the baseline nothing: that guard admits only SHORTLISTED sub-expressions, so the site count is the wrong denominator. Exactly ONE committed baseline imports this walk, not two. And the delta figures reproduce exactly while one of the four names does not -- at the variant producing `+124 / +181 / +4` the fourth new EXCEPTION_TEXT sub-expression is `server.py::_badge_refusal`, not `server.py::_error`; `_error` is added there as a PASSTHROUGH bucketed PAGE_OR_SITE_DERIVED and reaches EXCEPTION_TEXT only under the wider all-dicts scope. Full lift measured: 311/558/19 -> 480/792/37, baseline 19 -> 37 rows, 0 changed, 0 vanished, 5 rows needing adjudication across 3 functions -- a line, not a wave. Section 2.3's premise that widening would bring `_error` inside `test_no_message_publishes_a_landing` is separately false: that guard's subject rule is the address shortlist, and `_error`'s three expressions name no address. What governs `_error` is the DRIVEN guard at the envelope, `tests/test_tool_envelopes_emit_no_page_string.py`, which this document itself shipped.

### 6.3 THE QUOTING CALLEES: 14 OF 26 PROVEN, 9 SITES OUTSIDE THE READER GUARD, TRIAGED

The `quoting-callees` slice (`_audit/_slice-quoting-callees.md`,
`scripts/_census_quoting_callees.py`) answered the question
`ERROR-MESSAGE-RULED-AT-THE-RAISE` needs answered to be applicable: **which
stdlib callables quote their refused input at all**, proven by CALLING them
with a sentinel rather than by assertion.

    callees proven echoing        14 of 26 tested
    call sites found              238
      of those PAGE_OR_ARG         31
        in a function WITH a page parameter   22   <- the reader guard's set
        in a function WITHOUT one              9   <- outside it
      UNCLASSIFIED                146   (residual NOT forced to zero)
    subscript sites (separate)    970, of which PAGE_OR_ARG 18, only 2 with a page

Echoing, proven: `int` (incl. base 10/16), `float`, `strptime`,
`date.fromisoformat`, `datetime.fromisoformat`, `dict[k]`, `dict.pop(k)`,
`list.index`, `set.remove`, `getattr`, `ipaddress.ip_address`, an `Enum`
lookup. **Not echoing, which is the half that shrinks the class:** `complex`,
`Decimal`, `re.compile`, `json.loads`, `uuid.UUID`, `bytes.fromhex`,
`list.remove`, `str.index`, `list.pop`.

**I TRIAGED ALL NINE MYSELF RATHER THAN BANKING THE COUNT**, because a count
of sites is not a count of hazards:

| site | verdict |
|---|---|
| `auth.py::_cookie_expiry` `float` | **SAFE** -- inside `except (TypeError, ValueError)`, swallowed |
| `cookie_jar.py::_expires_from_row` `int` | **SAFE** -- same, swallowed |
| `server.py::_clamp` `int` | **SAFE** -- same, swallowed |
| `search_results.py::_lift_function` `.index` | **FALSE POSITIVE, and the census cannot avoid it.** The receiver is a `str`, and `str.index` was PROVEN not to echo; only `list.index` does. A name-based walk cannot tell them apart without types |
| `server.py::linkedin_login` `int(wait_seconds)` | **CALLER_SUPPLIED**, escapes to `_error`. Decision `D1` in `_audit/2026-09-21-the-read-triage.md`, still unruled |
| `server.py::linkedin_search_jobs` `int(start)` | **CALLER_SUPPLIED**, same class |
| `search_results.py::tally` `int(queries_present)` | **UNGUARDED**, but the value is a presence flag the module itself computes |
| `writes.py::aim_invitation` `int(matches)` x1, `int(position)` x1 | **THE SHARPEST RESIDUAL IN THE PACKAGE.** Unguarded `int()` on values that came off the page, in a module whose readers are recorded `not_driven:needs grant: WriteGrant` in `tests/reader_leak_baseline.json` -- **so nobody has ever driven them.** The surrounding prose says *"no label crossed into this process"* and the values are counts by construction, which is an argument rather than a measurement |

`writes.aim_invitation` is the one row a later wave should take first: it is
the intersection of *unguarded*, *page-derived* and *undriven*, and the repair
if it needs one is `coerce.as_int`, already shipped.

### 6.4 THE 27 `not_driven` TOOLS -- for a later wave, not for him

`PlantedPage` has no `context` and no `request`, so every tool opening with a
cookie read or a voyager call is `not_driven`. That is the honest verdict and
never a pass; the baseline makes a shrinking driven set loud. Widening the
double is ordinary work needing no ruling.

---

## 7. THE ONE PARAGRAPH THAT IS HIS

**Everything above was decided without him. This is the residue, and it is a
trade rather than a question of fact.** A library's exception text is
publishable (3.2) and a page value inside an exception is forbidden and guarded
(3.3). What is left is the case where the BROWSER ITSELF quotes page content in
its own message -- a Playwright error naming something LinkedIn drew. No needle
this package controls travels that path, so no offline instrument can measure
it; the only reading anyone has (Playwright's own driver source, two navigation
templates) says those interpolate the address we requested. The only remedy is
type-only at `_error`, which would delete the diagnostic channel every tool in
the package reports failures through. **The question: do you want that trade
taken blind, or do you want the measurement first -- driving a real failure
against the real browser, which is the one thing that would convert this from
unmeasured to measured and which needs your go because it means a live
session?** My recommendation is the measurement, and if you would rather not
spend a live run, my recommendation is to leave the message published:
deleting a real diagnosis to close an unwitnessed channel is a loss with the
evidence as it stands. **MEANWHILE, WHAT SHIPS IS SAFE:** the two driven
guards hold the payload class at both ends of the pipe, the option remains
available at one site, and nothing about this trade is made harder by waiting.

---

## 8. ANYTHING CONTRADICTING THE BRIEF

The brief asked for this, and disk disagreed with it five times. Every
disagreement is recorded above and is load-bearing.

| the brief said | disk says |
|---|---|
| three provenance classes to adjudicate separately | **classes 2 and 3 are the same TYPES with different PAYLOADS.** `int("<a label>")` is a stdlib `ValueError`. The discriminator is the payload's origin, not the exception's author (section 0) |
| *"this is a provenance class the corpus may not have ruled on at all"* | **the message field IS per-site ruled** -- `tests/test_no_message_publishes_a_landing.py`, five verdicts, `UNRULED` is a failure -- but scoped to ADDRESSES. Class 1 is governed; the gap is 2 and 3 (section 1.1) |
| *"`_error` is the error envelope for the whole package"* | **it is not the only one.** `linkedin_premium_job_collection` publishes `str(exc)` with no `scrub` at all and bypasses it; `preflight.py::report` is a third envelope (section 2.4) |
| *"89 sub-expressions, 86 of them under `except Exception`"* (correct) | the AUDIT it comes from prints 86 + 3 + 1 under a heading of 89. **89 = 86 + 3**; the fourth is a different bucket (section 2.2) |
| the `$.url` wave's own *"RECOMMENDED AS THE NEXT WAVE"* -- type-only the twelve | **declined.** All twelve are inside `test_readers_emit_no_page_string`'s subject set and green (4 clean, 8 returns_text, 0 not_driven). The payload class is already closed for them; type-only would delete twelve diagnoses to close a channel no needle travels (section 3.2) |

**AND ONE AGAINST MYSELF, WHICH IS THE ONE WORTH READING.** My guard's first
version convicted `linkedin_newsletter_subscriptions` for a refusal that names
what it saw -- i.e. for obeying a standing rule of this repository. A leak rule
built from the shape of an envelope rather than from its provenance convicts
contracts. Corrected to `_error`'s own closed vocabulary before anything was
committed, and recorded in the guard so the next author does not rebuild the
crude version (section 5.2a).

---

## 9. FILES

| path | what |
|---|---|
| `tests/test_tool_envelopes_emit_no_page_string.py` | NEW -- the driven guard for the 48 tool bodies the reader guard cannot discover |
| `tests/tool_envelope_baseline.json` | NEW -- 49 verdicts: clean 17, returns_text 5, not_driven 27. There is no verdict meaning "this leaks" |
| `scripts/_check_the_tool_envelope_guard_can_fail.py` | NEW -- the control, importing the sibling's plant |
| `linkedin_server/server.py` | `_error` carries the ruling's citation; `linkedin_premium_job_collection`'s unscrubbed `str(exc)` is DECLARED |
| `_audit/_slice-reader-guard-subjects.md` | slice: the reader guard's exact subject set, 3 agreeing measurements |
| `scripts/_census_reader_guard_subjects.py` | slice instrument (imports the shipped `discover_readers`) |
| `scripts/_census_quoting_callees.py` | slice instrument: 26 callables tested by CALLING them, 14 proven echoing |
| `scripts/build_rulings_index.py` | the judged entry for `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| `_audit/RULINGS.md`, `_audit/INDEX.md` | DERIVED, regenerated with `--write`, never hand-merged. 37 rulings, 215 documents, both `--check` green |
| `tests/test_a_correction_is_findable_from_the_claim.py` | one `NOT_A_CORRECTION` triage: section 6.3's table row corrects this wave's OWN census, not the document cited two rows below it |

**THE `quoting-callees` SLICE'S PROSE REPORT NEVER ARRIVED.** Its instrument
was on disk and complete, so rather than wait on a channel that is not durable
I reviewed the script (925 lines, ASCII, no side effects, no absolute paths, no
source text printed, and honest in its own docstring about the `.index`
over-approximation that I then found in its output) and **re-derived every
number in section 6.3 by running it myself**. The instrument is committed; the
numbers are re-derivable; the missing file is the report, not the measurement.
