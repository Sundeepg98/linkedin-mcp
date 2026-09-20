# The Premium block: 18 rows, none of them blocked on the subscription

Wave `premium-block`, 2026-09-20. Offline against committed fixtures and the tree.
No browser, no session, no `mcp__linkedin__*` call, no write fired.

## THE SHORT ANSWER TO THE QUESTION THAT STARTED THIS

The premise behind "why is our MCP not covering any of the premium things" is
half right, and the half that is wrong is worth saying first because it is the
half that flatters nobody if it goes unsaid.

**Premium is already exploited in three places, not zero:**

| what | where | what the entitlement buys |
|---|---|---|
| entitlement itself | `linkedin_premium_status`, `server.py:1944`, backed by `linkedin_server/premium.py` | a five-state verdict that refuses to collapse a tie |
| profile viewers | `linkedin_who_viewed_me`, `server.py:1551` | **365 days of depth instead of the free tier's five viewers** (`server.py:1557`) |
| job postings | `linkedin_job_detail`, `server.py:3881` | the Premium company panel, read and shaped (`server.py:4136`) |

**And then 18 rows are still GAP. Not one of them is blocked on entitlement.**
Sorted by what is actually in the way:

| what is actually in the way | rows | count |
|---|---|---|
| built already, never fired | J 123, N 135 | 2 |
| a control that is named, rendered and never pressed | J 124, J 126, N 133, N 134, (N 136) | 4 + 1 |
| a reader nobody wrote | J 127, N 132 | 2 |
| an address not on the read allowlist | J 113, J 114 | 2 |
| the recipient gate, which is RULED to refuse | J 129, M M47, N 192 | 3 |
| a census counting constraint, still being adjudicated | J 78, J 79, J 80 | 3 |
| genuinely unreached, zero code | P B9 | 1 |
| another wave's | N A7, N A8, N A9 | 3 |

The subscription is not the blocker anywhere on that list. Two rows need only a
session. Four need a press. Two need an address. Three need a gate that was
deliberately built to refuse.

---

# 1. THE VERDICT ASKED FOR FIRST: J 127 AND N 136

Both were banked MEASURED-ABSENT. **Both verdicts are unsound, for the same
reason, and it is the reason the brief predicted: in each case the instrument
that returned the absence could not have seen the thing if it were there.**

## 1.1 J 127 -- "Read the InMail credit balance" -- WRONGLY CLOSED

State today: `MEASURED-ABSENT SKILL` (`_audit/_census/jobs.md:343`).
Blocker map: `PREMIUM-READER-NOT-BUILT`, `state_at_freeze GAP`, `state_today
MEASURED-ABSENT` (`blocker-map.tsv`, row `J 127`).

**The blocker is right and the state is wrong.** The two cannot both stand, and
the blocker wins on the evidence.

### What the row claims

Its adjudication has two legs. Leg 1: the boundary claim expired -- true, and I
confirm it. `/premium/my-premium/` IS admitted; the pattern is compiled at
`readonly.py:1068`. Nothing there needs correcting.

Leg 2 is the one that fails: *"THE READER HALF IS MOOT, because the page was
opened and THE BALANCE IS NOT ON IT."*

### Why leg 2 does not hold

**The only instrument that has ever opened that page is
`scripts/_probe_premium_entitlement.py`**, whose logic `linkedin_server/premium.py`
packages verbatim -- the module's own header says so: *"Every needle tuple and
the verdict table below are lifted from `scripts/_probe_premium_entitlement.py`,
which opened `/premium/my-premium/` under CDP attach."*

That instrument does exactly this and nothing else:

* it selects `_CONTROL_SELECTOR = "a, button"` -- links and buttons only;
* it reads their accessible names into a local, case-folds them;
* it tallies substring hits against **16 needles this repository authors**:
  8 in `ENTITLED_NEEDLES` (cancel subscription, manage plan, billing, next
  payment, ...) and 8 in `UNENTITLED_NEEDLES` (start free trial, try premium,
  choose plan, ...);
* it returns, in its own docstring's words, *"an integer, a boolean, `None`, or
  one of our needle names -- never the control text that matched one."*

**Not one of those 16 needles is about a balance, a credit, or a number.**
Measured, not asserted: `balance`, `credit`, `inmail` and `numeric` each return
ZERO hits across the whole probe file.

So the instrument that produced the absence:

1. never looked for a balance, and
2. could not have reported one if it had -- a credit balance renders as page
   TEXT, and this reader reads `a`/`button` accessible names and publishes no
   text by construction.

**A reading that cannot express the positive result is not evidence for the
negative one.** That is the same law `_audit/_scratch/_progress-analytics-creator.md`
s11 already wrote down for a different page: *"A DETECTOR THAT IS RIGHT ABOUT
WHAT IT MEASURES CAN STILL BE THE WRONG INSTRUMENT FOR THE QUESTION, AND THE
SECOND FAILURE IS INVISIBLE INSIDE THE FIRST."* It was written in September and
not applied here.

### The sentence that got mistaken for an answer

`readonly.py`'s admission comment for that address reads:

> *"it exists to answer ONE question: whether an InMail balance is a countable
> thing this server can read."*

**That states the QUESTION. The census row banked it as the ANSWER.** The
comment goes on to establish only that the COMPOSER carries no balance (the
control named `InMail` there is a conversation FILTER PILL with
`aria-checked=false`) and concludes *"So the balance is either here or
nowhere"* -- an open disjunction, not a resolution.

Downstream, `writes.py` states flatly that *"`/premium/my-premium/` carries no
numeric balance of any kind."* **That claim has no instrument behind it.** It is
an inference from a needle sweep that never searched for a number.

### And there is no offline route to settle it

Zero committed fixtures of `/premium/my-premium/` -- `grep -rl "my-premium"
tests/fixtures/` returns nothing. So no corpus read can close this either way.

### VERDICT

**J 127 should read `GAP`, blocker `PREMIUM-READER-NOT-BUILT`.** The blocker
name was correct from the start. Restoring GAP moves the count the wrong way for
this slice and is still the only defensible state.

**KNOCK-ON, REPORTED AND NOT WRITTEN:** the sibling row `M4`
(`messaging-and-content.md:335`) carries the identical unbacked claim -- *"admits
`/premium/my-premium/` for exactly this and it carries no balance"* -- under
`EXCLUDED-RULED`. Same defect, different slice. The J 127 cell already flagged
the pair as "reported rather than changed"; this adds the reason the shared claim
fails. Whoever owns the messaging slice should take it.

## 1.2 N 136 -- "top locations, industries and companies of your viewers" -- CLOSED TOO HARD

State today: `MEASURED-ABSENT` (`_audit/_census/network.md:439`).

This one is subtler: the conclusion may well be true, but **the row cites two
sources, and the stronger of the two says the opposite of what the row banked.**

### The cited source refuses the verdict in its own words

The row cites `_audit/_scratch/_progress-analytics-creator.md` s11 as *"a
measurement that survived its own operator arguing against it."* That document's
s11 says, verbatim, in its own corrected disposition:

> * `N 136` -- top locations / industries / companies: **still not established.**
>   No control names them; `Company` is a FILTER ... **I have not improved on
>   that.**

**"Still not established" is not "measured absent."** The row promoted a
declared non-result into a verdict.

The same section says why, and generalises it:

> `N 135` -- the weekly trend graph: **still not established.** ... **My
> instrument counts controls; a graph is not a control, so this row is outside
> what this probe can answer.**

A top-locations breakdown is a rendered DISPLAY, exactly like a graph. By the
instrument's own stated limit it is outside what a control tally can answer --
in either direction.

### The best evidence is the one the row does not cite -- and I tested it

There is a third source: the docstring above `VIEWS_CHART_VIEW_NAME` in
`dom.py`, backed by `tests/fixtures/profile_views_analytics_hydrated.html` plus a
live confirmation on 2026-09-03. It asserts *"There is no top-companies panel
and no locations control of any kind, in the capture or live."* That is a much
better leg, because a hydrated capture holds rendered structure, not just
controls.

**I ran it offline. It half-holds.**

Vocabulary sweep of that fixture -- `top location`, `top companies`,
`Top industries`, `industries`, `Locations`: **all zero.** That supports absence.

But the same fixture's `data-view-name` values, enumerated in full (17 distinct,
45 occurrences), contain this:

```
 11  viewer-list-item              the viewer rows
  7  image
  6  viewer-list-item-cta
  4  relationship-building-button
  3  search-filter-top-bar-select  the filters  -> N 133
  2  viewer-list-item-company-logo
  2  message-button
  1  wvmp-entity-list-next-page-loaded   the viewer-list PAGINATOR
  1  viewer-list-tab-control             -> N 134
  1  viewer-list-see-all-recruiters
  1  viewer-list
  1  search-filter-top-bar-reset
  1  line-chart                          the trend graph -> N 135
  1  edge-creation-follow-action
  1  edge-creation-connect-action
  1  desktop-header-title-popover
  1  analytics-section-show-more    <-- THIS
```

**`analytics-section-show-more`.** LinkedIn's own name for the control the tally
recorded as `Show more analytics`. It is a DIFFERENT view name from
`wvmp-entity-list-next-page-loaded`, which kills the obvious objection that
"Show more analytics" merely loads more viewer rows -- the paginator is named
separately and is right there beside it. By its own name this control reveals an
additional analytics SECTION, and **it has never been pressed on a reading that
survived.**

### The press that was attempted proves nothing

Run 4 did press. The result, from the capture:

```
profile_views  unpressed: 68 controls
profile_views  pressed:   15 controls
DELTA: controls_read -53
shaped names that APPEARED   (0): []
shaped names that DISAPPEARED (29): [... "Show more analytics" ...]
```

Fifty-three controls gone, **zero appeared** -- including the global nav and
footer. That is a navigation or a teardown, not an expansion, and the capture's
own author says so: *"Nothing expanded. The page was REPLACED."* A post-press
reading of a page you have left cannot testify about the page you left.

### And the repository's own shipped reader forbids the inference

`read_profile_views_insights`, the function that reads this exact page, closes
its docstring with a standing rule:

> *"`observed` is always populated ... **Absent is UNKNOWN here, never zero:
> this reader does not scroll, and the page defers most of itself.**"*

The shipped instrument for this surface declares, as a matter of design, that
absence on it is unknown. N 136 is an absence claim about that surface.

### One measurement, quoted three times, reads like three confirmations

The "no top-companies, no top-locations" claim appears in `dom.py` (the
`VIEWS_CHART_VIEW_NAME` docstring), in `server.py:1652-1656` as a comment, and in
the census row. All three trace to the SAME fixture plus the SAME 2026-09-03
read. Three sites, one reading. That is the relayed-measurement class with a
codebase as the receiver.

### The inconsistency, in one sentence

**`N 133` and `N 134` are GAP because controls on that page are unpressed;
`N 136` is closed ABSENT on a reading taken with those same controls unpressed.
One page, one press state, two verdicts.**

### VERDICT

**N 136 should read `GAP`, blocker `ANALYTICS-CONTROLS-UNPRESSED`** -- the
blocker its two neighbours already carry. The narrow true statement, which is
worth keeping verbatim in the cell, is: *no breakdown panel is drawn on the
UNPRESSED render of `/analytics/profile-views/`, in the committed capture or on
the 2026-09-03 live read; the page carries exactly one unpressed control,
`analytics-section-show-more`, whose own view name says it reveals a further
analytics section.*

**REOPENER, now cheap and specific:** a single `linkedin_who_viewed_me` call
returns `insights.observed.view_names` -- see section 4.

### NOT WRITTEN, ON PURPOSE

I did not edit either census cell. `census-defects` and three sibling waves are
live in those files, the "CORRECTED BY" marker has already split the census
parser's table once (`5d0efb5`), and `build_blocker_map.py --write` is barred to
me. Both corrections above are stated as exact cell replacements so they can be
applied in one pass by whoever owns the freeze.

---

# 2. THE CHEAPEST WIN: J 123 AND N 135 ARE BUILT AND UNFIRED

Both are `COVERED-UNFIRED`. I traced both chains end to end from the current
tree, re-deriving every line number -- the numbers in the banking documents have
since moved.

## J 123 -- Premium hiring-company insights -- REACHABLE

```
linkedin_job_detail(job_id: str)                                 server.py:3881
  out["insights"] = await dom.read_job_insight_panels(page)      server.py:4136
    -> returns dict with key "company_insights"                    dom.py:8349
  return out
```

`read_job_insight_panels` builds `company_insights` from the section whose
heading starts with `JOB_COMPANY_PANEL_PREFIX` = `"Exclusive Job Seeker Insights
about "` -- LinkedIn's own name for the Premium panel -- and republishes the
heading as the SHAPE `Exclusive Job Seeker Insights about <company>`, so the
employer never leaves the reader.

## N 135 -- the weekly viewer trend graph -- REACHABLE

```
linkedin_who_viewed_me(limit: int = DEFAULT_LIMIT)               server.py:1551
  extra["insights"] = await dom.read_profile_views_insights(page)  server.py:1664
    -> returns dict with key "trend"                               dom.py:8628
  return shape.envelope(..., extra=extra)
    envelope: if extra: out.update(extra)                        shape.py:3985
```

`out.update(extra)` puts `insights` at the TOP LEVEL of the result, not nested
under `extra`. The trend field survives even where LinkedIn drops
`data-view-name`: the reader has a text fallback that finds the chart's own
sentence ("Line chart with N data points.") directly.

## BOTH CHAINS FAIL LOUDLY, WHICH IS WHY THE FIRING RULE HAS A PRECONDITION

Both assignments sit inside `try/except Exception`, and **neither except is
silent** -- each records `insights_error` carrying the exception TYPE:

```python
try:
    out["insights"] = await dom.read_job_insight_panels(page)
except Exception as exc:  # noqa: BLE001 - reported, never raised
    out["insights_error"] = type(exc).__name__
```

with the design stated above it: *"a silent absence here would read as 'LinkedIn
shows you no insights', which is a different and false claim."*

**So the firing rule is: check `insights_error` FIRST. If it is present, nothing
promotes** -- the reader failed, and the exception type is the finding, not the
row.

## BANKED HONESTLY

Both stay `COVERED-UNFIRED` in this document. Nothing has been fired. Section 4
is what would move them, and only a session that actually runs it may write
`COVERED-PROVEN`.

---

# 3. THE REMAINING ROWS, ONE DISPOSITION EACH

Evidence sweep across all 14 (census cell + blocker-map row + code reach +
address reach) is at
`_audit/_scratch/_rowsweep-premium.md` (gitignored, not tracked). Every one of
the 14 was found in both the census and the blocker map. Its control --
`aria-expanded` in `readonly.py` -- returned **0**, as predicted.

## NEEDS AN ADMISSION I DID NOT WRITE

**J 113, J 114** -- Page Insights (Premium), `COMPANY-PAGE-SURFACE`.
`/company/<slug>/` is **not on the read allowlist**. The two `/company/` hits in
`readonly.py` are a comment (`:562`) and `/mynetwork/network-manager/company/`
(`:796`), a network-manager filter route -- not a Company Page admission. The
census text agrees: *"Needs `/company/<slug>/` ... on the read allowlist."*
A sibling wave owns `readonly.py` for company-page work. **I did not touch it.**
Sanity control run: `page insight` -> 0 hits; the 7 `headcount` hits are
`shape.py` commentary about the job-posting headcount field, a different thing.

## NEEDS A LIVE SESSION -- EXACT CALL IN SECTION 4

**J 123, N 135** -- above.

**J 124** (Premium AI company intelligence), **J 126** (Premium AI job-fit tips)
-- `PREMIUM-JOBS-SURFACES`. These are **not** entitlement-blocked and they are
**not** unreached: `dom.py` already names the two controls that hide them,
measured once each in both committed job captures and on a live posting:

```python
JOB_COLLAPSED_CONTROL_NAMES: tuple[str, ...] = (
    "Show match details",
    "Show Premium Insights",
)
```

and `read_job_insight_panels` REPORTS them, by name, in
`more_behind_a_control`, on the stated principle that *"naming what this server
will not do is worth more than five silent nulls."* The same comment records
ZERO occurrences of the text behind them: *"it is one click away, and a click is
a different permission from a read."*
**So these two rows are a PRESS decision, not a build and not a subscription.**
Section 4 call 3 produces the citable evidence for free.

**N 132** -- switch Search appearances / WVYP, `SEARCH-APPEARANCES-SURFACE`.
Nearly closed and mis-shelved as a Premium row. `/analytics/search-appearances/`
IS admitted (`readonly.py:252`), `dom.read_search_appearances` exists, and the
page HAS been read live twice on 2026-09-05 (108 appearances both times). **What
is missing is a TOOL that returns the count** -- no entitlement question at all.

**PREMIUM CAVEAT, MEASURED, AND IT BEARS ON THE WHOLE QUESTION:** the unpressed
tally of `/analytics/search-appearances/` carries the control
**`Unlock details by upgrading`** -- on the account these documents record as
Premium Career. The same run measured the profile-views page at **0** hits for
`unlock|upgrade|premium`. Two analytics addresses, one account, and only one of
them upsells. This is precisely the case `premium.py`'s five-state model exists
for -- *"an upsell can sit beside a live subscription, so this does not resolve
and does not guess."* **It is the one live hint that holding Premium Career may
not unlock every row labelled Premium**, and it is a reason to run call 1 of the
session script rather than assume.

## RULED TO REFUSE -- NOT A GAP IN THE ORDINARY SENSE

**J 129** (InMail the job poster), **N 192** (InMail non-connection attendees).
Both are sends. Both sit downstream of `send_message`, which is
`COVERED-CANNOT-DELIVER`: it refuses at `_recipient_gate` (`writes.py:7799`),
which requires exactly one committed recipient whose accessible name carries the
operator's own needle, word-bounded, compared inside the page. Its docstring:

> *"IT IS EXPECTED TO REFUSE ON FIRST USE, and that is the design rather than a
> defect ... too strict costs a retry, too loose commits a stranger to an
> irreversible message under his name."*

J 129 additionally needs a compose surface distinct from the message composer,
plus a verification `send_message` cannot supply today. **Neither is an
entitlement problem; both are the recipient-addressing problem wearing a Premium
label.**

**M M47** -- respond to a Recruiter InMail, `THREAD-REPLY-BOX`. **This is the
most tractable of the three and the reason it has its own blocker name: a reply
in an existing thread needs no typeahead, because the thread has already
committed the recipient.** `/messaging/thread/` is already admitted for READ
(`readonly.py:200`). Checked against the prohibition table: `PERMANENTLY_FORBIDDEN`
contains `auto_accept_or_auto_reply` -- *"a reply in his name that he did not
read is a message from a stranger wearing his face."* The load-bearing words are
**"that he did not read"**: an operator-composed, operator-reviewed reply is NOT
covered by that ruling. An auto-reply is permanently out; a single reviewed reply
under the normal grant TTL is an open design question, not a forbidden one.

## STUCK ON THE CENSUS MACHINERY, NOT ON LINKEDIN

**J 78** (cover-letter assist), **J 79**, **J 80** (Top Choice x2) -- `UNASSIGNED`.
Nothing about these rows is measured, refused or unreachable. They are stuck
because a committed probe names SIX rows (J 78-J 83) against
`PREMIUM-APPLY-SURFACES` while the ledger publishes FIVE, so filing all six trips
an over-count assertion and filing five would be a choice wearing a forced row's
clothes. `PREMIUM-APPLY-SURFACES` currently holds **zero** rows in
`blocker-map.tsv`. Request 2a was filed, then **retracted by its own author**
(`_audit/2026-09-19-blocker-map-ruling-requests.md:330`), and the caution there
records that the blocker does not cleanly close even with J 81 removed.
**Sibling waves own this adjudication. I report it and leave it.** Worth saying
to the operator plainly: three Premium rows are open because of a counting rule
in our own ledger, not because of anything LinkedIn does.

## GENUINELY UNREACHED

**P B9** -- Premium profile badge show / hide, `BADGES-SURFACE`. Census reason
cell: *"no tool, no reason."* Code reach: `profile badge` -> **0 hits**. Sanity
control, because a zero needs one: sibling row B8's term `top voice` -> **0 hits**
as well, so both badge-display capabilities are equally unreached and the zero is
not an artifact of one unlucky search term. Bare `badge` returns 387 hits, all of
them the notification/invitation badge -- a different thing entirely, and the
reason the narrow term is the honest one.

## ANOTHER WAVE'S, AND I LEFT THEM ALONE

**N A7, N A8, N A9** -- auto-invitations, invite similar-Page followers,
`ADMIN-RIGHTS-NOT-HELD`. A sibling wave owns this blocker. **I did not read them
in, did not file them, and did not touch them.**

---

# 4. THE SINGLE SESSION SCRIPT

Three read calls, in this order, in one sitting. **Writes stay off**
(`LINKEDIN_ENABLE_WRITES` unset). No press, no navigation, nothing irreversible.

### Call 1 -- `linkedin_premium_status()`

No parameters. Opens `/premium/my-premium/` and returns one of five states:
`entitled`, `not_entitled`, `ambiguous`, `unmatched`, `error`.

Promotes no row by itself. It is here first because it turns "I have Premium"
into a measurement, and because of the `Unlock details by upgrading` string
measured on the search-appearances page: if that state comes back `ambiguous`,
every row below has to be read in that light. Record the state verbatim,
including `ambiguous` and `unmatched` -- both are real answers and neither may be
rounded up.

### Call 2 -- `linkedin_who_viewed_me()`

`limit` defaults to `DEFAULT_LIMIT`; no required parameters.

1. **Check `result.insights_error` first.** If present, STOP for this call:
   nothing promotes, and the exception type is the finding.
2. `result.insights.trend.present` and `result.insights.trend.description`
   -- a non-null description **promotes N 135 to COVERED-PROVEN.**
3. `result.insights.observed.view_names` -- **the N 136 instrument.** The reader
   collects every `data-view-name` on the page, unfiltered, up to 60.
   * **NON-EMPTY** -> a real measurement of the rendered DOM. Absence of any
     locations / industries / companies view name then settles N 136 as absent
     on the unpressed render, on an instrument that COULD have shown it.
     Expect `analytics-section-show-more` to be among them.
   * **EMPTY** -> **N 136 stays open and the call proved nothing about it.**
     This is a documented failure mode, not a surprise: the live page on
     2026-09-03 carried no `data-view-name` attribute anywhere, which is exactly
     why the reader ships a `<label>`-text fallback for its filters.
4. `result.insights.observed.main_chars` -- how much of the page rendered. A
   small number means the page deferred itself and no absence claim is available
   from this reading at all.
5. The viewer rows themselves are the 365-day Premium window in use.

### Call 3 -- `linkedin_job_detail(job_id="<a live posting id>")`

One required parameter, a string.

1. **Check `result.insights_error` first**, same rule.
2. `result.insights.company_insights.heading` and `.lines` -- content here
   **promotes J 123 to COVERED-PROVEN.** The heading comes back as the shape
   `Exclusive Job Seeker Insights about <company>`; the employer is replaced
   before it leaves the reader, so the result is safe to paste.
3. `result.insights.more_behind_a_control` -- expect `Show match details` and
   `Show Premium Insights`. **That list is the citable evidence that J 124 and
   J 126 are behind a named, rendered, unpressed control rather than behind the
   subscription**, which re-diagnoses both rows without pressing anything.
4. `result.insights.applicant_insights` corroborates the neighbouring rows in
   the same chain.

### WHAT ONE SITTING BUYS

* **2 rows promoted** to COVERED-PROVEN: J 123, N 135.
* **1 verdict settled** -- N 136 -- or explicitly left open WITH its reason
  recorded, which is the outcome that stops it being closed wrongly a second time.
* **2 rows re-diagnosed** from "GAP, unknown" to "GAP, behind a named press":
  J 124, J 126.
* **1 premise measured**: the entitlement state itself.

### WHAT IT CANNOT DO, SAID SO NOBODY EXPECTS IT

* **J 127 does not close.** Call 1 opens the right page, but
  `read_premium_surface` reads `a`/`button` names against 16 needles and returns
  no page text by construction. **No call on the current 44-tool surface can
  report a balance.** J 127 closes only after a numeric reader is built -- and
  that reader must ship with the closed-alphabet shaper (`[0-9]{1,N}`, never
  `\d`), because a balance line can carry a plan name beside the number. Ship it
  shown failing.
* **J 113 / J 114 do not close.** They need `/company/<slug>/` admitted. Not
  admitted; not mine to write.
* **No write row moves** -- J 78/79/80, J 129, M M47, N 192, P B9 all need writes
  enabled, and the InMail family additionally needs a recipient the gate can
  confirm.
